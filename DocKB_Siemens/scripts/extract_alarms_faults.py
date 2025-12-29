#!/usr/bin/env python3
"""
Estrae allarmi e fault dalla knowledge base SINAMICS
Crea file di configurazione per uso in TIA Portal
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class AlarmFaultExtractor:
    """Estrae e organizza dati di allarmi e fault"""

    def __init__(self, kb_dir: str = "knowledge_base"):
        self.kb_dir = Path(kb_dir)
        self.sections_dir = self.kb_dir / "sections"
        self.alarms = defaultdict(dict)
        self.faults = defaultdict(dict)

    def extract_from_section(self, section_id: str) -> Tuple[str, str, str]:
        """
        Estrae dati di alarm/fault da una sezione

        Args:
            section_id: ID della sezione

        Returns:
            Tuple (tipo, codice, descrizione) o None
        """
        section_file = self.sections_dir / f"{section_id}.json"

        if not section_file.exists():
            return None

        try:
            with open(section_file, 'r', encoding='utf-8') as f:
                section = json.load(f)

            content = section.get('content', '').lower()
            lines = section.get('content', '').split('\n')

            # Pattern per allarmi e fault
            alarm_pattern = r'(?:alarm|alm)\s+([0-9]+|[a-f0-9]{5})'
            fault_pattern = r'(?:fault|f[0-9]{4,5}|error|err)\s+([0-9]+|[a-f0-9]{5})'

            # Cerca pattern in contenuto
            alarm_match = re.search(alarm_pattern, content)
            fault_match = re.search(fault_pattern, content)

            description = '\n'.join(lines[:5])  # Prime 5 righe come descrizione

            if alarm_match:
                alarm_code = alarm_match.group(1)
                return ('alarm', alarm_code, description)
            elif fault_match:
                fault_code = fault_match.group(1)
                return ('fault', fault_code, description)

            return None
        except json.JSONDecodeError:
            return None

    def build_database(self) -> Dict[str, Dict]:
        """
        Costruisce il database di allarmi e fault

        Returns:
            Dizionario con allarmi e fault organizzati
        """
        print("Estrazione allarmi e fault dalla knowledge base...")

        # Cerca nella categoria alarm
        search_file = self.kb_dir / "search_index.json"
        if search_file.exists():
            with open(search_file, 'r', encoding='utf-8') as f:
                search_index = json.load(f)

            # Processa sezioni di allarmi
            if 'alarm' in search_index:
                print("\nELABORAZIONE ALLARMI:")
                for item in search_index['alarm'][:100]:  # Limita a 100
                    section_id = item.get('section_id')
                    content_preview = item.get('content_preview', '')

                    # Estrai codice allarme dal preview
                    alarm_match = re.search(r'([a-f0-9]{5}|[0-9]{4,5})', content_preview)
                    if alarm_match:
                        alarm_code = alarm_match.group(1)
                        description = content_preview[:200]

                        self.alarms[alarm_code] = {
                            'code': alarm_code,
                            'description': description.strip(),
                            'section_id': section_id,
                            'type': 'alarm'
                        }

            # Processa sezioni di fault
            if 'fault' in search_index:
                print("\nELABORAZIONE FAULT:")
                for item in search_index['fault'][:100]:  # Limita a 100
                    section_id = item.get('section_id')
                    content_preview = item.get('content_preview', '')

                    # Estrai codice fault dal preview
                    fault_match = re.search(r'([a-f0-9]{5}|[0-9]{4,5}|f[0-9]{4})', content_preview)
                    if fault_match:
                        fault_code = fault_match.group(1)
                        description = content_preview[:200]

                        self.faults[fault_code] = {
                            'code': fault_code,
                            'description': description.strip(),
                            'section_id': section_id,
                            'type': 'fault'
                        }

        print(f"\n✓ Estratti {len(self.alarms)} allarmi")
        print(f"✓ Estratti {len(self.faults)} fault")

        return {
            'alarms': dict(self.alarms),
            'faults': dict(self.faults),
            'total_alarms': len(self.alarms),
            'total_faults': len(self.faults),
        }

    def save_to_json(self, output_file: str = "alarms_faults.json") -> None:
        """Salva i dati in JSON"""
        data = self.build_database()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Database salvato: {output_file}")

    def save_to_csv(self, output_file: str = "alarms_faults.csv") -> None:
        """Salva i dati in CSV per Excel"""
        import csv

        data = self.build_database()

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(['Tipo', 'Codice', 'Descrizione', 'Sezione', 'Soluzione'])

            # Allarmi
            for code, alarm in sorted(data['alarms'].items()):
                writer.writerow([
                    'ALARM',
                    code,
                    alarm['description'],
                    alarm['section_id'],
                    'Vedere manuale SINAMICS'
                ])

            # Fault
            for code, fault in sorted(data['faults'].items()):
                writer.writerow([
                    'FAULT',
                    code,
                    fault['description'],
                    fault['section_id'],
                    'Vedere manuale SINAMICS'
                ])

        print(f"✓ CSV salvato: {output_file}")

    def save_to_scl_include(self, output_file: str = "Alarms_Faults.scl") -> None:
        """Genera un file SCL con i dati degli allarmi"""
        data = self.build_database()

        scl_content = '''(* Auto-generated from SINAMICS KB *)
(* Alarms and Faults Database for TIA Portal *)

TYPE AlarmRecord
STRUCT
    Code : STRING[10];
    Type : STRING[10];
    Description : STRING[256];
    Solution : STRING[256];
    SectionID : STRING[20];
END_STRUCT
END_TYPE

(* Tabella allarmi *)
VAR CONSTANT
    ALARM_TABLE : ARRAY [1..{alarm_count}] OF AlarmRecord := (
{alarms}
    );

    FAULT_TABLE : ARRAY [1..{fault_count}] OF AlarmRecord := (
{faults}
    );
END_VAR

FUNCTION SearchAlarm : AlarmRecord
    VAR_INPUT
        AlarmCode : STRING;
    END_VAR
    VAR
        i : INT;
        NotFound : AlarmRecord;
    END_VAR
BEGIN
    NotFound.Code := '';

    FOR i := 1 TO ARRAY_SIZE(ALARM_TABLE, 1) DO
        IF ALARM_TABLE[i].Code = AlarmCode THEN
            RETURN ALARM_TABLE[i];
        END_IF;
    END_FOR;

    RETURN NotFound;
END_FUNCTION

FUNCTION SearchFault : AlarmRecord
    VAR_INPUT
        FaultCode : STRING;
    END_VAR
    VAR
        i : INT;
        NotFound : AlarmRecord;
    END_VAR
BEGIN
    NotFound.Code := '';

    FOR i := 1 TO ARRAY_SIZE(FAULT_TABLE, 1) DO
        IF FAULT_TABLE[i].Code = FaultCode THEN
            RETURN FAULT_TABLE[i];
        END_IF;
    END_FOR;

    RETURN NotFound;
END_FUNCTION
'''

        # Genera righe allarmi
        alarm_entries = []
        for code, alarm in sorted(data['alarms'].items())[:50]:  # Limita a 50
            desc = alarm['description'].replace('"', '\\"')[:200]
            alarm_entries.append(
                f'        (\n'
                f'            Code := "{code}",\n'
                f'            Type := "ALARM",\n'
                f'            Description := "{desc}",\n'
                f'            Solution := "Consultare manuale SINAMICS S120/S150",\n'
                f'            SectionID := "{alarm.get("section_id", "")}"\n'
                f'        )'
            )

        # Genera righe fault
        fault_entries = []
        for code, fault in sorted(data['faults'].items())[:50]:  # Limita a 50
            desc = fault['description'].replace('"', '\\"')[:200]
            fault_entries.append(
                f'        (\n'
                f'            Code := "{code}",\n'
                f'            Type := "FAULT",\n'
                f'            Description := "{desc}",\n'
                f'            Solution := "Consultare manuale SINAMICS S120/S150",\n'
                f'            SectionID := "{fault.get("section_id", "")}"\n'
                f'        )'
            )

        alarms_str = ',\n'.join(alarm_entries)
        faults_str = ',\n'.join(fault_entries)

        scl_content = scl_content.format(
            alarm_count=len(alarm_entries),
            fault_count=len(fault_entries),
            alarms=alarms_str,
            faults=faults_str
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(scl_content)

        print(f"✓ File SCL generato: {output_file}")


def main():
    """Main function"""
    extractor = AlarmFaultExtractor(kb_dir="knowledge_base")

    print("=== Estrazione Allarmi e Fault da SINAMICS KB ===\n")

    # Estrai dati
    data = extractor.build_database()

    # Salva in vari formati
    print("\n=== Salvataggio file ===")
    extractor.save_to_json("alarms_faults.json")
    extractor.save_to_csv("alarms_faults.csv")
    extractor.save_to_scl_include("Alarms_Faults.scl")

    # Stampa statistiche
    print(f"\n=== Statistiche ===")
    print(f"Allarmi estratti: {data['total_alarms']}")
    print(f"Fault estratti: {data['total_faults']}")
    print(f"\nPrimi 5 allarmi:")
    for code, alarm in list(data['alarms'].items())[:5]:
        print(f"  {code}: {alarm['description'][:50]}...")

    print(f"\nPrimi 5 fault:")
    for code, fault in list(data['faults'].items())[:5]:
        print(f"  {code}: {fault['description'][:50]}...")


if __name__ == "__main__":
    main()
