# Pattern Recognition Rules v1.0.1

**Changes:** Portability-focused anti-pattern detection

---

## Device Taxonomy (2-level)

### device_family (high-level)
```
motion       â†’ Any motion control (servo, onoff, rotary, linear)
pneumatic    â†’ Pneumatic actuators (cylinders, valves, grippers)
hydraulic    â†’ Hydraulic systems
sensor       â†’ Smart sensors with processing
actuator     â†’ Generic actuators
generic      â†’ Fallback
```

### device_type (specific)
```
Motion family:
  linear_servo  â†’ MC_MoveAbsolute + linear motion
  rotary_servo  â†’ MC_MoveAbsolute + rotation
  linear_onoff  â†’ PosFbk_ITF + no servo (OnOffAxis pattern)
  servo_drive   â†’ TAx_DriveInterface integration

Pneumatic family:
  cylinder_double â†’ Extend + Retract
  cylinder_single â†’ Extend only
  valve           â†’ Open + Close
  gripper         â†’ Open + Close + Grip

Sensor family:
  distance_sensor â†’ Analog distance measurement
  vision_sensor   â†’ Image processing
  
Actuator family:
  actuator_generic â†’ Fallback
```

---

## Anti-Pattern Detection (Single Source of Truth)

### Portability Gate (CRITICAL severity)

**Rule PG-01: No Physical I/O**
```regex
%[IMQ][WDB]?[0-9]+(\.[0-9]+)?
```

Examples:
```scl
%I0.0       // âŒ CRITICAL - Digital input
%QW100      // âŒ CRITICAL - Analog output word
%MW50       // âŒ CRITICAL - Memory word
```

**Exceptions:**
- Inside comments: `// Example: %I0.0`
- Inside string literals: `'Address is %I0.0'`

**Impact:** Breaks portability - address is project-specific

**Fix:** Pass via VAR_INPUT parameter
```scl
// Instead of
IF %I0.0 THEN ...

// Use
VAR_INPUT
  LimitSwitch : Bool;
END_VAR
IF LimitSwitch THEN ...
```

---

**Rule PG-02: No AT Mapping**
```regex
\bAT\s+%[IMQ]
```

Examples:
```scl
VAR
  Output AT %Q0.0 : Bool;  // âŒ CRITICAL
END_VAR
```

**Impact:** AT mapping is project-specific

**Fix:** Remove AT, use symbolic I/O in hardware config

---

**Rule PG-03: No Hardcoded Global DB**
```regex
"DB_[A-Za-z0-9_]+"\.\w+
```

Examples:
```scl
"DB_GlobalArea".Cycle := TRUE;     // âŒ CRITICAL
value := "DB_Parameters".MaxSpeed; // âŒ CRITICAL
```

**Exceptions:**
- Inside comments
- String literals (e.g., logging messages)
- Instance DB access via # is OK: `#instance.field`

**Impact:** Global DB is project-specific

**Fix:** Pass via VAR_IN_OUT or UDT parameter
```scl
// Instead of
"DB_Area".Cycle := TRUE;

// Use
VAR_IN_OUT
  AreaInterface : AreaInterface;
END_VAR
AreaInterface.Cycle := TRUE;
```

---

### Code Quality (MEDIUM/LOW severity)

**Rule CQ-01: Manual Edge Detection (MEDIUM)**
```regex
\bAND\s+NOT\s+\w+_(old|prev|last)\b
```

Examples:
```scl
edge := signal AND NOT signal_old;  // âš ï¸ MEDIUM
signal_old := signal;
```

**Impact:** Code verbosity, non-standard

**Fix:** Use native R_TRIG/F_TRIG
```scl
VAR
  rtrig : R_TRIG;
END_VAR
rtrig(CLK := signal, Q => edge);
```

---

**Rule CQ-02: Magic Numbers (LOW)**
```regex
[^a-zA-Z_][0-9]+\.[0-9]+
```

Examples:
```scl
IF Position > 123.45 THEN  // âš ï¸ LOW - Magic number
```

**Exceptions:**
- VAR_CONSTANT declarations
- Config UDT assignments: `Config.MaxSpeed := 100.0`

**Impact:** Hard to maintain, not configurable

**Fix:** Use Config UDT or VAR_CONSTANT
```scl
// Instead of
IF Position > 123.45 THEN

// Use
VAR_INPUT
  Config : DeviceConfig;
END_VAR
IF Position > Config.MaxPosition THEN
```

---

## Portability Gate Logic

```bash
PORTABILITY_STATUS = "PASS"  # Default

# Collect CRITICAL anti-patterns
CRITICAL_APs = []

FOR each anti_pattern in anti_patterns:
  IF anti_pattern.severity == "CRITICAL":
    CRITICAL_APs.append(anti_pattern.id)
    
IF len(CRITICAL_APs) > 0:
  PORTABILITY_STATUS = "FAIL"
  PORTABILITY_VIOLATIONS = CRITICAL_APs
ELSE:
  PORTABILITY_STATUS = "PASS"
  PORTABILITY_VIOLATIONS = []
```

---

## Constraints (Derived from Anti-Patterns)

**NOT independent source - computed from anti_patterns array:**

```python
# portability_compliant
portability_compliant = (portability_gate.status == "PASS")

# multi_instance_safe
has_io_physical = any(ap.type == "io_physical" for ap in anti_patterns)
has_hardcoded_db = any(ap.type == "hardcoded_db" for ap in anti_patterns)
multi_instance_safe = not (has_io_physical or has_hardcoded_db)
```

---

## UDT Classification (unchanged)

```
*_Ctrl | *_Command     â†’ command_udt
*_Sts | *_Status       â†’ status_udt
*_Alr | *_Alarm        â†’ alarm_udt
*_Config | *_Par       â†’ config_udt
*_ITF | *_Interface    â†’ interface (InOut)
```

---

## Pattern Confidence (unchanged)

```
HIGH   (90-100%) : Permittedâ†’Requestâ†’Cmdâ†’Done pattern
MEDIUM (60-89%)  : Requestâ†’Cmd pattern
LOW    (30-59%)  : Direct Cmd assignment
```

---

## Version History

**v1.0.1** (2024-12-26)
- Added portability gate (PG-01, PG-02, PG-03)
- Separated device_family + device_type
- Anti-patterns as single source of truth
- Constraints derived (not independent)

**v1.0.0** (2024-12-26)
- Initial release
