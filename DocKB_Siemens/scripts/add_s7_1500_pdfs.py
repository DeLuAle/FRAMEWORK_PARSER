#!/usr/bin/env python3
"""
Script per aggiungere i 4 PDF S7-1500 alla Knowledge Base
Crea struttura separata per S7-1500, proprio come fatto per SINAMICS
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
    """Aggiunge i 4 PDF S7-1500"""

    # Riferimento alla cartella resources/pdfs
    resources_dir = Path(__file__).parent.parent / "resources" / "pdfs"

    pdfs = [
        (resources_dir / "s7_1500_manual_1.pdf", "s7_1500_manual_1",
         "S7-1500 Manual 1"),
        (resources_dir / "s7_1500_manual_2.pdf", "s7_1500_manual_2",
         "S7-1500 Manual 2"),
        (resources_dir / "s7_1500_manual_3.pdf", "s7_1500_manual_3",
         "S7-1500 Manual 3"),
        (resources_dir / "s7_1500_manual_4.pdf", "s7_1500_manual_4",
         "S7-1500 Manual 4"),
    ]

    print("=" * 70)
    print("AGGIUNTA PDF S7-1500 ALLA KNOWLEDGE BASE")
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
            import traceback
            traceback.print_exc()

    # Salva registry nella root
    registry_file = Path(__file__).parent.parent / "kb_registry.json"

    # Carica registry esistente e aggiungi le nuove KB
    if registry_file.exists():
        with open(registry_file, 'r', encoding='utf-8') as f:
            existing_registry = json.load(f)
        existing_registry["knowledge_bases"].extend(registry["knowledge_bases"])
        registry = existing_registry

    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"✓ ELABORAZIONE COMPLETATA!")
    print(f"✓ {len(registry['knowledge_bases'])} Knowledge Base totali registrate")
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
