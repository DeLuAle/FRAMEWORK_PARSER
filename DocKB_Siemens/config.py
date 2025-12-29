#!/usr/bin/env python3
"""
DocKB_Siemens - Configuration Module
Percorsi centralizzati cross-platform per il progetto
"""

from pathlib import Path
import os

# ========================================
# PROJECT ROOT
# ========================================
# Questo file si trova in: c:\Projects\DocKB_Siemens\config.py
# PROJECT_ROOT punterà automaticamente a c:\Projects\DocKB_Siemens
PROJECT_ROOT = Path(__file__).parent.absolute()

# ========================================
# MAIN DIRECTORIES
# ========================================
RESOURCES_DIR = PROJECT_ROOT / "resources"
PDF_DIR = RESOURCES_DIR / "pdfs"
PDF_SINAMICS_DIR = PDF_DIR / "sinamics"
PDF_S7_1500_DIR = PDF_DIR / "s7_1500"

KB_DIR = PROJECT_ROOT / "kb"
KB_SINAMICS_DIR = KB_DIR / "sinamics"
KB_S7_1500_DIR = KB_DIR / "s7_1500"
KB_UNIFIED_DIR = KB_DIR / "unified"

SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DOCS_DIR = PROJECT_ROOT / "docs"
TIA_PORTAL_DIR = PROJECT_ROOT / "tia_portal"
DATA_DIR = PROJECT_ROOT / "data"

# ========================================
# OUTPUT DIRECTORIES (auto-created)
# ========================================
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / "temp"

# ========================================
# REGISTRY FILES
# ========================================
KB_REGISTRY = PROJECT_ROOT / "kb_registry.json"

# ========================================
# SOURCE DIRECTORY (reference only)
# ========================================
# Percorso alla cartella originale (read-only)
# Modifica questo path se la cartella originale è altrove
SOURCE_DIR = Path("c:/Users/PM/Desktop/KB TO/KB_TO_Sinamics-claude-push-files-repo-oQZaz/KB_TO_Sinamics-claude-push-files-repo-oQZaz")

# ========================================
# HELPER FUNCTIONS
# ========================================

def ensure_directories():
    """Crea tutte le directory necessarie se non esistono"""
    directories = [
        RESOURCES_DIR,
        PDF_SINAMICS_DIR,
        PDF_S7_1500_DIR,
        KB_SINAMICS_DIR,
        KB_S7_1500_DIR,
        KB_UNIFIED_DIR,
        SCRIPTS_DIR,
        DOCS_DIR,
        TIA_PORTAL_DIR,
        DATA_DIR,
        OUTPUT_DIR,
        TEMP_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        
    print(f"OK Struttura directory creata in: {PROJECT_ROOT}")


def get_project_info():
    """Ritorna informazioni sul progetto"""
    return {
        "name": "DocKB_Siemens",
        "version": "2.0",
        "description": "Documentation Knowledge Base for Siemens PLC & Drive Systems",
        "root": str(PROJECT_ROOT),
        "platform": os.name,
    }


def validate_paths():
    """Valida che tutti i percorsi siano configurati correttamente"""
    issues = []
    
    # Check PROJECT_ROOT exists
    if not PROJECT_ROOT.exists():
        issues.append(f"PROJECT_ROOT non esiste: {PROJECT_ROOT}")
    
    # Check no hardcoded paths (Windows-style or Linux-style)
    for var_name, var_value in globals().items():
        if isinstance(var_value, Path):
            path_str = str(var_value)
            if path_str.startswith("/home/") or path_str.startswith("C:/Users/"):
                if var_name != "SOURCE_DIR":  # SOURCE_DIR può essere hardcoded
                    issues.append(f"{var_name} contiene percorso hardcoded: {path_str}")
    
    if issues:
        print("[WARN] Problemi di configurazione:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("[OK] Configurazione percorsi valida")
        return True


# ========================================
# AUTO-RUN ON IMPORT
# ========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("DocKB_Siemens - Configuration")
    print("="*50)
    
    info = get_project_info()
    for key, value in info.items():
        print(f"{key:20}: {value}")
    
    print("\n" + "="*50)
    print("Directory Paths:")
    print("="*50)
    print(f"PROJECT_ROOT    : {PROJECT_ROOT}")
    print(f"PDF_DIR         : {PDF_DIR}")
    print(f"KB_DIR          : {KB_DIR}")
    print(f"SCRIPTS_DIR     : {SCRIPTS_DIR}")
    print(f"DATA_DIR        : {DATA_DIR}")
    
    print("\n" + "="*50)
    validate_paths()
    print("="*50)

