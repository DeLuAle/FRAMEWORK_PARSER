"""
Debug script to check if nested struct members are being parsed
"""
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from udt_parser import UDTParser

def debug_nested_structs():
    """Debug nested struct parsing"""
    
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\PLC data types\Areas_ITF\ITF_A01.xml")
    
    parser = UDTParser(test_file)
    data = parser.parse()
    
    print("Checking nested struct members:")
    print("=" * 70)
    
    for member in data.get('members', []):
        name = member.get('name')
        datatype = member.get('datatype')
        is_struct = member.get('is_struct', False)
        has_members = 'members' in member
        num_members = len(member.get('members', []))
        
        print(f"{name:40} | Type: {datatype:15} | is_struct: {is_struct} | has_members: {has_members} | count: {num_members}")
        
        if has_members and num_members > 0:
            print(f"  └─ Nested members:")
            for nested in member['members'][:3]:  # Show first 3
                print(f"     - {nested.get('name')}: {nested.get('datatype')}")

if __name__ == "__main__":
    debug_nested_structs()
