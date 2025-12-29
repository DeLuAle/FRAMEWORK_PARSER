#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean XML placeholders (???) from TIA Portal exported XML files.

This script removes or replaces ??? placeholders found in:
- MultiLanguageText elements (descriptions)
- Text elements (comments and labels)

Placeholder patterns handled:
- "Passaggio XX - ??? lato operatore/motore" → "Passaggio XX - [TO BE DEFINED]"
- "Passaggio XX (???) - [description]" → "Passaggio XX (UNKNOWN) - [description]"
- Generic "??? what it means?" → "[TO BE CLARIFIED]"
"""

import re
import sys
import io
from pathlib import Path
from typing import Tuple, List
import xml.etree.ElementTree as ET

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class PlaceholderCleaner:
    """Clean placeholder tokens from XML files."""

    # Regex patterns to match and replace
    PATTERNS = [
        # Pattern 1: Passaggio XX - ??? lato operatore/motore
        (
            r'(Passaggio\s+\d+\s*-\s*)\?\?\?(\s+lato)',
            r'\1[UNDEFINED]\2'
        ),
        # Pattern 2: Passaggio XX (???) - description
        (
            r'(Passaggio\s+\d+\s*\()\?\?\?(\))',
            r'\1UNKNOWN\2'
        ),
        # Pattern 3: Generic ??? with context
        (
            r'\?\?\?\s+what it means\?',
            r'[TO BE CLARIFIED]'
        ),
        # Pattern 4: Any remaining ???
        (
            r'\?\?\?',
            r'[PLACEHOLDER]'
        ),
    ]

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.files_processed = 0
        self.placeholders_found = 0
        self.placeholders_replaced = 0

    def clean_text(self, text: str) -> Tuple[str, int]:
        """
        Clean placeholder tokens from text.

        Returns:
            Tuple of (cleaned_text, placeholder_count)
        """
        placeholder_count = text.count('???')

        if placeholder_count == 0:
            return text, 0

        cleaned = text
        for pattern, replacement in self.PATTERNS:
            cleaned = re.sub(pattern, replacement, cleaned)

        return cleaned, placeholder_count

    def clean_xml_file(self, xml_path: Path) -> Tuple[int, int]:
        """
        Clean placeholders from XML file.

        Returns:
            Tuple of (placeholders_found, placeholders_replaced)
        """
        try:
            # Parse XML
            tree = ET.parse(str(xml_path))
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"[ERROR] Error parsing {xml_path}: {e}", file=sys.stderr)
            return 0, 0

        found = 0
        replaced = 0

        # Namespaces used in TIA Portal XML
        namespaces = {
            'p': 'http://www.siemens.com/automation/Openness/SW/Interface/v5',
            '': 'http://www.siemens.com/automation/Openness/SW/Interface/v5'
        }

        # Find all text elements
        for elem in root.iter():
            # Check tag name (handle namespaces)
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

            # MultiLanguageText or Text elements
            if tag in ('MultiLanguageText', 'Text') and elem.text:
                if '???' in elem.text:
                    found += elem.text.count('???')
                    old_text = elem.text
                    elem.text, _ = self.clean_text(elem.text)
                    replaced += 1

                    if self.verbose:
                        print(f"  [{tag}]")
                        print(f"    Before: {old_text[:80]}")
                        print(f"    After:  {elem.text[:80]}")

        # Write back to file only if changes were made
        if replaced > 0:
            try:
                tree.write(
                    str(xml_path),
                    encoding='utf-8',
                    xml_declaration=True
                )
                self.files_processed += 1
                self.placeholders_found += found
                self.placeholders_replaced += replaced

                if not self.verbose:
                    print(f"[OK] {xml_path.name}: {found} found, {replaced} cleaned")
            except Exception as e:
                print(f"[ERROR] Error writing {xml_path}: {e}", file=sys.stderr)
                return found, 0

        return found, replaced

    def process_directory(self, root_dir: Path) -> None:
        """
        Process all XML files in directory recursively.
        """
        xml_files = list(root_dir.rglob('*.xml'))
        print(f"\n[INFO] Found {len(xml_files)} XML files\n")

        files_with_placeholders = []

        for xml_file in xml_files:
            found, replaced = self.clean_xml_file(xml_file)
            if found > 0:
                files_with_placeholders.append((xml_file, found, replaced))

        # Print summary
        print(f"\n{'='*80}")
        print(f"CLEANUP SUMMARY")
        print(f"{'='*80}")
        print(f"Total Files Processed: {len(xml_files)}")
        print(f"Files With Placeholders: {len(files_with_placeholders)}")
        print(f"Total Placeholders Found: {self.placeholders_found}")
        print(f"Total Placeholders Replaced: {self.placeholders_replaced}")
        print(f"{'='*80}\n")

        if files_with_placeholders:
            print("[INFO] FILES WITH PLACEHOLDERS FOUND:\n")
            for file_path, found, replaced in files_with_placeholders:
                rel_path = file_path.relative_to(root_dir)
                print(f"  * {rel_path}")
                print(f"    Found: {found}, Replaced: {replaced}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project_dir> [--verbose]")
        print(f"\nExample: {sys.argv[0]} PLC_410D1 --verbose")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    if not project_dir.exists():
        print(f"❌ Directory not found: {project_dir}", file=sys.stderr)
        sys.exit(1)

    verbose = '--verbose' in sys.argv

    print(f"\n{'='*80}")
    print(f"TIA PORTAL XML PLACEHOLDER CLEANER")
    print(f"{'='*80}")
    print(f"Project Directory: {project_dir}")
    print(f"Verbose Mode: {'ON' if verbose else 'OFF'}")
    print(f"{'='*80}\n")

    cleaner = PlaceholderCleaner(verbose=verbose)
    cleaner.process_directory(project_dir)

    if cleaner.placeholders_replaced > 0:
        print(f"[SUCCESS] CLEANUP COMPLETED - {cleaner.placeholders_replaced} files updated")
    else:
        print(f"[INFO] No placeholders found - no changes made")


if __name__ == '__main__':
    main()
