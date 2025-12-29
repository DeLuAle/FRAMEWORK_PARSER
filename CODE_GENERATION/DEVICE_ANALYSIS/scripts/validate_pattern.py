#!/usr/bin/env python3
"""
validate_pattern.py - Validate device pattern JSON against schema v1.0.2

Usage:
    python validate_pattern.py <pattern.json> [schema.json]

Example:
    python validate_pattern.py device_pattern_OnOffAxis.json
    python validate_pattern.py device_pattern_OnOffAxis.json custom_schema.json
"""

import sys
import json
import os

def validate_pattern(pattern_path, schema_path=None):
    """Validate a device pattern JSON file against the schema."""
    
    # Default schema path
    if schema_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(script_dir, '..', 'device_pattern_schema.json')
    
    # Load files
    try:
        with open(pattern_path, 'r', encoding='utf-8') as f:
            pattern = json.load(f)
    except FileNotFoundError:
        print(f"âŒ Pattern file not found: {pattern_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"âŒ Invalid JSON in pattern file: {e}")
        return False
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"âŒ Schema file not found: {schema_path}")
        return False
    
    # Try jsonschema library first
    try:
        import jsonschema
        has_jsonschema = True
    except ImportError:
        has_jsonschema = False
    
    if has_jsonschema:
        try:
            jsonschema.validate(pattern, schema)
            print(f"✅ VALID: {pattern_path}")
            print(f"   Schema: v{pattern.get('schema_version', 'unknown')}")
            print(f"   FB: {pattern.get('metadata', {}).get('fb_name', 'unknown')}")
            print(f"   Portability: {pattern.get('metadata', {}).get('portability_gate', {}).get('status', 'unknown')}")
            return True
        except jsonschema.ValidationError as e:
            print(f"âŒ INVALID: {pattern_path}")
            print(f"   Error: {e.message}")
            print(f"   Path: {' -> '.join(str(p) for p in e.absolute_path)}")
            return False
    else:
        # Fallback: basic validation without jsonschema library
        return validate_basic(pattern, schema)


def validate_basic(pattern, schema):
    """Basic validation without jsonschema library."""
    
    errors = []
    
    # Check required top-level fields
    required = schema.get('required', [])
    for field in required:
        if field not in pattern:
            errors.append(f"Missing required field: {field}")
    
    # Check schema_version
    if 'schema_version' in pattern:
        expected = schema.get('properties', {}).get('schema_version', {}).get('const')
        if expected and pattern['schema_version'] != expected:
            errors.append(f"Schema version mismatch: expected {expected}, got {pattern['schema_version']}")
    
    # Check metadata required fields
    metadata = pattern.get('metadata', {})
    meta_required = schema.get('properties', {}).get('metadata', {}).get('required', [])
    for field in meta_required:
        if field not in metadata:
            errors.append(f"Missing required metadata field: {field}")
    
    # Check device_family enum
    device_family = metadata.get('device_family')
    valid_families = schema.get('properties', {}).get('metadata', {}).get('properties', {}).get('device_family', {}).get('enum', [])
    if device_family and valid_families and device_family not in valid_families:
        errors.append(f"Invalid device_family: {device_family}. Valid: {valid_families}")
    
    # Check portability_gate
    gate = metadata.get('portability_gate', {})
    if 'status' in gate and gate['status'] not in ['PASS', 'PASS_WITH_WARNINGS', 'FAIL', 'SKIP']:
        errors.append(f"Invalid portability_gate.status: {gate['status']}")
    
    # Check anti_patterns format
    for i, ap in enumerate(pattern.get('anti_patterns', [])):
        if 'id' not in ap:
            errors.append(f"anti_patterns[{i}]: missing 'id'")
        elif not ap['id'].startswith('AP') or len(ap['id']) != 5:
            errors.append(f"anti_patterns[{i}]: invalid id format '{ap['id']}' (expected AP###)")
        
        if 'type' not in ap:
            errors.append(f"anti_patterns[{i}]: missing 'type'")
        
        if 'severity' not in ap:
            errors.append(f"anti_patterns[{i}]: missing 'severity'")
        elif ap['severity'] not in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'WARNING', 'INFO']:
            errors.append(f"anti_patterns[{i}]: invalid severity '{ap['severity']}'")
    
    # Check constraints derivation
    constraints = pattern.get('constraints', {})
    gate_status = gate.get('status')
    if gate_status == 'PASS' and constraints.get('portability_compliant') is False:
        errors.append("Inconsistency: portability_gate=PASS but portability_compliant=false")
    if gate_status == 'FAIL' and constraints.get('portability_compliant') is True:
        errors.append("Inconsistency: portability_gate=FAIL but portability_compliant=true")
    
    if errors:
        print(f"âŒ INVALID (basic check): {len(errors)} error(s)")
        for err in errors:
            print(f"   - {err}")
        return False
    else:
        print(f"✅ VALID (basic check)")
        print(f"   Schema: v{pattern.get('schema_version', 'unknown')}")
        print(f"   FB: {pattern.get('metadata', {}).get('fb_name', 'unknown')}")
        print(f"   Portability: {gate_status}")
        print(f"   ⚠️  Install jsonschema for full validation: pip install jsonschema")
        return True


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    pattern_path = sys.argv[1]
    schema_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = validate_pattern(pattern_path, schema_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
