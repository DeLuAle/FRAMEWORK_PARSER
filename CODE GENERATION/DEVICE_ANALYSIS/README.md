# DEVICE_ANALYSIS Module

**Pattern Extraction for PLC Function Blocks - v1.0.6**

---

## 🎯 Purpose

Analizza Function Block SCL per estrarre:
1. **Device patterns** (command/status, state machine, alarms)
2. **UDT contracts** (input/output/inout)
3. **Anti-patterns** (portability violations)
4. **Configuration templates**

---

## 📁 Structure

```
DEVICE_ANALYSIS/
├── scripts/
│   ├── analyze_device.py      # Main analyzer v1.0.6
│   └── validate_pattern.py    # Schema validator
├── schemas/
│   └── device_pattern_schema.json  # JSON Schema v1.0.2
├── docs/
│   ├── PATTERN_RULES.md       # Detection rules
│   ├── FRAMEWORK_PATTERNS.md  # L1-L5 architecture
│   ├── standard_udt.md        # UDT reference
│   └── HMI_BUTTONS_PATTERN.md # HMI/Safe patterns
├── examples/
│   ├── device_pattern_OnOffAxis.json
│   └── device_pattern_Motor.json
├── skill/
│   └── SKILL.md               # Claude Code skill definition
├── README.md
└── CHANGELOG.md
```

---

## 🚀 Usage

### Basic Analysis

```bash
python scripts/analyze_device.py Motor.scl --output ./output
```

### With UDT Folder

```bash
python scripts/analyze_device.py Motor.scl --udt-path ./UDT --output ./output
```

### Validate Output

```bash
python scripts/validate_pattern.py device_pattern_Motor.json
```

---

## 📊 Output

### JSON Pattern

```json
{
  "schema_version": "1.0.2",
  "metadata": {
    "fb_name": "Motor",
    "device_family": "actuator",
    "device_type": "motor_contactor",
    "portability_gate": { "status": "PASS", "violations": [] }
  },
  "contract": { ... },
  "patterns": { ... },
  "anti_patterns": [],
  "constraints": { "portability_compliant": true }
}
```

### Markdown Report

- Portability status con emoji
- Pattern recognition summary
- Contract summary (inputs/outputs/interfaces)
- Anti-patterns by severity
- Dependencies

---

## 🚦 Portability Gate

| Status | Significato |
|--------|-------------|
| ✅ PASS | Nessuna dipendenza esterna |
| ⚠️ PASS_WITH_WARNINGS | Simboli esterni (verificare) |
| ⭐ SKIP | FB _CALL o Generic_* |
| ❌ FAIL | Violazioni CRITICAL |

### Skip Rules

- `*_CALL` - FC wrapper per I/O mapping
- `Generic*` - Blocchi HW-specific

### Whitelist

- `Sys.*` - Framework symbols automaticamente permessi

---

## 🏗️ Device Taxonomy

### Families

| Family | Detection Keywords |
|--------|-------------------|
| motion | MC_*, TAx_DriveInterface, PosFbk_ITF |
| pneumatic | Extend/Retract, Open/Close/Grip |
| actuator | MotorCtrl, MotorSts |
| drive | SinaInfeed, Infeed_ON |
| sensor | PosFbk_, Encoder |
| orchestrator | AreaInterface, MachineInterface |
| aggregator | 2+ L2 FB instances |

### Types

- motion: `linear_servo`, `rotary_servo`, `linear_onoff`, `servo_drive`
- pneumatic: `cylinder_double`, `valve`, `gripper`
- actuator: `motor_contactor`, `motor_vfd`
- drive: `infeed`, `drive_control`
- orchestrator: `area_manager`, `zone_manager`, `machine_coordinator`
- aggregator: `multi_device`

---

## 📐 Anti-Pattern Detection

| ID | Type | Severity | Fix |
|----|------|----------|-----|
| AP-01 | external_dependency | WARNING | Declare in VAR_INPUT/VAR_IN_OUT |
| AP-02 | manual_edge_detection | MEDIUM | Use R_TRIG/F_TRIG |

---

## 🔧 Claude Code Skill

Per usare con Claude Code, copia `skill/SKILL.md` in:

```bash
/mnt/skills/user/device-analysis/SKILL.md
```

---

## 📚 Documentation

- [PATTERN_RULES.md](docs/PATTERN_RULES.md) - Detection rules
- [FRAMEWORK_PATTERNS.md](docs/FRAMEWORK_PATTERNS.md) - L1-L5 architecture
- [standard_udt.md](docs/standard_udt.md) - UDT reference
- [HMI_BUTTONS_PATTERN.md](docs/HMI_BUTTONS_PATTERN.md) - HMI/Safe patterns

---

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md)

**Current:** v1.0.6 (Symbol-based portability, aggregator detection)
