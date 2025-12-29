"""
Test script for PLC Tag Parser
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from plc_tag_parser import PLCTagParser
from utils import setup_logging

def test_tag_parser():
    setup_logging()
    
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\PLC tags\Default tag table.xml")
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False
        
    print(f"Testing Tag Parser with: {test_file.name}")
    print("=" * 70)
    
    try:
        parser = PLCTagParser()
        tags = parser.parse(test_file)
        
        print(f"\nFound {len(tags)} items (Tags + Constants)")
        
        print("\nSample Tags:")
        for i, tag in enumerate(tags[:10]):
            print(f"  {i+1}. Name: {tag['name']:<50} Type: {tag['data_type']:<20} Addr: {tag.get('logical_address', '')}")
            if tag.get('comment'):
                print(f"     Comment: {tag['comment']}")
                
        # Test Generation
        from plc_tag_generator import PLCTagGenerator
        
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "Default tag table.csv"
        
        generator = PLCTagGenerator(tags)
        generator.generate(output_file)
        print(f"\nTags exported to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tag_parser()
    sys.exit(0 if success else 1)
