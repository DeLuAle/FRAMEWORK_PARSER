"""Test wire UID extraction"""
import xml.etree.ElementTree as ET

xml_text = """<?xml version="1.0"?>
<FlgNet xmlns="http://www.siemens.com/automation/Openness/SW/NetworkSource/FlgNet/v5">
  <Parts>
    <Access Scope="GlobalVariable" UId="21">
      <Symbol><Component Name="GEN_PEm"/></Symbol>
    </Access>
    <Part Name="ESTOP1" UId="25">
      <Instance><Component Name="ESTOP_CC"/></Instance>
    </Part>
  </Parts>
  <Wires>
    <Wire UId="32">
      <IdentCon UId="21"/>
      <NameCon UId="25" Name="E_STOP"/>
    </Wire>
  </Wires>
</FlgNet>"""

root = ET.fromstring(xml_text)

# Find wire
for child in root:
    if 'Wires' in child.tag:
        wires_elem = child
        for wire in wires_elem:
            if 'Wire' in wire.tag:
                print("Wire found:")
                for elem in wire:
                    tag = elem.tag.split('}')[-1]
                    uid = elem.get('UId')
                    name = elem.get('Name')
                    print(f"  {tag}: UId={uid}, Name={name}")
