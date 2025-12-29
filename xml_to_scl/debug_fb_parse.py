"""
Debug FB parsing to understand structure
"""

import json
from pathlib import Path
from main import FBFCParser

# Path to the test file
test_file = Path("../Software units/1_Orchestrator_Safety/Program blocks/002_PrjBlocks/03_Machines/05_POSITIONING_MOTOR_OPEN_LOOP_MACHINE/Positioning_MOL_Machine_FB.xml")

if test_file.exists():
    parser = FBFCParser(test_file)
    parser.parse()

    # Show parsed data structure
    data = parser.parsed_data

    print("Parsed FB Block Data:")
    print(f"  Name: {data.get('name')}")
    print(f"  Block Type: {data.get('block_type')}")
    print(f"  Programming Language: {data.get('programming_language')}")
    print(f"  Has Graphical Logic: {data.get('has_graphical_logic')}")

    networks = data.get('networks', [])
    print(f"\nNetworks: {len(networks)}")

    for i, net in enumerate(networks[:3], 1):  # Show first 3
        print(f"\n  Network {i}:")
        print(f"    Number: {net.get('number')}")
        print(f"    Type: {net.get('type')}")
        print(f"    Title: {net.get('title')}")
        print(f"    FB Calls: {len(net.get('fb_calls', []))}")
        print(f"    Logic Ops: {len(net.get('logic_ops', []))}")

        if net.get('fb_calls'):
            for j, fb in enumerate(net['fb_calls'][:2], 1):
                print(f"\n      FB Call {j}:")
                print(f"        Instance: {fb.get('instance')}")
                print(f"        Type: {fb.get('fb_type')}")
                print(f"        Inputs: {fb.get('inputs')}")
                print(f"        Outputs: {fb.get('outputs')}")

    # Check if there are legacy fb_calls at root level
    fb_calls_legacy = data.get('fb_calls', [])
    print(f"\nLegacy FB Calls (at root): {len(fb_calls_legacy)}")

    if fb_calls_legacy:
        print("\nFB Call Details:")
        for i, fb in enumerate(fb_calls_legacy, 1):
            print(f"\n  {i}. {fb.get('instance')} ({fb.get('fb_type')})")
            inputs = fb.get('inputs', {})
            outputs = fb.get('outputs', {})

            if inputs:
                print(f"     Inputs ({len(inputs)}):")
                for param, value in list(inputs.items())[:3]:
                    display = value if len(str(value)) <= 50 else str(value)[:47] + "..."
                    print(f"       - {param}: {display}")
                if len(inputs) > 3:
                    print(f"       ... and {len(inputs)-3} more")

            if outputs:
                print(f"     Outputs ({len(outputs)}):")
                for param, value in list(outputs.items())[:3]:
                    print(f"       - {param}: {value}")
                if len(outputs) > 3:
                    print(f"       ... and {len(outputs)-3} more")
            else:
                print(f"     Outputs: None")

else:
    print(f"File not found: {test_file}")
