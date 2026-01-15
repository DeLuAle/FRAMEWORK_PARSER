# Action Plan: Move Operations Documentation

This plan tracks the documentation status of SCL functions identified from the "Move operations" group in TIA Portal.

**Source Image:** `uploaded_image_1768495219671.png`

## Status Check

### Serialization
- [x] **Deserialize** (Deserializes a byte stream into a variable)
- [x] **Serialize** (Serializes a variable into a byte stream)

### Block Data Movement
- [x] **MOVE_BLK** (Already in `move.json`)
- [x] **MOVE_BLK_VARIANT** (Move block with Variant types)
- [x] **UMOVE_BLK** (Uninterruptible Move Block)

### Reference Assignment
- [x] **?=** (Attempt assignment to a reference - `Ref_to_Type` assignment check)

### Block Filling
- [x] **FILL_BLK** (Already in `move.json`)
- [x] **UFILL_BLK** (Uninterruptible Fill Block)

### Bit Sequence Parsing/Merging (Scatter/Gather)
- [x] **SCATTER** (Parse bit sequence into individual bits)
- [x] **SCATTER_BLK** (Parse array elements into bits)
- [x] **GATHER** (Merge bits into sequence)
- [x] **GATHER_BLK** (Merge bits into array elements)

### Other
- [x] **SWAP** (Already in `move.json`)

## Execution Steps

1.  [ ] Research and Document **Serialization** functions (`Serialize`, `Deserialize`).
2.  [ ] Research and Document **Scatter/Gather** functions (`SCATTER`, `GATHER`, etc.).
3.  [ ] Research and Document **Variant/Uninterruptible** moves (`MOVE_BLK_VARIANT`, `UMOVE_BLK`, `UFILL_BLK`).
4.  [ ] Research and Document **Reference Assignment** (`?=`).
5.  [ ] Update `move.json` (or create new `variant_ops.json` / `bit_ops.json` as appropriate - *Decision: Keep in `move.json` for consistency with TIA category, or split if too large*).
6.  [ ] Register all new functions in `index.json`.
