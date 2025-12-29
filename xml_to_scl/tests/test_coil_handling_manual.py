"""
Test script for FB/FC parser with CoilHandling_FB.xml
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fbfc_parser import FBFCParser
from fbfc_generator import FBFCGenerator
from utils import setup_logging

def test_coil_handling_parser():
    """Test FB parser with CoilHandling_FB.xml"""
    
    setup_logging()
    
    # Path to test file
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\31_Area01\Program blocks\10_MANAGER\CoilHandling_FB.xml")
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False
    
    print(f"Testing FB parser with: {test_file.name}")
    print("=" * 70)
    
    try:
        # Parse XML
        parser = FBFCParser(test_file)
        data = parser.parse()
        
        print(f"\nParsed FB: {data.get('name')}")
        print(f"Block Type: {data.get('block_type')}")
        print(f"Programming Language: {data.get('programming_language')}")
        
        interface = data.get('interface', {})
        print(f"\nInterface sections:")
        for section_name, members in interface.items():
            print(f"  {section_name}: {len(members)} members")
            
        print(f"\nExtracted FB Calls: {len(data.get('fb_calls', []))}")
            
        # Generator
        generator = FBFCGenerator(data)
        scl_code = generator.generate()
        
        print("\nGenerated SCL code (First 3000 chars):")
        print("=" * 70)
        print(scl_code[:3000])
        print("..." if len(scl_code) > 3000 else "")
        print("=" * 70)
        
        # Save to output file
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{data.get('name', 'test')}.scl"
        
        generator.generate(output_file)
        print(f"\nSCL code saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_coil_handling_parser()
    sys.exit(0 if success else 1)
