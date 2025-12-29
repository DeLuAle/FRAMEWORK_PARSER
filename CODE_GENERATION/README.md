# FRAMEWORK_PARSER - CODE GENERATION

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
CODE_GENERATION/
├── DEVICE_ANALYSIS/           # 🔧 Core module - Pattern extraction
│   ├── scripts/               # Python analysis scripts
│   │   ├── analyze_device.py  # Main analyzer v1.0.6
│   │   └── validate_pattern.py # JSON schema validator
│   ├── schemas/               # JSON schemas
│   │   └── device_pattern_schema.json
│   ├── docs/                  # Documentation
│   │   ├── FRAMEWORK_PATTERNS.md  # L1-L5 architecture
│   │   ├── PATTERN_RULES.md       # Detection rules
│   │   ├── standard_udt.md        # UDT reference
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
│   └── REVISION_NOTES.md
│
└── README.md                  # This file
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

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ **PASS** | No external dependencies | Ready for reusable library |
| ⚠️ **PASS_WITH_WARNINGS** | External symbols detected | Verify if intentional |
| ⭐ **SKIP** | FB _CALL or Generic_* | Portability check skipped |
| ❌ **FAIL** | CRITICAL violations | Requires refactoring |

---

## 🏗️ Architecture (L1-L5)

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

See: [`DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md`](DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md)

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

| Document | Description |
|----------|-------------|
| [DEVICE_ANALYSIS/README.md](DEVICE_ANALYSIS/README.md) | Module guide |
| [DEVICE_ANALYSIS/docs/PATTERN_RULES.md](DEVICE_ANALYSIS/docs/PATTERN_RULES.md) | Detection rules |
| [DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md](DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md) | L1-L5 architecture |
| [DEVICE_ANALYSIS/docs/standard_udt.md](DEVICE_ANALYSIS/docs/standard_udt.md) | UDT reference |
| [DEVICE_ANALYSIS/docs/HMI_BUTTONS_PATTERN.md](DEVICE_ANALYSIS/docs/HMI_BUTTONS_PATTERN.md) | HMI/Safe patterns |

---

## 🛠️ Requirements

- Python 3.8+
- (Optional) `jsonschema` for advanced validation

```bash
pip install jsonschema
```

---

## 📈 Roadmap

- [x] v1.0 - Device analysis con portability gate
- [x] v1.0.6 - Symbol-based portability, aggregator detection
- [ ] v1.1 - AST-based analysis (symbol table, CFG)
- [ ] v1.2 - Code generation from patterns
- [ ] v2.0 - MCP server for TIA Portal integration

---

## 👤 Author

**Alessandro** - PM Forming  
Industrial Automation | Siemens S7-1500 | TIA Portal

---

## 📄 License

MIT License - See [LICENSE](LICENSE)
