#!/usr/bin/env python3
"""
analyze_device.py v1.0.5 - Analyze PLC Function Block and extract patterns

CHANGELOG v1.0.5:
- CHANGED: Portability check now detects UNDECLARED SYMBOLS (not %I/%Q)
- NEW: Skip portability check for *_CALL and Generic_* blocks
- NEW: Whitelist for Sys.* framework symbols
- CHANGED: External dependency severity = WARNING (not CRITICAL)
- REMOVED: %I/%Q/%M check (unrealistic - TIA uses symbolic)
- REMOVED: "DB_xxx" check (unpredictable naming)

Usage:
    python analyze_device.py <fb_file.scl> [--udt-path <udt_folder>] [--output <output_folder>]
"""

import os
import re
import json
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set

# =============================================================================
# CONSTANTS
# =============================================================================

PRIMITIVE_TYPES = {
    'Bool', 'Byte', 'Word', 'DWord', 'LWord',
    'SInt', 'USInt', 'Int', 'UInt', 'DInt', 'UDInt', 'LInt', 'ULInt',
    'Real', 'LReal',
    'Char', 'WChar', 'String', 'WString',
    'Time', 'LTime', 'Date', 'TOD', 'LTOD', 'DT', 'LDT',
    'S5Time', 'DTL'
}

FB_INSTANCE_TYPES = {
    'IEC_TIMER', 'IEC_COUNTER', 'IEC_LTIMER', 'IEC_SCOUNTER', 'IEC_UCOUNTER',
    'TON', 'TOF', 'TP', 'TONR',
    'CTU', 'CTD', 'CTUD',
    'R_TRIG', 'F_TRIG'
}

# SCL keywords to ignore when extracting symbols
SCL_KEYWORDS = {
    # Control flow
    'IF', 'THEN', 'ELSE', 'ELSIF', 'END_IF',
    'CASE', 'OF', 'END_CASE',
    'FOR', 'TO', 'BY', 'DO', 'END_FOR',
    'WHILE', 'END_WHILE',
    'REPEAT', 'UNTIL', 'END_REPEAT',
    'RETURN', 'EXIT', 'CONTINUE', 'GOTO',
    # Operators
    'AND', 'OR', 'XOR', 'NOT', 'MOD', 'DIV',
    # Literals
    'TRUE', 'FALSE',
    # Region
    'REGION', 'END_REGION',
    # Block structure
    'BEGIN', 'END_FUNCTION_BLOCK', 'END_FUNCTION', 'END_PROGRAM',
    'VAR', 'VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 'VAR_TEMP', 'VAR_CONSTANT',
    'END_VAR', 'END_STRUCT', 'STRUCT', 'ARRAY',
    'FUNCTION_BLOCK', 'FUNCTION', 'PROGRAM', 'TYPE', 'END_TYPE',
    # Other
    'AT', 'RETAIN', 'CONSTANT', 'VERSION', 'TITLE', 'AUTHOR'
}

# Native SCL functions to ignore
SCL_NATIVE_FUNCTIONS = {
    # Math
    'ABS', 'MAX', 'MIN', 'LIMIT', 'SEL', 'MUX', 'SQRT',
    'SIN', 'COS', 'TAN', 'ASIN', 'ACOS', 'ATAN', 'ATAN2',
    'LN', 'LOG', 'EXP', 'EXPT', 'TRUNC', 'ROUND', 'FLOOR', 'CEIL',
    # Bit operations
    'SHL', 'SHR', 'ROL', 'ROR', 'SWAP',
    # Move/Copy
    'MOVE', 'MOVE_BLK', 'UMOVE_BLK', 'FILL_BLK', 'UFILL_BLK',
    'SCATTER', 'GATHER', 'SERIALIZE', 'DESERIALIZE',
    # String
    'CONCAT', 'LEN', 'LEFT', 'RIGHT', 'MID', 'INSERT', 'DELETE', 'REPLACE', 'FIND',
    # Comparison
    'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
    # Timer/Counter calls (as functions)
    'TON', 'TOF', 'TP', 'TONR', 'CTU', 'CTD', 'CTUD',
    'R_TRIG', 'F_TRIG',
    # Edge detection
    'PosEdge', 'NegEdge',
    # System
    'ENO', 'EN',
    # Conversion (pattern)
    'TO_BOOL', 'TO_BYTE', 'TO_WORD', 'TO_DWORD', 'TO_INT', 'TO_DINT', 'TO_REAL', 'TO_LREAL',
    'BOOL_TO_INT', 'INT_TO_BOOL', 'INT_TO_REAL', 'REAL_TO_INT', 'DINT_TO_REAL',
    'BYTE_TO_INT', 'INT_TO_BYTE', 'WORD_TO_INT', 'INT_TO_WORD',
    # MC functions
    'MC_Power', 'MC_Home', 'MC_MoveAbsolute', 'MC_MoveRelative', 'MC_MoveVelocity',
    'MC_Stop', 'MC_Halt', 'MC_Reset', 'MC_ReadActualPosition', 'MC_ReadActualVelocity'
}

# Whitelist prefixes for framework symbols
# Note: we extract ROOT symbols, so 'Sys.Clock' becomes just 'Sys'
FRAMEWORK_WHITELIST_PREFIXES = [
    'Sys',         # System framework DB (Sys.Clock_1S, etc.)
]

# =============================================================================
# VAR EXTRACTION
# =============================================================================

def extract_var_sections(content: str) -> Dict[str, str]:
    """
    Extract all VAR sections from SCL content.
    Returns dict: {'VAR_INPUT': '...content...', 'VAR_OUTPUT': '...', ...}
    """
    sections = {}
    
    var_section_pattern = r'\b(VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|VAR_TEMP|VAR\s+CONSTANT|VAR_STATIC|VAR)\b(.*?)END_VAR'
    
    matches = re.finditer(var_section_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        section_type = match.group(1).strip().upper()
        section_content = match.group(2).strip()
        
        if section_type == 'VAR CONSTANT':
            section_type = 'VAR_CONSTANT'
        
        if section_type in sections:
            sections[section_type] += '\n' + section_content
        else:
            sections[section_type] = section_content
    
    return sections


def parse_var_declaration(line: str) -> Optional[Dict]:
    """
    Parse a single VAR declaration line.
    Returns: {name, type, is_array, is_struct, default, comment, at_mapping}
    """
    line = line.strip()
    if not line or line.startswith('//'):
        return None
    
    comment = None
    if '//' in line:
        code_part, comment = line.split('//', 1)
        comment = comment.strip()
        line = code_part.strip()
    
    line = line.rstrip(';').strip()
    if not line:
        return None
    
    # Check for AT mapping
    at_mapping = None
    at_match = re.search(r'\bAT\s+(%[IMQ][WDB]?[0-9]+(?:\.[0-9]+)?)', line, re.I)
    if at_match:
        at_mapping = at_match.group(1)
        line = re.sub(r'\s*AT\s+%[IMQ][WDB]?[0-9]+(?:\.[0-9]+)?\s*', ' ', line, flags=re.I)
    
    # Check for RETAIN/CONSTANT attributes
    has_retain = bool(re.search(r'\{\s*RETAIN\s*\}', line, re.I))
    has_constant = 'VAR CONSTANT' in line.upper() or bool(re.search(r'\{\s*CONSTANT\s*\}', line, re.I))
    line = re.sub(r'\{[^}]*\}', '', line).strip()
    
    # Parse name : type := default
    match = re.match(r'(\w+)\s*:\s*(.+?)(?:\s*:=\s*(.+))?$', line)
    if not match:
        return None
    
    name = match.group(1)
    type_str = match.group(2).strip()
    default = match.group(3).strip() if match.group(3) else None
    
    # Detect array
    is_array = type_str.upper().startswith('ARRAY')
    array_bounds = None
    element_type = type_str
    if is_array:
        array_match = re.match(r'Array\s*\[([^\]]+)\]\s+of\s+(.+)', type_str, re.I)
        if array_match:
            array_bounds = array_match.group(1)
            element_type = array_match.group(2).strip()
    
    # Detect inline struct
    is_struct = element_type.upper() == 'STRUCT'
    
    return {
        'name': name,
        'type': element_type,
        'full_type': type_str,
        'is_array': is_array,
        'array_bounds': array_bounds,
        'is_struct': is_struct,
        'default': default,
        'comment': comment,
        'at_mapping': at_mapping,
        'retain': has_retain,
        'constant': has_constant
    }


def parse_var_section(section_content: str, section_type: str) -> List[Dict]:
    """
    Parse all declarations in a VAR section, handling inline Structs.
    """
    variables = []
    lines = section_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line or line.startswith('//'):
            i += 1
            continue
        
        parsed = parse_var_declaration(line)
        if parsed:
            if parsed['is_struct']:
                # Collect struct fields until END_STRUCT
                struct_fields = []
                i += 1
                while i < len(lines):
                    struct_line = lines[i].strip()
                    if struct_line.upper().startswith('END_STRUCT'):
                        break  # Don't increment here, let the outer loop do it
                    field = parse_var_declaration(struct_line)
                    if field:
                        struct_fields.append(field)
                    i += 1
                parsed['struct_fields'] = struct_fields
            
            parsed['section'] = section_type
            variables.append(parsed)
        i += 1
    
    return variables


def extract_all_variables(content: str) -> Dict[str, List[Dict]]:
    """
    Extract all variables from all VAR sections.
    Returns: {'VAR_INPUT': [...], 'VAR_OUTPUT': [...], ...}
    """
    sections = extract_var_sections(content)
    all_vars = {}
    
    for section_type, section_content in sections.items():
        variables = parse_var_section(section_content, section_type)
        all_vars[section_type] = variables
    
    return all_vars


# =============================================================================
# SYMBOL EXTRACTION (NEW in v1.0.5)
# =============================================================================

def extract_declared_symbols(all_vars: Dict[str, List[Dict]]) -> Set[str]:
    """
    Build set of all declared symbol names from VAR sections.
    Only includes root variable names (not struct fields).
    """
    declared = set()
    
    for section_type, variables in all_vars.items():
        for var in variables:
            declared.add(var['name'])
    
    return declared


def extract_body(content: str) -> str:
    """
    Extract the code body (BEGIN...END_FUNCTION_BLOCK).
    Remove comments and parser artifacts.
    """
    match = re.search(r'\bBEGIN\b(.+?)(?:END_FUNCTION_BLOCK|END_FUNCTION|END_PROGRAM)', 
                      content, re.DOTALL | re.IGNORECASE)
    if match:
        body = match.group(1)
        # Remove single-line comments
        body = re.sub(r'//.*$', '', body, flags=re.MULTILINE)
        # Remove block comments /* ... */
        body = re.sub(r'/\*.*?\*/', '', body, flags=re.DOTALL)
        # Remove [LAD code not found] and similar parser artifacts
        body = re.sub(r'\[.*?\]', '', body)
        return body
    return ""


# Timer/Counter field names (built-in, not user symbols)
TIMER_COUNTER_FIELDS = {
    'IN', 'PT', 'Q', 'ET', 'R', 'PV', 'CV', 'QU', 'QD', 'CLK'
}

def extract_used_symbols(body: str) -> Dict[str, List[int]]:
    """
    Extract all ROOT symbols used in code body with line numbers.
    Returns: {symbol: [line_numbers]}
    
    For dot-notation (symbol.field.subfield), only extracts 'symbol'.
    For #local_var, extracts 'local_var'.
    """
    used_symbols = {}
    lines = body.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Remove comments
        if '//' in line:
            line = line.split('//')[0]
        
        # Remove string literals (single and double quotes)
        line = re.sub(r"'[^']*'", '', line)
        line = re.sub(r'"[^"]*"', '', line)
        
        # Remove time/date literals: T#xxx, TIME#xxx, S5T#xxx, D#xxx, DT#xxx, TOD#xxx
        line = re.sub(r'\b(T|TIME|S5T|S5TIME|LT|LTIME|D|DATE|DT|DATE_AND_TIME|TOD|TIME_OF_DAY|LTOD|LDT)#[^\s;,\)]+', '', line, flags=re.I)
        
        # Find complete identifiers with optional dot-notation
        # Match: #?identifier(.field)* 
        # We only care about the ROOT identifier
        full_refs = re.findall(r'#?([A-Za-z_][A-Za-z0-9_]*)(?:\.[A-Za-z_][A-Za-z0-9_]*)*', line)
        
        for token in full_refs:
            # Skip if empty
            if not token:
                continue
            
            # Skip keywords
            if token.upper() in SCL_KEYWORDS:
                continue
            
            # Skip primitive types
            if token in PRIMITIVE_TYPES:
                continue
            
            # Skip FB instance types
            if token in FB_INSTANCE_TYPES:
                continue
            
            # Skip native functions
            if token in SCL_NATIVE_FUNCTIONS:
                continue
            
            # Skip timer/counter fields (in case they appear standalone)
            if token in TIMER_COUNTER_FIELDS:
                continue
            
            # Skip conversion functions (pattern-based)
            if re.match(r'^[A-Z]+_TO_[A-Z]+$', token):
                continue
            
            # Skip numeric literals that matched as identifiers
            if re.match(r'^[0-9]', token):
                continue
            
            # Record usage
            if token not in used_symbols:
                used_symbols[token] = []
            if line_num not in used_symbols[token]:
                used_symbols[token].append(line_num)
    
    return used_symbols


def is_whitelisted(symbol: str) -> bool:
    """Check if symbol is in framework whitelist."""
    for prefix in FRAMEWORK_WHITELIST_PREFIXES:
        if symbol.startswith(prefix):
            return True
    return False


def find_undeclared_symbols(declared: Set[str], used: Dict[str, List[int]]) -> List[Tuple[str, List[int]]]:
    """
    Find symbols used but not declared.
    Returns: [(symbol, [line_numbers]), ...]
    """
    undeclared = []
    
    for symbol, lines in used.items():
        # Check if declared
        if symbol in declared:
            continue
        
        # Check whitelist
        if is_whitelisted(symbol):
            continue
        
        undeclared.append((symbol, lines))
    
    return undeclared


# =============================================================================
# CONTRACT BUILDING
# =============================================================================

def classify_variable_for_contract(var: Dict) -> Tuple[str, Optional[Dict]]:
    """
    Classify a variable for contract placement.
    Returns: (category, contract_entry) where category is:
    - 'command_udt', 'config_udt', 'status_udt' for UDTs
    - 'logical_input', 'logical_output' for primitives
    - 'interface' for VAR_IN_OUT
    - 'skip' for FB instances, internal structs, etc.
    """
    name = var['name']
    var_type = var['type']
    section = var.get('section', '')
    
    # Skip FB instances (timers, triggers, etc.)
    if var_type in FB_INSTANCE_TYPES:
        return ('skip', None)
    
    # Skip internal Structs named Ctrl, Sts, Alarm, Warning, Diag (internal state)
    if var.get('is_struct') and name in ['Ctrl', 'Sts', 'Alarm', 'Warning', 'Diag']:
        return ('skip', None)
    
    # Check if it's a known UDT type by naming convention
    is_command_udt = bool(re.search(r'_Ctrl$|_Command$|Ctrl$', var_type))
    is_config_udt = bool(re.search(r'_Config$|_Par$|Config$', var_type))
    is_status_udt = bool(re.search(r'_Sts$|_Status$|Sts$', var_type))
    is_interface_udt = bool(re.search(r'_ITF$|Interface$', var_type))
    
    # VAR_INPUT handling
    if section == 'VAR_INPUT':
        if is_command_udt:
            return ('command_udt', {
                'name': name,
                'udt_type': var_type,
                'category': 'command_udt'
            })
        elif is_config_udt:
            return ('config_udt', {
                'name': name,
                'udt_type': var_type,
                'category': 'config_udt'
            })
        elif var_type in PRIMITIVE_TYPES or var.get('is_struct'):
            entry = {
                'name': name,
                'type': var_type if not var.get('is_struct') else 'Struct',
                'description': var.get('comment', '')
            }
            if var.get('is_struct') and var.get('struct_fields'):
                entry['fields'] = [
                    {'name': f['name'], 'type': f['type']}
                    for f in var['struct_fields']
                ]
            return ('logical_input', entry)
        else:
            # Unknown UDT in input - treat as logical input
            return ('logical_input', {
                'name': name,
                'type': var_type,
                'description': var.get('comment', '')
            })
    
    # VAR_OUTPUT handling
    elif section == 'VAR_OUTPUT':
        if is_status_udt:
            return ('status_udt', {
                'name': name,
                'udt_type': var_type,
                'category': 'status_udt'
            })
        elif var_type in PRIMITIVE_TYPES or var.get('is_struct'):
            entry = {
                'name': name,
                'type': var_type if not var.get('is_struct') else 'Struct',
                'description': var.get('comment', '')
            }
            if var.get('is_struct') and var.get('struct_fields'):
                entry['fields'] = [
                    {'name': f['name'], 'type': f['type']}
                    for f in var['struct_fields']
                ]
            return ('logical_output', entry)
        else:
            return ('logical_output', {
                'name': name,
                'type': var_type,
                'description': var.get('comment', '')
            })
    
    # VAR_IN_OUT handling
    elif section == 'VAR_IN_OUT':
        ownership = 'external'
        if is_interface_udt or is_command_udt or is_status_udt or is_config_udt:
            ownership = 'shared'
        
        return ('interface', {
            'name': name,
            'udt': var_type,
            'description': var.get('comment', ''),
            'retain': var.get('retain', False),
            'ownership': ownership
        })
    
    return ('skip', None)


def build_contract_from_variables(all_vars: Dict[str, List[Dict]]) -> Dict:
    """
    Build contract section from extracted variables.
    """
    contract = {
        'input': {
            'command_udt': [],
            'config_udt': [],
            'logical_inputs': []
        },
        'output': {
            'status_udt': [],
            'logical_outputs': []
        },
        'inout': {
            'interfaces': []
        }
    }
    
    for section_type, variables in all_vars.items():
        for var in variables:
            category, entry = classify_variable_for_contract(var)
            
            if category == 'skip' or entry is None:
                continue
            
            if category == 'command_udt':
                contract['input']['command_udt'].append(entry)
            elif category == 'config_udt':
                contract['input']['config_udt'].append(entry)
            elif category == 'logical_input':
                contract['input']['logical_inputs'].append(entry)
            elif category == 'status_udt':
                contract['output']['status_udt'].append(entry)
            elif category == 'logical_output':
                contract['output']['logical_outputs'].append(entry)
            elif category == 'interface':
                contract['inout']['interfaces'].append(entry)
    
    return contract


# =============================================================================
# METADATA EXTRACTION
# =============================================================================

def extract_metadata(content: str, fb_path: str) -> Tuple[str, str, str]:
    """Extract FB metadata from SCL content."""
    fb_name_match = re.search(r'FUNCTION_BLOCK\s+"([^"]+)"', content)
    fb_name = fb_name_match.group(1) if fb_name_match else os.path.basename(fb_path).replace('.scl', '')
    
    version_match = re.search(r'VERSION\s*:\s*([\d.]+)', content)
    version = version_match.group(1) if version_match else "1.0"
    
    author_match = re.search(r'AUTHOR\s*:\s*([^\n;]+)', content)
    author = author_match.group(1).strip() if author_match else "Unknown"
    
    return fb_name, version, author


def detect_device_taxonomy(content: str, fb_name: str) -> Tuple[str, str]:
    """Detect device_family and device_type from code patterns."""
    device_family = "generic"
    device_type = "actuator_generic"
    
    # Priority 0: AGGREGATOR (L3 - coordinates multiple L2 machines)
    # Detect by presence of multiple L2 FB instance types
    l2_fb_types = ['ValveMachine_FB', 'FeedMachine_FB', 'SpeedMachine_FB', 
                   'Positioning_DOL_Machine_FB', 'MotorMachine_FB', 'CylinderMachine_FB']
    l2_instance_count = sum(1 for fb in l2_fb_types if fb in content)
    if l2_instance_count >= 2:
        device_family = "aggregator"
        device_type = "multi_device"
        return device_family, device_type
    
    # Priority 1: MOTION (most specific patterns)
    if re.search(r'MC_MoveAbsolute|MC_Home|MC_MoveRelative|MC_Power', content):
        device_family = "motion"
        if re.search(r'Rot|Turn|Rotation', fb_name, re.I):
            device_type = "rotary_servo"
        else:
            device_type = "linear_servo"
        return device_family, device_type
    
    if re.search(r'TAx_DriveInterface', content):
        device_family = "motion"
        device_type = "servo_drive"
        return device_family, device_type
    
    if re.search(r'PosFbk_ITF', content) and not re.search(r'MC_', content):
        device_family = "motion"
        device_type = "linear_onoff"
        return device_family, device_type
    
    # Priority 2: DRIVE
    if re.search(r'SinaInfeed|Infeed_ON|EnableInfeed', content):
        device_family = "drive"
        device_type = "infeed"
        return device_family, device_type
    
    if re.search(r'SinaSpeed|SinaMC', content):
        device_family = "drive"
        device_type = "drive_control"
        return device_family, device_type
    
    # Priority 3: ACTUATOR (specific patterns)
    if re.search(r'\bMotorCtrl\b|\bMotorSts\b', content):
        device_family = "actuator"
        device_type = "motor_contactor"
        return device_family, device_type
    
    if re.search(r'VFD|FrequencyConverter', content):
        device_family = "actuator"
        device_type = "motor_vfd"
        return device_family, device_type
    
    # Priority 4: PNEUMATIC
    if re.search(r'Extend.*Retract|Retract.*Extend', content, re.I | re.S):
        device_family = "pneumatic"
        device_type = "cylinder_double"
        return device_family, device_type
    
    if re.search(r'Open.*Close.*Grip|Grip.*Open.*Close', content, re.I | re.S):
        device_family = "pneumatic"
        device_type = "gripper"
        return device_family, device_type
    
    if re.search(r'\bOpen\b.*\bClose\b|\bClose\b.*\bOpen\b', content, re.I | re.S):
        device_family = "pneumatic"
        device_type = "valve"
        return device_family, device_type
    
    # Priority 5: SENSOR
    if re.search(r'PosFbk_|Encoder|TExtEncoder', content):
        device_family = "sensor"
        device_type = "encoder"
        return device_family, device_type
    
    # Priority 6: ORCHESTRATOR (only if no device patterns matched)
    if re.search(r'\bAreaInterface\b|\bAreaConfig\b', content):
        device_family = "orchestrator"
        device_type = "area_manager"
        return device_family, device_type
    
    if re.search(r'ZoneInterface|ZoneSafetyInterface', content):
        device_family = "orchestrator"
        device_type = "zone_manager"
        return device_family, device_type
    
    if re.search(r'\bMachineInterface\b|\bMachineStatus\b', content):
        device_family = "orchestrator"
        device_type = "machine_coordinator"
        return device_family, device_type
    
    return device_family, device_type


# =============================================================================
# PORTABILITY ANALYSIS (REDESIGNED in v1.0.5)
# =============================================================================

def should_skip_portability_check(fb_name: str) -> bool:
    """
    Check if this FB should skip portability analysis.
    Skip: *_CALL (FC wrappers), Generic_* (HW-specific)
    """
    if fb_name.endswith('_CALL'):
        return True
    if fb_name.startswith('Generic'):
        return True
    return False


def analyze_portability(content: str, fb_path: str, all_vars: Dict[str, List[Dict]]) -> Tuple[str, List[str], List[Dict]]:
    """
    Analyze portability by detecting undeclared symbols.
    
    Returns: (status, violation_ids, anti_patterns)
    """
    anti_patterns = []
    violations = []
    ap_counter = 1
    
    fb_name = os.path.basename(fb_path).replace('.scl', '')
    fb_filename = os.path.basename(fb_path)
    
    # Check if should skip
    if should_skip_portability_check(fb_name):
        return "SKIP", [], [{
            "id": "INFO001",
            "type": "portability_skipped",
            "severity": "INFO",
            "file": fb_filename,
            "line": 0,
            "code": f"Portability check skipped for {fb_name}",
            "rule": "skip_call_and_generic",
            "impact": "None - this block type is exempt",
            "suggested_fix": "N/A"
        }]
    
    # Extract declared and used symbols
    declared = extract_declared_symbols(all_vars)
    body = extract_body(content)
    used = extract_used_symbols(body)
    
    # Find undeclared symbols
    undeclared = find_undeclared_symbols(declared, used)
    
    # Create anti-patterns for undeclared symbols
    for symbol, line_numbers in undeclared:
        ap_id = f"AP{ap_counter:03d}"
        anti_patterns.append({
            "id": ap_id,
            "type": "external_dependency",
            "severity": "WARNING",
            "file": fb_filename,
            "line": line_numbers[0] if line_numbers else 0,
            "code": f"Symbol '{symbol}' used but not declared",
            "rule": "portability_no_external_symbols",
            "impact": "FB depends on external symbol - may not be portable",
            "suggested_fix": f"Add '{symbol}' to VAR_INPUT or VAR_IN_OUT",
            "all_lines": line_numbers
        })
        violations.append(ap_id)
        ap_counter += 1
    
    # Additional checks: Manual edge detection (MEDIUM)
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        if re.match(r'^\s*//', line):
            continue
        if re.search(r'\bAND\s+NOT\s+\w+_(old|prev|last)\b', line, re.I):
            ap_id = f"AP{ap_counter:03d}"
            anti_patterns.append({
                "id": ap_id,
                "type": "manual_edge_detection",
                "severity": "MEDIUM",
                "file": fb_filename,
                "line": line_num,
                "code": line.strip()[:80],
                "rule": "use_native_triggers",
                "impact": "Code verbosity, non-standard",
                "suggested_fix": "Use R_TRIG or F_TRIG"
            })
            ap_counter += 1
    
    # Determine status
    # WARNING-level issues don't cause FAIL, only INFO that there are dependencies
    has_critical = any(ap['severity'] == 'CRITICAL' for ap in anti_patterns)
    
    if has_critical:
        status = "FAIL"
    elif violations:
        status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"
    
    return status, violations, anti_patterns


# =============================================================================
# PATTERN DETECTION
# =============================================================================

def detect_patterns(content: str) -> Dict:
    """Detect command/status patterns, state machine, timers, edge detection."""
    
    pattern_cmd = "unknown"
    confidence = "LOW"
    evidence = ""
    
    if re.search(r'\.Permitted\s*:=.*NOT', content) and re.search(r'\.Request\s*:=.*\.Permitted', content):
        pattern_cmd = "PermittedÃ¢â€ â€™RequestÃ¢â€ â€™CmdÃ¢â€ â€™Done"
        confidence = "HIGH"
        match = re.search(r'(\w+\.Permitted\s*:=[^;]+;)', content)
        if match:
            evidence = match.group(1)[:80]
    elif re.search(r'SafeStop.*RunPermitted|RunPermitted.*SafeStop', content, re.S):
        pattern_cmd = "SafeStopÃ¢â€ â€™RunPermittedÃ¢â€ â€™Run"
        confidence = "MEDIUM"
        match = re.search(r'(RunPermitted\s*:=[^;]+;)', content)
        if match:
            evidence = match.group(1)[:80]
    elif re.search(r'Request.*Command|Command.*Request', content):
        pattern_cmd = "RequestÃ¢â€ â€™Cmd"
        confidence = "MEDIUM"
    
    # State machine
    state_type = "implicit"
    if re.search(r'CASE\s+\w+\s+OF', content):
        state_type = "explicit_case"
    elif re.search(r'\w+\.Request.*\.Permitted', content):
        state_type = "struct_pattern"
    
    # States from REGION
    states = re.findall(r'REGION\s+"([^"]+)"', content)
    if not states:
        states = re.findall(r'REGION\s+([A-Za-z][A-Za-z0-9_]*)', content)
        states = [s for s in states if s not in ['END_REGION', 'REGION']]
    if not states:
        states = ["Main"]
    seen = set()
    states = [s for s in states if not (s in seen or seen.add(s))]
    
    # Timers
    timers = list(set(re.findall(r'(\w+)\s*:\s*(?:IEC_TIMER|TON|TOF|TP)\b', content)))
    
    # Edge detection
    edge = "none"
    if re.search(r'\bR_TRIG\b|\bF_TRIG\b', content):
        edge = "R_TRIG/F_TRIG"
    elif re.search(r'\bPosEdge\s*\(|\bNegEdge\s*\(', content):
        edge = "FC_PosEdge/NegEdge"
    elif re.search(r'\bAND\s+NOT\s+\w+_(old|prev|aux)', content, re.I):
        edge = "manual"
    
    # Math functions
    math_funcs = []
    for func in ['ABS', 'MAX', 'MIN', 'LIMIT', 'SEL', 'SQRT', 'SIN', 'COS', 'ROUND', 'TRUNC']:
        if re.search(rf'\b{func}\s*\(', content):
            math_funcs.append(func)
    
    # Motion control functions
    motion_funcs = []
    for func in ['MC_MoveAbsolute', 'MC_MoveRelative', 'MC_Home', 'MC_Power', 'MC_Stop', 'MC_Halt']:
        if func in content:
            motion_funcs.append(func)
    
    # FB calls
    fb_calls = list(set(re.findall(r'#(\w+)\s*\(', content)))
    
    return {
        "command_status": {"pattern": pattern_cmd, "confidence": confidence, "evidence": evidence},
        "state_machine": {"type": state_type, "states": states},
        "timers": timers,
        "edge_detection": edge,
        "math": math_funcs,
        "motion_control": motion_funcs,
        "fb_called": fb_calls
    }


# =============================================================================
# UDT CLASSIFICATION (from files)
# =============================================================================

def classify_udts(udt_path: Optional[str]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Classify UDTs by naming convention from file names."""
    command_udts = []
    config_udts = []
    status_udts = []
    
    if not udt_path or not os.path.exists(udt_path):
        return command_udts, config_udts, status_udts
    
    for filename in os.listdir(udt_path):
        if not filename.endswith('.xml') and not filename.endswith('.udt'):
            continue
        udt_name = re.sub(r'\.(xml|udt)$', '', filename)
        
        if re.search(r'_Ctrl$|_Command$', udt_name):
            command_udts.append({"name": udt_name, "category": "command_udt", "source_file": filename, "fields": []})
        elif re.search(r'_Config$|_Par', udt_name):
            config_udts.append({"name": udt_name, "category": "config_udt", "fields": []})
        elif re.search(r'_Sts$|_Status$', udt_name):
            status_udts.append({"name": udt_name, "category": "status_udt", "fields": []})
    
    return command_udts, config_udts, status_udts


# =============================================================================
# JSON GENERATION
# =============================================================================

def generate_pattern_json(fb_path: str, fb_name: str, version: str, author: str,
                          device_family: str, device_type: str,
                          portability_status: str, portability_violations: List[str],
                          anti_patterns: List[Dict], patterns: Dict,
                          contract: Dict, udt_path: Optional[str]) -> Dict:
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
                "fb_scl": fb_path,
                "udt_path": udt_path or ""
            },
            "portability_gate": {
                "status": portability_status,
                "violations": portability_violations,
                "notes": "" if portability_status == "PASS" else 
                         "Skipped for CALL/Generic blocks" if portability_status == "SKIP" else
                         "External dependencies detected" if portability_status == "PASS_WITH_WARNINGS" else
                         "Fix CRITICAL violations before reuse"
            }
        },
        "contract": contract,
        "logic": {
            "state_machine": {
                "type": patterns["state_machine"]["type"],
                "states": patterns["state_machine"]["states"],
                "mutual_exclusion": ""
            },
            "key_algorithms": []
        },
        "patterns": {
            "command_status": patterns["command_status"],
            "alarm_handling": {"pattern": "unknown", "confidence": "LOW"},
            "native_functions": {
                "timers": patterns["timers"],
                "edge_detection": patterns["edge_detection"],
                "motion_control": patterns["motion_control"],
                "math": patterns["math"]
            }
        },
        "anti_patterns": anti_patterns,
        "dependencies": {
            "fb_called": patterns["fb_called"],
            "custom_udts": [],
            "external_devices": []
        },
        "constraints": {
            "portability_compliant": portability_status in ["PASS", "SKIP"],
            "multi_instance_safe": portability_status in ["PASS", "SKIP"],
            "notes": ""
        },
        "configuration": {
            "example_config": {},
            "validation_rules": []
        }
    }


# =============================================================================
# MARKDOWN REPORT
# =============================================================================

def generate_markdown_report(pattern_data: Dict) -> str:
    """Generate human-readable markdown report."""
    md = pattern_data["metadata"]
    gate = md["portability_gate"]
    patterns = pattern_data["patterns"]
    anti = pattern_data["anti_patterns"]
    
    status_emoji = {
        "PASS": "Ã¢Å“â€¦",
        "PASS_WITH_WARNINGS": "Ã¢Å¡Â Ã¯Â¸Â",
        "FAIL": "Ã¢ÂÅ’",
        "SKIP": "Ã¢ÂÂ­Ã¯Â¸Â"
    }
    
    report = f"""# Device Analysis: {md['fb_name']}

**Version:** {md['version']}  
**Author:** {md['author']}  
**Family:** {md['device_family']}  
**Type:** {md['device_type']}  
**Analyzed:** {md['analyzed_at'][:10]}

---

## Portability Gate: {status_emoji.get(gate['status'], '?')} {gate['status']}

"""
    if gate['status'] == "FAIL":
        report += "### Ã¢ÂÅ’ CRITICAL Violations\n\n"
        for v in gate['violations']:
            report += f"- {v}\n"
        report += "\n**This FB cannot be reused across projects without modifications.**\n"
    elif gate['status'] == "PASS_WITH_WARNINGS":
        report += "### Ã¢Å¡Â Ã¯Â¸Â External Dependencies Detected\n\n"
        report += f"Found {len(gate['violations'])} undeclared symbol(s).\n"
        report += "These may be intentional (framework symbols) or need to be declared.\n"
    elif gate['status'] == "SKIP":
        report += "### Ã¢ÂÂ­Ã¯Â¸Â Skipped\n\n"
        report += "Portability check skipped for CALL/Generic blocks.\n"
    else:
        report += "### Ã¢Å“â€¦ Portable\n\nNo external dependencies detected.\n"
    
    report += f"""
---

## Pattern Recognition

**Command/Status:** {patterns['command_status']['pattern']} ({patterns['command_status']['confidence']})  
**State Machine:** {pattern_data['logic']['state_machine']['type']}  
**States:** {', '.join(pattern_data['logic']['state_machine']['states'])}  
**Edge Detection:** {patterns['native_functions']['edge_detection']}  
**Timers:** {', '.join(patterns['native_functions']['timers']) or 'none'}

---

## Contract Summary

**Inputs:** {len(pattern_data['contract']['input']['logical_inputs'])} logical, """
    report += f"{len(pattern_data['contract']['input']['command_udt'])} cmd_udt, "
    report += f"{len(pattern_data['contract']['input']['config_udt'])} cfg_udt\n"
    report += f"**Outputs:** {len(pattern_data['contract']['output']['logical_outputs'])} logical, "
    report += f"{len(pattern_data['contract']['output']['status_udt'])} sts_udt\n"
    report += f"**InOut:** {len(pattern_data['contract']['inout']['interfaces'])} interfaces\n"
    
    report += f"""
---

## Anti-Patterns Detected

Total: {len(anti)}

"""
    # Group by severity
    for severity in ['CRITICAL', 'WARNING', 'MEDIUM', 'LOW', 'INFO']:
        sev_aps = [ap for ap in anti if ap['severity'] == severity]
        if sev_aps:
            report += f"### {severity}\n\n"
            for ap in sev_aps:
                report += f"**{ap['id']}** - {ap['type']}  \n"
                report += f"Line {ap['line']}: `{ap['code'][:60]}`  \n"
                report += f"Fix: {ap['suggested_fix']}\n\n"
    
    report += f"""---

## Dependencies

**FB Called:** {', '.join(pattern_data['dependencies']['fb_called']) or 'none'}  
**Motion Control:** {', '.join(patterns['native_functions']['motion_control']) or 'none'}  
**Math Functions:** {', '.join(patterns['native_functions']['math']) or 'none'}

---

## Next Steps

"""
    if gate['status'] == "FAIL":
        report += """1. Fix CRITICAL anti-patterns listed above
2. Re-run analysis to verify PASS
3. Use as template for code generation
"""
    elif gate['status'] == "PASS_WITH_WARNINGS":
        report += """1. Review external dependencies - add to whitelist or declare
2. Ã¢Å¡Â Ã¯Â¸Â Conditional use for code generation
"""
    else:
        report += """1. Review LOW/MEDIUM anti-patterns (optional)
2. Ã¢Å“â€¦ Ready for code generation
3. Add to reusable device library
"""
    
    report += f"\n---\n\nSee: `device_pattern_{md['fb_name']}.json` for full data.\n"
    
    return report


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def analyze_device(fb_path: str, udt_path: Optional[str] = None, 
                   output_path: Optional[str] = None) -> Dict:
    """Main analysis function."""
    
    if output_path is None:
        output_path = os.path.dirname(fb_path) or '.'
    
    # Read FB
    with open(fb_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Extract metadata
    fb_name, version, author = extract_metadata(content, fb_path)
    print(f"Analyzing: {fb_name} v{version} by {author}")
    
    # Device taxonomy
    device_family, device_type = detect_device_taxonomy(content, fb_name)
    print(f"Device: {device_family}/{device_type}")
    
    # Extract variables
    all_vars = extract_all_variables(content)
    var_counts = {k: len(v) for k, v in all_vars.items()}
    print(f"Variables: {var_counts}")
    
    # Build contract
    contract = build_contract_from_variables(all_vars)
    
    # Portability analysis (NEW in v1.0.5)
    portability_status, portability_violations, anti_patterns = analyze_portability(
        content, fb_path, all_vars
    )
    print(f"Portability: {portability_status} ({len(portability_violations)} issues)")
    
    # Pattern detection
    patterns = detect_patterns(content)
    print(f"Pattern: {patterns['command_status']['pattern']} ({patterns['command_status']['confidence']})")
    
    # Generate JSON
    pattern_data = generate_pattern_json(
        fb_path, fb_name, version, author, device_family, device_type,
        portability_status, portability_violations, anti_patterns,
        patterns, contract, udt_path
    )
    
    os.makedirs(output_path, exist_ok=True)
    json_path = os.path.join(output_path, f"device_pattern_{fb_name}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(pattern_data, f, indent=2, ensure_ascii=False)
    print(f"Ã¢Å“â€¦ JSON: {json_path}")
    
    # Generate Markdown
    md_content = generate_markdown_report(pattern_data)
    md_path = os.path.join(output_path, f"DEVICE_{fb_name}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Ã¢Å“â€¦ MD: {md_path}")
    
    # Summary
    warning_count = len([a for a in anti_patterns if a['severity'] == 'WARNING'])
    medium_count = len([a for a in anti_patterns if a['severity'] == 'MEDIUM'])
    low_count = len([a for a in anti_patterns if a['severity'] == 'LOW'])
    
    print(f"""
========================================
ANALYSIS COMPLETE: {fb_name}
========================================
Family:        {device_family}
Type:          {device_type}
Pattern:       {patterns['command_status']['pattern']}
Confidence:    {patterns['command_status']['confidence']}

Portability:   {portability_status}
Anti-Patterns: {len(anti_patterns)} total
  WARNING:     {warning_count}
  MEDIUM:      {medium_count}
  LOW:         {low_count}

Contract:
  Inputs:      {len(contract['input']['logical_inputs'])} logical
  Outputs:     {len(contract['output']['logical_outputs'])} logical
  Interfaces:  {len(contract['inout']['interfaces'])}

{"Ã¢Å¡Â Ã¯Â¸Â  Review external dependencies" if portability_status == "PASS_WITH_WARNINGS" else ""}
{"Ã¢Å“â€¦ Ready for reuse" if portability_status == "PASS" else ""}
{"Ã¢ÂÂ­Ã¯Â¸Â  Portability check skipped" if portability_status == "SKIP" else ""}
========================================
""")
    
    return pattern_data


def main():
    parser = argparse.ArgumentParser(description='Analyze PLC Function Block and extract patterns (v1.0.5)')
    parser.add_argument('fb_file', help='Path to SCL Function Block file')
    parser.add_argument('--udt-path', '-u', help='Path to UDT folder (optional)')
    parser.add_argument('--output', '-o', help='Output directory (default: same as FB)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.fb_file):
        print(f"Ã¢ÂÅ’ File not found: {args.fb_file}")
        return 1
    
    analyze_device(args.fb_file, args.udt_path, args.output)
    return 0


if __name__ == '__main__':
    exit(main())
