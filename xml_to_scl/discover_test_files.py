"""
Discover all available .xml files in the project for testing
"""

import os
from pathlib import Path
from collections import defaultdict
from main import identify_file_type

print("="*80)
print("TEST FILE DISCOVERY")
print("="*80)

# Start from current directory and search upward
search_root = Path(__file__).parent.parent.parent  # Go up to PLC_410D1

print(f"\nSearching in: {search_root}")
print()

# Find all .xml files
xml_files = list(search_root.rglob("*.xml"))

print(f"Found {len(xml_files)} total .xml files\n")

# Categorize by file type
by_type = defaultdict(list)
by_size = defaultdict(list)

for xml_file in sorted(xml_files):
    try:
        file_type = identify_file_type(xml_file)
        size = xml_file.stat().st_size

        by_type[file_type].append((xml_file, size))

        if size < 10_000:
            size_cat = "small (<10KB)"
        elif size < 100_000:
            size_cat = "medium (10-100KB)"
        elif size < 1_000_000:
            size_cat = "large (100KB-1MB)"
        else:
            size_cat = "very large (>1MB)"

        by_size[size_cat].append((xml_file, size))

    except Exception as e:
        by_type['error'].append((xml_file, str(e)))

# Print results by type
print("FILES BY TYPE:")
print("-" * 80)

for file_type in sorted(by_type.keys(), key=lambda x: (x is None, x)):
    files = by_type[file_type]
    type_label = file_type.upper() if file_type and file_type != 'error' else ('ERROR' if file_type == 'error' else 'UNKNOWN')
    print(f"\n{type_label}: {len(files)} files")

    for xml_file, info in sorted(files[:5]):  # Show first 5
        size_kb = info / 1024 if isinstance(info, int) else "?"
        if isinstance(info, int):
            rel_path = xml_file.relative_to(search_root)
            print(f"  - {rel_path.name:50s} ({size_kb:6.1f} KB)")
        else:
            print(f"  - {xml_file.name}: {info}")

    if len(files) > 5:
        print(f"  ... and {len(files) - 5} more")

# Print results by size
print("\n" + "-" * 80)
print("\nFILES BY SIZE:")
print("-" * 80)

for size_cat in ["small (<10KB)", "medium (10-100KB)", "large (100KB-1MB)", "very large (>1MB)"]:
    files = by_size[size_cat]
    if files:
        print(f"\n{size_cat}: {len(files)} files")

        for xml_file, size in sorted(files[:3]):
            size_kb = size / 1024
            rel_path = xml_file.relative_to(search_root)
            print(f"  - {rel_path.name:50s} ({size_kb:6.1f} KB)")

        if len(files) > 3:
            print(f"  ... and {len(files) - 3} more")

# Identify candidates for comprehensive testing
print("\n" + "=" * 80)
print("RECOMMENDED TEST CANDIDATES")
print("=" * 80)

# Get one example of each type (excluding 'none' and 'error')
selected = {}
for file_type in ['fb', 'fc', 'db', 'udt']:
    if file_type in by_type:
        # Prefer medium-sized files
        files_by_size = sorted(by_type[file_type], key=lambda x: x[1])

        # Try to find a medium-sized file
        medium = [f for f in files_by_size if 50_000 <= f[1] <= 200_000]
        if medium:
            selected[file_type] = medium[0]
        elif files_by_size:
            selected[file_type] = files_by_size[len(files_by_size) // 2]

# Add our known good test file
positioning_file = search_root / "Software units" / "1_Orchestrator_Safety" / "Program blocks" / "002_PrjBlocks" / "03_Machines" / "05_POSITIONING_MOTOR_OPEN_LOOP_MACHINE" / "Positioning_MOL_Machine_FB.xml"
if positioning_file.exists():
    selected['positioning'] = (positioning_file, positioning_file.stat().st_size)

print("\nSuggested test files for Session #5:\n")

for label, (file_path, size) in sorted(selected.items()):
    size_kb = size / 1024
    rel_path = file_path.relative_to(search_root)
    print(f"{label.upper():20s}: {str(rel_path):70s} ({size_kb:6.1f} KB)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total .xml files found: {len(xml_files)}")
for file_type in sorted(by_type.keys()):
    if file_type != 'error':
        print(f"  {file_type.upper():10s}: {len(by_type[file_type]):3d} files")
if 'error' in by_type and by_type['error']:
    print(f"  ERROR:     {len(by_type['error']):3d} files (couldn't identify)")

print("\nRecommended test files: " + str(len(selected)))
print("=" * 80)
