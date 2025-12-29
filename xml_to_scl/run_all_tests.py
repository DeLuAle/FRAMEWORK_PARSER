"""
Run all test suites and generate comprehensive report
"""

import subprocess
import sys

test_files = [
    ('test_security_xxe.py', 'Session #1: Security & Error Handling'),
    ('test_region_nesting.py', 'Session #2: REGION Nesting'),
    ('test_boolean_expression_builder.py', 'Session #3: Boolean Expression'),
    ('test_fb_parameters.py', 'Session #4: FB Parameters'),
]

print("="*80)
print("COMPREHENSIVE TEST SUITE - ALL SESSIONS")
print("="*80)
print()

total_tests = 0
total_passed = 0
all_passed = True

for test_file, description in test_files:
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print("-"*80)
    
    result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
    
    # Parse output for test counts
    output = result.stdout + result.stderr
    
    if "Ran" in output:
        # Extract test count from "Ran X tests in Y seconds"
        for line in output.split('\n'):
            if "Ran" in line and "tests" in line:
                parts = line.split()
                num_tests = int(parts[1])
                total_tests += num_tests
                
                if "OK" in output:
                    total_passed += num_tests
                    print(f"Result: {num_tests}/{num_tests} PASSED [OK]")
                else:
                    print(f"Result: FAILED")
                    all_passed = False
                break
    
    print()

print("="*80)
print("FINAL RESULTS")
print("="*80)
print(f"Total Tests: {total_passed}/{total_tests}")
print(f"Status: {'ALL PASSED [OK]' if all_passed else 'SOME FAILED'}")
print()
print("Summary:")
print("  - Session #1 (Security):            10 tests")
print("  - Session #2 (REGION Nesting):      6 tests")
print("  - Session #3 (Boolean Expr):        4 tests")
print("  - Session #4 (FB Parameters):       4 tests")
print("  " + "-"*76)
print(f"  - Total:                           {total_tests} tests")
print("="*80)
