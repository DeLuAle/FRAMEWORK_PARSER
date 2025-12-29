# DEVICE_ANALYSIS Module

**Pattern Extraction for PLC Function Blocks - v1.0.6**

---

## 🎯 Purpose

Analyze SCL Function Blocks to extract:
1. Device patterns (command/status, state machine, alarms)
2. UDT contracts (input/output/inout)
3. Anti-patterns (portability violations)
4. Configuration templates

---

## 🚀 Quick Start

### 1. Analyze a Function Block

```bash
cd scripts

# Basic analysis
python analyze_device.py /path/to/Motor.scl --output ./output

# With UDT folder
python analyze_device.py /path/to/Motor.scl --udt-path /path/to/UDT --output ./output
```

### 2. Validate Output

```bash
python validate_pattern.py ./output/device_pattern_Motor.json
```

### 3. Check Results

```
output/
├── device_pattern_Motor.json   # Machine-readable pattern
└── DEVICE_Motor.md             # Human-readable report
```

---

## 📊 Portability Gate

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ **PASS** | No external dependencies | Ready for reusable library |
| ⚠️ **PASS_WITH_WARNINGS** | External symbols detected | Verify if intentional |
| ⭐ **SKIP** | FB _CALL or Generic_* | Portability check skipped |
| ❌ **FAIL** | CRITICAL violations | Requires refactoring |

### Detection Rules

| Rule | Type | Severity | Impact |
|------|------|----------|--------|
| AP-01 | External dependency | WARNING | Undeclared symbol |
| AP-02 | Manual edge detection | MEDIUM | Use R_TRIG/F_TRIG |

**Framework Whitelist:** `Sys.*` symbols are automatically allowed.

---

## 🏗️ Device Taxonomy

### Families (High-level)

| Family | Description | Detection Keywords |
|--------|-------------|-------------------|
| `motion` | Servo, axes, positioning | MC_*, TAx_DriveInterface |
| `pneumatic` | Cylinders, valves, grippers | Extend/Retract, Open/Close |
| `actuator` | Motors, contactors | MotorCtrl, MotorSts |
| `drive` | Infeed, power supplies | SinaInfeed, Infeed_ON |
| `sensor` | Encoders, smart sensors | PosFbk_, Encoder |
| `orchestrator` | Area/Zone managers | AreaInterface, MachineInterface |
| `aggregator` | Multi-device coordinators | 2+ L2 FB instances |

### Types (Specific)

```
motion:       linear_servo, rotary_servo, linear_onoff, servo_drive
pneumatic:    cylinder_double, valve, gripper
actuator:     motor_contactor, motor_vfd
drive:        infeed, drive_control
sensor:       encoder
orchestrator: area_manager, zone_manager, machine_coordinator
aggregator:   multi_device
```

---

## 📦 Output Format

### JSON Pattern (Schema v1.0.2)

```json
{
  "schema_version": "1.0.2",
  "metadata": {
    "fb_name": "Motor",
    "device_family": "actuator",
    "device_type": "motor_contactor",
    "portability_gate": {
      "status": "PASS",
      "violations": []
    }
  },
  "contract": {
    "input": { "command_udt": [], "config_udt": [], "logical_inputs": [] },
    "output": { "status_udt": [], "logical_outputs": [] },
    "inout": { "interfaces": [] }
  },
  "patterns": {
    "command_status": { "pattern": "SafeStop→RunPermitted→Run", "confidence": "MEDIUM" }
  },
  "anti_patterns": [],
  "constraints": { "portability_compliant": true }
}
```

---

## 📁 Module Structure

```
DEVICE_ANALYSIS/
├── scripts/
│   ├── analyze_device.py      # Main analyzer v1.0.6
│   └── validate_pattern.py    # JSON schema validator
├── schemas/
│   └── device_pattern_schema.json  # Schema v1.0.2
├── docs/
│   ├── FRAMEWORK_PATTERNS.md  # L1-L5 architecture
│   ├── PATTERN_RULES.md       # Detection rules
│   ├── standard_udt.md        # UDT reference
│   └── HMI_BUTTONS_PATTERN.md # HMI/Safe patterns
├── examples/
│   ├── device_pattern_Motor.json
│   └── device_pattern_OnOffAxis.json
├── skill/
│   └── SKILL.md               # Claude Code skill
├── CHANGELOG.md
└── README.md
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [FRAMEWORK_PATTERNS.md](docs/FRAMEWORK_PATTERNS.md) | L1-L5 architecture reference |
| [PATTERN_RULES.md](docs/PATTERN_RULES.md) | Detection rules and anti-patterns |
| [standard_udt.md](docs/standard_udt.md) | UDT reference |
| [HMI_BUTTONS_PATTERN.md](docs/HMI_BUTTONS_PATTERN.md) | HMI/Safe button patterns |

---

## 🔧 Requirements

- Python 3.8+
- (Optional) `jsonschema` for advanced validation

```bash
pip install jsonschema
```

---

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for full history.

**Current:** v1.0.6 (2025-12-29)
