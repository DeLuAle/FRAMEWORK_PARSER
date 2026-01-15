---
name: scl-reference
description: Riferimento per funzioni di sistema SCL (TIA Portal V20+) con sintassi e anti-pattern. Usa quando devi generare o revisionare codice SCL per S7-1200/S7-1500, scegliere funzioni native o chiarire la sintassi di costrutti di controllo, conversioni, stringhe, timer e contatori.
---

# SCL Reference - TIA Portal V20+

## Quando usare questa skill

Usa questa documentazione prima di scrivere codice SCL se devi:
- usare funzioni di sistema (LIMIT, CONCAT, MOVE_BLK, ecc.)
- verificare la sintassi esatta di una funzione TIA
- sostituire logica manuale con una funzione nativa equivalente
- risolvere errori di compilazione legati a funzioni TIA
- usare costrutti di controllo (IF, FOR, CASE, WHILE, REPEAT)

## REGOLE OBBLIGATORIE

### R1: Usa sempre le funzioni di sistema TIA

NON reimplementare funzioni che esistono native.
Usa le funzioni di sistema documentate in questa skill.

**Motivazioni tecniche:**
1. **Performance**: funzioni TIA sono ottimizzate dal compilatore S7-1500 (esecuzione CPU piu veloce)
2. **Certificazione**: testate e certificate da Siemens
3. **Leggibilita**: codice riconoscibile da altri programmatori PLC
4. **Manutenibilita**: chi legge sa cosa fa LIMIT, non deve interpretare IF/THEN
5. **Conformita**: standard IEC 61131-3

### R2: Anti-pattern vietati

| NON SCRIVERE | USA INVECE |
|-----------------|---------------|
| `IF val < min THEN val := min; ELSIF val > max THEN val := max; END_IF;` | `val := LIMIT(MN:=min, IN:=val, MX:=max);` |
| `IF a < b THEN result := a; ELSE result := b; END_IF;` | `result := MIN(IN1:=a, IN2:=b);` |
| `IF a > b THEN result := a; ELSE result := b; END_IF;` | `result := MAX(IN1:=a, IN2:=b);` |
| `IF cond THEN result := valTrue; ELSE result := valFalse; END_IF;` | `result := SEL(G:=cond, IN0:=valFalse, IN1:=valTrue);` |
| `IF NOT prev AND curr THEN...` (fronte salita manuale) | Istanza `R_TRIG` |
| `IF prev AND NOT curr THEN...` (fronte discesa manuale) | Istanza `F_TRIG` |
| Concatenazione stringhe manuale | `CONCAT(IN1:=str1, IN2:=str2)` |
| Conversioni implicite | Funzioni `CONVERT` o `TO_*` esplicite |
| `IF val >= min AND val <= max THEN...` | `IN_RANGE(MIN:=min, VAL:=val, MAX:=max)` |
| Calcoli manuali su date/tempi | `T_ADD`, `T_SUB`, `T_DIFF` |
| Scaling manuale `(val - rawMin) * (engMax - engMin) / (rawMax - rawMin) + engMin` | `SCALE_X` e `NORM_X` |
| Loop con indice per copiare array | `MOVE_BLK` o `FILL_BLK` |
| `val := val * (-1);` per negazione | `val := NEG(IN:=val);` |

### R3: Self-check prima di consegnare codice

Prima di finalizzare codice SCL, verifica:

- [ ] Ho usato IF/THEN/ELSE per qualcosa che ha una funzione nativa?
- [ ] Ho reimplementato MIN/MAX/LIMIT/ABS/SEL/IN_RANGE?
- [ ] Ho gestito fronti senza R_TRIG/F_TRIG?
- [ ] Ho fatto conversioni di tipo senza funzioni CONVERT/TO_*?
- [ ] Ho manipolato stringhe senza funzioni STRING native (CONCAT, MID, FIND)?
- [ ] Ho fatto calcoli su date/tempi senza T_ADD/T_SUB/T_DIFF?
- [ ] Ho fatto scaling manuale senza SCALE_X/NORM_X?
- [ ] Ho copiato array con loop invece di MOVE_BLK?
- [ ] Ho usato timer/counter senza istanze IEC (TON, TOF, CTU)?
- [ ] Ho scritto costrutti di controllo con sintassi incerta?

Se anche una sola risposta e' SI, riscrivi usando le funzioni di sistema.

## Quick Index

### Basic Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| Math | [functions/math.json](functions/math.json) | LIMIT, MIN, MAX, ABS, NEG, MOD, SQR, SQRT, SIN, COS, ROUND, TRUNC |
| Comparison | [functions/comparison.json](functions/comparison.json) | SEL, IN_RANGE, OUT_RANGE, EQ, NE, LT, GT, LE, GE |
| Conversion | [functions/conversion.json](functions/conversion.json) | CONVERT, SCALE_X, NORM_X, TO_INT, TO_REAL, TO_BOOL |
| Move | [functions/move.json](functions/move.json) | MOVE, MOVE_BLK, FILL_BLK, SWAP, CountOfElements, IS_ARRAY |
| Bitwise | [functions/bitwise.json](functions/bitwise.json) | AND, OR, XOR, NOT, SHL, SHR, ROL, ROR |
| Timers | [functions/timers.json](functions/timers.json) | TON, TOF, TP, TONR |
| Counters | [functions/counters.json](functions/counters.json) | CTU, CTD, CTUD |
| Triggers | [functions/triggers.json](functions/triggers.json) | R_TRIG, F_TRIG, P_TRIG, N_TRIG |
| Program Control | [functions/program_control.json](functions/program_control.json) | IF, CASE, FOR, WHILE, REPEAT, EXIT, CONTINUE, RETURN, GOTO |

### Extended Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| String | [functions/string.json](functions/string.json) | CONCAT, LEN, LEFT, RIGHT, MID, FIND, REPLACE, DELETE, INSERT, S_CONV |
| Date and Time | [functions/date_time.json](functions/date_time.json) | RD_SYS_T, RD_LOC_T, T_ADD, T_SUB, T_DIFF, T_COMBINE |
| Alarms & Diag | [functions/alarms_diagnostics.json](functions/alarms_diagnostics.json) | Program_Alarm, Get_AlarmState, GET_DIAG, LED |
| Addressing | [functions/data_block_addressing.json](functions/data_block_addressing.json) | PEEK, POKE, READ_DBL, WRIT_DBL, TypeOf, GetSymbolName |
| Distributed I/O| [functions/distributed_io.json](functions/distributed_io.json) | RDREC, WRREC, DPRD_DAT, DPWR_DAT |
| Communication | [functions/communication.json](functions/communication.json) | TSEND_C, TRCV_C, TCON, TDISCON, GET, PUT |
| Tech & Safety | [functions/technology_safety.json](functions/technology_safety.json) | PID_Compact, CTRL_HSC, ESTOP1, ACK_GL |
| Motion Control| [functions/motion_control.json](functions/motion_control.json) | MC_Power, MC_Reset, MC_Home, MC_MoveAbsolute |

### Data Types Reference
| Documento | Contenuto |
|-----------|-----------|
| [data_types.json](data_types.json) | Tutti i tipi di dati SCL: BOOL, INT, DINT, REAL, STRING, ARRAY, STRUCT, DTL, ecc. |

### Programming Fundamentals
| Documento | Contenuto |
|-----------|-----------|
| [code_blocks.json](code_blocks.json) | Blocchi di codice: OB, FC, FB, DB, UDT - quando usarli e come |
| [block_interface.json](block_interface.json) | Interfacce blocchi: VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR_TEMP, VAR, regole dichiarazione |
| [plc_tags.json](plc_tags.json) | PLC Tags: organizzazione, I/O mapping, retentive, best practices |

## Procedura di Consultazione

1. Identifica la categoria dalla tabella sopra
2. Leggi solo il file .json necessario (risparmio token)
3. Se la funzione non e' nell'indice, cercala su support.industry.siemens.com
4. Se non esiste funzione nativa, implementa con IF/THEN documentando il motivo

## Sintassi Costrutti di Controllo

Per la sintassi completa di tutti i costrutti di controllo (IF, CASE, FOR, WHILE, REPEAT) con tutte le varianti, consulta [program_control.json](functions/program_control.json).

**Punti chiave:**
- `ELSIF` (non ELSEIF) per condizioni multiple in IF
- `CASE` supporta valori singoli, range (`min..max`), e liste (`val1, val2, val3`)
- `FOR...TO` incrementa, `FOR...DOWNTO` decrementa
- `WHILE` testa prima (pre-test), `REPEAT...UNTIL` testa dopo (post-test)
- `EXIT` esce dal loop, `CONTINUE` salta all'iterazione successiva
- `RETURN` esce dalla funzione/FB

## Fallback

Se una funzione non e' documentata qui:
1. Cerca in `index.json`
2. Se non presente, usa web search su: `site:support.industry.siemens.com SCL <nome_funzione>`
3. Documenta la nuova funzione per uso futuro

## Riferimenti

- [sources.md](sources.md) - Fonti consultate
- [incomplete.md](incomplete.md) - Funzioni non documentate
- [index.json](index.json) - Lookup rapido funzioni

## LINT and Syntax Rules

- LINT rules: [lint_rules.json](lint_rules.json)
- Syntax patterns: [syntax_rules.json](syntax_rules.json)

Expanded coverage: control structures, types, and best-practice lint checks in lint_rules.json; syntax patterns in syntax_rules.json.
Expanded coverage includes safety, style, naming, and performance lint rules.
## Lint Data Files

- lint_rules.json
- lint_patterns.json
- lint_checks.json
- lint_functions.json
- lint_types.json

## Motion Control Data Files

- mc_functions.json
- mc_to_structures.json
- mc_error_codes.json

## Motion Control Lint Data

- mc_status_lint.json
- mc_naming_conventions.json

## Lint Examples

- lint_examples.json

## Motion Control Categories

- mc_move.json
- mc_stop.json
- mc_power.json
- mc_sync.json
- mc_cam.json
- mc_other.json
- mc_params_schema.json

## Motion Control Index

- mc_rule_map.json
- mc_index.json
