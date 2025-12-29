"""
Debug script to check XML parsing
"""
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from udt_parser import UDTParser

def debug_xml_parsing():
    """Debug XML parsing to see what datatypes are read"""
    
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\PLC data types\Areas_ITF\ITF_A01.xml")
    
    # Parse with our parser
    parser = UDTParser(test_file)
    data = parser.parse()
    
    print("Parsed members and their datatypes:")
    print("=" * 70)
    
    for member in data.get('members', [])[:15]:
        name = member.get('name')
        datatype = member.get('datatype')
        print(f"{name:40} : {datatype}")
    
    print("\n" + "=" * 70)
    print("\nDirect XML parsing:")
    print("=" * 70)
    
    # Parse XML directly
    tree = ET.parse(test_file)
    root = tree.getroot()
    
    # Find all Member elements with Datatype attribute
    for member in root.findall('.//Member[@Datatype]')[:15]:
        name = member.get('Name')
        datatype = member.get('Datatype')
        print(f"{name:40} : {datatype}")

if __name__ == "__main__":
    debug_xml_parsing()
