# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**FRAMEWORK_PARSER** is a comprehensive PLC (Programmable Logic Controller) development toolchain for Siemens TIA Portal projects. It converts XML exports to readable SCL code, extracts device patterns for code generation, and provides knowledge base systems for Siemens documentation.

**Source of Truth**: XML files exported from TIA Portal are the definitive source of truth. All SCL/CSV generated outputs are heuristic conversions that may contain interpretation errors.

## Repository Structure

The repository consists of three main subsystems:

### 1. **xml_to_scl/** - TIA Portal XML to SCL Converter
Converts PLC blocks (FB, FC, DB, UDT) and Tag Tables from TIA Portal XML format to readable/importable SCL or CSV files.

### 2. **CODE_GENERATION/** - Pattern Analysis & Extraction
Analyzes SCL function blocks to extract device patterns, UDT contracts, and detect portability issues for automated code generation.

### 3. **DocKB_Siemens/** - Documentation Knowledge Base
Information retrieval system for Siemens manuals (SINAMICS, S7-1500). Extracts PDF content into searchable JSON databases.

## Common Development Commands

### XML to SCL Conversion

**Batch convert entire PLC project:**
```bash
python xml_to_scl/batch_convert_project.py "PLC_410D1" --output "PLC_410D1_Parsed"
```

**Single file conversion:**
```bash
python xml_to_scl/main.py path/to/file.xml --output "output_folder"
```

**Run all xml_to_scl tests:**
```bash
cd xml_to_scl
python run_all_tests.py
```

**Run specific test suites:**
```bash
python test_security_xxe.py          # Security tests (XXE protection)
python test_region_nesting.py        # REGION structure tests
python test_boolean_expression_builder.py  # Boolean logic tests
python test_fb_parameters.py         # Parameter extraction tests
python test_integration_suite.py     # Real-world file tests
```

### Device Pattern Analysis

**Analyze a Function Block:**
```bash
cd CODE_GENERATION/DEVICE_ANALYSIS/scripts
python analyze_device.py /path/to/Motor.scl --output ./output
```

**With UDT folder:**
```bash
python analyze_device.py /path/to/Motor.scl --udt-path /path/to/UDT --output ./output
```

**Validate pattern JSON:**
```bash
python validate_pattern.py ./output/device_pattern_Motor.json
```

### DocKB Knowledge Base

**Extract PDF to JSON (Phase 1):**
```bash
cd DocKB_Siemens
python scripts/extract_pdf_to_json.py --pdf-dir "resources/pdfs/sinamics" --output-dir "output/sinamics"
```

**Build Knowledge Base (Phase 2):**
```bash
python scripts/build_knowledge_base.py --input-dir "output/sinamics" --output-dir "kb/sinamics"
```

**Search Knowledge Base:**
```bash
python scripts/sinamics_kb_search.py --kb "kb/sinamics" --search "fault F3000"
```

## Architecture & Key Concepts

### xml_to_scl Pipeline

**Parsing Flow:**
```
XML File → xml_parser_base.py (XXE-protected parser)
         → fbfc_parser.py / db_parser.py / udt_parser.py / plc_tag_parser.py
         → lad_parser.py (for Ladder/FBD logic reconstruction)
         → fbfc_generator.py / db_generator.py / udt_generator.py / plc_tag_generator.py
         → SCL/CSV Output
```

**Critical Implementation Details:**

1. **XXE Protection**: Uses `defusedxml` with ElementTree fallback (xml_parser_base.py)
2. **Encoding Safety**: Uses `errors='replace'` instead of `'ignore'` to avoid silent data loss
3. **REGION Nesting**: Generates sequential REGION blocks, NOT nested (fixed in fbfc_generator.py:201)
4. **Boolean Expressions**: Reconstructs from Ladder/FBD using wire tracing and powerrail resolution
5. **Placeholder Policy**: Uses `???` for unresolved expressions - these indicate manual review needed

**Known Parsing Complexities:**

- **Ladder Logic**: Wire UID tracing through powerrails, contacts, and coils (lad_parser.py)
- **FB Parameters**: Extraction requires resolving both interface and internal networks
- **Nested Blocks**: Deep nesting in original XML requires careful handling to avoid stack overflow

### CODE_GENERATION Device Taxonomy

**5-Level Framework Architecture:**
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

**Device Families:**
- `motion`: Servo, axes, positioning (MC_*, TAx_DriveInterface)
- `pneumatic`: Cylinders, valves, grippers (Extend/Retract, Open/Close)
- `actuator`: Motors, contactors (MotorCtrl, MotorSts)
- `drive`: Infeed, power supplies (SinaInfeed, Infeed_ON)
- `sensor`: Encoders, smart sensors (PosFbk_, Encoder)
- `orchestrator`: Area/Zone managers (AreaInterface, MachineInterface)
- `aggregator`: Multi-device coordinators (2+ L2 FB instances)

**Portability Gate:**
- ✅ PASS: No external dependencies, ready for reuse
- ⚠️ PASS_WITH_WARNINGS: External symbols detected, verify intentional
- ⭐ SKIP: FB _CALL or Generic_* (portability check skipped)
- ❌ FAIL: Critical violations, requires refactoring

**Output Format:** `device_pattern_<name>.json` (Schema v1.0.2) + `DEVICE_<name>.md` (human-readable report)

### DocKB Information Retrieval

**Two-Phase Process:**

1. **Extraction (Slow, Run Once)**: PDF → pdftotext → JSON sections
   - Splits on empty lines to create ~28,000 section files per manual
   - Uses system tools: `pdftotext`, `pdfinfo`, `pandoc`

2. **KB Build (Fast, Repeatable)**: JSON sections → Indexed KB
   - Categories: parameter, fault, alarm, motor, safety, function, appendix
   - Keyword-based indexing (no AI/LLM, completely offline)
   - Output: `index.json`, `search_index.json`, `metadata.json`

**System Dependencies Required:**
- **Windows**: `choco install poppler pandoc`
- **Linux**: `sudo apt-get install poppler-utils pandoc`
- **macOS**: `brew install poppler pandoc`

**No Python dependencies beyond standard library** - pure stdlib implementation.

### Integration JSON Patterns

**Location:** `JSON_integrazione/` contains semantic integration patterns for various machine types:
- FeedMachine, PositioningMachine, SpeedMachine, ValveMachine (L1-L3 semantics)
- HydraulicUnit, Lubrication, SmartLoopControl (L3 semantic)
- Button, Area, Infeed integration patterns

These are used by CODE_GENERATION for pattern matching and device classification.

## Testing Strategy

### xml_to_scl Testing

**Test Coverage:** 34 unit tests + 11 real-world files = 45 total test cases

**Test Files:**
- `test_security_xxe.py`: 10 tests for XXE protection
- `test_region_nesting.py`: 6 tests for correct REGION structure
- `test_boolean_expression_builder.py`: 4 tests for logic reconstruction
- `test_fb_parameters.py`: 4 tests for parameter extraction
- `test_integration_suite.py`: 10 real-world file conversions

**Run individual test file:**
```bash
cd xml_to_scl
python test_<name>.py
```

**Real-world validation:**
```bash
python validate_real_conversion.py
```

**Performance expectation:** ~6ms average conversion per file, linear scalability

### Manual Testing Files

Located in `xml_to_scl/tests/`:
- `test_*_manual.py`: Manual testing scripts for specific components
- `debug_*.py`: Debug utilities for troubleshooting specific issues
- `quick_test.py`: Rapid smoke testing

### CODE_GENERATION Testing

**Schema validation:**
```bash
cd CODE_GENERATION/DEVICE_ANALYSIS/scripts
python validate_pattern.py <pattern_json_file>
```

## Special Skills & Extensions

### SKILL_SCL_SYNTAX/
SCL programming reference and best practices for TIA Portal V20+:
- **SKILL.md**: Complete SCL syntax reference
- **data-types.md**: SCL data type reference
- **core-functions.md**: Native Siemens functions (200+ functions)
- **anti-patterns.md**: Common mistakes to avoid

### SCL Syntax Reference Database
**Location:** `xml_to_scl/SCL Syntax/scl-reference/`

JSON-based reference for:
- `data_types.json`: SCL data types
- `block_interface.json`: FB/FC interface syntax
- `functions/*.json`: Math, bitwise, comparison, conversion, timers, etc.
- `index.json`: Central registry

## Important Development Notes

### Security Considerations

**XXE Protection (xml_parser_base.py):**
- MUST use `defusedxml` for XML parsing
- Falls back to ElementTree if defusedxml unavailable
- Disables entity expansion to prevent XXE attacks

**Encoding:**
- ALWAYS use `errors='replace'` instead of `'ignore'` for encoding operations
- This prevents silent data loss

### Code Quality Rules

**From xml_to_scl development:**
1. Use specific exception types, not generic `except Exception:`
2. Validate input only at system boundaries
3. Handle encoding explicitly with `errors='replace'`
4. Test with real-world files, not just synthetic tests
5. Document all placeholders (`???`) for manual review

### File Structure Conventions

**xml_to_scl parsers:**
- `*_parser.py`: Extract data from XML
- `*_generator.py`: Generate SCL/CSV output
- Base classes in `xml_parser_base.py`, `scl_generator_base.py`

**CODE_GENERATION:**
- `analyze_device.py`: Main analyzer script (v1.0.6)
- Output: `device_pattern_<name>.json` + `DEVICE_<name>.md`
- Schema: `schemas/device_pattern_schema.json` (v1.0.2)

### Verification Documents

Several verification documents exist in root for evidence tracking:
- `VERIFICATION_*`: Evidence verification summaries
- `CODE_EVIDENCE_MAPPING.md`: Maps claims to code locations
- `N2_CORRECTED_SECTION.md`: Documented corrections

These track the accuracy of parser weakness analysis.

## Working with PLC Projects

### Typical Workflow

1. **Export from TIA Portal:** Export project as XML structured format
2. **Convert to SCL:** `python xml_to_scl/batch_convert_project.py <input_dir> --output <output_dir>`
3. **Review placeholders:** Check `batch_conversion_report.csv` for files with `???` placeholders
4. **Analyze patterns:** Run device analysis on generated SCL files
5. **Validate portability:** Check portability_gate status in pattern JSON

### SCL Code Generation Context

When analyzing or generating SCL code:
- **Named Parameters**: TIA Portal V20+ requires named parameters: `TON(IN := x, PT := T#5s)`
- **Persistent Instances**: Multi-instance FBs require static instances
- **Data Type Naming**: Use PascalCase for UDTs: `MotorCtrl`, `MotorSts`
- **Interface Patterns**: Separate Command/Status/Config UDTs for clean contracts

### UDT Standards

Reference: `CODE_GENERATION/DEVICE_ANALYSIS/docs/standard_udt.md`

Common UDT patterns:
- `*Ctrl`: Command/Control inputs
- `*Sts`: Status outputs
- `*Cfg`: Configuration parameters
- `*Interface`: L4/L5 coordination structures

## Performance Expectations

### xml_to_scl
- Average: 6ms per file
- Small files (<10 KB): 2-5ms
- Large files (50-200 KB): 6-15ms
- Memory: <50 MB typical
- Scalability: Linear (1000 files ~10 seconds)

### DEVICE_ANALYSIS
- Analysis time: Depends on SCL complexity
- Output size: JSON typically 5-50 KB
- Memory: Minimal, text processing only

### DocKB
- PDF extraction: Slow (minutes per manual), run once
- KB build: Fast (seconds), repeatable
- Search: Instant (keyword matching)

## Git Branch Workflow

**Current branch:** `claude/init-project-setup-dU4W7`

**All development should occur on designated feature branches starting with `claude/` and ending with the session ID.**

## Additional References

- **xml_to_scl full documentation:** `xml_to_scl/docs/README.md`
- **CODE_GENERATION patterns:** `CODE_GENERATION/DEVICE_ANALYSIS/docs/FRAMEWORK_PATTERNS.md`
- **DocKB setup:** `DocKB_Siemens/docs/QUICK_START.md`
- **SCL syntax skill:** `SKILL_SCL_SYNTAX/SKILL.md`
