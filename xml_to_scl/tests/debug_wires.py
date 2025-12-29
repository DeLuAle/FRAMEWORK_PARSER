"""
Debug LAD parser to see wire connections in detail
"""
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fbfc_parser import FBFCParser
from utils import setup_logging
import logging

def debug_lad_wires():
    """Debug LAD wire connections"""
    
    setup_logging(level=logging.INFO)  # Less verbose
    
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\Program blocks\000_Safety\F_Estop_FB.xml")
    
    parser = FBFCParser(test_file)
    data = parser.parse()
    
    fb_calls = data.get('fb_calls', [])
    if fb_calls:
        print(f"\nFound {len(fb_calls)} FB calls\n")
        
        # Show first FB call in detail
        fb_call = fb_calls[0]
        print(f"Instance: {fb_call.get('instance')}")
        print(f"Type: {fb_call.get('fb_type')}")
        print(f"\nInputs ({len(fb_call.get('inputs', {}))} parameters):")
        for name, value in fb_call.get('inputs', {}).items():
            print(f"  {name} := {value}")
        print(f"\nOutputs ({len(fb_call.get('outputs', {}))} parameters):")
        for name, value in fb_call.get('outputs', {}).items():
            print(f"  {name} => {value}")

if __name__ == "__main__":
    debug_lad_wires()
