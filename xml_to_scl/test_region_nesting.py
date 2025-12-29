"""
Unit Tests for REGION Nesting Structure

Tests verify that:
1. Multiple networks generate sequential REGION blocks (not nested)
2. Each REGION has matching REGION/END_REGION pairs
3. REGION indentation is consistent
4. No deeply nested REGION structures exist
"""

import unittest
import re
from pathlib import Path
from fbfc_generator import FBFCGenerator


class TestREGIONNesting(unittest.TestCase):
    """Test REGION nesting structure in generated SCL code."""

    def parse_region_structure(self, scl_code: str) -> list:
        """
        Parse REGION blocks from SCL code and return structure.

        Returns:
            List of dicts with 'name', 'start_line', 'end_line', 'indent'
        """
        lines = scl_code.split('\n')
        regions = []
        stack = []

        for i, line in enumerate(lines, 1):
            # Count leading spaces for indentation
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            if stripped.startswith('REGION '):
                # Extract region name
                match = re.search(r'REGION\s+"([^"]*)"', stripped)
                if match:
                    name = match.group(1)
                    region_info = {
                        'name': name,
                        'start_line': i,
                        'end_line': None,
                        'indent': indent,
                        'depth': len(stack),
                    }
                    stack.append(region_info)
                    regions.append(region_info)

            elif stripped.startswith('END_REGION'):
                if stack:
                    region = stack.pop()
                    region['end_line'] = i

        return regions

    def test_regions_are_sequential_not_nested(self):
        """Test that REGION blocks are sequential (same indent) not nested."""
        # Create a minimal test data structure
        test_data = {
            'name': 'TestBlock',
            'block_type': 'FB',
            'has_graphical_logic': True,
            'programming_language': 'LAD',
            'interface': {'Input': [], 'Output': [], 'Static': []},
            'networks': [
                {
                    'number': 1,
                    'type': 'LAD',
                    'title': 'Network 1',
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                },
                {
                    'number': 2,
                    'type': 'LAD',
                    'title': 'Network 2',
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                },
                {
                    'number': 3,
                    'type': 'LAD',
                    'title': 'Network 3',
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                },
            ],
        }

        # Generate SCL code
        generator = FBFCGenerator(test_data)
        scl_code = generator.generate()

        # Parse regions
        regions = self.parse_region_structure(scl_code)

        # Verify we have 3 regions
        self.assertEqual(len(regions), 3, "Should have exactly 3 REGION blocks")

        # Verify all regions are at the same depth (not nested)
        for region in regions:
            self.assertGreater(region['depth'], -1, f"Region should have depth >= 0")
            self.assertLess(
                region['depth'], 2,
                f"Region '{region['name']}' should not be nested (depth={region['depth']})"
            )

        # Verify all regions have the same indentation
        indents = [r['indent'] for r in regions]
        self.assertTrue(
            all(indent == indents[0] for indent in indents),
            f"All REGIONs should have same indentation, got: {indents}"
        )

    def test_region_pairs_are_balanced(self):
        """Test that all REGION blocks have matching END_REGION."""
        test_data = {
            'name': 'TestBlock',
            'block_type': 'FB',
            'has_graphical_logic': True,
            'programming_language': 'LAD',
            'interface': {'Input': [], 'Output': [], 'Static': []},
            'networks': [
                {
                    'number': 1,
                    'type': 'LAD',
                    'title': 'Network 1',
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                },
            ],
        }

        generator = FBFCGenerator(test_data)
        scl_code = generator.generate()

        regions = self.parse_region_structure(scl_code)

        # Every region should have a matching END_REGION
        for region in regions:
            self.assertIsNotNone(
                region['end_line'],
                f"Region '{region['name']}' missing END_REGION"
            )
            self.assertGreater(
                region['end_line'], region['start_line'],
                f"Region '{region['name']}' has invalid line numbers"
            )

    def test_no_deeply_nested_regions(self):
        """Test that no REGION blocks are nested more than 1 level deep."""
        test_data = {
            'name': 'TestBlock',
            'block_type': 'FB',
            'has_graphical_logic': True,
            'programming_language': 'LAD',
            'interface': {'Input': [], 'Output': [], 'Static': []},
            'networks': [
                {
                    'number': i,
                    'type': 'LAD',
                    'title': f'Network {i}',
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                }
                for i in range(1, 6)
            ],
        }

        generator = FBFCGenerator(test_data)
        scl_code = generator.generate()

        regions = self.parse_region_structure(scl_code)

        # Maximum depth should be 0 (no nesting in graphical logic)
        max_depth = max(r['depth'] for r in regions) if regions else -1
        self.assertLessEqual(
            max_depth, 0,
            f"REGIONs are nested {max_depth + 1} levels deep, should be 1 level max"
        )

    def test_scl_code_indentation_is_consistent(self):
        """Test that SCL code indentation is consistent (uses 3-space tabs)."""
        test_data = {
            'name': 'TestBlock',
            'block_type': 'FB',
            'has_graphical_logic': True,
            'programming_language': 'LAD',
            'interface': {'Input': [], 'Output': [], 'Static': []},
            'networks': [
                {
                    'number': 1,
                    'type': 'SCL',
                    'title': 'Network 1',
                    'comment': 'Test comment',
                    'code': 'x := 1;',
                },
            ],
        }

        generator = FBFCGenerator(test_data)
        scl_code = generator.generate()

        lines = scl_code.split('\n')
        for i, line in enumerate(lines):
            if line and line[0] == ' ':
                # Count leading spaces
                spaces = len(line) - len(line.lstrip(' '))
                # Should be multiple of 3 (standard indentation)
                self.assertEqual(
                    spaces % 3, 0,
                    f"Line {i+1} has {spaces} spaces, should be multiple of 3"
                )

    def test_multiple_networks_generate_separate_regions(self):
        """Test that each network generates its own REGION block."""
        num_networks = 10
        test_data = {
            'name': 'TestBlock',
            'block_type': 'FB',
            'has_graphical_logic': True,
            'programming_language': 'LAD',
            'interface': {'Input': [], 'Output': [], 'Static': []},
            'networks': [
                {
                    'number': i,
                    'type': 'LAD',
                    'title': f'Network {i}',
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                }
                for i in range(1, num_networks + 1)
            ],
        }

        generator = FBFCGenerator(test_data)
        scl_code = generator.generate()

        regions = self.parse_region_structure(scl_code)

        # Should have exactly num_networks regions
        self.assertEqual(
            len(regions), num_networks,
            f"Should generate {num_networks} REGION blocks for {num_networks} networks"
        )

    def test_region_names_are_preserved(self):
        """Test that network titles become REGION names."""
        network_titles = ['Init Phase', 'Main Loop', 'Error Handler']
        test_data = {
            'name': 'TestBlock',
            'block_type': 'FB',
            'has_graphical_logic': True,
            'programming_language': 'LAD',
            'interface': {'Input': [], 'Output': [], 'Static': []},
            'networks': [
                {
                    'number': i,
                    'type': 'LAD',
                    'title': title,
                    'comment': '',
                    'fb_calls': [],
                    'logic_ops': [],
                }
                for i, title in enumerate(network_titles, 1)
            ],
        }

        generator = FBFCGenerator(test_data)
        scl_code = generator.generate()

        # Check that all titles appear in REGION declarations
        for title in network_titles:
            self.assertIn(
                f'REGION "{title}"',
                scl_code,
                f"REGION name '{title}' not found in generated code"
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
