---
skill: device-analysis
version: 1.0.2
date: 2024-12-26
purpose: Extract reusable patterns from PLC Function Blocks for code generation
---

# Device Analysis Skill v1.0.2

## Purpose
Analyze SCL Function Blocks to extract:
1. Device patterns (command/status, state machine, alarms)
2. UDT contracts (input/output/inout)
3. Anti-patterns (portability violations)
4. Configuration templates

## Input Requirements
- `FB_PATH`: Path to .scl Function Block file
- `UDT_PATH`: Path to UDT folder (.xml files) - optional
- `OUTPUT_PATH`: Output directory (default: current dir)

## Output
- `device_pattern_{FB_NAME}.json` - Machine-readable pattern (schema v1.0.2)
- `DEVICE_{FB_NAME}.md` - Human-readable documentation

---

## Execution Instructions for Claude Code

When user provides an SCL file for analysis, execute these steps in order.

### STEP 1: Setup and Read Files

```python
import os
import re
import json
from datetime import datetime

# Get paths from user or use defaults
FB_PATH = "{{FB_PATH}}"  # User must provide
UDT_PATH = "{{UDT_PATH}}"  # Optional
OUTPUT_PATH = "{{OUTPUT_PATH}}"  # Default: /home/claude/output

# Read FB content
with open(FB_PATH, 'r', encoding='utf-8') as f:
    fb_content = f.read()

# Extract metadata
fb_name_match = re.search(r'FUNCTION_BLOCK\s+"([^"]+)"', fb_content)
FB_NAME = fb_name_match.group(1) if fb_name_match else os.path.basename(FB_PATH).replace('.scl', '')

version_match = re.search(r'VERSION\s*:\s*([\d.]+)', fb_content)
VERSION = version_match.group(1) if version_match else "1.0"

author_match = re.search(r'AUTHOR\s*:\s*([^\n;]+)', fb_content)
AUTHOR = author_match.group(1).strip() if author_match else "Unknown"

print(f"Analyzing: {FB_NAME} v{VERSION} by {AUTHOR}")
```

### STEP 2: Device Taxonomy Detection

```python
def detect_device_taxonomy(content, fb_name):
    """Detect device_family and device_type from code patterns."""
    
    device_family = "generic"
    device_type = "actuator_generic"
    
    # Motion family detection
    if re.search(r'MC_MoveAbsolute|MC_Home|MC_MoveRelative|MC_Power', content):
        device_family = "motion"
        if re.search(r'Rot|Turn|Rotation', fb_name, re.I):
            device_type = "rotary_servo"
        else:
            device_type = "linear_servo"
    elif re.search(r'TAx_DriveInterface', content):
        device_family = "motion"
        device_type = "servo_drive"
    elif re.search(r'PosFbk_ITF', content) and not re.search(r'MC_', content):
        device_family = "motion"
        device_type = "linear_onoff"
    
    # Pneumatic family detection
    elif re.search(r'Extend.*Retract|Retract.*Extend', content, re.I | re.S):
        device_family = "pneumatic"
        device_type = "cylinder_double"
    elif re.search(r'Open.*Close.*Grip|Grip.*Open.*Close', content, re.I | re.S):
        device_family = "pneumatic"
        device_type = "gripper"
    elif re.search(r'Open.*Close|Close.*Open', content, re.I | re.S):
        device_family = "pneumatic"
        device_type = "valve"
    
    return device_family, device_type

DEVICE_FAMILY, DEVICE_TYPE = detect_device_taxonomy(fb_content, FB_NAME)
print(f"Device: {DEVICE_FAMILY}/{DEVICE_TYPE}")
```

### STEP 3: Portability Gate Analysis (CRITICAL)

```python
def analyze_portability(content):
    """
    Detect CRITICAL portability violations.
    Returns: (status, violations_list, anti_patterns_list)
    """
    anti_patterns = []
    violations = []
    ap_counter = 1
    
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if re.match(r'^\s*//', line):
            continue
        
        # PG-01: Physical I/O (%I, %Q, %M)
        io_matches = re.finditer(r'%[IMQ][WDB]?[0-9]+(\.[0-9]+)?', line)
        for match in io_matches:
            # Skip if inside string literal
            if "'" in line and line.index("'") < match.start():
                continue
            ap_id = f"AP{ap_counter:03d}"
            anti_patterns.append({
                "id": ap_id,
                "type": "io_physical",
                "severity": "CRITICAL",
                "line": line_num,
                "code": line.strip()[:80],
                "rule": "portability_no_physical_io",
                "impact": "Breaks portability - project-specific address",
                "suggested_fix": "Pass via VAR_INPUT parameter"
            })
            violations.append(ap_id)
            ap_counter += 1
        
        # PG-02: AT mapping
        if re.search(r'\bAT\s+%[IMQ]', line):
            ap_id = f"AP{ap_counter:03d}"
            anti_patterns.append({
                "id": ap_id,
                "type": "io_at_mapping",
                "severity": "CRITICAL",
                "line": line_num,
                "code": line.strip()[:80],
                "rule": "portability_no_at_mapping",
                "impact": "AT mapping is project-specific",
                "suggested_fix": "Remove AT, use symbolic access"
            })
            violations.append(ap_id)
            ap_counter += 1
        
        # PG-03: Hardcoded global DB
        db_match = re.search(r'"DB_[A-Za-z0-9_]+"', line)
        if db_match:
            # Skip if inside string literal or comment
            if "'" in line and line.index("'") < db_match.start():
                continue
            ap_id = f"AP{ap_counter:03d}"
            anti_patterns.append({
                "id": ap_id,
                "type": "hardcoded_db",
                "severity": "CRITICAL",
                "line": line_num,
                "code": line.strip()[:80],
                "rule": "portability_no_global_db",
                "impact": "Global DB is project-specific",
                "suggested_fix": "Pass data via VAR_IN_OUT or UDT parameter"
            })
            violations.append(ap_id)
            ap_counter += 1
    
    # Non-critical: Manual edge detection (MEDIUM)
    for line_num, line in enumerate(lines, 1):
        if re.match(r'^\s*//', line):
            continue
        if re.search(r'\bAND\s+NOT\s+\w+_(old|prev|last)\b', line, re.I):
            ap_id = f"AP{ap_counter:03d}"
            anti_patterns.append({
                "id": ap_id,
                "type": "manual_edge_detection",
                "severity": "MEDIUM",
                "line": line_num,
                "code": line.strip()[:80],
                "rule": "use_native_triggers",
                "impact": "Code verbosity, non-standard",
                "suggested_fix": "Use R_TRIG or F_TRIG from standard library"
            })
            ap_counter += 1
    
    # Non-critical: Magic numbers (LOW) - limit to 5 examples
    magic_count = 0
    for line_num, line in enumerate(lines, 1):
        if magic_count >= 5:
            break
        if re.match(r'^\s*//', line):
            continue
        if re.search(r'VAR_CONSTANT|Config\.', line):
            continue
        magic_match = re.search(r'[^a-zA-Z_][0-9]+\.[0-9]+', line)
        if magic_match:
            ap_id = f"AP{ap_counter:03d}"
            anti_patterns.append({
                "id": ap_id,
                "type": "magic_number",
                "severity": "LOW",
                "line": line_num,
                "code": line.strip()[:80],
                "rule": "use_named_constants",
                "impact": "Hard to maintain, not configurable",
                "suggested_fix": "Define in Config UDT or VAR_CONSTANT"
            })
            ap_counter += 1
            magic_count += 1
    
    status = "FAIL" if violations else "PASS"
    return status, violations, anti_patterns

PORTABILITY_STATUS, PORTABILITY_VIOLATIONS, ANTI_PATTERNS = analyze_portability(fb_content)
print(f"Portability: {PORTABILITY_STATUS} ({len(PORTABILITY_VIOLATIONS)} violations)")
```

### STEP 4: Pattern Detection

```python
def detect_patterns(content):
    """Detect command/status patterns, state machine, timers, edge detection."""
    
    # Command/Status pattern
    pattern_cmd = "unknown"
    confidence = "LOW"
    
    if re.search(r'\.Permitted\s*:=.*NOT.*AND', content) and re.search(r'\.Request\s*:=.*\.Permitted', content):
        pattern_cmd = "Permittedâ†’Requestâ†’Cmdâ†’Done"
        confidence = "HIGH"
    elif re.search(r'Request.*Command|Command.*Request', content):
        pattern_cmd = "Requestâ†’Cmd"
        confidence = "MEDIUM"
    
    # State machine type
    state_type = "implicit"
    if re.search(r'CASE\s+\w+\s+OF', content):
        state_type = "explicit_case"
    elif re.search(r'\w+\.Request.*\.Permitted', content):
        state_type = "struct_pattern"
    
    # Extract states from REGION
    states = re.findall(r'REGION\s+(\w+)', content)
    if not states:
        states = ["Main"]
    
    # Timers
    timers = re.findall(r'(\w+)\s*:\s*(?:IEC_TIMER|TON|TOF|TP)', content)
    
    # Edge detection
    edge = "none"
    if re.search(r'R_TRIG|F_TRIG', content):
        edge = "R_TRIG"
    elif re.search(r'\bAND\s+NOT\s+\w+_(old|prev)', content):
        edge = "manual"
    
    # Math functions
    math_funcs = []
    for func in ['ABS', 'MAX', 'MIN', 'LIMIT', 'SEL', 'SQRT', 'SIN', 'COS']:
        if re.search(rf'\b{func}\s*\(', content):
            math_funcs.append(func)
    
    return {
        "command_status": {"pattern": pattern_cmd, "confidence": confidence},
        "state_machine": {"type": state_type, "states": states},
        "timers": timers,
        "edge_detection": edge,
        "math": math_funcs
    }

PATTERNS = detect_patterns(fb_content)
print(f"Pattern: {PATTERNS['command_status']['pattern']} ({PATTERNS['command_status']['confidence']})")
```

### STEP 5: UDT Classification (if UDT_PATH provided)

```python
def classify_udts(udt_path):
    """Classify UDTs by naming convention."""
    command_udts = []
    config_udts = []
    status_udts = []
    
    if not udt_path or not os.path.exists(udt_path):
        return command_udts, config_udts, status_udts
    
    for filename in os.listdir(udt_path):
        if not filename.endswith('.xml'):
            continue
        udt_name = filename.replace('.xml', '')
        
        if re.search(r'_Ctrl$|_Command$', udt_name):
            command_udts.append({"name": udt_name, "category": "command_udt"})
        elif re.search(r'_Config$|_Par', udt_name):
            config_udts.append({"name": udt_name, "category": "config_udt"})
        elif re.search(r'_Sts$|_Status$', udt_name):
            status_udts.append({"name": udt_name, "category": "status_udt"})
    
    return command_udts, config_udts, status_udts

COMMAND_UDTS, CONFIG_UDTS, STATUS_UDTS = classify_udts(UDT_PATH if 'UDT_PATH' in dir() else None)
```

### STEP 6: Generate JSON Output

```python
def generate_pattern_json(fb_name, version, author, device_family, device_type,
                          portability_status, portability_violations, anti_patterns,
                          patterns, command_udts, config_udts, status_udts):
    """Generate device_pattern JSON according to schema v1.0.2."""
    
    return {
        "schema_version": "1.0.2",
        "metadata": {
            "fb_name": fb_name,
            "version": version,
            "author": author,
            "device_family": device_family,
            "device_type": device_type,
            "analyzed_at": datetime.now().isoformat(),
            "source_files": {
                "fb_scl": FB_PATH
            },
            "portability_gate": {
                "status": portability_status,
                "violations": portability_violations
            }
        },
        "contract": {
            "input": {
                "command_udt": command_udts,
                "config_udt": config_udts,
                "logical_inputs": []
            },
            "output": {
                "status_udt": status_udts,
                "logical_outputs": []
            },
            "inout": {
                "interfaces": []
            }
        },
        "logic": {
            "state_machine": {
                "type": patterns["state_machine"]["type"],
                "states": patterns["state_machine"]["states"]
            },
            "key_algorithms": []
        },
        "patterns": {
            "command_status": patterns["command_status"],
            "alarm_handling": {"pattern": "unknown", "confidence": "LOW"},
            "native_functions": {
                "timers": patterns["timers"],
                "edge_detection": patterns["edge_detection"],
                "motion_control": [],
                "math": patterns["math"]
            }
        },
        "anti_patterns": anti_patterns,
        "dependencies": {
            "fb_called": [],
            "custom_udts": [],
            "external_devices": []
        },
        "constraints": {
            "portability_compliant": portability_status == "PASS",
            "multi_instance_safe": portability_status == "PASS",
            "notes": ""
        },
        "configuration": {
            "example_config": {},
            "validation_rules": []
        }
    }

# Generate JSON
pattern_data = generate_pattern_json(
    FB_NAME, VERSION, AUTHOR, DEVICE_FAMILY, DEVICE_TYPE,
    PORTABILITY_STATUS, PORTABILITY_VIOLATIONS, ANTI_PATTERNS,
    PATTERNS, COMMAND_UDTS, CONFIG_UDTS, STATUS_UDTS
)

# Save JSON
os.makedirs(OUTPUT_PATH, exist_ok=True)
json_path = os.path.join(OUTPUT_PATH, f"device_pattern_{FB_NAME}.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(pattern_data, f, indent=2, ensure_ascii=False)

print(f"âœ… JSON saved: {json_path}")
```

### STEP 7: Generate Markdown Report

```python
def generate_markdown_report(pattern_data):
    """Generate human-readable markdown report."""
    
    md = pattern_data["metadata"]
    gate = md["portability_gate"]
    patterns = pattern_data["patterns"]
    anti = pattern_data["anti_patterns"]
    
    report = f"""# Device Analysis: {md['fb_name']}

**Version:** {md['version']}  
**Family:** {md['device_family']}  
**Type:** {md['device_type']}  
**Analyzed:** {md['analyzed_at'][:10]}

---

## Portability Gate: {gate['status']}

"""
    if gate['status'] == "FAIL":
        report += "### âŒ CRITICAL Violations\n\n"
        for v in gate['violations']:
            report += f"- {v}\n"
        report += "\n**This FB cannot be reused across projects without modifications.**\n"
    else:
        report += "### âœ… Portable\n\nNo physical I/O, AT mapping, or hardcoded DBs detected.\n"
    
    report += f"""
---

## Pattern Recognition

**Command/Status:** {patterns['command_status']['pattern']} ({patterns['command_status']['confidence']})  
**State Machine:** {pattern_data['logic']['state_machine']['type']}  
**Edge Detection:** {patterns['native_functions']['edge_detection']}

---

## Anti-Patterns Detected

Total: {len(anti)}

"""
    for ap in anti:
        report += f"### {ap['id']} - {ap['type']} ({ap['severity']})\n"
        report += f"Line {ap['line']}: `{ap['code']}`\n\n"
    
    report += f"""---

## Next Steps

"""
    if gate['status'] == "FAIL":
        report += """1. Fix CRITICAL anti-patterns
2. Re-analyze to verify PASS
3. Use as template for code generation
"""
    else:
        report += """1. Review LOW/MEDIUM anti-patterns
2. Ready for code generation
"""
    
    report += f"\n---\n\nSee: `device_pattern_{md['fb_name']}.json` for full details\n"
    
    return report

# Generate MD
md_content = generate_markdown_report(pattern_data)
md_path = os.path.join(OUTPUT_PATH, f"DEVICE_{FB_NAME}.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"âœ… Markdown saved: {md_path}")
```

### STEP 8: Final Report

```python
print(f"""
========================================
DEVICE ANALYSIS v1.0.2 COMPLETE
========================================
FB Name:       {FB_NAME}
Family:        {DEVICE_FAMILY}
Type:          {DEVICE_TYPE}
Pattern:       {PATTERNS['command_status']['pattern']}
Confidence:    {PATTERNS['command_status']['confidence']}

Portability:   {PORTABILITY_STATUS}
Anti-Patterns: {len(ANTI_PATTERNS)} total
  CRITICAL:    {len(PORTABILITY_VIOLATIONS)}
  
Output:
  JSON: {json_path}
  MD:   {md_path}

{"âš ï¸  FIX CRITICAL violations before using as template" if PORTABILITY_STATUS == "FAIL" else "âœ… Ready for reuse across projects"}
========================================
""")
```

---

## Usage Examples

### Example 1: Analyze Single FB
```
User: Analyze /path/to/OnOffAxis.scl
Claude: [Executes STEP 1-8 with FB_PATH="/path/to/OnOffAxis.scl"]
```

### Example 2: With UDT Path
```
User: Analyze FB at /code/MyDevice.scl with UDTs in /code/UDT/
Claude: [Sets FB_PATH="/code/MyDevice.scl", UDT_PATH="/code/UDT/", executes workflow]
```

### Example 3: Quick Check Only
```
User: Check portability of /code/LegacyFB.scl
Claude: [Executes only STEP 1-3, reports PASS/FAIL with violations]
```

---

## Schema Validation

After generating JSON, validate against schema:

```bash
python scripts/validate_pattern.py device_pattern_X.json
```

---

## Notes

- **Portability Gate** is CRITICAL: FAIL blocks code generation
- **Anti-patterns** are the single source of truth for violations
- **Constraints** are derived from anti-patterns (not independent)
- This skill uses Python (not bash) for reliable cross-platform execution
