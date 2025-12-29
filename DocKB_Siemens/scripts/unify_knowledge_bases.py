#!/usr/bin/env python3
"""
Unifica tutte le Knowledge Base in un indice master globale
Combina sezioni, capitoli, allarmi e fault da tutte le KB
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class UnifiedKnowledgeBase:
    """Crea una KB unificata da multiple KB separate"""

    def __init__(self):
        self.kbs = {}
        self.unified_index = {}
        self.unified_search_index = defaultdict(list)
        self.unified_alarms = {}
        self.unified_faults = {}

    def load_kb(self, kb_dir: str, kb_name: str, description: str = "") -> None:
        """Carica una KB"""
        kb_path = Path(kb_dir)
        index_file = kb_path / "knowledge_base" / "index.json"

        if not index_file.exists():
            print(f"❌ Index non trovato: {index_file}")
            return

        with open(index_file, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)

        self.kbs[kb_name] = {
            'path': kb_path,
            'index': kb_data,
            'description': description,
            'metadata': kb_data.get('metadata', {})
        }

        print(f"✓ Caricata KB: {kb_name}")
        print(f"  Sezioni: {self.kbs[kb_name]['metadata'].get('total_sections', 0)}")
        print(f"  Capitoli: {self.kbs[kb_name]['metadata'].get('total_chapters', 0)}")

    def load_alarms_faults(self, kb_dir: str, kb_name: str) -> None:
        """Carica allarmi e fault da una KB"""
        kb_path = Path(kb_dir)
        alarms_file = kb_path / "alarms_faults.json"

        if not alarms_file.exists():
            print(f"  ⚠ Allarmi/fault non trovati")
            return

        with open(alarms_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Aggiungi con prefisso KB
        for alarm_code, alarm_info in data.get('alarms', {}).items():
            key = f"{kb_name}_{alarm_code}"
            self.unified_alarms[key] = {
                **alarm_info,
                'source_kb': kb_name
            }

        for fault_code, fault_info in data.get('faults', {}).items():
            key = f"{kb_name}_{fault_code}"
            self.unified_faults[key] = {
                **fault_info,
                'source_kb': kb_name
            }

        print(f"  Allarmi: {len(data.get('alarms', {}))}")
        print(f"  Fault: {len(data.get('faults', {}))}")

    def build_unified_index(self) -> Dict[str, Any]:
        """Costruisce l'indice unificato"""
        print("\n🔗 Costruzione indice unificato...")

        total_sections = sum(
            kb['metadata'].get('total_sections', 0)
            for kb in self.kbs.values()
        )

        total_chapters = sum(
            kb['metadata'].get('total_chapters', 0)
            for kb in self.kbs.values()
        )

        self.unified_index = {
            'metadata': {
                'title': 'SINAMICS Unified Knowledge Base',
                'description': 'Unificazione di tutte le KB SINAMICS S120/S150',
                'version': '2025-12-21',
                'total_knowledge_bases': len(self.kbs),
                'total_sections': total_sections,
                'total_chapters': total_chapters,
                'total_alarms': len(self.unified_alarms),
                'total_faults': len(self.unified_faults),
            },
            'knowledge_bases': [
                {
                    'name': kb_name,
                    'description': kb['description'],
                    'sections_count': kb['metadata'].get('total_sections', 0),
                    'chapters_count': kb['metadata'].get('total_chapters', 0),
                    'path': str(kb['path']),
                }
                for kb_name, kb in self.kbs.items()
            ],
            'chapters': self._aggregate_chapters(),
            'search_categories': self._get_search_categories(),
        }

        print(f"✓ Indice unificato costruito")
        print(f"  Total sections: {total_sections:,}")
        print(f"  Total chapters: {total_chapters:,}")
        print(f"  Total alarms: {len(self.unified_alarms)}")
        print(f"  Total faults: {len(self.unified_faults)}")

        return self.unified_index

    def _aggregate_chapters(self) -> List[Dict[str, Any]]:
        """Aggrega capitoli da tutte le KB"""
        chapters = []
        chapter_id = 1

        for kb_name, kb in self.kbs.items():
            for chapter in kb['index'].get('chapters', []):
                chapters.append({
                    'id': f"ch_{chapter_id:04d}",
                    'source_kb': kb_name,
                    'original_id': chapter.get('id'),
                    'title': chapter.get('title', ''),
                    'sections_count': chapter.get('sections_count', 0),
                })
                chapter_id += 1

        return chapters

    def _get_search_categories(self) -> List[str]:
        """Ritorna categorie di ricerca disponibili"""
        categories = set()

        for kb in self.kbs.values():
            for chapter in kb['index'].get('chapters', []):
                categories.add('parameter')
                categories.add('fault')
                categories.add('alarm')
                categories.add('motor')
                categories.add('safety')
                categories.add('function')
                categories.add('appendix')

        return sorted(list(categories))

    def build_unified_search_index(self) -> Dict[str, List]:
        """Costruisce indice di ricerca unificato"""
        print("\n🔍 Costruzione indice ricerca unificato...")

        # Carica e combina search index da tutte le KB
        for kb_name, kb in self.kbs.items():
            search_file = kb['path'] / "knowledge_base" / "search_index.json"

            if search_file.exists():
                with open(search_file, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)

                for category, items in search_data.items():
                    for item in items:
                        item['source_kb'] = kb_name
                        self.unified_search_index[category].append(item)

        print(f"✓ Search index unificato: {len(self.unified_search_index)} categorie")

        return dict(self.unified_search_index)

    def save_unified_kb(self, output_dir: str = "unified_knowledge_base") -> None:
        """Salva la KB unificata"""
        out_path = Path(output_dir)
        out_path.mkdir(exist_ok=True)

        print(f"\n💾 Salvataggio KB unificata in {output_dir}...")

        # Salva indice master
        with open(out_path / "index.json", 'w', encoding='utf-8') as f:
            json.dump(self.unified_index, f, indent=2, ensure_ascii=False)
        print(f"  ✓ index.json")

        # Salva search index
        with open(out_path / "search_index.json", 'w', encoding='utf-8') as f:
            json.dump(dict(self.unified_search_index), f, indent=2, ensure_ascii=False)
        print(f"  ✓ search_index.json")

        # Salva allarmi e fault
        with open(out_path / "alarms_faults.json", 'w', encoding='utf-8') as f:
            json.dump({
                'alarms': self.unified_alarms,
                'faults': self.unified_faults,
                'total_alarms': len(self.unified_alarms),
                'total_faults': len(self.unified_faults),
            }, f, indent=2, ensure_ascii=False)
        print(f"  ✓ alarms_faults.json ({len(self.unified_alarms)} allarmi, {len(self.unified_faults)} fault)")

        # Salva CSV allarmi
        import csv
        with open(out_path / "alarms_faults.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Tipo', 'KB', 'Codice', 'Descrizione', 'Soluzione'])

            for code, alarm in self.unified_alarms.items():
                writer.writerow([
                    'ALARM',
                    alarm.get('source_kb', ''),
                    code,
                    alarm.get('description', '')[:100],
                    alarm.get('solution', '')[:100]
                ])

            for code, fault in self.unified_faults.items():
                writer.writerow([
                    'FAULT',
                    fault.get('source_kb', ''),
                    code,
                    fault.get('description', '')[:100],
                    fault.get('solution', '')[:100]
                ])
        print(f"  ✓ alarms_faults.csv")

        # Salva metadati
        with open(out_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump({
                'title': 'SINAMICS Unified Knowledge Base',
                'description': 'Knowledge base unificata da multiple manuali SINAMICS',
                'knowledge_bases': len(self.kbs),
                'total_sections': self.unified_index['metadata']['total_sections'],
                'total_chapters': self.unified_index['metadata']['total_chapters'],
                'total_alarms': len(self.unified_alarms),
                'total_faults': len(self.unified_faults),
                'creation_date': self.unified_index['metadata'].get('version', ''),
            }, f, indent=2, ensure_ascii=False)
        print(f"  ✓ metadata.json")

        print(f"\n✓ KB unificata salvata in {output_dir}/")


def main():
    """Funzione principale"""
    print("=" * 70)
    print("UNIFICAZIONE KNOWLEDGE BASE SINAMICS")
    print("=" * 70)

    # Base path per le KB
    kb_base_path = Path(__file__).parent.parent / "kb"

    unifier = UnifiedKnowledgeBase()

    # Carica tutte le KB
    print("\n📚 Caricamento Knowledge Base...")
    unifier.load_kb(
        str(kb_base_path / "sinamics_s120_communication"),
        "sinamics_s120_communication",
        "SINAMICS S120 Communication Function Manual 06/2019"
    )
    unifier.load_alarms_faults(str(kb_base_path / "sinamics_s120_communication"), "sinamics_s120_communication")

    unifier.load_kb(
        str(kb_base_path / "sinamics_s120_drive_functions"),
        "sinamics_s120_drive_functions",
        "SINAMICS S120 Drive Functions Function Manual 06/2020"
    )
    unifier.load_alarms_faults(str(kb_base_path / "sinamics_s120_drive_functions"), "sinamics_s120_drive_functions")

    unifier.load_kb(
        str(kb_base_path / "sinamics_s120_s150_list_manual"),
        "sinamics_s120_s150_list_manual",
        "SINAMICS S120/S150 List Manual 06/2020"
    )
    unifier.load_alarms_faults(str(kb_base_path / "sinamics_s120_s150_list_manual"), "sinamics_s120_s150_list_manual")

    # Costruisci indici unificati
    unifier.build_unified_index()
    unifier.build_unified_search_index()

    # Salva KB unificata in kb/unified_knowledge_base
    unified_output_dir = str(kb_base_path / "unified_knowledge_base")
    unifier.save_unified_kb(unified_output_dir)

    # Statistiche finali
    print("\n" + "=" * 70)
    print("📊 STATISTICHE FINALI")
    print("=" * 70)
    print(f"Knowledge Base unificate: {len(unifier.kbs)}")
    print(f"Sezioni totali: {unifier.unified_index['metadata']['total_sections']:,}")
    print(f"Capitoli totali: {unifier.unified_index['metadata']['total_chapters']:,}")
    print(f"Allarmi totali: {len(unifier.unified_alarms):,}")
    print(f"Fault totali: {len(unifier.unified_faults):,}")
    print(f"Directory: kb/unified_knowledge_base/")
    print("=" * 70)


if __name__ == "__main__":
    main()
