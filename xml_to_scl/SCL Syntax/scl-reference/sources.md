# Fonti Documentazione SCL

## Fonti principali utilizzate o da verificare

### Documentazione ufficiale Siemens
- TIA Portal Online Help (V20+): https://docs.tia.siemens.cloud
- Siemens Industry Support - Comparison list S7-300/400/1200/1500 (doc 109797648, A5E33285102)
- Siemens Industry Support - IEC Timers (TON, TOF, TP, TONR)
- Siemens Industry Support - Edge Detection (R_TRIG, F_TRIG)
- Siemens Industry Support - SCL String Instructions (CONCAT, LEN, LEFT, RIGHT, MID)
- Siemens Industry Support - SCL Conversion/Scaling (CONVERT, SCALE_X, NORM_X)
- Siemens Industry Support - SCL Control Structures (IF, CASE, FOR, WHILE, REPEAT)

### Risorse community (da usare solo per confronto)
- https://solisplc.com
- https://plcblog.in

### Web Search Results
- Siemens Industry Support - Explicit Conversion Functions Table (SINT, USINT, BYTE X_TO_Y)

## Data consultazione
2026-01-15 (Includes Web Research updates)

## Note
Documentazione estesa per includere:
- Funzioni di stringa avanzate (DELETE, INSERT, S_CONV)
- Gestione Date e Tempi (T_ADD, T_SUB, RD_SYS_T, ecc.)
- Diagnostica e Allarmi (Program_Alarm, GET_DIAG, LED)
- Accesso diretto alla memoria (PEEK, POKE)
- I/O Distribuito (RDREC, WRREC, DPRD_DAT)
- Comunicazione (TSEND_C, TRCV_C, TCON, GET, PUT)
- Tecnologia e Safety (PID_Compact, ESTOP1, ACK_GL)

Tutte le firme sono state verificate rispetto alla documentazione TIA Help V20+.

## Motion Control Sources
- Local document: xml_to_scl/SCL Syntax/Docs_SCL/LINT_SKILL_MC_1.MD
- Local MC datasets: mc_functions.json, mc_to_structures.json, mc_error_codes.json, mc_status_lint.json, mc_naming_conventions.json
- Derived datasets: mc_move.json, mc_stop.json, mc_power.json, mc_sync.json, mc_cam.json, mc_other.json, lint_examples.json, mc_params_schema.json
- Derived MC indexes: mc_rule_map.json, mc_index.json
