"""Quick test to verify LAD parser works with first network"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lad_parser import LADLogicParser
import xml.etree.ElementTree as ET

# Parse the XML
xml_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\Program blocks\000_Safety\F_Estop_FB.xml")
tree = ET.parse(xml_file)
root = tree.getroot()

# Find first CompileUnit with NetworkSource
for elem in root.iter():
    if 'CompileUnit' in elem.tag:
        network_source = None
        for child in elem:
            if 'NetworkSource' in child.tag and len(child) > 0:
                network_source = child
                break
        
        if network_source:
            print("Found first network with FlgNet")
            parser = LADLogicParser(elem)
            fb_calls = parser.parse()
            
            if fb_calls:
                print(f"\nExtracted {len(fb_calls)} FB calls:")
                for fb in fb_calls:
                    print(f"\n  {fb['instance']} ({fb['fb_type']}):")
                    print(f"    Inputs: {fb['inputs']}")
                    print(f"    Outputs: {fb['outputs']}")
            break
