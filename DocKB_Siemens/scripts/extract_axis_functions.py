#!/usr/bin/env python3
"""
Script per estrarre funzioni MC dai PDF S7-1500
Crea Knowledge Base searchable dai 4 manuali e poi estrae funzioni MC
"""

import subprocess
import sys
from pathlib import Path
import json
import shutil

# Aggiungi scripts directory al path per importare i moduli
sys.path.insert(0, str(Path(__file__).parent))

def add_pdf_to_kb(pdf_file, kb_name, description):
    """Aggiunge un PDF come nuova Knowledge Base"""

    kb_dir = Path(__file__).parent.parent / "kb_axis" / kb_name
    kb_dir.mkdir(exist_ok=True, parents=True)

    # Copia PDF
    dest_pdf = kb_dir / Path(pdf_file).name
    shutil.copy2(pdf_file, dest_pdf)

    print(f"\n[*] Elaborazione: {kb_name}")
    print(f"   PDF: {pdf_file}")

    # 1. Estrai JSON
    print(f"   --> Estrazione JSON...")
    from extract_pdf_to_json_minimal import PDFExtractor
    extractor = PDFExtractor(str(dest_pdf))
    extractor.extract_to_json(str(kb_dir / 'output'))

    # 2. Costruisci KB
    print(f"   --> Costruzione Knowledge Base...")
    from build_knowledge_base import KnowledgeBaseBuilder
    builder = KnowledgeBaseBuilder(str(kb_dir / 'output'))
    builder.load_sections()
    builder.identify_chapters()
    builder.build_search_index()
    builder.build_master_index()
    builder.save_knowledge_base(str(kb_dir / 'knowledge_base'))

    print(f"   [OK] Completato!")

    return {
        "name": kb_name,
        "pdf_file": str(dest_pdf),
        "kb_directory": str(kb_dir),
        "description": description,
        "status": "active"
    }

def main():
    """Estrae i 4 PDF S7-1500 Motion Control"""

    # Cartella con i PDF (SCL Syntax V2 SIEMENS TO PDF)
    pdf_dir = Path(r"c:\Projects\SCL Syntax V2\SIEMENS TO PDF")

    pdfs = [
        (pdf_dir / "s71500_s71500t_axis_function_manual_it-IT_it-IT.pdf",
         "axis_function_it",
         "S7-1500 Axis Function Manual (Italian)"),
        (pdf_dir / "s71500_s71500t_motion_control_overview_function_manual_en-US_en-US.pdf",
         "motion_control_overview_en",
         "S7-1500 Motion Control Overview (English)"),
        (pdf_dir / "s71500_s71500t_measuringinput_outputcam_function_manual_en-US_en-US.pdf",
         "measuring_cam_en",
         "S7-1500 Measuring Input/Output Cam (English)"),
        (pdf_dir / "s71500_s71500t_synchronous_operation_function_manual_en-US_en-US.pdf",
         "synchronous_operation_en",
         "S7-1500 Synchronous Operation (English)"),
    ]

    print("=" * 70)
    print("ESTRAZIONE PDF S7-1500 MOTION CONTROL")
    print("=" * 70)

    registry = {"knowledge_bases": []}

    for pdf_file, kb_name, description in pdfs:
        if not Path(pdf_file).exists():
            print(f"[MISSING] {pdf_file} non trovato")
            continue

        try:
            kb_entry = add_pdf_to_kb(str(pdf_file), kb_name, description)
            registry["knowledge_bases"].append(kb_entry)
        except Exception as e:
            print(f"[ERROR] Errore: {e}")
            import traceback
            traceback.print_exc()

    # Salva registry
    registry_file = Path(__file__).parent.parent / "kb_axis_registry.json"
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"[OK] ELABORAZIONE COMPLETATA!")
    print(f"[OK] {len(registry['knowledge_bases'])} Knowledge Base create")
    print("=" * 70)

    # Mostra statistiche
    print("\n[STATS] STATISTICHE:\n")
    for kb in registry['knowledge_bases']:
        kb_dir = Path(kb['kb_directory'])
        try:
            sections_count = len(list((kb_dir / 'output').glob('sezione_*.json')))
            print(f"[OK] {kb['description']}")
            print(f"  - Sezioni estratte: {sections_count}")
            print(f"  - Directory: {kb['kb_directory']}\n")
        except:
            print(f"[OK] {kb['description']} (errore nel conteggio sezioni)\n")

if __name__ == "__main__":
    main()
