#!/usr/bin/env python3
"""
Script per costruire una knowledge base strutturata dai JSON estratti
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict


class KnowledgeBaseBuilder:
    def __init__(self, json_dir: str = "output"):
        """Inizializza il builder della knowledge base"""
        self.json_dir = Path(json_dir)
        self.sections = {}
        self.chapters = {}
        self.search_index = defaultdict(list)
        self.metadata = {}

    def load_sections(self) -> Dict[int, Dict[str, Any]]:
        """Carica tutti i file sezione JSON (anche in sottocartelle)"""
        print(f"Ricerca file JSON in {self.json_dir}...")
        # Usa rglob per trovare i file anche nelle sottocartelle
        section_files = list(self.json_dir.rglob('sezione_*.json'))
        total_files = len(section_files)
        
        if total_files == 0:
            print(f"⚠ Nessun file trovato in {self.json_dir}. Verificare il percorso.")
            return {}

        print(f"Caricamento di {total_files:,} sezioni...")

        sections = {}
        # Contatore per ID univoci 
        global_id_counter = 1
        
        for idx, section_file in enumerate(section_files, 1):
            if idx % 1000 == 0:
                print(f"  → Caricamento: {idx:,} / {total_files:,} ({(idx/total_files)*100:.1f}%)")
                
            try:
                with open(section_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    section_id = global_id_counter
                    sections[section_id] = {
                        'id': f'sezione_{section_id:06d}',
                        'file': section_file.name,
                        'source_pdf': section_file.parent.name,
                        'content': data.get('content', ''),
                        'length': data.get('length', 0),
                        'line_count': data.get('line_count', 0)
                    }
                    global_id_counter += 1
            except Exception as e:
                print(f"⚠ Errore parsing {section_file.name}: {e}")

        print(f"✓ Caricate {len(sections):,} sezioni totali")
        self.sections = sections
        return sections

    def identify_chapters(self) -> Dict[str, List[int]]:
        """Identifica capitoli dal contenuto"""
        print("\nIdentificazione capitoli...")

        chapters = defaultdict(list)
        chapter_patterns = [
            r'^(\d+)\s+(.+?)$',  # Numero capitolo
            r'^([A-D])\s+(.+?)$',  # Appendici (A, B, C, D)
            r'^(Safety|Preface|List of|Index|References)',  # Sezioni speciali
        ]

        for section_id, section in self.sections.items():
            content = section['content'].strip()
            lines = content.split('\n')
            first_line = lines[0] if lines else ''

            # Cerca pattern di capitolo
            for pattern in chapter_patterns:
                match = re.match(pattern, first_line, re.IGNORECASE)
                if match:
                    chapter_key = match.group(1) if match.groups() else 'Unknown'
                    chapters[chapter_key].append(section_id)
                    break

        # Se non trovati capitoli, raggruppa per numero sezione
        if not chapters:
            print("⚠ Nessun pattern di capitolo trovato, utilizzo divisione per ogni 1000 sezioni")
            for section_id in self.sections.keys():
                chapter_id = f"ch{section_id // 1000:02d}"
                chapters[chapter_id].append(section_id)

        print(f"✓ Identificati {len(chapters)} capitoli")
        self.chapters = dict(sorted(chapters.items()))
        return self.chapters

    def build_search_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """Crea indice di ricerca per keywords"""
        total_sections = len(self.sections)
        print(f"\nCostruzione indice di ricerca per {total_sections:,} sezioni...")

        search_index = defaultdict(list)
        categories = {
            'parameter': [r'parameter', r'p[0-9]+', r'config', r'setting'],
            'fault': [r'fault', r'error', r'fail', r'warning'],
            'alarm': [r'alarm', r'alm', r'event'],
            'motor': [r'motor', r'drive', r'speed', r'frequency'],
            'safety': [r'safety', r'notice', r'warning', r'danger'],
            'function': [r'function', r'feature', r'operation'],
            'appendix': [r'appendix', r'a:', r'b:', r'c:', r'd:'],
        }

        # Pre-compila le regex per categoria per velocità
        compiled_regex = {cat: [re.compile(kw, re.IGNORECASE) for kw in kws] 
                         for cat, kws in categories.items()}

        for idx, (section_id, section) in enumerate(self.sections.items(), 1):
            if idx % 5000 == 0:
                print(f"  → Indicizzazione: {idx:,} / {total_sections:,} ({(idx/total_sections)*100:.1f}%)")
                
            content = section['content']
            
            for category, regex_list in compiled_regex.items():
                match_found = False
                for pattern in regex_list:
                    if pattern.search(content):
                        match_found = True
                        break
                
                if match_found:
                    search_index[category].append({
                        'section_id': section['id'],
                        'section_num': section_id,
                        'content_preview': content[:100].replace('\n', ' '),
                        'relevance': 0.8
                    })

        print(f"✓ Indicizzate {len(search_index)} categorie")
        self.search_index = search_index
        return dict(search_index)

    def build_master_index(self) -> Dict[str, Any]:
        """Crea indice master con struttura gerarchica"""
        print("\nCostruction indice master...")

        master_index = {
            'metadata': {
                'title': 'SINAMICS S120/S150 Knowledge Base',
                'version': '01/2013',
                'source': 'documento.pdf',
                'total_sections': len(self.sections),
                'total_chapters': len(self.chapters),
                'creation_date': self._get_timestamp(),
            },
            'chapters': [],
            'search_categories': list(self.search_index.keys())
        }

        # Aggiungi capitoli all'indice
        for chapter_id, section_ids in self.chapters.items():
            chapter_data = {
                'id': f'ch_{chapter_id}',
                'title': self._get_chapter_title(chapter_id, section_ids),
                'sections_count': len(section_ids),
                'section_ids': [self.sections[sid]['id'] for sid in sorted(section_ids)],
                'first_section': self.sections[min(section_ids)]['id'],
                'last_section': self.sections[max(section_ids)]['id'],
            }
            master_index['chapters'].append(chapter_data)

        print(f"✓ Indice master creato con {len(master_index['chapters'])} capitoli")
        self.metadata = master_index
        return master_index

    def _get_chapter_title(self, chapter_id: str, section_ids: List[int]) -> str:
        """Estrae il titolo del capitolo dalla prima sezione"""
        if section_ids:
            first_section = self.sections[min(section_ids)]
            content = first_section['content'].strip()
            lines = content.split('\n')
            # Prendi la prima riga non vuota come titolo
            for line in lines:
                if line.strip() and len(line.strip()) > 5:
                    return line.strip()[:100]
        return f"Chapter {chapter_id}"

    def enrich_sections(self) -> Dict[str, Any]:
        """Arricchisce le sezioni con metadati e link"""
        total = len(self.sections)
        print(f"\nArricchimento di {total:,} sezioni con metadati...")

        # Crea mappa inversa per velocità: section_id -> chapter_id
        section_to_chapter = {}
        for chap_id, s_ids in self.chapters.items():
            for sid in s_ids:
                section_to_chapter[sid] = chap_id

        enriched = {}

        for idx, (section_id, section) in enumerate(self.sections.items(), 1):
            if idx % 10000 == 0:
                print(f"  → Arricchimento: {idx:,} / {total:,} ({(idx/total)*100:.1f}%)")
                
            # Trova capitolo della sezione (veloce via mappa)
            chapter_id = section_to_chapter.get(section_id)

            # Estrai keywords dal contenuto
            keywords = self._extract_keywords(section['content'])

            enriched_section = {
                'id': section['id'],
                'file': section['file'],
                'chapter': chapter_id,
                'position': section_id,
                'content': section['content'],
                'metadata': {
                    'length': section['length'],
                    'line_count': section['line_count'],
                    'word_count': len(section['content'].split()),
                    'keywords': keywords,
                },
                'links': {
                    'previous': self._get_neighbor_section(section_id, -1),
                    'next': self._get_neighbor_section(section_id, 1),
                }
            }

            enriched[section['id']] = enriched_section

        print(f"✓ Arricchite {len(enriched):,} sezioni")
        return enriched

    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Estrae keywords dal testo"""
        # Parole comuni da escludere
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'di', 'da',
            'e', 'il', 'la', 'le', 'i', 'un', 'una', 'degli', 'delle'
        }

        words = re.findall(r'\b[a-z0-9]{4,}\b', text.lower())
        keywords = list(set(w for w in words if w not in stopwords))[:top_n]
        return keywords

    def _get_neighbor_section(self, section_id: int, offset: int) -> Optional[str]:
        """Ottiene sezione vicina"""
        neighbor_id = section_id + offset
        if neighbor_id in self.sections:
            return self.sections[neighbor_id]['id']
        return None

    def _get_timestamp(self) -> str:
        """Ritorna timestamp corrente"""
        from datetime import datetime
        return datetime.now().isoformat()

    def save_knowledge_base(self, output_dir: str = "knowledge_base") -> None:
        """Salva la knowledge base completa"""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        print(f"\nSalvataggio knowledge base in {output_dir}...")

        # Salva indice master
        with open(out_path / 'index.json', 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        print(f"✓ index.json salvato")

        # Salva search index
        with open(out_path / 'search_index.json', 'w', encoding='utf-8') as f:
            json.dump(dict(self.search_index), f, indent=2, ensure_ascii=False)
        print(f"✓ search_index.json salvato")

        # Salva sezioni arricchite
        enriched = self.enrich_sections()
        sections_dir = out_path / 'sections'
        sections_dir.mkdir(exist_ok=True)

        total_save = len(enriched)
        print(f"\nSalvataggio di {total_save:,} file sezione...")

        for idx, (section_id, enriched_data) in enumerate(enriched.items(), 1):
            if idx % 5000 == 0:
                print(f"  → Salvataggio: {idx:,} / {total_save:,} ({(idx/total_save)*100:.1f}%)")
                
            section_file = sections_dir / f"{section_id}.json"
            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_data, f, indent=2, ensure_ascii=False)

        print(f"✓ {len(enriched):,} sezioni arricchite salvate in sections/")

        # Salva metadata globali
        metadata = {
            'title': 'SINAMICS S120/S150 Knowledge Base',
            'version': '01/2013',
            'description': 'Knowledge base strutturata per Claude Code',
            'total_sections': len(self.sections),
            'total_chapters': len(self.chapters),
            'search_categories': list(self.search_index.keys()),
            'creation_date': self._get_timestamp(),
        }
        with open(out_path / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"✓ metadata.json salvato")

        print(f"\n✓ Knowledge base completata in {output_dir}/")


def main():
    """Funzione principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build Knowledge Base from extracted JSON sections')
    parser.add_argument('--input-dir', default='output', help='Directory containing extracted JSON sections (default: output)')
    parser.add_argument('--output-dir', default='knowledge_base', help='Directory where to save the KB (default: knowledge_base)')
    
    args = parser.parse_args()
    
    builder = KnowledgeBaseBuilder(json_dir=args.input_dir)

    # Carica sezioni
    builder.load_sections()

    if not builder.sections:
        print(f"Errore: Nessuna sezione trovata in {args.input_dir}")
        return

    # Identifica capitoli
    builder.identify_chapters()

    # Crea search index
    builder.build_search_index()

    # Crea indice master
    builder.build_master_index()

    # Salva knowledge base
    builder.save_knowledge_base(output_dir=args.output_dir)

    # Stampa statistiche
    print("\n=== Statistiche Knowledge Base ===")
    print(f"Input: {args.input_dir}")
    print(f"Capitoli: {len(builder.chapters)}")
    print(f"Sezioni: {len(builder.sections)}")
    print(f"Categorie ricerca: {len(builder.search_index)}")
    print(f"Directory: {args.output_dir}/")


if __name__ == "__main__":
    main()
