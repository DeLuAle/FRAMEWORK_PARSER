# FRAMEWORK_PARSER

**Automated PLC Code Analysis & Pattern Extraction for Siemens TIA Portal**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![TIA Portal](https://img.shields.io/badge/TIA%20Portal-V18+-green.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)]()

---

## 🎯 Purpose

Framework per l'analisi automatica di codice SCL e l'estrazione di pattern riutilizzabili dai progetti TIA Portal. Obiettivo: **code generation automatica** da PRD (Product Requirements Documents).

```
TIA Portal XML → Parser → SCL Files → Analyzer → Pattern JSON → Code Generator
```

---

## 📁 Repository Structure

```
FRAMEWORK_PARSER/
├── DEVICE_ANALYSIS/           # 🔧 Core module - Pattern extraction
│   ├── scripts/               # Python analysis scripts
│   │   ├── analyze_device.py  # Main analyzer v1.0.6
│   │   └── validate_pattern.py # JSON schema validator
│   ├── schemas/               # JSON schemas
│   │   └── device_pattern_schema.json
│   ├── docs/                  # Documentation
│   │   ├── PATTERN_RULES.md   # Detection rules
│   │   ├── FRAMEWORK_PATTERNS.md # L1-L5 architecture
│   │   ├── standard_udt.md    # UDT reference
│   │   └── HMI_BUTTONS_PATTERN.md
│   ├── examples/              # Sample outputs
│   │   ├── device_pattern_OnOffAxis.json
│   │   └── device_pattern_Motor.json
│   ├── skill/                 # Claude Code skill
│   │   └── SKILL.md
│   ├── README.md
│   └── CHANGELOG.md
│
├── docs/                      # Project-wide documentation
│   └── REVISION_NOTES.md      # Design decisions
│
└── samples/                   # Sample SCL files for testing
```

---

## 🚀 Quick Start

### 1. Analyze a Function Block

```bash
cd DEVICE_ANALYSIS/scripts

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

Il sistema classifica ogni FB in base alla **portabilità cross-progetto**:

| Status | Significato | Azione |
|--------|-------------|--------|
| ✅ **PASS** | Nessuna dipendenza esterna | Pronto per libreria riusabile |
| ⚠️ **PASS_WITH_WARNINGS** | Simboli esterni rilevati | Verificare se intenzionali |
| ⭐ **SKIP** | FB _CALL o Generic_* | Portability check saltato |
| ❌ **FAIL** | Violazioni CRITICAL | Richiede refactoring |

### Detection Rules

| Rule | Type | Severity | Impact |
|------|------|----------|--------|
| AP-01 | External dependency | WARNING | Simbolo non dichiarato |
| AP-02 | Manual edge detection | MEDIUM | Usa R_TRIG/F_TRIG |

**Whitelist Framework:** Simboli `Sys.*` sono automaticamente permessi.

---

## 🏗️ Device Taxonomy

Sistema a 2 livelli per classificazione automatica:

### Families (High-level)

| Family | Descrizione | Keyword Detection |
|--------|-------------|-------------------|
| `motion` | Servo, assi, positioning | MC_*, TAx_DriveInterface |
| `pneumatic` | Cilindri, valvole, gripper | Extend/Retract, Open/Close |
| `actuator` | Motori, contattori | MotorCtrl, MotorSts |
| `drive` | Infeed, alimentatori | SinaInfeed, Infeed_ON |
| `sensor` | Encoder, sensori smart | PosFbk_, Encoder |
| `orchestrator` | Area/Zone manager | AreaInterface, MachineInterface |
| `aggregator` | Multi-device coordinator | 2+ L2 FB instances |

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

## 📐 Architecture (L1-L5)

Il framework documenta l'architettura a 5 livelli:

```
L5 - Area Manager      │ Modo Man/Aut, Ciclo, Broadcast AreaInterface
        ↓
L4 - Zone Manager      │ Coordinamento macchine zona, sequenze processo
        ↓
L3 - Aggregator        │ Multi-device coordinator (es. Decoiler completo)
        ↓
L2 - Single-Actuator   │ Machine wrapper con Control_ON, CheckNext/ExtEnable
        ↓
L1 - Device            │ Logica attuatore singolo (Motor, Valve, Axis)
```

Vedi: [`DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md`](DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md)

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
    "command_status": { "pattern": "SafeStop→RunPermitted→Run", "confidence": "MEDIUM" },
    "native_functions": { "timers": ["DelayContactorFeedbackON"], "edge_detection": "none" }
  },
  "anti_patterns": [],
  "constraints": { "portability_compliant": true, "multi_instance_safe": true }
}
```

### Markdown Report

```markdown
# Device Analysis: Motor

**Family:** actuator | **Type:** motor_contactor | **Portability:** ✅ PASS

## Pattern Recognition
- Command/Status: SafeStop→RunPermitted→Run (MEDIUM)
- State Machine: implicit
- Timers: DelayContactorFeedbackON

## Contract Summary
- Inputs: 5 logical
- Outputs: 3 logical
- Interfaces: 2
```

---

## 🔧 Integration Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIA PORTAL PROJECT                           │
│  ┌─────────────┐                                                │
│  │  Export XML │ → Structured export                            │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    XML TO SCL CONVERTER                         │
│  python xml_to_scl/batch_convert_project.py                     │
│  Input:  PLC_Project_Parsed/                                    │
│  Output: scl_files/                                             │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEVICE ANALYSIS                              │
│  python DEVICE_ANALYSIS/scripts/analyze_device.py               │
│  Input:  scl_files/*.scl                                        │
│  Output: patterns/*.json + reports/*.md                         │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PATTERN LIBRARY                              │
│  Reusable patterns for code generation                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Documentation

| Document | Descrizione |
|----------|-------------|
| [DEVICE_ANALYSIS/README.md](DEVICE_ANALYSIS/README.md) | Guida modulo analisi |
| [DEVICE_ANALYSIS/docs/PATTERN_RULES.md](DEVICE_ANALYSIS/docs/PATTERN_RULES.md) | Regole detection |
| [DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md](DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md) | Architettura L1-L5 |
| [DEVICE_ANALYSIS/docs/standard_udt.md](DEVICE_ANALYSIS/docs/standard_udt.md) | UDT reference |
| [DEVICE_ANALYSIS/docs/HMI_BUTTONS_PATTERN.md](DEVICE_ANALYSIS/docs/HMI_BUTTONS_PATTERN.md) | Pattern HMI/Safe |

---

## 🛠️ Requirements

- Python 3.8+
- (Optional) `jsonschema` per validazione avanzata

```bash
pip install jsonschema
```

---

## 📈 Roadmap

- [x] v1.0 - Device analysis con portability gate
- [x] v1.0.6 - Symbol-based portability, aggregator detection
- [ ] v1.1 - AST-based analysis (symbol table, CFG)
- [ ] v1.2 - Code generation da patterns
- [ ] v2.0 - MCP server per TIA Portal integration

---

## 👤 Author

**Alessandro** - PM Forming  
Industrial Automation | Siemens S7-1500 | TIA Portal

---

## 📄 License

MIT License - See [LICENSE](LICENSE)
