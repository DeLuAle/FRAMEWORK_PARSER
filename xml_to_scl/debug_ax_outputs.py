"""
Debug why Ax FB doesn't have outputs
"""

import logging
from pathlib import Path
from lad_parser import LADLogicParser
from xml_parser_base import XMLParserBase

# Set logging to debug level to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Path to test file
test_file = Path("../Software units/1_Orchestrator_Safety/Program blocks/002_PrjBlocks/03_Machines/05_POSITIONING_MOTOR_OPEN_LOOP_MACHINE/Positioning_MOL_Machine_FB.xml")

if test_file.exists():
    import xml.etree.ElementTree as ET
    try:
        from defusedxml.ElementTree import parse as safe_parse
        tree = safe_parse(test_file)
    except ImportError:
        tree = ET.parse(test_file)

    root = tree.getroot()

    # Create LAD parser
    lad_parser = LADLogicParser(root)
    lad_parser.parse()

    # Get all FB calls with debug logging
    print("\n" + "="*80)
    print("EXTRACTING FB CALLS WITH DEBUG LOGGING")
    print("="*80 + "\n")

    fb_calls = lad_parser._extract_fb_calls()

    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80 + "\n")

    # Check Ax specifically
    ax = next((fc for fc in fb_calls if fc['instance'] == 'Ax'), None)
    if ax:
        print("AX FB INSTANCE DETAILS:")
        print(f"  Instance: {ax['instance']}")
        print(f"  Type: {ax['fb_type']}")
        print(f"  Inputs: {ax['inputs']}")
        print(f"  Outputs: {ax['outputs']}")
        print(f"  InOuts: {ax.get('inouts', {})}")

        if not ax['outputs']:
            print("\nNo outputs found. Checking connections in LAD parser:")
            print(f"  Total connections: {len(lad_parser.connections)}")

            # Find connections where Ax (which should have a UID) is the source
            ax_uid = None
            for uid, part in lad_parser.parts.items():
                if part.get('instance_name') == 'Ax':
                    ax_uid = uid
                    print(f"  Ax UID: {ax_uid}")
                    break

            if ax_uid:
                print(f"\n  Connections from Ax (dest->source):")
                for (dest_uid, dest_pin), source_info in lad_parser.connections.items():
                    if source_info['uid'] == ax_uid:
                        dest_part = lad_parser.parts.get(dest_uid)
                        print(f"    {source_info.get('name')} -> {dest_uid} {dest_pin}")
                        if dest_part:
                            print(f"      (dest type: {dest_part.get('type')}, name: {dest_part.get('name')})")
else:
    print(f"File not found: {test_file}")
