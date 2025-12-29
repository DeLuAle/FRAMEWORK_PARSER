#!/usr/bin/env python3
"""
Master script per gestire multiple PDF e Knowledge Base SINAMICS
Automatizza l'intero workflow di estrazione, indicizzazione e ricerca
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse


class MultiPDFKnowledgeBase:
    """Gestisce multiple Knowledge Base da PDF"""

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.kb_registry = self.load_registry()

    def load_registry(self) -> Dict[str, Any]:
        """Carica il registro delle KB"""
        registry_file = self.base_dir / "kb_registry.json"

        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"knowledge_bases": []}

    def save_registry(self) -> None:
        """Salva il registro delle KB"""
        registry_file = self.base_dir / "kb_registry.json"

        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.kb_registry, f, indent=2, ensure_ascii=False)

    def add_pdf(self, pdf_path: str, kb_name: str, description: str = "") -> None:
        """
        Aggiunge un nuovo PDF al sistema

        Args:
            pdf_path: Path al file PDF
            kb_name: Nome della knowledge base (es. "sinamics_s120", "sinamics_s150")
            description: Descrizione della KB
        """
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF non trovato: {pdf_path}")

        # Crea directory per la KB
        kb_dir = self.base_dir / kb_name
        kb_dir.mkdir(exist_ok=True)

        print(f"\n=== Elaborazione PDF per KB: {kb_name} ===")
        print(f"PDF: {pdf_file}")
        print(f"Directory: {kb_dir}")

        # 1. Copia il PDF
        import shutil
        dest_pdf = kb_dir / pdf_file.name
        shutil.copy2(pdf_file, dest_pdf)
        print(f"✓ PDF copiato")

        # 2. Estrai JSON
        self._extract_pdf_to_json(dest_pdf, kb_dir)

        # 3. Costruisci Knowledge Base
        self._build_knowledge_base(kb_dir)

        # 4. Estrai allarmi/fault
        self._extract_alarms_faults(kb_dir)

        # 5. Registra nel registry
        self._register_kb(kb_name, str(dest_pdf), description, kb_dir)

        print(f"✓ KB '{kb_name}' completata\n")

    def _extract_pdf_to_json(self, pdf_file: Path, output_dir: Path) -> None:
        """Estrae PDF a JSON"""
        print("  Estrazione PDF → JSON...")

        # Crea uno script temporaneo
        script = output_dir / "extract_pdf.py"

        # Usa lo script di estrazione globale
        cmd = [
            sys.executable,
            str(self.base_dir / "extract_pdf_to_json.py")
        ]

        # Esegui con directory output
        # Copia dello script e esecuzione locale
        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{self.base_dir}')
from extract_pdf_to_json import PDFExtractor

extractor = PDFExtractor('{pdf_file}')
extractor.extract_to_json('{output_dir / 'output'}')
"""],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  Errore: {result.stderr}")
            raise RuntimeError("Estrazione PDF fallita")

        print("  ✓ JSON estratto")

    def _build_knowledge_base(self, kb_dir: Path) -> None:
        """Costruisce la knowledge base"""
        print("  Costruzione Knowledge Base...")

        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{self.base_dir}')
from build_knowledge_base import KnowledgeBaseBuilder

builder = KnowledgeBaseBuilder('{kb_dir / 'output'}')
builder.load_sections()
builder.identify_chapters()
builder.build_search_index()
builder.build_master_index()
builder.save_knowledge_base('{kb_dir / 'knowledge_base'}')
"""],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  Errore: {result.stderr}")
            raise RuntimeError("Costruzione KB fallita")

        print("  ✓ Knowledge Base costruita")

    def _extract_alarms_faults(self, kb_dir: Path) -> None:
        """Estrae allarmi e fault"""
        print("  Estrazione allarmi/fault...")

        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{self.base_dir}')
from extract_alarms_faults import AlarmFaultExtractor

extractor = AlarmFaultExtractor('{kb_dir / 'knowledge_base'}')
extractor.save_to_json('{kb_dir / 'alarms_faults.json'}')
extractor.save_to_csv('{kb_dir / 'alarms_faults.csv'}')
extractor.save_to_scl_include('{kb_dir / 'AlarmHandler.scl'}')
"""],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  Avviso: Estrazione allarmi parziale")

        print("  ✓ Allarmi/fault estratti")

    def _register_kb(self, kb_name: str, pdf_path: str, description: str, kb_dir: Path) -> None:
        """Registra la KB nel registry"""
        entry = {
            "name": kb_name,
            "pdf_file": pdf_path,
            "kb_directory": str(kb_dir),
            "description": description,
            "output_dir": str(kb_dir / "output"),
            "knowledge_base_dir": str(kb_dir / "knowledge_base"),
            "status": "active"
        }

        # Aggiungi al registry
        self.kb_registry["knowledge_bases"].append(entry)
        self.save_registry()

    def list_kbs(self) -> None:
        """Lista tutte le KB registrate"""
        kbs = self.kb_registry.get("knowledge_bases", [])

        if not kbs:
            print("Nessuna Knowledge Base registrata")
            return

        print(f"\n=== Knowledge Base Registrate ({len(kbs)}) ===\n")

        for kb in kbs:
            print(f"Nome: {kb['name']}")
            print(f"  Directory: {kb['kb_directory']}")
            print(f"  Descrizione: {kb['description']}")
            print(f"  Status: {kb['status']}")
            print()

    def search_all_kbs(self, keyword: str, limit: int = 5) -> Dict[str, List]:
        """Ricerca in tutte le KB"""
        results = {}

        for kb in self.kb_registry.get("knowledge_bases", []):
            kb_name = kb['name']
            kb_dir = Path(kb['knowledge_base_dir'])

            try:
                result = subprocess.run(
                    [sys.executable, str(self.base_dir / "sinamics_kb_search.py"),
                     "--search", keyword,
                     "--limit", str(limit),
                     "--kb-dir", str(kb_dir),
                     "--json"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    results[kb_name] = json.loads(result.stdout)
            except Exception as e:
                print(f"Errore ricerca in {kb_name}: {e}")

        return results

    def generate_unified_index(self, output_file: str = "unified_kb_index.json") -> None:
        """Genera un indice unificato di tutte le KB"""
        print("\nGenerazione indice unificato...")

        unified = {
            "total_kbs": len(self.kb_registry.get("knowledge_bases", [])),
            "knowledge_bases": []
        }

        for kb in self.kb_registry.get("knowledge_bases", []):
            kb_index_file = Path(kb['knowledge_base_dir']) / "index.json"

            if kb_index_file.exists():
                with open(kb_index_file, 'r', encoding='utf-8') as f:
                    kb_index = json.load(f)

                unified["knowledge_bases"].append({
                    "name": kb['name'],
                    "description": kb['description'],
                    "metadata": kb_index.get('metadata', {}),
                    "chapters_count": len(kb_index.get('chapters', []))
                })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)

        print(f"✓ Indice unificato salvato: {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Gestione Multiple PDF Knowledge Base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Esempi:
  %(prog)s --add documento.pdf --name sinamics_s120 --desc "SINAMICS S120/S150"
  %(prog)s --list
  %(prog)s --search "parametri" --name sinamics_s120
  %(prog)s --unified-index
        '''
    )

    parser.add_argument('--add', metavar='PDF_FILE', help='Aggiungi nuovo PDF')
    parser.add_argument('--name', help='Nome della knowledge base')
    parser.add_argument('--desc', default='', help='Descrizione KB')
    parser.add_argument('--list', action='store_true', help='Lista KB registrate')
    parser.add_argument('--search', help='Ricerca in tutte le KB')
    parser.add_argument('--kb-name', help='Filtra ricerca per KB specifica')
    parser.add_argument('--limit', type=int, default=5, help='Limite risultati')
    parser.add_argument('--unified-index', action='store_true', help='Genera indice unificato')

    args = parser.parse_args()

    try:
        kb_manager = MultiPDFKnowledgeBase()

        if args.add:
            if not args.name:
                print("Errore: --name è obbligatorio con --add")
                sys.exit(1)
            kb_manager.add_pdf(args.add, args.name, args.desc)

        elif args.list:
            kb_manager.list_kbs()

        elif args.search:
            print(f"\nRicerca '{args.search}' in tutte le KB...")
            results = kb_manager.search_all_kbs(args.search, args.limit)

            for kb_name, kb_results in results.items():
                print(f"\n{kb_name}:")
                if isinstance(kb_results, list):
                    for i, result in enumerate(kb_results[:5], 1):
                        print(f"  {i}. {result}")
                else:
                    print(f"  {kb_results}")

        elif args.unified_index:
            kb_manager.generate_unified_index()

        else:
            parser.print_help()

    except Exception as e:
        print(f"Errore: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
