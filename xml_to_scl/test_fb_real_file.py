"""
Test FB parameter extraction with real file: Positioning_MOL_Machine_FB.xml
"""

import logging
from pathlib import Path
from lad_parser import LADLogicParser
from main import identify_file_type

# Set up logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Path to the test file
test_file = Path("../Software units/1_Orchestrator_Safety/Program blocks/002_PrjBlocks/03_Machines/05_POSITIONING_MOTOR_OPEN_LOOP_MACHINE/Positioning_MOL_Machine_FB.xml")

if test_file.exists():
    print(f"Analyzing file: {test_file.name}\n")

    # Check file type
    file_type = identify_file_type(test_file)
    print(f"File type identified: {file_type}\n")

    if file_type == 'fb':
        # Parse the FB XML
        from main import FBFCParser
        import xml.etree.ElementTree as ET

        parser = FBFCParser(test_file)
        parser.parse()
        root = parser.root

        if root is not None:
            print("FB parsed successfully. Analyzing LAD logic...\n")

            # Create LAD parser with the full root
            lad_parser = LADLogicParser(root)
            lad_parser.parse()

            # Extract FB calls
            fb_calls = lad_parser._extract_fb_calls()

            print(f"Found {len(fb_calls)} FB instances:\n")
            print("=" * 80)

            for i, fb_call in enumerate(fb_calls, 1):
                print(f"\n{i}. FB Instance: {fb_call['instance']}")
                print(f"   Type: {fb_call['fb_type']}")
                print(f"   Version: {fb_call.get('version', 'N/A')}")

                inputs = fb_call.get('inputs', {})
                outputs = fb_call.get('outputs', {})

                if inputs:
                    print(f"\n   Inputs ({len(inputs)}):")
                    for param_name, value in sorted(inputs.items()):
                        # Truncate long expressions for readability
                        display_value = value if len(value) <= 60 else value[:57] + "..."
                        status = "✓" if value != "???" else "✗"
                        print(f"      {status} {param_name}: {display_value}")
                else:
                    print(f"\n   Inputs: None")

                if outputs:
                    print(f"\n   Outputs ({len(outputs)}):")
                    for param_name, value in sorted(outputs.items()):
                        status = "✓" if value != "???" else "✗"
                        print(f"      {status} {param_name}: {value}")
                else:
                    print(f"\n   Outputs: None")

                print()

            print("=" * 80)
            print(f"\nSummary:")
            print(f"  Total FB instances: {len(fb_calls)}")

            # Count parameters with ???
            total_inputs = sum(len(fc.get('inputs', {})) for fc in fb_calls)
            total_outputs = sum(len(fc.get('outputs', {})) for fc in fb_calls)
            unresolved_inputs = sum(
                1 for fc in fb_calls
                for val in fc.get('inputs', {}).values()
                if val == '???'
            )
            unresolved_outputs = sum(
                1 for fc in fb_calls
                for val in fc.get('outputs', {}).values()
                if val == '???'
            )

            print(f"  Total input parameters: {total_inputs}")
            print(f"  Unresolved inputs (???): {unresolved_inputs}")
            print(f"  Total output parameters: {total_outputs}")
            print(f"  Unresolved outputs (???): {unresolved_outputs}")
            print(f"\n  Success Rate:")
            if total_inputs > 0:
                print(f"    Inputs:  {(total_inputs - unresolved_inputs) / total_inputs * 100:.1f}%")
            if total_outputs > 0:
                print(f"    Outputs: {(total_outputs - unresolved_outputs) / total_outputs * 100:.1f}%")

        else:
            print("Parser returned None for root")
else:
    print(f"File not found: {test_file}")
    print("Looking for file in alternative location...")
    alt_path = Path("Positioning_MOL_Machine_FB.xml")
    if alt_path.exists():
        print(f"Found at: {alt_path}")
    else:
        print("File not found at alternative location either")
