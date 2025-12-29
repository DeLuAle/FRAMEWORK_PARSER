"""
Simple test script for UDT parser
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from udt_parser import UDTParser
from udt_generator import UDTGenerator
from utils import setup_logging

def test_udt_parser():
    """Test UDT parser with ITF_A01.xml"""
    
    setup_logging()
    
    # Path to test file
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety\PLC data types\Areas_ITF\ITF_A01.xml")
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False
    
    print(f"Testing UDT parser with: {test_file.name}")
    print("=" * 70)
    
    try:
        # Parse XML
        parser = UDTParser(test_file)
        data = parser.parse()
        
        print(f"\nParsed UDT: {data.get('name')}")
        print(f"Number of members: {len(data.get('members', []))}")
        
        # Generate SCL
        generator = UDTGenerator(data)
        scl_code = generator.generate()
        
        print("\nGenerated SCL code:")
        print("=" * 70)
        print(scl_code)
        print("=" * 70)
        
        # Save to output file
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{data.get('name', 'test')}.udt"
        
        generator.generate(output_file)
        print(f"\nSCL code saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_udt_parser()
    sys.exit(0 if success else 1)
