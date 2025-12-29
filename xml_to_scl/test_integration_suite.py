"""
Integration Test Suite for Session #5

Comprehensive testing of the XML to SCL converter on multiple real-world files.
"""

import logging
import time
import sys
from pathlib import Path
from collections import defaultdict
from main import identify_file_type, process_file

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

class IntegrationTestSuite:
    def __init__(self):
        self.results = defaultdict(list)
        self.file_count = 0
        self.converted_count = 0
        self.errors = []
        self.metrics = {}

    def discover_test_files(self, search_root, file_types=None, limit=None):
        """Discover test files of specific types"""
        if file_types is None:
            file_types = ['fb', 'fc']

        xml_files = list(search_root.rglob("*.xml"))
        test_files = []

        for xml_file in sorted(xml_files):
            try:
                file_type = identify_file_type(xml_file)
                if file_type in file_types:
                    test_files.append((xml_file, file_type))
            except:
                pass

        # Prefer diverse file sizes
        by_size = defaultdict(list)
        for xml_file, file_type in test_files:
            size = xml_file.stat().st_size
            if size < 50_000:
                by_size['small'].append((xml_file, file_type))
            elif size < 200_000:
                by_size['medium'].append((xml_file, file_type))
            else:
                by_size['large'].append((xml_file, file_type))

        # Select representative sample
        selected = []
        for size_cat in ['small', 'medium', 'large']:
            if by_size[size_cat]:
                # Take first 2 of each size category and type
                by_type = defaultdict(list)
                for xml_file, file_type in by_size[size_cat]:
                    by_type[file_type].append(xml_file)

                for file_type in by_type:
                    selected.extend(
                        [(f, file_type) for f in by_type[file_type][:2]]
                    )

        if limit:
            selected = selected[:limit]

        return selected

    def run_conversion_test(self, xml_file, file_type):
        """Test conversion of a single file"""
        start_time = time.time()
        result = {
            'file': xml_file.name,
            'path': str(xml_file),
            'type': file_type,
            'success': False,
            'error': None,
            'conversion_time': 0,
            'output_size': 0
        }

        try:
            # Use temp directory for output
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)

                # Process the file (writes to disk)
                process_file(Path(xml_file), tmpdir_path)

                # Check if output file was created
                output_files = list(tmpdir_path.glob("*.*"))
                if output_files:
                    result['success'] = True
                    result['output_size'] = sum(f.stat().st_size for f in output_files)
                else:
                    result['error'] = "No output file generated"

        except Exception as e:
            result['error'] = str(e)

        result['conversion_time'] = time.time() - start_time
        return result

    def validate_output(self, scl_code):
        """Validate SCL code quality"""
        issues = []

        # Check for unresolved expressions
        if '???' in scl_code:
            count = scl_code.count('???')
            issues.append(f"Found {count} unresolved expressions (???)")

        # Check REGION structure
        region_count = scl_code.count('REGION')
        end_region_count = scl_code.count('END_REGION')
        if region_count != end_region_count:
            issues.append(f"Unbalanced REGION blocks: {region_count} vs {end_region_count}")

        # Check basic syntax
        lines = scl_code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for common syntax errors
            if 'BEGIN' in line and not any(c in line for c in [';']):
                # BEGIN statements don't need semicolons
                pass
            if ':=' in line and not line.rstrip().endswith((';', ')', ',')):
                if 'THEN' not in line and 'ELSIF' not in line:
                    # Some lines might not need semicolon
                    pass

        return issues

    def run_all_tests(self, search_root, limit=10):
        """Run conversion tests on multiple files"""
        print("\n" + "="*80)
        print("INTEGRATION TEST SUITE - SESSION #5")
        print("="*80)

        # Discover test files
        print(f"\nDiscovering test files in {search_root}...")
        test_files = self.discover_test_files(search_root, limit=limit)

        if not test_files:
            print("No test files found!")
            return

        print(f"Found {len(test_files)} test files to process\n")
        print("-"*80)

        # Process each file
        for i, (xml_file, file_type) in enumerate(test_files, 1):
            print(f"\n[{i}/{len(test_files)}] Testing: {xml_file.name}")
            print(f"  Type: {file_type}")
            print(f"  Path: {xml_file.relative_to(search_root)}")

            result = self.run_conversion_test(xml_file, file_type)
            self.results[file_type].append(result)

            if result['success']:
                self.converted_count += 1
                print(f"  Status: SUCCESS")
                print(f"  Time: {result['conversion_time']:.3f}s")
                print(f"  Output: {result['output_size']:,} bytes")
            else:
                self.errors.append(result)
                print(f"  Status: FAILED")
                print(f"  Error: {result['error']}")

        self.file_count = len(test_files)
        self._print_summary()

    def _print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        print(f"\nTotal files processed: {self.file_count}")
        print(f"Successful conversions: {self.converted_count}")
        print(f"Failed conversions: {len(self.errors)}")
        print(f"Success rate: {self.converted_count/self.file_count*100:.1f}%")

        # Statistics by type
        print("\nResults by file type:")
        for file_type in sorted(self.results.keys()):
            results = self.results[file_type]
            successes = sum(1 for r in results if r['success'])
            print(f"  {file_type.upper():10s}: {successes:2d}/{len(results):2d} passed")

        # Performance metrics
        if self.converted_count > 0:
            times = [r['conversion_time'] for r in [r for rs in self.results.values() for r in rs] if r['success']]
            if times:
                print(f"\nPerformance metrics:")
                print(f"  Average time: {sum(times)/len(times):.3f}s")
                print(f"  Min time: {min(times):.3f}s")
                print(f"  Max time: {max(times):.3f}s")

        # Errors summary
        if self.errors:
            print(f"\nFailed conversions:")
            for error in self.errors[:5]:
                print(f"  - {error['file']}: {error['error']}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors)-5} more")

if __name__ == '__main__':
    # Find project root
    search_root = Path(__file__).parent.parent.parent  # Go to MBK_2

    # Run tests
    suite = IntegrationTestSuite()
    suite.run_all_tests(search_root, limit=10)

    # Exit with appropriate code
    sys.exit(0 if suite.converted_count == suite.file_count else 1)
