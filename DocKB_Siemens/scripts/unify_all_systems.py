#!/usr/bin/env python3
"""
Unifica SINAMICS + S7-1500 in un unico master index globale
Sistema completo di documentazione tecnica Siemens
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class MasterUnifiedKB:
    """Master unified KB per SINAMICS + S7-1500"""

    def __init__(self):
        self.systems = {}  # {system_name: {kbs_data}}
        self.master_index = {}
        self.master_search_index = defaultdict(list)
        self.master_alarms = {}
        self.master_faults = {}

    def load_system(self, system_name: str, unified_kb_dir: str) -> None:
        """Carica un sistema già unificato"""
        kb_path = Path(unified_kb_dir)
        index_file = kb_path / "index.json"
        alarms_file = kb_path / "alarms_faults.json"
        search_file = kb_path / "search_index.json"

        if not index_file.exists():
            print(f"❌ Index non trovato: {index_file}")
            return

        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)

        alarms_data = {}
        if alarms_file.exists():
            with open(alarms_file, 'r', encoding='utf-8') as f:
                alarms_data = json.load(f)

        search_data = {}
        if search_file.exists():
            with open(search_file, 'r', encoding='utf-8') as f:
                search_data = json.load(f)

        self.systems[system_name] = {
            'path': kb_path,
            'index': index_data,
            'alarms': alarms_data.get('alarms', {}),
            'faults': alarms_data.get('faults', {}),
            'search_index': search_data,
            'metadata': index_data.get('metadata', {})
        }

        print(f"✓ Caricato sistema: {system_name}")
        metadata = self.systems[system_name]['metadata']
        print(f"  Sezioni: {metadata.get('total_sections', 0):,}")
        print(f"  Capitoli: {metadata.get('total_chapters', 0)}")
        print(f"  Allarmi: {len(self.systems[system_name]['alarms'])}")
        print(f"  Fault: {len(self.systems[system_name]['faults'])}")

    def build_master_index(self) -> Dict[str, Any]:
        """Costruisce l'indice master"""
        print("\n🔗 Costruzione master index...")

        total_sections = sum(
            system['metadata'].get('total_sections', 0)
            for system in self.systems.values()
        )

        total_chapters = sum(
            system['metadata'].get('total_chapters', 0)
            for system in self.systems.values()
        )

        # Consolida allarmi e fault
        for system_name, system_data in self.systems.items():
            for code, alarm in system_data['alarms'].items():
                key = f"{system_name}_{code}"
                self.master_alarms[key] = {**alarm, 'source_system': system_name}

            for code, fault in system_data['faults'].items():
                key = f"{system_name}_{code}"
                self.master_faults[key] = {**fault, 'source_system': system_name}

            # Consolidate search indices
            for category, items in system_data['search_index'].items():
                for item in items:
                    item['source_system'] = system_name
                    self.master_search_index[category].append(item)

        self.master_index = {
            'metadata': {
                'title': 'SIEMENS Master Knowledge Base',
                'description': 'Master unified KB: SINAMICS S120/S150 + S7-1500',
                'version': '2025-12-21',
                'systems': list(self.systems.keys()),
                'total_systems': len(self.systems),
                'total_sections': total_sections,
                'total_chapters': total_chapters,
                'total_alarms': len(self.master_alarms),
                'total_faults': len(self.master_faults),
            },
            'systems': [
                {
                    'name': system_name,
                    'sections_count': system['metadata'].get('total_sections', 0),
                    'chapters_count': system['metadata'].get('total_chapters', 0),
                    'alarms_count': len(system['alarms']),
                    'faults_count': len(system['faults']),
                    'path': str(system['path']),
                }
                for system_name, system in self.systems.items()
            ],
        }

        print(f"✓ Master index costruito")
        print(f"  Sistemi: {len(self.systems)}")
        print(f"  Sezioni totali: {total_sections:,}")
        print(f"  Capitoli totali: {total_chapters}")
        print(f"  Allarmi totali: {len(self.master_alarms)}")
        print(f"  Fault totali: {len(self.master_faults)}")

        return self.master_index

    def save_master_kb(self, output_dir: str) -> None:
        """Salva il master KB"""
        out_path = Path(output_dir)
        out_path.mkdir(exist_ok=True, parents=True)

        print(f"\n💾 Salvataggio Master KB in {output_dir}...")

        # Salva master index
        with open(out_path / "master_index.json", 'w', encoding='utf-8') as f:
            json.dump(self.master_index, f, indent=2, ensure_ascii=False)
        print(f"  ✓ master_index.json")

        # Salva master search index
        with open(out_path / "master_search_index.json", 'w', encoding='utf-8') as f:
            json.dump(dict(self.master_search_index), f, indent=2, ensure_ascii=False)
        print(f"  ✓ master_search_index.json")

        # Salva master allarmi/fault
        with open(out_path / "master_alarms_faults.json", 'w', encoding='utf-8') as f:
            json.dump({
                'alarms': self.master_alarms,
                'faults': self.master_faults,
                'total_alarms': len(self.master_alarms),
                'total_faults': len(self.master_faults),
            }, f, indent=2, ensure_ascii=False)
        print(f"  ✓ master_alarms_faults.json ({len(self.master_alarms)} allarmi, {len(self.master_faults)} fault)")

        # Salva CSV
        import csv
        with open(out_path / "master_alarms_faults.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Tipo', 'Sistema', 'Codice', 'Descrizione', 'Soluzione'])

            for code, alarm in self.master_alarms.items():
                writer.writerow([
                    'ALARM',
                    alarm.get('source_system', ''),
                    code,
                    alarm.get('description', '')[:100],
                    alarm.get('solution', '')[:100]
                ])

            for code, fault in self.master_faults.items():
                writer.writerow([
                    'FAULT',
                    fault.get('source_system', ''),
                    code,
                    fault.get('description', '')[:100],
                    fault.get('solution', '')[:100]
                ])
        print(f"  ✓ master_alarms_faults.csv")

        # Salva metadata
        with open(out_path / "master_metadata.json", 'w', encoding='utf-8') as f:
            json.dump({
                'title': 'SIEMENS Master Knowledge Base',
                'description': 'Unified technical documentation for SINAMICS and S7-1500',
                'systems': len(self.systems),
                'total_sections': self.master_index['metadata']['total_sections'],
                'total_chapters': self.master_index['metadata']['total_chapters'],
                'total_alarms': len(self.master_alarms),
                'total_faults': len(self.master_faults),
                'creation_date': self.master_index['metadata'].get('version', ''),
                'system_list': self.master_index['metadata'].get('systems', []),
            }, f, indent=2, ensure_ascii=False)
        print(f"  ✓ master_metadata.json")

        print(f"\n✓ Master KB salvata in {output_dir}/")


def main():
    """Funzione principale"""
    print("=" * 80)
    print("UNIFICAZIONE MASTER KB: SINAMICS + S7-1500")
    print("=" * 80)

    kb_base_path = Path(__file__).parent.parent / "kb"

    master = MasterUnifiedKB()

    # Carica i due sistemi unificati
    print("\n📚 Caricamento sistemi...")

    sinamics_path = kb_base_path / "unified_knowledge_base"
    if sinamics_path.exists():
        master.load_system("SINAMICS_S120_S150", str(sinamics_path))

    s7_1500_path = kb_base_path / "unified_s7_1500_knowledge_base"
    if s7_1500_path.exists():
        master.load_system("S7-1500", str(s7_1500_path))

    if not master.systems:
        print("❌ Nessun sistema unificato trovato!")
        return

    # Costruisci master index
    master.build_master_index()

    # Salva master KB
    master_output_dir = str(kb_base_path / "master_knowledge_base")
    master.save_master_kb(master_output_dir)

    # Statistiche finali
    print("\n" + "=" * 80)
    print("📊 STATISTICHE FINALI MASTER KB")
    print("=" * 80)
    print(f"Sistemi totali: {len(master.systems)}")
    print(f"Sezioni totali: {master.master_index['metadata']['total_sections']:,}")
    print(f"Capitoli totali: {master.master_index['metadata']['total_chapters']}")
    print(f"Allarmi totali: {len(master.master_alarms)}")
    print(f"Fault totali: {len(master.master_faults)}")
    print(f"\nSistemi includedri:")
    for system in master.systems.keys():
        print(f"  • {system}")
    print(f"\nDirectory: kb/master_knowledge_base/")
    print("=" * 80)


if __name__ == "__main__":
    main()
