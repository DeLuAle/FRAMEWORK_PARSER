
import os
import sys
import logging
from plc_tag_parser import PLCTagParser

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_parser():
    # Path to the specific XML file
    xml_path = r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\PLC tags\Default tag table.xml"
    
    if not os.path.exists(xml_path):
        logging.error(f"File not found: {xml_path}")
        return

    parser = PLCTagParser()
    try:
        results = parser.parse(xml_path)
        
        print(f"\n--- Parsed {len(results)} items ---")
        
        # Print first 5 items
        for i, item in enumerate(results[:5]):
            print(f"[{i}] {item}")
            
        # Check for specific known tag
        known_tag = "A01_Straightener_Ax_Actor_Interface_AddressIn"
        found = any(x['name'] == known_tag for x in results)
        if found:
            print(f"\nSUCCESS: Found expected tag '{known_tag}'")
        else:
            print(f"\nFAILURE: Could not find '{known_tag}'")

    except Exception as e:
        logging.error(f"Error during parsing: {e}")
        raise

if __name__ == "__main__":
    test_parser()
