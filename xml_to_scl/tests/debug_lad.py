"""
Debug LAD parser to see what's being extracted
"""
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fbfc_parser import FBFCParser
from utils import setup_logging
import logging

def debug_lad_parser():
    """Debug LAD parser"""
    
    setup_logging(level=logging.DEBUG)
    
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\Program blocks\000_Safety\F_Estop_FB.xml")
    
    parser = FBFCParser(test_file)
    data = parser.parse()
    
    print(f"Parsed FB: {data.get('name')}")
    print(f"Has graphical logic: {data.get('has_graphical_logic')}")
    print(f"FB calls extracted: {len(data.get('fb_calls', []))}")
    
    fb_calls = data.get('fb_calls', [])
    if fb_calls:
        print("\nFB Calls:")
        for fb_call in fb_calls:
            print(f"\n  Instance: {fb_call.get('instance')}")
            print(f"  Type: {fb_call.get('fb_type')}")
            print(f"  Inputs: {fb_call.get('inputs')}")
            print(f"  Outputs: {fb_call.get('outputs')}")
    else:
        print("\nNo FB calls extracted - debugging needed")

if __name__ == "__main__":
    debug_lad_parser()
