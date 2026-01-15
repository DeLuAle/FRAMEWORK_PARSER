# SCL Documentation Gap Analysis

This document tracks the missing SCL instructions identified by comparing the current knowledge base against Siemens TIA Portal reference lists.

## Missing Categories & Functions

### Variant & DB_ANY Operations
- [x] **VariantGet** (Read value from Variant)
- [x] **VariantPut** (Write value to Variant)
- [x] **VARIANT_TO_DB_ANY** (Get DB number from Variant)
- [x] **DB_ANY_TO_VARIANT** (Create Variant from DB number)
- [x] **CountOfElements** (Done in `move.json`)
- [x] **IS_ARRAY** (Done in `move.json`)

### Memory Access (Endianness)
- [x] **Deserialize** (Done)
- [x] **Serialize** (Done)
- [x] **PEEK/POKE** (Done in `data_block_addressing.json`)
- [x] **READ_LITTLE** (Read Little Endian)
- [x] **WRITE_LITTLE** (Write Little Endian)
- [x] **READ_BIG** (Read Big Endian)
- [x] **WRITE_BIG** (Write Big Endian)

### Math & Control
- [x] **CALCULATE** (Handled via native expressions)
- [x] **INC** (Added to `math.json`)
- [x] **DEC** (Added to `math.json`)
- [x] **RUNTIME** (Added to `program_control.json`)

### Comparators / Validation
- [x] **OK** (Added to `comparison.json`)
- [x] **NOT_OK** (Added to `comparison.json`)
- [x] **IN_RANGE** (Done)
- [x] **OUT_RANGE** (Done)

## Verification Actions
1. [ ] Check `index.json` for `INC`, `DEC`, `CALCULATE`.
2. [ ] Check `index.json` for `VariantGet`, `VariantPut`.
3. [ ] Check `index.json` for `READ_LITTLE`, `WRITE_LITTLE` etc.
4. [ ] Check `index.json` for `OK`, `NOT_OK`.
5. [ ] Create documentation for confirmed missing items.

## Completed Categories (Reference)
- [x] Implicit/Explicit Conversion
- [x] Motion Control
- [x] ProfiEnergy
- [x] Recipe / DataLog
- [x] Bit Logic / Timers / Counters (Basic)
- [x] String Functions
- [x] Move / Block Move (Scatter/Gather/Serialize)
