# SCL Reference - TIA Portal V20+

## Quando usare questa skill

Leggi questa documentazione **PRIMA** di scrivere codice SCL se:
- Devi usare funzioni di sistema (LIMIT, CONCAT, MOVE_BLK, ecc.)
- Non conosci la sintassi esatta di una funzione TIA
- Stai scrivendo logica che potrebbe avere una funzione nativa equivalente
- Ricevi errori di compilazione su funzioni TIA
- Devi scrivere costrutti di controllo (IF, FOR, CASE, WHILE, REPEAT)

## REGOLE OBBLIGATORIE

### R1: Usa SEMPRE le funzioni di sistema TIA

❌ **VIETATO** reimplementare funzioni che esistono native.
✅ **USA** le funzioni di sistema documentate in questa skill.

**Motivazioni tecniche:**
1. **Performance**: funzioni TIA sono ottimizzate dal compilatore S7-1500 (esecuzione CPU più veloce)
2. **Certificazione**: testate e certificate da Siemens
3. **Leggibilità**: codice riconoscibile da altri programmatori PLC
4. **Manutenibilità**: chi legge sa cosa fa LIMIT, non deve interpretare IF/THEN
5. **Conformità**: standard IEC 61131-3

### R2: Anti-pattern vietati

| ❌ NON SCRIVERE | ✅ USA INVECE |
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

**Se anche solo una risposta è SÌ → RISCRIVI usando le funzioni di sistema.**

## Quick Index

### Basic Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| Math | [functions/math.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/math.json) | LIMIT, MIN, MAX, ABS, NEG, MOD, SQR, SQRT, SIN, COS, ROUND, TRUNC |
| Comparison | [functions/comparison.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/comparison.json) | SEL, IN_RANGE, OUT_RANGE, EQ, NE, LT, GT, LE, GE |
| Conversion | [functions/conversion.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/conversion.json) | CONVERT, SCALE_X, NORM_X, TO_INT, TO_REAL, TO_BOOL |
| Move | [functions/move.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/move.json) | MOVE, MOVE_BLK, FILL_BLK, SWAP, CountOfElements, IS_ARRAY |
| Bitwise | [functions/bitwise.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/bitwise.json) | AND, OR, XOR, NOT, SHL, SHR, ROL, ROR |
| Timers | [functions/timers.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/timers.json) | TON, TOF, TP, TONR |
| Counters | [functions/counters.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/counters.json) | CTU, CTD, CTUD |
| Triggers | [functions/triggers.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/triggers.json) | R_TRIG, F_TRIG, P_TRIG, N_TRIG |
| Program Control | [functions/program_control.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/program_control.json) | IF, CASE, FOR, WHILE, REPEAT, EXIT, CONTINUE, RETURN |

### Extended Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| String | [functions/string.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/string.json) | CONCAT, LEN, LEFT, RIGHT, MID, FIND, REPLACE |

### Data Types Reference
| Documento | Contenuto |
|-----------|-----------|
| [data_types.json](file:///c:/Projects/SCL%20Syntax/scl-reference/data_types.json) | Tutti i tipi di dati SCL: BOOL, INT, DINT, REAL, STRING, ARRAY, STRUCT, DTL, ecc. |

### Programming Fundamentals
| Documento | Contenuto |
|-----------|-----------|
| [code_blocks.json](file:///c:/Projects/SCL%20Syntax/scl-reference/code_blocks.json) | Blocchi di codice: OB, FC, FB, DB, UDT - quando usarli e come |
| [block_interface.json](file:///c:/Projects/SCL%20Syntax/scl-reference/block_interface.json) | Interfacce blocchi: VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR_TEMP, VAR, regole dichiarazione |
| [plc_tags.json](file:///c:/Projects/SCL%20Syntax/scl-reference/plc_tags.json) | PLC Tags: organizzazione, I/O mapping, retentive, best practices |

## Procedura di Consultazione

1. Identifica la categoria dalla tabella sopra
2. Leggi **SOLO** il file .json necessario (risparmio token)
3. Se la funzione non è nell'indice → cerca su support.industry.siemens.com
4. Se non esiste funzione nativa → implementa con IF/THEN documentando il motivo

## Sintassi Costrutti di Controllo

Per la sintassi completa di tutti i costrutti di controllo (IF, CASE, FOR, WHILE, REPEAT) con tutte le varianti, consulta [program_control.json](file:///c:/Projects/SCL%20Syntax/scl-reference/functions/program_control.json).

**Punti chiave:**
- `ELSIF` (non ELSEIF) per condizioni multiple in IF
- `CASE` supporta valori singoli, range (`min..max`), e liste (`val1, val2, val3`)
- `FOR...TO` incrementa, `FOR...DOWNTO` decrementa
- `WHILE` testa prima (pre-test), `REPEAT...UNTIL` testa dopo (post-test)
- `EXIT` esce dal loop, `CONTINUE` salta all'iterazione successiva
- `RETURN` esce dalla funzione/FB

## Fallback

Se una funzione non è documentata qui:
1. Cerca in `index.json`
2. Se non presente, usa web search su: `site:support.industry.siemens.com SCL <nome_funzione>`
3. Documenta la nuova funzione per uso futuro

## Riferimenti

- [sources.md](file:///c:/Projects/SCL%20Syntax/scl-reference/sources.md) - Fonti consultate
- [incomplete.md](file:///c:/Projects/SCL%20Syntax/scl-reference/incomplete.md) - Funzioni non documentate
- [index.json](file:///c:/Projects/SCL%20Syntax/scl-reference/index.json) - Lookup rapido funzioni
