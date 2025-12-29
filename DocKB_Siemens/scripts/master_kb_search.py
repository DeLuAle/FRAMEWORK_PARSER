#!/usr/bin/env python3
"""
Master Knowledge Base Search Skill for Claude Code
Ricerca unificata in SINAMICS S120/S150 + S7-1500
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


class MasterKBSearcher:
    """Ricerca nel Master Knowledge Base"""

    def __init__(self, kb_dir: str = None):
        """Inizializza il searcher"""
        if kb_dir is None:
            # Default path per Master KB
            kb_dir = str(Path(__file__).parent.parent / "kb" / "master_knowledge_base")

        self.kb_path = Path(kb_dir)
        self.index = {}
        self.search_index = {}
        self.alarms_faults = {}

        self._load_kb()

    def _load_kb(self) -> None:
        """Carica la Master KB"""
        # Carica master index
        index_file = self.kb_path / "master_index.json"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)

        # Carica search index
        search_file = self.kb_path / "master_search_index.json"
        if search_file.exists():
            with open(search_file, 'r', encoding='utf-8') as f:
                self.search_index = json.load(f)

        # Carica allarmi/fault
        alarms_file = self.kb_path / "master_alarms_faults.json"
        if alarms_file.exists():
            with open(alarms_file, 'r', encoding='utf-8') as f:
                self.alarms_faults = json.load(f)

    def search_by_keyword(self, keyword: str, system: str = None,
                         category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Ricerca per keyword"""
        results = []

        for cat, items in self.search_index.items():
            if category and cat != category:
                continue

            for item in items:
                # Filtra per sistema se specificato
                if system and item.get('source_system') != system:
                    continue

                # Cerca in content_preview
                content = str(item.get('content_preview', '')).lower()
                keyword_lower = keyword.lower()

                if keyword_lower in content:
                    results.append({
                        'section_id': item.get('section_id', ''),
                        'section_num': item.get('section_num', 0),
                        'content': item.get('content_preview', '')[:200],
                        'category': cat,
                        'system': item.get('source_system', 'UNKNOWN'),
                        'relevance': item.get('relevance', 0.5)
                    })

        # Ordina per relevance e limita risultati
        results.sort(key=lambda x: -x['relevance'])
        return results[:limit]

    def search_alarm_by_code(self, code: str, system: str = None) -> Dict[str, Any]:
        """Ricerca allarme per codice"""
        alarms = self.alarms_faults.get('alarms', {})

        for key, alarm in alarms.items():
            if system and alarm.get('source_system') != system:
                continue

            if key.endswith(code) or alarm.get('code', '') == code:
                return {
                    'found': True,
                    'code': alarm.get('code', ''),
                    'type': 'ALARM',
                    'description': alarm.get('description', ''),
                    'solution': alarm.get('solution', ''),
                    'system': alarm.get('source_system', 'UNKNOWN'),
                    'section_id': alarm.get('section_id', '')
                }

        return {
            'found': False,
            'code': code,
            'type': 'ALARM',
            'error': f'Allarme {code} non trovato'
        }

    def search_fault_by_code(self, code: str, system: str = None) -> Dict[str, Any]:
        """Ricerca fault per codice"""
        faults = self.alarms_faults.get('faults', {})

        for key, fault in faults.items():
            if system and fault.get('source_system') != system:
                continue

            if key.endswith(code) or fault.get('code', '') == code:
                return {
                    'found': True,
                    'code': fault.get('code', ''),
                    'type': 'FAULT',
                    'description': fault.get('description', ''),
                    'solution': fault.get('solution', ''),
                    'system': fault.get('source_system', 'UNKNOWN'),
                    'section_id': fault.get('section_id', '')
                }

        return {
            'found': False,
            'code': code,
            'type': 'FAULT',
            'error': f'Fault {code} non trovato'
        }

    def search_alarm_or_fault(self, code: str, system: str = None) -> Dict[str, Any]:
        """Ricerca unificata allarme/fault"""
        # Prova prima gli allarmi
        result = self.search_alarm_by_code(code, system)
        if result['found']:
            return result

        # Se non trovato, prova i fault
        return self.search_fault_by_code(code, system)

    def list_systems(self) -> Dict[str, Any]:
        """Lista i sistemi disponibili"""
        return {
            'systems': self.index.get('metadata', {}).get('systems', []),
            'metadata': self.index.get('metadata', {})
        }

    def list_chapters(self, system: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Lista capitoli"""
        chapters = []

        for cat, items in self.search_index.items():
            if cat != 'chapters':
                continue

            for item in items:
                if system and item.get('source_system') != system:
                    continue

                chapters.append({
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'system': item.get('source_system', 'UNKNOWN'),
                    'sections_count': item.get('sections_count', 0)
                })

        return chapters[:limit]

    def get_system_stats(self, system: str = None) -> Dict[str, Any]:
        """Statistiche del sistema"""
        metadata = self.index.get('metadata', {})

        if system:
            # Filtra per sistema specifico
            for sys_info in self.index.get('systems', []):
                if sys_info.get('name') == system:
                    return {
                        'system': system,
                        'sections': sys_info.get('sections_count', 0),
                        'chapters': sys_info.get('chapters_count', 0),
                        'alarms': sys_info.get('alarms_count', 0),
                        'faults': sys_info.get('faults_count', 0)
                    }
        else:
            # Statistiche globali
            return {
                'total_systems': metadata.get('total_systems', 0),
                'total_sections': metadata.get('total_sections', 0),
                'total_chapters': metadata.get('total_chapters', 0),
                'total_alarms': metadata.get('total_alarms', 0),
                'total_faults': metadata.get('total_faults', 0),
                'systems': metadata.get('systems', [])
            }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Master Knowledge Base Search - SINAMICS + S7-1500',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Esempi:
  # Ricerca keyword
  %(prog)s --search "motor" --limit 10

  # Ricerca alarm
  %(prog)s --alarm "0230"

  # Ricerca fault
  %(prog)s --fault "F3000"

  # Ricerca unificata
  %(prog)s --code "2135"

  # Lista sistemi
  %(prog)s --list-systems

  # Statistiche
  %(prog)s --stats

  # Filtro per sistema S7-1500
  %(prog)s --search "parameter" --system S7-1500

  # Output JSON
  %(prog)s --search "thermal" --json
        '''
    )

    parser.add_argument('--search', help='Ricerca per keyword')
    parser.add_argument('--alarm', help='Ricerca allarme per codice')
    parser.add_argument('--fault', help='Ricerca fault per codice')
    parser.add_argument('--code', help='Ricerca unificata (alarm o fault)')
    parser.add_argument('--system', help='Filtra per sistema (SINAMICS_S120_S150 o S7-1500)')
    parser.add_argument('--category', help='Filtra per categoria')
    parser.add_argument('--list-systems', action='store_true', help='Lista sistemi disponibili')
    parser.add_argument('--list-chapters', action='store_true', help='Lista capitoli')
    parser.add_argument('--stats', action='store_true', help='Mostra statistiche')
    parser.add_argument('--limit', type=int, default=5, help='Limite risultati')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--kb-dir', help='Path della Master KB')

    args = parser.parse_args()

    # Inizializza searcher
    searcher = MasterKBSearcher(args.kb_dir)

    # Processa comandi
    result = None

    if args.search:
        result = searcher.search_by_keyword(
            args.search,
            system=args.system,
            category=args.category,
            limit=args.limit
        )
        if not args.json:
            print(f"\n🔍 Ricerca: '{args.search}'")
            if not result:
                print("   ❌ Nessun risultato trovato")
            else:
                for i, item in enumerate(result, 1):
                    print(f"\n   {i}. Sezione {item['section_num']} ({item['section_id']})")
                    print(f"      Contenuto: {item['content']}")
                    print(f"      Sistema: {item['system']} | Categoria: {item['category']} | Relevance: {item['relevance']}")

    elif args.alarm:
        result = searcher.search_alarm_by_code(args.alarm, system=args.system)
        if not args.json:
            if result['found']:
                print(f"\n✓ Allarme trovato: {result['code']}")
                print(f"  Descrizione: {result['description']}")
                print(f"  Soluzione: {result['solution']}")
                print(f"  Sistema: {result['system']}")
            else:
                print(f"\n❌ {result['error']}")

    elif args.fault:
        result = searcher.search_fault_by_code(args.fault, system=args.system)
        if not args.json:
            if result['found']:
                print(f"\n✓ Fault trovato: {result['code']}")
                print(f"  Descrizione: {result['description']}")
                print(f"  Soluzione: {result['solution']}")
                print(f"  Sistema: {result['system']}")
            else:
                print(f"\n❌ {result['error']}")

    elif args.code:
        result = searcher.search_alarm_or_fault(args.code, system=args.system)
        if not args.json:
            if result['found']:
                print(f"\n✓ {result['type']} trovato: {result['code']}")
                print(f"  Descrizione: {result['description']}")
                print(f"  Soluzione: {result['solution']}")
                print(f"  Sistema: {result['system']}")
            else:
                print(f"\n❌ {result['error']}")

    elif args.list_systems:
        result = searcher.list_systems()
        if not args.json:
            metadata = result.get('metadata', {})
            print(f"\n📚 Sistemi disponibili:")
            for sys in result.get('systems', []):
                print(f"  • {sys}")
            print(f"\n📊 Statistiche Master:")
            print(f"   Sezioni totali: {metadata.get('total_sections', 0):,}")
            print(f"   Capitoli totali: {metadata.get('total_chapters', 0)}")
            print(f"   Allarmi totali: {metadata.get('total_alarms', 0)}")
            print(f"   Fault totali: {metadata.get('total_faults', 0)}")

    elif args.list_chapters:
        result = searcher.list_chapters(system=args.system, limit=args.limit)
        if not args.json:
            print(f"\n📖 Capitoli disponibili:")
            for chapter in result:
                print(f"  • {chapter['title']}")
                print(f"    Sistema: {chapter['system']} | Sezioni: {chapter['sections_count']}")

    elif args.stats:
        result = searcher.get_system_stats(system=args.system)
        if not args.json:
            if 'system' in result:
                print(f"\n📊 Statistiche per {result['system']}:")
                print(f"   Sezioni: {result['sections']:,}")
                print(f"   Capitoli: {result['chapters']}")
                print(f"   Allarmi: {result['alarms']}")
                print(f"   Fault: {result['faults']}")
            else:
                print(f"\n📊 Statistiche Master Knowledge Base:")
                print(f"   Sistemi: {result['total_systems']}")
                print(f"   Sezioni: {result['total_sections']:,}")
                print(f"   Capitoli: {result['total_chapters']}")
                print(f"   Allarmi: {result['total_alarms']}")
                print(f"   Fault: {result['total_faults']}")

    else:
        parser.print_help()
        return

    # Output JSON se richiesto
    if args.json and result is not None:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
