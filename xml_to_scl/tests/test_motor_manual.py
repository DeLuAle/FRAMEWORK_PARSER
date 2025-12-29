"""
Test script for FB/FC parser with Motor.xml
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from fbfc_parser import FBFCParser
from fbfc_generator import FBFCGenerator
from utils import setup_logging

def test_motor_parser():
    """Test FB parser with Motor.xml"""
    
    setup_logging()
    
    # Path to test file
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\Program blocks\001_StdBlocks\002_Device\Motor\Motor.xml")
    
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
        
        # Generate SCL
        generator = FBFCGenerator(data)
        scl_code = generator.generate()
        
        print("\nGenerated SCL code:")
        print("=" * 70)
        # Print relevant logic part (Region LOGIC)
        if "REGION Logic" in scl_code:
            start = scl_code.find("REGION Logic")
            print(scl_code[start:start+2000])
        else:
            print(scl_code)
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
    success = test_motor_parser()
    sys.exit(0 if success else 1)
