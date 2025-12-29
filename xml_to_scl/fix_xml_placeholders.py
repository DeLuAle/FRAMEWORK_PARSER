#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix XML placeholders using regex on file contents.
This is safer than parsing XML and re-writing.
"""

import re
import sys
from pathlib import Path


def fix_placeholders_in_file(xml_path: Path, dry_run=False) -> tuple:
    """
    Fix placeholders in XML file using regex.

    Returns: (found_count, replaced_count)
    """
    try:
        content = xml_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"[ERROR] Cannot read {xml_path.name}: {e}")
        return 0, 0

    original = content
    found_count = content.count('???')

    if found_count == 0:
        return 0, 0

    # Pattern 1: Passaggio XX - ??? lato operatore/motore
    content = re.sub(
        r'(Passaggio\s+\d+\s*-\s*)\?\?\?(\s+lato)',
        r'\1[UNDEFINED]\2',
        content
    )

    # Pattern 2: Passaggio XX (???) - description
    content = re.sub(
        r'(Passaggio\s+\d+\s*\()\?\?\?(\))',
        r'\1UNKNOWN\2',
        content
    )

    # Pattern 3: Generic ??? with context
    content = re.sub(
        r'\?\?\?\s+what it means\?',
        r'[TO BE CLARIFIED]',
        content
    )

    # Pattern 4: Any remaining ???
    content = re.sub(r'\?\?\?', r'[PLACEHOLDER]', content)

    replaced_count = (original.count('???') - content.count('???'))

    if replaced_count > 0 and not dry_run:
        try:
            xml_path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Cannot write {xml_path.name}: {e}")
            return found_count, 0

    return found_count, replaced_count


def main():
    root_dir = Path("C:\\Projects\\MODULBLOCK_MBK2\\MBK_2\\PLC_410D1")

    print("\n" + "="*80)
    print("TIA PORTAL XML PLACEHOLDER FIXER")
    print("="*80 + "\n")

    xml_files = list(root_dir.rglob('*.xml'))
    print(f"[INFO] Found {len(xml_files)} XML files\n")

    total_found = 0
    total_replaced = 0
    files_with_issues = []

    for xml_file in xml_files:
        found, replaced = fix_placeholders_in_file(xml_file, dry_run=False)
        if found > 0:
            total_found += found
            total_replaced += replaced
            files_with_issues.append((xml_file.relative_to(root_dir), found, replaced))
            print(f"[OK] {xml_file.name}: {found} found, {replaced} fixed")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Files Scanned: {len(xml_files)}")
    print(f"Files With Placeholders: {len(files_with_issues)}")
    print(f"Total Placeholders Found: {total_found}")
    print(f"Total Placeholders Fixed: {total_replaced}")
    print("="*80 + "\n")

    if files_with_issues:
        print("[INFO] FILES MODIFIED:\n")
        for rel_path, found, replaced in files_with_issues:
            print(f"  * {rel_path}")
            print(f"    Found: {found}, Fixed: {replaced}\n")

    if total_replaced > 0:
        print(f"[SUCCESS] Fixed {total_replaced} placeholder(s) in {len(files_with_issues)} file(s)")
    else:
        print("[INFO] No changes made")


if __name__ == '__main__':
    main()
