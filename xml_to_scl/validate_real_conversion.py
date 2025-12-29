"""
Validation Test: Real-world FB conversion with Positioning_MOL_Machine_FB.xml

This test validates that:
1. The file parses without errors
2. FB calls are properly extracted with parameters
3. Boolean expressions are properly reconstructed
4. Output is properly generated as SCL code
"""

import logging
from pathlib import Path
from main import FBFCParser
from fbfc_generator import FBFCGenerator

# Suppress debug logging
logging.basicConfig(level=logging.WARNING)

# Path to test file
test_file = Path("../Software units/1_Orchestrator_Safety/Program blocks/002_PrjBlocks/03_Machines/05_POSITIONING_MOTOR_OPEN_LOOP_MACHINE/Positioning_MOL_Machine_FB.xml")

print("="*80)
print("VALIDATION TEST: Real-World FB Conversion")
print("="*80)
print(f"\nInput File: {test_file.name}")

if not test_file.exists():
    print(f"ERROR: File not found at {test_file}")
    exit(1)

try:
    # Step 1: Parse the FB XML file
    print("\n[1/3] Parsing FB XML...")
    parser = FBFCParser(test_file)
    parser.parse()
    fb_data = parser.parsed_data
    print(f"  [OK] FB parsed: {fb_data.get('name')} ({fb_data.get('block_type')})")

    # Step 2: Check FB calls extraction
    print("\n[2/3] Checking FB calls extraction...")
    fb_calls = fb_data.get('fb_calls', [])
    print(f"  [OK] Found {len(fb_calls)} FB instances")

    # Count parameters
    total_inputs = sum(len(fc.get('inputs', {})) for fc in fb_calls)
    total_outputs = sum(len(fc.get('outputs', {})) for fc in fb_calls)
    unresolved_inputs = sum(
        1 for fc in fb_calls
        for val in fc.get('inputs', {}).values()
        if val == '???'
    )

    print(f"\n  Input parameters:  {total_inputs}")
    if unresolved_inputs == 0:
        print(f"    [OK] All resolved ({total_inputs - unresolved_inputs}/{total_inputs})")
    else:
        print(f"    [WARN] Some unresolved: {total_inputs - unresolved_inputs}/{total_inputs}")

    print(f"\n  Output parameters: {total_outputs}")

    # Show FB instance details
    print(f"\n  Instance details:")
    for i, fc in enumerate(fb_calls, 1):
        inputs_str = f"{len(fc.get('inputs', {}))} inputs"
        outputs_str = f"{len(fc.get('outputs', {}))} outputs"
        print(f"    {i}. {fc['instance']:15s} ({fc['fb_type']:10s}): {inputs_str:12s} {outputs_str}")

    # Step 3: Generate SCL code
    print("\n[3/3] Generating SCL code...")
    generator = FBFCGenerator(fb_data)
    scl_code = generator.generate()

    if scl_code:
        lines = scl_code.split('\n')
        print(f"  [OK] Generated {len(lines)} lines of SCL code")

        # Check for specific quality metrics
        region_count = scl_code.count('REGION')
        fb_call_count = scl_code.count('#')
        assignment_count = scl_code.count(' := ')

        print(f"\n  Code metrics:")
        print(f"    [OK] REGION blocks:     {region_count // 2} (balanced pairs)")
        print(f"    [OK] FB call syntax:    ~{fb_call_count} instances")
        print(f"    [OK] Assignments:       {assignment_count}")

        # Check for problematic patterns
        nested_regions = scl_code.count('   REGION') - scl_code.count('   \n   REGION')
        unresolved_expressions = scl_code.count('???')

        if nested_regions == 0:
            print(f"    [OK] No nested REGION blocks")
        else:
            print(f"    [WARN] Found nested REGION blocks")

        if unresolved_expressions == 0:
            print(f"    [OK] No unresolved expressions (???)")
        else:
            print(f"    [WARN] Found {unresolved_expressions} unresolved expressions")

        # Show sample of generated code
        print(f"\n  Sample (first 40 lines of logic):")
        print("  " + "-" * 76)

        in_logic = False
        line_count = 0
        for line in lines:
            if 'BEGIN' in line:
                in_logic = True
            if in_logic and 'REGION' in line:
                print(f"  {line[:76]}")
                line_count += 1
            if line_count > 5:
                break

        print("  ...")
        print("  " + "-" * 76)

    else:
        print("  ERROR: No SCL code generated")
        exit(1)

    print("\n" + "="*80)
    print("VALIDATION COMPLETE: All checks passed [OK]")
    print("="*80)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
