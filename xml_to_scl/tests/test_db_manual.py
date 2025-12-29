"""
Test script for DB parser
"""

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from db_parser import DBParser
from db_generator import DBGenerator
from utils import setup_logging

def test_db_parser():
    """Test DB parser with Encoder.xml"""
    
    setup_logging()
    
    # Path to test file
    test_file = Path(r"c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Program blocks\Encoder.xml")
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {test_file}")
        return False
    
    print(f"Testing DB parser with: {test_file.name}")
    print("=" * 70)
    
    try:
        # Parse XML
        parser = DBParser(test_file)
        data = parser.parse()
        
        print(f"\nParsed DB: {data.get('name')}")
        print(f"DB Type: {data.get('db_type')}")
        print(f"Number: {data.get('number')}")
        print(f"Number of variables: {len(data.get('variables', []))}")
        
        # Generate SCL
        generator = DBGenerator(data)
        scl_code = generator.generate()
        
        print("\nGenerated SCL code:")
        print("=" * 70)
        print(scl_code)
        print("=" * 70)
        
        # Save to output file
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{data.get('name', 'test')}.db"
        
        generator.generate(output_file)
        print(f"\nSCL code saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_db_parser()
    sys.exit(0 if success else 1)
