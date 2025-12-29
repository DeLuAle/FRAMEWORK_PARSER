#!/usr/bin/env python3
"""
Script per aggiungere rapidamente i 3 PDF alla Knowledge Base
"""

import subprocess
import sys
from pathlib import Path
import json

# Aggiungi scripts directory al path per importare i moduli
sys.path.insert(0, str(Path(__file__).parent))

def add_pdf_to_kb(pdf_file, kb_name, description):
    """Aggiunge un PDF come nuova Knowledge Base"""

    kb_dir = Path(__file__).parent.parent / "kb" / kb_name
    kb_dir.mkdir(exist_ok=True, parents=True)

    # Copia PDF
    import shutil
    dest_pdf = kb_dir / Path(pdf_file).name
    shutil.copy2(pdf_file, dest_pdf)

    print(f"\n📦 Elaborazione: {kb_name}")
    print(f"   PDF: {pdf_file}")

    # 1. Estrai JSON
    print(f"   → Estrazione JSON...")
    from extract_pdf_to_json import PDFExtractor
    extractor = PDFExtractor(str(dest_pdf))
    extractor.extract_to_json(str(kb_dir / 'output'))

    # 2. Costruisci KB
    print(f"   → Costruzione Knowledge Base...")
    from build_knowledge_base import KnowledgeBaseBuilder
    builder = KnowledgeBaseBuilder(str(kb_dir / 'output'))
    builder.load_sections()
    builder.identify_chapters()
    builder.build_search_index()
    builder.build_master_index()
    builder.save_knowledge_base(str(kb_dir / 'knowledge_base'))

    # 3. Estrai allarmi
    print(f"   → Estrazione allarmi/fault...")
    from extract_alarms_faults import AlarmFaultExtractor
    alarm_extractor = AlarmFaultExtractor(str(kb_dir / 'knowledge_base'))
    alarm_extractor.save_to_json(str(kb_dir / 'alarms_faults.json'))
    alarm_extractor.save_to_csv(str(kb_dir / 'alarms_faults.csv'))

    print(f"   ✓ Completato!")

    return {
        "name": kb_name,
        "pdf_file": str(dest_pdf),
        "kb_directory": str(kb_dir),
        "description": description,
        "status": "active"
    }

def main():
    """Aggiunge i 3 PDF"""

    # Riferimento alla cartella resources/pdfs
    resources_dir = Path(__file__).parent.parent / "resources" / "pdfs"

    pdfs = [
        (resources_dir / "pdf1.pdf", "sinamics_s120_communication",
         "SINAMICS S120 Communication Function Manual 06/2019"),
        (resources_dir / "pdf2.pdf", "sinamics_s120_drive_functions",
         "SINAMICS S120 Drive Functions Function Manual 06/2020"),
        (resources_dir / "pdf3.pdf", "sinamics_s120_s150_list_manual",
         "SINAMICS S120/S150 List Manual 06/2020"),
    ]

    print("=" * 70)
    print("AGGIUNTA PDF ALLA KNOWLEDGE BASE SINAMICS")
    print("=" * 70)

    registry = {"knowledge_bases": []}

    for pdf_file, kb_name, description in pdfs:
        if not Path(pdf_file).exists():
            print(f"❌ {pdf_file} non trovato")
            continue

        try:
            kb_entry = add_pdf_to_kb(str(pdf_file), kb_name, description)
            registry["knowledge_bases"].append(kb_entry)
        except Exception as e:
            print(f"❌ Errore: {e}")

    # Salva registry nella root
    registry_file = Path(__file__).parent.parent / "kb_registry.json"
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"✓ ELABORAZIONE COMPLETATA!")
    print(f"✓ {len(registry['knowledge_bases'])} Knowledge Base aggiunte")
    print("=" * 70)

    # Mostra statistiche
    print("\n📊 STATISTICHE:\n")
    for kb in registry['knowledge_bases']:
        kb_dir = Path(kb['kb_directory'])
        sections_count = len(list((kb_dir / 'output').glob('sezione_*.json')))
        print(f"• {kb['name']}")
        print(f"  Sezioni estratte: {sections_count}")
        print(f"  Descrizione: {kb['description']}")
        print()

if __name__ == "__main__":
    main()
