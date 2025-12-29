#!/usr/bin/env python3
"""
DocKB_Siemens - Validation Script
Valida che il setup sia completo e corretto
"""

import sys
import json
import subprocess
from pathlib import Path
from config import (
    PROJECT_ROOT, PDF_DIR, KB_DIR, SCRIPTS_DIR, DATA_DIR, 
    TIA_PORTAL_DIR, KB_REGISTRY, validate_paths
)


def check_python_version():
    """Verifica versione Python"""
    print("\n1. Python Version Check...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   [ERRORE] Python {version.major}.{version.minor} - Richiesto >= 3.7")
        return False


def check_system_tools():
    """Verifica che pdftotext e pandoc siano installati"""
    print("\n2. System Tools Check...")
    tools = {
        'pdftotext': ['pdftotext', '-v'],
        'pandoc': ['pandoc', '--version']
    }
    
    all_ok = True
    for tool_name, command in tools.items():
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5
            )
            print(f"   [OK] {tool_name} installed")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"   [ERRORE] {tool_name} NOT FOUND")
            print(f"      Install: choco install {tool_name}")
            all_ok = False
    
    return all_ok


def check_directory_structure():
    """Verifica che tutte le directory esistano"""
    print("\n3. Directory Structure Check...")
    
    required_dirs = [
        PDF_DIR,
        KB_DIR,
        SCRIPTS_DIR,
        DATA_DIR,
        TIA_PORTAL_DIR,
    ]
    
    all_ok = True
    for directory in required_dirs:
        if directory.exists():
            print(f"   [OK] {directory.name}/")
        else:
            print(f"   [ERRORE] Missing: {directory}")
            all_ok = False
    
    return all_ok


def check_registry_file():
    """Verifica che kb_registry.json sia valido"""
    print("\n4. Registry File Check...")
    
    if not KB_REGISTRY.exists():
        print(f"   [ERRORE] kb_registry.json not found")
        return False
    
    try:
        with open(KB_REGISTRY, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        if 'knowledge_bases' not in registry:
            print("   [ERRORE] Invalid registry format")
            return False
        
        kb_count = len(registry['knowledge_bases'])
        print(f"   [OK] Registry valid ({kb_count} KBs registered)")
        
        # Verifica percorsi relativi
        for kb in registry['knowledge_bases']:
            pdf_path = kb.get('pdf_file', '')
            if pdf_path.startswith('/') or pdf_path.startswith('C:'):
                print(f"   [WARN] Hardcoded path in: {kb['name']}")
        
        return True
        
    except json.JSONDecodeError:
        print("   [ERRORE] Invalid JSON in registry")
        return False


def check_pdf_files():
    """Verifica che i PDF esistano"""
    print("\n5. PDF Files Check...")
    
    pdf_count = 0
    for pdf_dir in [PDF_DIR / "sinamics", PDF_DIR / "s7_1500"]:
        if pdf_dir.exists():
            pdfs = list(pdf_dir.glob("*.pdf"))
            pdf_count += len(pdfs)
            print(f"   [OK] {pdf_dir.name}: {len(pdfs)} PDFs")
    
    if pdf_count == 0:
        print("   [WARN] No PDFs found - add PDFs to resources/pdfs/")
    
    return True


def check_scripts():
    """Verifica che gli script esistano"""
    print("\n6. Python Scripts Check...")
    
    key_scripts = [
        'extract_pdf_to_json.py',
        'build_knowledge_base.py',
        'sinamics_kb_search.py',
    ]
    
    all_ok = True
    for script in key_scripts:
        script_path = SCRIPTS_DIR / script
        if script_path.exists():
            print(f"   [OK] {script}")
        else:
            print(f"   [WARN] Missing: {script}")
            all_ok = False
    
    return all_ok


def check_data_files():
    """Verifica file dati"""
    print("\n7. Data Files Check...")
    
    data_files = [
        'alarms_faults.json',
        'mc_functions_list.json',
    ]
    
    for filename in data_files:
        file_path = DATA_DIR / filename
        if file_path.exists():
            print(f"   [OK] {filename}")
        else:
            print(f"   [WARN] Missing: {filename}")
    
    return True


def check_cross_platform_paths():
    """Verifica che i percorsi siano cross-platform"""
    print("\n8. Cross-Platform Paths Check...")
    return validate_paths()


def print_summary(results):
    """Stampa riepilogo validazione"""
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    all_critical = all([
        results['python'],
        results['tools'],
        results['dirs'],
        results['registry'],
    ])
    
    if all_critical:
        print("\n[OK] All critical checks PASSED")
        print("\nYour DocKB_Siemens setup is ready!")
        print("\nNext steps:")
        print("  1. Extract PDF:")
        print("     > cd scripts")
        print("     > python extract_pdf_to_json.py")
        print("  2. Build Knowledge Base:")
        print("     > python build_knowledge_base.py")
        print("  3. Search:")
        print("     > python sinamics_kb_search.py --search fault")
    else:
        print("\n[ERRORE] Some critical checks FAILED")
        print("\nFix the errors above before proceeding.")
        return 1
    
    print("\n" + "="*60)
    return 0


def main():
    """Main validation"""
    print("="*60)
    print("DocKB_Siemens - Setup Validation")
    print("="*60)
    print(f"\nProject Root: {PROJECT_ROOT}")
    
    results = {
        'python': check_python_version(),
        'tools': check_system_tools(),
        'dirs': check_directory_structure(),
        'registry': check_registry_file(),
        'pdfs': check_pdf_files(),
        'scripts': check_scripts(),
        'data': check_data_files(),
        'paths': check_cross_platform_paths(),
    }
    
    return print_summary(results)


if __name__ == "__main__":
    sys.exit(main())
