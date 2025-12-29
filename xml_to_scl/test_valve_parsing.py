#!/usr/bin/env python3
"""Debug script to test ValveMachine_FB parsing"""

import xml.etree.ElementTree as ET
from pathlib import Path

# Load XML
xml_path = Path("../Software units/1_Orchestrator_Safety/Program blocks/002_PrjBlocks/03_Machines/01_VALVE_MACHINE/ValveMachine_FB.xml")
tree = ET.parse(xml_path)
root = tree.getroot()

# Find all Parts and Wires
parts = {}
wires = []

# Extract Parts
for elem in root.iter():
    if elem.tag.endswith('}Part'):
        uid = elem.get('UId')
        name = elem.get('Name')
        if uid and name:
            parts[uid] = {'name': name, 'elem': elem}
            print(f"Part UId={uid} Name={name}")

print(f"\nTotal parts found: {len(parts)}\n")

# Find wire that connects to RestLimitSwitch (NameCon with UId=101, Name=RestLimitSwitch)
print("=" * 80)
print("SEARCHING FOR WIRES CONNECTED TO RestLimitSwitch")
print("=" * 80)

# Find NameCon elements with RestLimitSwitch
for namecon in root.iter():
    if namecon.tag.endswith('}NameCon'):
        uid = namecon.get('UId')
        name = namecon.get('Name')
        if name == 'RestLimitSwitch':
            print(f"\nFound RestLimitSwitch NameCon: UId={uid}")
            # Find parent wire
            for wire in root.iter():
                if wire.tag.endswith('}Wire'):
                    for child in wire:
                        if child == namecon or (child.get('UId') == uid and child.get('Name') == 'RestLimitSwitch'):
                            print(f"  Wire: {wire.attrib}")
                            for conn in wire:
                                print(f"    Connection: {conn.tag} {conn.attrib}")

