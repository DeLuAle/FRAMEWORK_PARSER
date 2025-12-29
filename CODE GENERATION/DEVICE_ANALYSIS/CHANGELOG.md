# Changelog - Device Analysis Skill

All notable changes to this skill.

---

## [1.0.2] - 2024-12-26

### Added - Portability Focus

**Schema Changes:**
- âœ… `schema_version` field (mandatory "1.0.2")
- âœ… `metadata.device_family` (high-level taxonomy)
- âœ… `metadata.portability_gate` (PASS/FAIL status)
- âœ… `anti_patterns` array with unique IDs (AP001, AP002...)
- âœ… `anti_pattern.severity` (CRITICAL/HIGH/MEDIUM/LOW)
- âœ… `constraints.portability_compliant` (derived from gate)

**Removed (Breaking):**
- âŒ `contract.input.hw_inputs` (conflicts with portability)
- âŒ `contract.output.actor_outputs` (conflicts with portability)
- âŒ `contract.input.other_inputs`
- âŒ `contract.output.other_outputs`

**Replaced:**
- `contract.input.logical_inputs` â†’ Pure Bool/Int/Real, NO hardware
- `contract.output.logical_outputs` â†’ Pure Bool/Int/Real, NO hardware

**Portability Gate Rules:**
- PG-01: No physical I/O (`%I`, `%Q`, `%M`)
- PG-02: No AT mapping
- PG-03: No hardcoded global DB (`"DB_xxx"`)

**Anti-Pattern Detection:**
- CRITICAL severity â†’ portability_gate = FAIL
- Unique IDs (AP001, AP002...) for traceability
- Evidence: file, line, code snippet, suggested fix

**Device Taxonomy:**
- 2-level: `device_family` + `device_type`
- Families: motion, pneumatic, hydraulic, sensor, actuator, generic
- Types: linear_servo, linear_onoff, cylinder_double, valve, etc.

**Constraints as Derived Values:**
- No longer independent source
- Computed from anti_patterns array
- `portability_compliant` = (gate.status == "PASS")
- `multi_instance_safe` = no io_physical OR hardcoded_db

---

### Changed

**SKILL.md Workflow:**
- STEP 3: Portability gate analysis (grep-based, comment-aware)
- STEP 6: JSON generation with schema_version
- STEP 7: Markdown report with gate status
- STEP 8: Final report shows CRITICAL count

**PATTERN_RULES.md:**
- Portability gate section (PG-01, PG-02, PG-03)
- Device taxonomy 2-level explanation
- Constraints derivation logic
- Version history added

---

### Migration Guide (v1.0.0 â†’ v1.0.1)

**Breaking Changes:**

1. **Remove hw_inputs/actor_outputs:**
```json
// v1.0.0 (DEPRECATED)
"contract": {
  "input": {
    "hw_inputs": [...]  // âŒ Remove
  },
  "output": {
    "actor_outputs": [...] // âŒ Remove
  }
}

// v1.0.1
"contract": {
  "input": {
    "logical_inputs": [...]  // âœ… Use this
  }
}
```

2. **Add schema_version:**
```json
{
  "schema_version": "1.0.2",  // âœ… Mandatory
  "metadata": {...}
}
```

3. **Add portability_gate:**
```json
"metadata": {
  "portability_gate": {
    "status": "PASS|FAIL",
    "violations": ["AP001", "AP002"]
  }
}
```

4. **Update anti_patterns format:**
```json
// v1.0.0
"anti_patterns_detected": [
  {"type": "hardcoded_db", "line": 42}
]

// v1.0.1
"anti_patterns": [
  {
    "id": "AP001",
    "type": "hardcoded_db",
    "severity": "CRITICAL",
    "line": 42,
    "rule": "portability_no_global_db"
  }
]
```

---

## [1.0.0] - 2024-12-26

### Initial Release

**Core Functionality:**
- Device pattern extraction from SCL
- JSON output with schema validation
- Device type inference (7 types)
- UDT classification
- State machine detection
- Anti-pattern detection (basic)
- Confidence scoring

**Supported:**
- motion_linear/rotary
- cylinder/valve/gripper
- sensor/actuator_generic

**Patterns:**
- Command/Status (HIGH/MEDIUM/LOW confidence)
- Alarm handling
- Native functions (TON, R_TRIG)

**Anti-Patterns (v1.0.0):**
- Hardcoded DB (basic detection)
- Manual edge detection
- Magic numbers

**Output:**
- device_pattern_X.json
- DEVICE_X.md

---

## [Planned 1.1.0] - AST-Based Analysis

**Requires:** SCL parser with AST output

**Will Add:**
- Typization with symbol table
- Evidence with AST nodes (line + column)
- State machine with control flow graph
- Confidence with numeric score + features
- Cross-device pattern comparison

**See:** Revisione_FB_SCL_Riusabili_v1_1.md

---

## Version Comparison

| Feature | v1.0.0 | v1.0.1 | v1.1.0 (planned) |
|---------|--------|--------|------------------|
| Schema version | âŒ | âœ… | âœ… |
| Portability gate | âŒ | âœ… | âœ… |
| hw_inputs/actor_outputs | âœ… | âŒ | âŒ |
| Anti-pattern IDs | âŒ | âœ… | âœ… |
| Device taxonomy 2-level | âŒ | âœ… | âœ… |
| AST-based analysis | âŒ | âŒ | âœ… |
| Symbol table | âŒ | âŒ | âœ… |
| Control flow graph | âŒ | âŒ | âœ… |

---

**Current Version:** 1.0.2 (Portability-Focused)  
**Last Updated:** 2024-12-26  
**Maintained by:** Alessandro (PM Forming)

## [1.0.2] - 2025-12-26
- Fixed schema/example mismatch: `contract.output.logical_outputs` is primitive-only; removed inline `Struct` from example and flattened to primitive logical outputs.
- Added `ownership` and `storage_hint` to `contract.inout.interfaces` (replaces ad-hoc `shared` field in example).
- Simplified anti-pattern taxonomy: removed `absolute_io` (use `io_physical` and `io_at_mapping`).
