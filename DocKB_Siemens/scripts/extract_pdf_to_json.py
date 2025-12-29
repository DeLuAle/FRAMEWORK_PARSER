#!/usr/bin/env python3
"""
Script per estrarre dati da PDF e salvarli in JSON usando pandoc
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


class PDFExtractor:
    def __init__(self, pdf_path: str):
        """Inizializza l'estrattore PDF"""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"File PDF non trovato: {pdf_path}")

        # Verifica se pandoc è disponibile
        self._check_pandoc()

    def _check_pandoc(self) -> None:
        """Verifica che i tool necessari siano installati"""
        tools = ['pdftotext', 'pandoc']
        missing = []

        for tool in tools:
            try:
                subprocess.run([tool, '--version' if tool != 'pdftotext' else '-h'],
                             capture_output=True,
                             check=False)
            except FileNotFoundError:
                missing.append(tool)

        if missing:
            # Messaggio d'errore OS-specific
            if sys.platform == 'win32':
                install_msg = (
                    f"Tool mancanti: {', '.join(missing)}.\n\n"
                    f"POCHE COSE DA FARE PER WINDOWS:\n"
                    f"  1. Verifica se hai Git installato. Se sì, aggiungi questo al PATH:\n"
                    f"     C:\\Program Files\\Git\\mingw64\\bin\n"
                    f"  2. Oppure scarica i binari di Poppler da qui:\n"
                    f"     https://github.com/oschwartz10612/poppler-windows/releases/\n"
                    f"     E aggiungi la cartella 'bin' al PATH."
                )
            else:
                install_msg = (
                    f"Tool mancanti: {', '.join(missing)}.\n"
                    f"Installare con: sudo apt-get install poppler-utils pandoc"
                )
            
            raise RuntimeError(install_msg)

    def extract_text(self) -> str:
        """Estrae il testo dal PDF usando pdftotext"""
        print(f"Estrazione testo da: {self.pdf_path}")

        try:
            result = subprocess.run(
                ['pdftotext', str(self.pdf_path), '-'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Errore durante estrazione: {e.stderr}")

    def extract_to_json(self, output_dir: str = ".") -> Dict[str, Any]:
        """
        Estrae PDF e struttura i dati in formato JSON

        Args:
            output_dir: Directory dove salvare i file JSON

        Returns:
            Dizionario con i dati estratti
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Estrai il testo
        text_content = self.extract_text()

        # Struttura i dati
        data = self._structure_content(text_content)

        # Salva il JSON principale
        main_json_path = output_path / "documento.json"
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ JSON salvato: {main_json_path}")

        # Se il documento ha sezioni, salva anche file separati
        if 'sezioni' in data and data['sezioni']:
            self._save_sections(data['sezioni'], output_path)

        return data

    def _structure_content(self, text: str) -> Dict[str, Any]:
        """
        Struttura il contenuto del testo estratto

        Args:
            text: Testo estratto dal PDF

        Returns:
            Dizionario con dati strutturati
        """
        lines = text.split('\n')

        # Rimuovi righe vuote iniziali/finali
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        # Struttura base
        structured_data = {
            "metadata": {
                "source": self.pdf_path.name,
                "total_lines": len(lines),
                "extraction_method": "pandoc"
            },
            "sezioni": self._extract_sections(lines),
            "content": {
                "text": text.strip(),
                "lines_count": len([l for l in lines if l.strip()])
            }
        }

        return structured_data

    def _extract_sections(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Estrae sezioni dal contenuto (basato su righe vuote e lunghezza)

        Args:
            lines: List di righe di testo

        Returns:
            List di sezioni strutturate
        """
        sezioni = []
        current_section = []

        for line in lines:
            if not line.strip():
                if current_section:
                    sezioni.append({
                        "content": '\n'.join(current_section),
                        "length": len('\n'.join(current_section)),
                        "line_count": len(current_section)
                    })
                    current_section = []
            else:
                current_section.append(line)

        # Aggiungi l'ultima sezione se esiste
        if current_section:
            sezioni.append({
                "content": '\n'.join(current_section),
                "length": len('\n'.join(current_section)),
                "line_count": len(current_section)
            })

        return sezioni

    def _save_sections(self, sezioni: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Salva ogni sezione in un file JSON separato

        Args:
            sezioni: List di sezioni
            output_path: Directory di output
        """
        for idx, sezione in enumerate(sezioni, 1):
            section_file = output_path / f"sezione_{idx:03d}.json"
            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(sezione, f, indent=2, ensure_ascii=False)

        print(f"✓ {len(sezioni)} sezioni separate salvate in {output_path}")

    def save_text(self, text: str, output_path: str) -> None:
        """
        Salva il testo estratto in un file di testo

        Args:
            text: Testo da salvare
            output_path: Path dove salvare il file
        """
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"✓ Testo salvato: {output_path} ({len(text):,} caratteri)")


def main():
    """Funzione principale"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract PDF(s) to JSON',
        epilog='Esempi:\n'
               '  python extract_pdf_to_json.py --pdf manual.pdf --output-dir output\n'
               '  python extract_pdf_to_json.py --pdf-dir pdfs/ --output-dir output',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Gruppo mutualmente esclusivo per PDF singolo o directory
    pdf_group = parser.add_mutually_exclusive_group(required=True)
    pdf_group.add_argument('--pdf', help='Single PDF file path')
    pdf_group.add_argument('--pdf-dir', help='Directory containing PDF files')
    
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    # Determina la lista di file PDF da elaborare
    pdf_files = []
    
    if args.pdf:
        # Singolo file PDF
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"Errore: {args.pdf} non trovato")
            sys.exit(1)
        pdf_files = [pdf_path]
    
    elif args.pdf_dir:
        # Directory di PDF
        pdf_dir = Path(args.pdf_dir)
        if not pdf_dir.exists():
            print(f"Errore: Directory {args.pdf_dir} non trovata")
            sys.exit(1)
        
        pdf_files = list(pdf_dir.glob('*.pdf'))
        
        if not pdf_files:
            print(f"Errore: Nessun file PDF trovato in {args.pdf_dir}")
            sys.exit(1)
        
        print(f"📁 Trovati {len(pdf_files)} file PDF in {args.pdf_dir}")
    
    output_dir = args.output_dir
    
    # Elabora tutti i file PDF
    total_sections = 0
    processed_count = 0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"\n{'='*60}")
            print(f"📄 Elaborazione [{idx}/{len(pdf_files)}]: {pdf_file.name}")
            print(f"{'='*60}")
            
            # Crea sottodirectory per ogni PDF se elaboriamo multipli file
            if len(pdf_files) > 1:
                pdf_output_dir = Path(output_dir) / pdf_file.stem
            else:
                pdf_output_dir = Path(output_dir)
            
            # Crea l'estrattore
            extractor = PDFExtractor(str(pdf_file))

            # Estrai a JSON
            print("\n=== Estrazione a JSON ===")
            json_data = extractor.extract_to_json(str(pdf_output_dir))
            print(f"Dati estratti: {json_data['metadata']}")
            print(f"Sezioni trovate: {len(json_data['sezioni'])}")
            total_sections += len(json_data['sezioni'])

            # Salva il testo estratto
            print("\n=== Salvataggio testo estratto ===")
            text_content = json_data['content']['text']
            txt_filename = f"{pdf_output_dir}/{pdf_file.stem}.txt"
            extractor.save_text(text_content, txt_filename)

            # Stampa statistiche per questo PDF
            print("\n=== Statistiche ===")
            print(f"File PDF: {pdf_file}")
            print(f"Dimensione PDF: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"Output directory: {pdf_output_dir}")
            json_files = list(Path(pdf_output_dir).glob('*.json'))
            txt_files = list(Path(pdf_output_dir).glob('*.txt'))
            print(f"File JSON: {len(json_files)}")
            print(f"File TXT: {len(txt_files)}")
            if json_files:
                json_size = sum(f.stat().st_size for f in json_files) / 1024 / 1024
                print(f"Dimensione totale JSON: {json_size:.2f} MB")

            print("\n✓ Estrazione completata!")
            processed_count += 1

        except Exception as e:
            print(f"❌ Errore elaborando {pdf_file.name}: {e}", file=sys.stderr)
            continue
    
    # Statistiche finali se elaborati multipli file
    if len(pdf_files) > 1:
        print(f"\n{'='*60}")
        print(f"🎯 RIEPILOGO FINALE")
        print(f"{'='*60}")
        print(f"PDF elaborati: {processed_count}/{len(pdf_files)}")
        print(f"Sezioni totali estratte: {total_sections:,}")
        print(f"Output directory: {output_dir}")
        
        if processed_count < len(pdf_files):
            print(f"⚠️  {len(pdf_files) - processed_count} file falliti")
    
    if processed_count == 0:
        print("\n❌ Nessun file elaborato con successo")
        sys.exit(1)
    else:
        print("\n✅ Processo completato!")



if __name__ == "__main__":
    main()
