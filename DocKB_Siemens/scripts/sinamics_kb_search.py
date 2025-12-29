#!/usr/bin/env python3
"""
sinamics-kb-search: Knowledge Base Search Tool
Interfaccia per consultare la SINAMICS Knowledge Base da Claude Code
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
import re


class SinamicsKBSearch:
    """Interfaccia di ricerca per la knowledge base SINAMICS"""

    def __init__(self, kb_dir: str = "knowledge_base"):
        """Inizializza la ricerca nella KB"""
        self.kb_dir = Path(kb_dir)
        self.index_file = self.kb_dir / "index.json"
        self.search_file = self.kb_dir / "search_index.json"
        self.sections_dir = self.kb_dir / "sections"
        self.metadata_file = self.kb_dir / "metadata.json"

        self._validate_kb()
        self._load_indexes()

    def _validate_kb(self) -> None:
        """Valida che la KB esista"""
        if not self.kb_dir.exists():
            raise FileNotFoundError(f"Knowledge base non trovata: {self.kb_dir}")
        if not self.index_file.exists():
            raise FileNotFoundError(f"Indice non trovato: {self.index_file}")

    def _load_indexes(self) -> None:
        """Carica gli indici in memoria"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            self.index = json.load(f)

        with open(self.search_file, 'r', encoding='utf-8') as f:
            self.search_index = json.load(f)

        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ricerca per keyword nel contenuto delle sezioni

        Args:
            keyword: Parola chiave da cercare
            limit: Numero massimo di risultati

        Returns:
            Lista di sezioni corrispondenti
        """
        results = []
        keyword_lower = keyword.lower()
        pattern = re.compile(keyword_lower, re.IGNORECASE)

        # Ricerca nel search index prima
        for category, sections in self.search_index.items():
            for section in sections:
                if keyword_lower in category.lower() or keyword_lower in str(section).lower():
                    results.append({
                        'type': 'category',
                        'category': category,
                        'section_id': section.get('section_id'),
                        'relevance': section.get('relevance', 0.5)
                    })

        # Ordina per relevance e limita
        results = sorted(results, key=lambda x: x.get('relevance', 0), reverse=True)[:limit]
        return results

    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Ricerca per categoria

        Args:
            category: Categoria di ricerca

        Returns:
            Sezioni della categoria
        """
        category_lower = category.lower()

        if category_lower not in self.search_index:
            available = list(self.search_index.keys())
            raise ValueError(f"Categoria '{category}' non trovata. Disponibili: {', '.join(available)}")

        sections = self.search_index[category_lower]
        return [
            {
                'section_id': s['section_id'],
                'relevance': s.get('relevance', 0.5),
                'preview': s.get('content_preview', '')
            }
            for s in sections
        ]

    def get_section(self, section_id: str) -> Dict[str, Any]:
        """
        Recupera una sezione completa

        Args:
            section_id: ID della sezione (es. sezione_000001)

        Returns:
            Dati completi della sezione
        """
        section_file = self.sections_dir / f"{section_id}.json"

        if not section_file.exists():
            raise FileNotFoundError(f"Sezione non trovata: {section_id}")

        with open(section_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_chapter(self, chapter_id: str) -> Dict[str, Any]:
        """
        Recupera informazioni di un capitolo

        Args:
            chapter_id: ID del capitolo (es. ch_0)

        Returns:
            Dati del capitolo
        """
        for chapter in self.index.get('chapters', []):
            if chapter['id'] == chapter_id:
                return chapter

        raise ValueError(f"Capitolo non trovato: {chapter_id}")

    def list_chapters(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Lista tutti i capitoli

        Args:
            limit: Numero massimo di capitoli

        Returns:
            Lista di capitoli
        """
        chapters = self.index.get('chapters', [])
        if limit:
            chapters = chapters[:limit]

        return [
            {
                'id': ch['id'],
                'title': ch.get('title', ''),
                'sections_count': ch.get('sections_count', 0)
            }
            for ch in chapters
        ]

    def list_categories(self) -> List[str]:
        """Lista le categorie di ricerca disponibili"""
        return list(self.search_index.keys())

    def get_metadata(self) -> Dict[str, Any]:
        """Ritorna i metadati della KB"""
        return {
            'title': self.metadata.get('title', 'SINAMICS Knowledge Base'),
            'version': self.metadata.get('version', ''),
            'total_sections': self.metadata.get('total_sections', 0),
            'total_chapters': self.metadata.get('total_chapters', 0),
            'categories': self.list_categories(),
        }

    def navigate(self, section_id: str, direction: str = 'next') -> Optional[Dict[str, Any]]:
        """
        Naviga tra sezioni

        Args:
            section_id: ID della sezione corrente
            direction: 'next' o 'previous'

        Returns:
            Sezione successiva/precedente
        """
        try:
            section = self.get_section(section_id)
            link_id = section.get('links', {}).get(direction)

            if not link_id:
                return None

            return self.get_section(link_id)
        except FileNotFoundError:
            return None


def format_results(results: List[Dict[str, Any]], verbose: bool = False) -> str:
    """Formatta i risultati per output CLI"""
    if not results:
        return "Nessun risultato trovato."

    output = []
    for i, result in enumerate(results, 1):
        if 'section_id' in result:
            output.append(f"{i}. {result['section_id']}")
            if 'relevance' in result:
                output.append(f"   Relevance: {result['relevance']:.2%}")
            if 'preview' in result and result['preview']:
                preview = result['preview'][:80].replace('\n', ' ')
                output.append(f"   Preview: {preview}...")
        elif 'category' in result:
            output.append(f"{i}. [{result['category']}] {result['section_id']}")
            output.append(f"   Relevance: {result['relevance']:.2%}")

    return '\n'.join(output)


def main():
    """Interfaccia CLI principale"""
    parser = argparse.ArgumentParser(
        description='SINAMICS Knowledge Base Search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Esempi:
  %(prog)s --search "parametri di sicurezza"
  %(prog)s --category parameter
  %(prog)s --get sezione_000001
  %(prog)s --chapter ch_0
  %(prog)s --list-chapters
  %(prog)s --list-categories
  %(prog)s --metadata
        '''
    )

    parser.add_argument('--kb-dir', default='knowledge_base', help='Directory knowledge base')
    parser.add_argument('--search', help='Ricerca per keyword')
    parser.add_argument('--category', help='Ricerca per categoria')
    parser.add_argument('--get', metavar='SECTION_ID', help='Recupera una sezione')
    parser.add_argument('--chapter', help='Informazioni su un capitolo')
    parser.add_argument('--list-chapters', action='store_true', help='Lista tutti i capitoli')
    parser.add_argument('--list-categories', action='store_true', help='Lista categorie')
    parser.add_argument('--navigate', metavar='SECTION_ID', help='Naviga sezione (con --direction)')
    parser.add_argument('--direction', choices=['next', 'previous'], default='next')
    parser.add_argument('--metadata', action='store_true', help='Mostra metadati KB')
    parser.add_argument('--limit', type=int, default=10, help='Limite risultati')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Output verbose')

    args = parser.parse_args()

    try:
        kb = SinamicsKBSearch(args.kb_dir)

        # Esegui comando
        if args.search:
            results = kb.search_by_keyword(args.search, limit=args.limit)
            output = format_results(results, verbose=args.verbose)

        elif args.category:
            results = kb.search_by_category(args.category)
            output = format_results(results, verbose=args.verbose)

        elif args.get:
            result = kb.get_section(args.get)
            output = json.dumps(result, indent=2, ensure_ascii=False)

        elif args.chapter:
            result = kb.get_chapter(args.chapter)
            output = json.dumps(result, indent=2, ensure_ascii=False)

        elif args.list_chapters:
            chapters = kb.list_chapters(limit=args.limit)
            output = json.dumps(chapters, indent=2, ensure_ascii=False) if args.json else \
                     '\n'.join([f"{ch['id']}: {ch['title']} ({ch['sections_count']} sezioni)"
                              for ch in chapters])

        elif args.list_categories:
            categories = kb.list_categories()
            output = json.dumps(categories, indent=2, ensure_ascii=False) if args.json else \
                     '\n'.join(categories)

        elif args.navigate:
            result = kb.navigate(args.navigate, args.direction)
            if result:
                output = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                output = f"Nessuna sezione {args.direction}."

        elif args.metadata:
            metadata = kb.get_metadata()
            output = json.dumps(metadata, indent=2, ensure_ascii=False)

        else:
            parser.print_help()
            sys.exit(0)

        if args.json and not args.json:
            pass
        print(output)

    except Exception as e:
        print(f"Errore: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
