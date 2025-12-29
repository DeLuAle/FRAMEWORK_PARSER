#!/usr/bin/env python3
"""
Script per estrarre dati da PDF e salvarli in JSON (versione minimalista)
Non richiede pandoc o pdfinfo - solo pdftotext
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

        # Verifica che pdftotext sia disponibile
        self._check_pdftotext()

    def _check_pdftotext(self) -> None:
        """Verifica che pdftotext sia installato"""
        try:
            subprocess.run(['pdftotext', '-h'],
                         capture_output=True,
                         check=False)
        except FileNotFoundError:
            raise RuntimeError(f"pdftotext non trovato. "
                             f"Installare con: choco install pdftotext OR apt-get install poppler-utils")

    def extract_text(self) -> str:
        """Estrae il testo dal PDF usando pdftotext"""
        print(f"Estrazione testo da: {self.pdf_path}")

        try:
            result = subprocess.run(
                ['pdftotext', str(self.pdf_path), '-'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
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

        print(f"[OK] JSON salvato: {main_json_path}")

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
                "extraction_method": "pdftotext"
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

    def _save_sections(self, sezioni: List[Dict], output_path: Path) -> None:
        """Salva le sezioni come file JSON separati"""
        total = len(sezioni)
        print(f"[OK] Salvataggio {total} sezioni...")

        for idx, sezione in enumerate(sezioni, 1):
            section_file = output_path / f"sezione_{idx:06d}.json"
            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(sezione, f, indent=2, ensure_ascii=False)

            if idx % 1000 == 0:
                print(f"    ... {idx}/{total} sezioni salvate")

        print(f"[OK] Tutte le sezioni salvate in {output_path}")

    def save_text(self, text: str, output_path: Path) -> None:
        """Salva il testo estratto come file TXT"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"[OK] Testo salvato: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilizzo: python extract_pdf_to_json_minimal.py <pdf_file> [output_dir]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"

    try:
        extractor = PDFExtractor(pdf_file)
        extractor.extract_to_json(output_dir)
        print("[OK] Estrazione completata!")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
