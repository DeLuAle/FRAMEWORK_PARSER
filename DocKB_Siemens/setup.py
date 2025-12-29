#!/usr/bin/env python3
"""
DocKB_Siemens - Setup Script
Automatizza la creazione struttura e copia file dalla cartella originale
"""

import shutil
import json
from pathlib import Path
from config import (
    PROJECT_ROOT, PDF_DIR, KB_DIR, SCRIPTS_DIR, DATA_DIR, TIA_PORTAL_DIR,
    SOURCE_DIR, ensure_directories, get_project_info
)


def setup_structure():
    """Crea la struttura directory completa"""
    print("\n" + "="*60)
    print("DocKB_Siemens - Setup")
    print("="*60)
    
    print("\n1. Creazione struttura directory...")
    ensure_directories()
    print("   [OK] Struttura creata")


def copy_pdfs():
    """Copia PDF dalla cartella originale"""
    print("\n2. Copia PDF dalla cartella originale...")
    
    if not SOURCE_DIR.exists():
        print(f"   [WARN] Cartella originale non trovata: {SOURCE_DIR}")
        print("   Modifica SOURCE_DIR in config.py")
        return
    
    # Trova PDF nella cartella originale
    pdf_count = 0
    
    # PDF nella root
    for pdf in SOURCE_DIR.glob("*.pdf"):
        if pdf.name not in ["documento.pdf"]:  # Skip temporanei
            dest = PDF_DIR / "sinamics" / pdf.name
            if not dest.exists():
                shutil.copy2(pdf, dest)
                print(f"   [OK] Copiato: {pdf.name}")
                pdf_count += 1
    
    # PDF in kb_axis
    kb_axis = SOURCE_DIR / "kb_axis"
    if kb_axis.exists():
        for subdir in kb_axis.iterdir():
            if subdir.is_dir():
                for pdf in subdir.glob("*.pdf"):
                    dest = PDF_DIR / "s7_1500" / pdf.name
                    if not dest.exists():
                        shutil.copy2(pdf, dest)
                        print(f"   [OK] Copiato: {pdf.name}")
                        pdf_count += 1
    
    print(f"   [OK] {pdf_count} PDF copiati")


def copy_scripts():
    """Copia script Python dalla cartella originale"""
    print("\n3. Copia script Python...")
    
    source_scripts = SOURCE_DIR / "scripts"
    if not source_scripts.exists():
        print("   [WARN] Cartella scripts originale non trovata")
        return
    
    script_count = 0
    for script in source_scripts.glob("*.py"):
        dest = SCRIPTS_DIR / script.name
        if not dest.exists():
            shutil.copy2(script, dest)
            print(f"   [OK] {script.name}")
            script_count += 1
    
    print(f"   [OK] {script_count} script copiati")


def copy_data_files():
    """Copia file dati (JSON, CSV)"""
    print("\n4. Copia file dati...")
    
    data_files = [
        "alarms_faults.json",
        "alarms_faults.csv",
        "mc_functions_list.json",
        "mc_functions_found.json",
    ]
    
    file_count = 0
    for filename in data_files:
        source = SOURCE_DIR / filename
        if source.exists():
            dest = DATA_DIR / filename
            shutil.copy2(source, dest)
            print(f"   [OK] {filename}")
            file_count += 1
    
    print(f"   [OK] {file_count} file dati copiati")


def copy_tia_portal_files():
    """Copia file SCL TIA Portal"""
    print("\n5. Copia file TIA Portal...")
    
    source_tia = SOURCE_DIR / "tia_portal"
    if not source_tia.exists():
        print("   [WARN] Cartella tia_portal originale non trovata")
        return
    
    # Copia solo i file attivi (no backup/duplicati)
    scl_files = [
        "SINAMICS_AlarmHandler.scl",
        "Alarms_Faults.scl",
    ]
    
    file_count = 0
    for filename in scl_files:
        source = source_tia / filename
        if source.exists():
            dest = TIA_PORTAL_DIR / filename
            shutil.copy2(source, dest)
            print(f"   [OK] {filename}")
            file_count += 1
    
    print(f"   [OK] {file_count} file SCL copiati")


def create_registry():
    """Crea kb_registry.json scansionando PDF"""
    print("\n6. Creazione registry...")
    
    registry = {
        "version": "2.0",
        "description": "Knowledge Base Registry - DocKB_Siemens",
        "knowledge_bases": []
    }
    
    # Scansiona PDF SINAMICS
    for pdf in (PDF_DIR / "sinamics").glob("*.pdf"):
        entry = {
            "id": pdf.stem.lower().replace(" ", "_"),
            "name": pdf.stem,
            "pdf_file": f"resources/pdfs/sinamics/{pdf.name}",
            "kb_directory": f"kb/sinamics/{pdf.stem}",
            "description": f"SINAMICS - {pdf.stem}",
            "status": "active",
            "language": "en"
        }
        registry["knowledge_bases"].append(entry)
    
    # Scansiona PDF S7-1500
    for pdf in (PDF_DIR / "s7_1500").glob("*.pdf"):
        # Determina lingua dal nome file
        lang = "it" if "it-IT" in pdf.name else "en"
        
        entry = {
            "id": pdf.stem.lower().replace(" ", "_"),
            "name": pdf.stem,
            "pdf_file": f"resources/pdfs/s7_1500/{pdf.name}",
            "kb_directory": f"kb/s7_1500/{pdf.stem}",
            "description": f"S7-1500 - {pdf.stem}",
            "status": "active",
            "language": lang
        }
        registry["knowledge_bases"].append(entry)
    
    # Salva registry
    registry_path = PROJECT_ROOT / "kb_registry.json"
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"   [OK] Registry creato: {len(registry['knowledge_bases'])} PDF registrati")


def print_summary():
    """Stampa riepilogo setup"""
    print("\n" + "="*60)
    print("Setup Completato!")
    print("="*60)
    
    info = get_project_info()
    print(f"\nProgetto: {info['name']}")
    print(f"Versione: {info['version']}")
    print(f"Root:     {info['root']}")
    
    # Conta file
    pdf_count = len(list(PDF_DIR.glob("**/*.pdf")))
    script_count = len(list(SCRIPTS_DIR.glob("*.py")))
    data_count = len(list(DATA_DIR.glob("*.json"))) + len(list(DATA_DIR.glob("*.csv")))
    
    print(f"\nFile copiati:")
    print(f"  PDF:     {pdf_count}")
    print(f"  Script:  {script_count}")
    print(f"  Data:    {data_count}")
    
    print("\n" + "="*60)
    print("Prossimi Passi:")
    print("="*60)
    print("\n1. Sposta questa cartella in c:\\Projects\\DocKB_Siemens")
    print("2. Esegui validazione:")
    print("   > python validate_setup.py")
    print("\n3. Estrai un PDF:")
    print("   > cd scripts")
    print("   > python extract_pdf_to_json.py --pdf-dir ../resources/pdfs/sinamics")
    print("\n4. Costruisci KB:")
    print("   > python build_knowledge_base.py")
    print("\n5. Cerca nella KB:")
    print("   > python sinamics_kb_search.py --search \"fault\"")
    print("\n" + "="*60)


def main():
    """Main setup function"""
    try:
        setup_structure()
        copy_pdfs()
        copy_scripts()
        copy_data_files()
        copy_tia_portal_files()
        create_registry()
        print_summary()
        
    except Exception as e:
        print(f"\n[ERRORE] Errore durante setup: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

