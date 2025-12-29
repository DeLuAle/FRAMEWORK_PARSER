# Specifica per Generazione Documentazione SCL - TIA Portal

## Obiettivo

Creare una knowledge base strutturata delle **funzioni di sistema SCL** di TIA Portal (V20+) per uso da parte di un AI coding assistant (Claude Code). La documentazione deve permettere all'AI di:

1. Conoscere la sintassi esatta delle funzioni native
2. **Preferire sempre** le funzioni di sistema rispetto a reimplementazioni manuali
3. Identificare anti-pattern e correggerli automaticamente

**Riferimento principale**: Siemens "Comparison list for S7-300, S7-400, S7-1200, S7-1500" (A5E33285102-AH)

---

## Contesto d'uso

- **Target**: Programmazione PLC Siemens S7-1500 / S7-1200
- **Linguaggio**: SCL (Structured Control Language) conforme IEC 61131-3
- **IDE**: TIA Portal V20 o superiore
- **Consumatore**: AI assistant per generazione codice PLC

---

## Struttura Output Richiesta

```
scl-reference/
├── SKILL.md              ← File principale con regole e indice
├── index.json            ← Lookup rapido nome_funzione → file
├── sources.md            ← Fonti consultate (OBBLIGATORIO)
├── incomplete.md         ← Funzioni non trovate (se necessario)
└── functions/
    │
    ├── ## BASIC INSTRUCTIONS ##
    ├── math.json
    ├── comparison.json
    ├── conversion.json
    ├── move.json
    ├── bitwise.json
    ├── timers.json
    ├── counters.json
    ├── triggers.json
    ├── program_control.json
    │
    ├── ## EXTENDED INSTRUCTIONS ##
    ├── string.json
    ├── date_time.json
    ├── alarms.json
    ├── interrupts.json
    ├── diagnostics.json
    ├── data_block.json
    ├── addressing.json
    ├── distributed_io.json
    ├── profienergy.json
    ├── recipe_datalog.json
    │
    ├── ## TECHNOLOGY INSTRUCTIONS ##
    ├── pid_control.json
    ├── motion_control.json
    ├── high_speed_counter.json
    │
    ├── ## COMMUNICATION INSTRUCTIONS ##
    ├── s7_communication.json
    ├── open_user_comm.json
    │
    └── ## SAFETY INSTRUCTIONS ##
        └── safety.json
```

---

## Categorie di Funzioni da Documentare

### BASIC INSTRUCTIONS

| Categoria | File | Funzioni da includere |
|-----------|------|----------------------|
| **Math** | math.json | ADD, SUB, MUL, DIV, MOD, NEG, ABS, MIN, MAX, LIMIT, SQR, SQRT, LN, EXP, POW, LOG, SIN, COS, TAN, ASIN, ACOS, ATAN, ATAN2, FRAC, EXPT |
| **Comparison** | comparison.json | CMP (==, <>, <, >, <=, >=), EQ, NE, LT, LE, GT, GE, IN_RANGE, OUT_RANGE, OK, NOT_OK, SEL, MUX, DEMUX, MOVE_IF |
| **Conversion** | conversion.json | CONVERT, ROUND, TRUNC, CEIL, FLOOR, SCALE_X, NORM_X, SCALE, UNSCALE, TO_* (tutte le varianti), *_TO_* (tutte le varianti), BOOL_TO_*, *_TO_BOOL |
| **Move** | move.json | MOVE, MOVE_BLK, UMOVE_BLK, FILL_BLK, UFILL_BLK, MOVE_BLK_VARIANT, Serialize, Deserialize, SCATTER, GATHER, SWAP, VariantGet, VariantPut, CountOfElements, TypeOf, TypeOfElements, IS_NULL, NOT_NULL, IS_ARRAY |
| **Bitwise** | bitwise.json | AND, OR, XOR, NOT, SHL, SHR, ROL, ROR, SWAP, DECO, ENCO, SET_BIT, RESET_BIT, SET_BF, RESET_BF, INVERT |
| **Timers** | timers.json | TP, TON, TOF, TONR (IEC Timers), RT, PT (Reset/Preset Timer), S_PULSE, S_PEXT, S_ODT, S_ODTS, S_OFFDT (S5 Timer legacy) |
| **Counters** | counters.json | CTU, CTD, CTUD (IEC Counters), S_CU, S_CD (S5 Counter legacy) |
| **Triggers** | triggers.json | R_TRIG, F_TRIG, P_TRIG, N_TRIG |
| **Program Control** | program_control.json | IF/THEN/ELSE/ELSIF/END_IF, CASE/OF/END_CASE, FOR/TO/BY/DO/END_FOR, WHILE/DO/END_WHILE, REPEAT/UNTIL/END_REPEAT, CONTINUE, EXIT, RETURN, GOTO, JMP, JMPN, LABEL, RET, RUNTIME |

### EXTENDED INSTRUCTIONS

| Categoria | File | Funzioni da includere |
|-----------|------|----------------------|
| **String** | string.json | LEN, MAX_LEN, CONCAT, LEFT, RIGHT, MID, DELETE, INSERT, REPLACE, FIND, EQUAL, S_CONV, Strg_TO_Chars, Chars_TO_Strg, ATH, HTA, VAL_STRG, STRG_VAL, S_MOVE, IS_STRING |
| **Date/Time** | date_time.json | T_CONV, T_ADD, T_SUB, T_DIFF, T_COMBINE, T_EXTRACT, T_COMP, RD_SYS_T, WR_SYS_T, RD_LOC_T, WR_LOC_T, SET_TIMEZONE, TIME_TCK, DTL_TO_*, *_TO_DTL, LDT_TO_*, *_TO_LDT |
| **Alarms** | alarms.json | Program_Alarm, Gen_UsrMsg, Get_AlarmState, Ack_Alarms, Get_Alarm, Query_Alarm, Get_Err_ID, GetError, GetErrorID |
| **Interrupts** | interrupts.json | ATTACH, DETACH, DIS_AIRT, EN_AIRT, QRY_TINT, SRT_DINT, CAN_DINT, ACT_TINT, RE_TRIGR, SET_TINTL, SRT_SCLK, SRT_DCLK |
| **Diagnostics** | diagnostics.json | GET_DIAG, GET_NAME, LED, DeviceStates, ModuleStates, GET_LADDR, LOG_DIAG, Get_IM_Data, RD_DPARA, WR_DPARA, RD_ADDR, WR_ADDR, RDSYSST |
| **Data Block** | data_block.json | READ_DBL, WRIT_DBL, CREATE_DB, DELETE_DB, ATTR_DB, COMPRESS, READ_LITTLE, READ_BIG, WRITE_LITTLE, WRITE_BIG, PEEK, POKE, PEEK_BOOL, POKE_BOOL |
| **Addressing** | addressing.json | GetSymbolName, GetSymbolPath, GetInstancePath, GetBlockName, GetInstanceName, TypeOf, TypeOfDB, TypeOfElements, IS_NULL, VARIANT_TO_DB_ANY, DB_ANY_TO_VARIANT |
| **Distributed I/O** | distributed_io.json | RDREC, WRREC, DPRD_DAT, DPWR_DAT, RALRM, D_ACT_DP, DPNRM_DG, DPSYC_FR, GETIO, SETIO, GETIO_PART, SETIO_PART |
| **PROFIenergy** | profienergy.json | PE_START_END, PE_CMD, PE_DS3_Write_ET, PE_WOL, PE_I_DEV, PE_ENERGY_REPORT |
| **Recipe/DataLog** | recipe_datalog.json | RecipeExport, RecipeImport, RecipeRename, RecipeDelete, DataLogCreate, DataLogOpen, DataLogWrite, DataLogClose, DataLogDelete, DataLogClear, DataLogNewFile |

### TECHNOLOGY INSTRUCTIONS

| Categoria | File | Funzioni da includere |
|-----------|------|----------------------|
| **PID Control** | pid_control.json | PID_Compact, PID_3Step, PID_Temp, CONT_C, CONT_S, TCONT_CP, TCONT_S, PULSEGEN, RAMP_SOAK, Polyline, SplitRange, RampFunction, Filter_PT1, Filter_PT2, Filter_DT1 |
| **Motion Control** | motion_control.json | MC_Power, MC_Reset, MC_Home, MC_Halt, MC_Stop, MC_MoveAbsolute, MC_MoveRelative, MC_MoveVelocity, MC_MoveJog, MC_MoveSuperimposed, MC_SetPosition, MC_ReadAxisError, MC_ReadStatus, MC_ReadParameter, MC_WriteParameter, MC_GearIn, MC_GearOut, MC_GearInPos, MC_CamIn, MC_CamOut, MC_PhasingRelative, MC_PhasingAbsolute, MC_OffsetRelative, MC_OffsetAbsolute, MC_TorqueAdditive, MC_TorqueRange, MC_TorqueLimiting, MC_MeasuringInput, MC_OutputCam, MC_CamTrack, MC_CommandTable, MC_ChangeDynamic |
| **High Speed Counter** | high_speed_counter.json | CTRL_HSC, CTRL_HSC_EXT, High_Speed_Counter, SSI_Absolut_Encoder, CTRL_PWM, CTRL_PTO |

### COMMUNICATION INSTRUCTIONS

| Categoria | File | Funzioni da includere |
|-----------|------|----------------------|
| **S7 Communication** | s7_communication.json | GET, PUT, BSEND, BRCV, USEND, URCV, C_CNTRL, PRINT, READ_SEND_DATA, WRITE_SEND_DATA |
| **Open User Comm** | open_user_comm.json | TCON, TDISCON, TSEND, TRCV, TUSEND, TURCV, TSEND_C, TRCV_C, TMAIL_C, T_CONFIG, T_RESET, TM_MAIL, MB_CLIENT, MB_SERVER, MB_MASTER, MB_SLAVE |

### SAFETY INSTRUCTIONS (F-CPU)

| Categoria | File | Funzioni da includere |
|-----------|------|----------------------|
| **Safety** | safety.json | ESTOP1, SF_EDM, SF_GuardLocking, SF_GuardMonitoring, SF_MutingSeq, SF_MutingPar, SF_TwoHandControlTypeII, SF_TwoHandControlTypeIII, SF_EnableSwitch, SF_ModeSelector, SF_SLS, SF_SLA, SF_SLP, SF_SafelyLimitSpeed, ACK_GL, ACK_OP, DIAG_SF, F_SENDDP, F_RCVDP, F_SENDS7, F_RCVS7, FDBACK, TWO_HAND |

---

## Schema JSON per Ogni Funzione

Ogni funzione deve essere documentata con questo schema:

```json
{
  "name": "NOME_FUNZIONE",
  "signature": "Firma completa con parametri nominati",
  "parameters": [
    {
      "name": "PARAM_NAME",
      "type": "Tipo dati (INT, REAL, ANY, VARIANT, ecc.)",
      "direction": "IN | OUT | IN_OUT",
      "description": "Descrizione parametro",
      "optional": false
    }
  ],
  "return": {
    "type": "Tipo ritorno o VOID",
    "description": "Descrizione valore ritornato"
  },
  "description": "Descrizione breve della funzione (1-2 righe)",
  "example": "Esempio codice SCL funzionante",
  "anti_pattern": "Codice equivalente da NON usare (se applicabile)",
  "why_native": "Motivazione tecnica per preferire la funzione nativa",
  "mandatory": true,
  "notes": "Note aggiuntive, limitazioni, compatibilità",
  "see_also": ["FUNZIONI_CORRELATE"],
  "tia_version": "V20+"
}
```

### Campi Obbligatori
- `name`
- `signature`
- `return`
- `description`
- `example`
- `mandatory` (sempre `true` per funzioni con anti-pattern)

### Campi Opzionali
- `anti_pattern` → Solo se esiste un pattern comune da evitare
- `why_native` → Obbligatorio se `anti_pattern` è presente
- `parameters` → Dettaglio completo se la funzione è complessa
- `notes`, `see_also`

---

## Schema JSON per File di Categoria

```json
{
  "category": "Nome Categoria",
  "description": "Descrizione della categoria",
  "tia_version": "V20+",
  "source": "TIA Portal Help / Siemens Documentation",
  "functions": [
    { /* funzione 1 */ },
    { /* funzione 2 */ }
  ]
}
```

---

## Schema index.json

Lookup rapido per trovare il file corretto:

```json
{
  "LIMIT": "functions/math.json",
  "MIN": "functions/math.json",
  "MAX": "functions/math.json",
  "CONCAT": "functions/string.json",
  "R_TRIG": "functions/triggers.json",
  "_metadata": {
    "generated": "2025-XX-XX",
    "total_functions": 250,
    "categories": 21
  }
}
```

---

## Template SKILL.md

```markdown
# SCL Reference - TIA Portal V20+

## Quando usare questa skill

Leggi questa documentazione **PRIMA** di scrivere codice SCL se:
- Devi usare funzioni di sistema (LIMIT, CONCAT, MOVE_BLK, ecc.)
- Non conosci la sintassi esatta di una funzione TIA
- Stai scrivendo logica che potrebbe avere una funzione nativa equivalente
- Ricevi errori di compilazione su funzioni TIA

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
| Concatenazione stringhe con `+` | `CONCAT(IN1:=str1, IN2:=str2)` |
| Conversioni implicite | Funzioni `CONVERT` o `TO_*` esplicite |
| `IF val >= min AND val <= max THEN...` | `IN_RANGE(MIN:=min, VAL:=val, MAX:=max)` |
| Calcoli manuali su date/tempi | `T_ADD`, `T_SUB`, `T_DIFF`, `T_COMBINE` |
| Scaling manuale `(val - rawMin) * (engMax - engMin) / (rawMax - rawMin) + engMin` | `SCALE_X` e `NORM_X` |
| Loop con indice per copiare array | `MOVE_BLK` o `MOVE_BLK_VARIANT` |
| `val := val * (-1);` per negazione | `val := NEG(IN:=val);` |
| Check bit manuale con AND/shift | `SET_BIT`, `RESET_BIT`, `PEEK_BOOL` |

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

**Se anche solo una risposta è SÌ → RISCRIVI usando le funzioni di sistema.**

## Quick Index

### Basic Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| Math | functions/math.json | LIMIT, MIN, MAX, ABS, MOD, SQRT, SIN, COS, POW |
| Comparison | functions/comparison.json | SEL, MUX, IN_RANGE, CMP, EQ, NE, LT, GT |
| Conversion | functions/conversion.json | CONVERT, ROUND, CEIL, FLOOR, SCALE_X, NORM_X |
| Move | functions/move.json | MOVE, MOVE_BLK, Serialize, Deserialize, VariantGet |
| Bitwise | functions/bitwise.json | SHL, SHR, ROL, ROR, SWAP, SET_BIT, RESET_BIT |
| Timers | functions/timers.json | TP, TON, TOF, TONR |
| Counters | functions/counters.json | CTU, CTD, CTUD |
| Triggers | functions/triggers.json | R_TRIG, F_TRIG, P_TRIG, N_TRIG |
| Program Control | functions/program_control.json | IF, CASE, FOR, WHILE, RETURN, EXIT |

### Extended Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| String | functions/string.json | CONCAT, LEN, LEFT, RIGHT, MID, FIND, REPLACE |
| Date/Time | functions/date_time.json | T_CONV, T_ADD, T_SUB, T_DIFF, RD_SYS_T, WR_SYS_T |
| Alarms | functions/alarms.json | Program_Alarm, Gen_UsrMsg, Get_AlarmState |
| Interrupts | functions/interrupts.json | ATTACH, DETACH, DIS_AIRT, EN_AIRT |
| Diagnostics | functions/diagnostics.json | GET_DIAG, LED, DeviceStates, ModuleStates |
| Data Block | functions/data_block.json | READ_DBL, WRIT_DBL, CREATE_DB, PEEK, POKE |
| Addressing | functions/addressing.json | GetSymbolName, GetInstancePath, TypeOf |
| Distributed I/O | functions/distributed_io.json | RDREC, WRREC, DPRD_DAT, DPWR_DAT |
| PROFIenergy | functions/profienergy.json | PE_START_END, PE_CMD |
| Recipe/DataLog | functions/recipe_datalog.json | RecipeExport, DataLogWrite |

### Technology Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| PID Control | functions/pid_control.json | PID_Compact, PID_3Step, PID_Temp |
| Motion Control | functions/motion_control.json | MC_Power, MC_Home, MC_MoveAbsolute |
| High Speed Counter | functions/high_speed_counter.json | CTRL_HSC, High_Speed_Counter |

### Communication Instructions
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| S7 Communication | functions/s7_communication.json | GET, PUT, BSEND, BRCV |
| Open User Comm | functions/open_user_comm.json | TCON, TSEND, TRCV, MB_CLIENT, MB_SERVER |

### Safety Instructions (F-CPU)
| Categoria | File | Funzioni principali |
|-----------|------|---------------------|
| Safety | functions/safety.json | ESTOP1, SF_EDM, SF_GuardLocking, ACK_GL |

## Procedura di Consultazione

1. Identifica la categoria dalla tabella sopra
2. Leggi **SOLO** il file .json necessario (risparmio token)
3. Se la funzione non è nell'indice → cerca su support.industry.siemens.com
4. Se non esiste funzione nativa → implementa con IF/THEN documentando il motivo

## Fallback

Se una funzione non è documentata qui:
1. Cerca in `index.json`
2. Se non presente, usa web search su: `site:support.industry.siemens.com SCL <nome_funzione>`
3. Documenta la nuova funzione per uso futuro
```

---

## Esempio Completo: math.json

```json
{
  "category": "Math Functions",
  "description": "Funzioni matematiche standard per operazioni numeriche",
  "tia_version": "V20+",
  "source": "TIA Portal Help - SCL Instructions",
  "functions": [
    {
      "name": "LIMIT",
      "signature": "LIMIT(MN := <min>, IN := <value>, MX := <max>)",
      "parameters": [
        {"name": "MN", "type": "ANY_NUM", "direction": "IN", "description": "Valore minimo"},
        {"name": "IN", "type": "ANY_NUM", "direction": "IN", "description": "Valore da limitare"},
        {"name": "MX", "type": "ANY_NUM", "direction": "IN", "description": "Valore massimo"}
      ],
      "return": {"type": "Same as IN", "description": "Valore limitato tra MN e MX"},
      "description": "Limita il valore IN nell'intervallo [MN, MX]. Se IN < MN ritorna MN, se IN > MX ritorna MX.",
      "example": "speed := LIMIT(MN := 0, IN := rawSpeed, MX := 100);",
      "anti_pattern": "IF val < min THEN val := min; ELSIF val > max THEN val := max; END_IF;",
      "why_native": "Compilato in singola istruzione CPU, nessun branch prediction overhead",
      "mandatory": true,
      "see_also": ["MIN", "MAX"],
      "tia_version": "V20+"
    },
    {
      "name": "MIN",
      "signature": "MIN(IN1 := <value1>, IN2 := <value2>)",
      "parameters": [
        {"name": "IN1", "type": "ANY_NUM", "direction": "IN", "description": "Primo valore"},
        {"name": "IN2", "type": "ANY_NUM", "direction": "IN", "description": "Secondo valore"}
      ],
      "return": {"type": "Same as inputs", "description": "Il minore tra IN1 e IN2"},
      "description": "Ritorna il valore minore tra i due input.",
      "example": "smaller := MIN(IN1 := a, IN2 := b);",
      "anti_pattern": "IF a < b THEN result := a; ELSE result := b; END_IF;",
      "why_native": "Istruzione singola, evita branching",
      "mandatory": true,
      "see_also": ["MAX", "LIMIT"],
      "tia_version": "V20+"
    },
    {
      "name": "MAX",
      "signature": "MAX(IN1 := <value1>, IN2 := <value2>)",
      "parameters": [
        {"name": "IN1", "type": "ANY_NUM", "direction": "IN", "description": "Primo valore"},
        {"name": "IN2", "type": "ANY_NUM", "direction": "IN", "description": "Secondo valore"}
      ],
      "return": {"type": "Same as inputs", "description": "Il maggiore tra IN1 e IN2"},
      "description": "Ritorna il valore maggiore tra i due input.",
      "example": "larger := MAX(IN1 := a, IN2 := b);",
      "anti_pattern": "IF a > b THEN result := a; ELSE result := b; END_IF;",
      "why_native": "Istruzione singola, evita branching",
      "mandatory": true,
      "see_also": ["MIN", "LIMIT"],
      "tia_version": "V20+"
    },
    {
      "name": "ABS",
      "signature": "ABS(IN := <value>)",
      "parameters": [
        {"name": "IN", "type": "ANY_NUM", "direction": "IN", "description": "Valore di input"}
      ],
      "return": {"type": "Same as IN", "description": "Valore assoluto"},
      "description": "Ritorna il valore assoluto di IN.",
      "example": "distance := ABS(IN := delta);",
      "anti_pattern": "IF val < 0 THEN val := -val; END_IF;",
      "why_native": "Istruzione CPU nativa per valore assoluto",
      "mandatory": true,
      "tia_version": "V20+"
    },
    {
      "name": "MOD",
      "signature": "MOD(IN1 := <dividend>, IN2 := <divisor>)",
      "parameters": [
        {"name": "IN1", "type": "ANY_INT", "direction": "IN", "description": "Dividendo"},
        {"name": "IN2", "type": "ANY_INT", "direction": "IN", "description": "Divisore"}
      ],
      "return": {"type": "Same as inputs", "description": "Resto della divisione"},
      "description": "Ritorna il resto della divisione intera IN1/IN2.",
      "example": "remainder := MOD(IN1 := counter, IN2 := 10);",
      "mandatory": true,
      "notes": "IN2 non deve essere 0",
      "tia_version": "V20+"
    },
    {
      "name": "SQRT",
      "signature": "SQRT(IN := <value>)",
      "parameters": [
        {"name": "IN", "type": "REAL/LREAL", "direction": "IN", "description": "Valore di input (>= 0)"}
      ],
      "return": {"type": "Same as IN", "description": "Radice quadrata"},
      "description": "Calcola la radice quadrata di IN.",
      "example": "root := SQRT(IN := value);",
      "mandatory": true,
      "notes": "IN deve essere >= 0, altrimenti risultato indefinito",
      "tia_version": "V20+"
    },
    {
      "name": "SQR",
      "signature": "SQR(IN := <value>)",
      "parameters": [
        {"name": "IN", "type": "ANY_NUM", "direction": "IN", "description": "Valore di input"}
      ],
      "return": {"type": "Same as IN", "description": "Quadrato del valore"},
      "description": "Calcola il quadrato di IN (IN * IN).",
      "example": "squared := SQR(IN := value);",
      "anti_pattern": "result := value * value;",
      "why_native": "Più leggibile, stessa performance",
      "mandatory": true,
      "tia_version": "V20+"
    },
    {
      "name": "TRUNC",
      "signature": "TRUNC(IN := <value>)",
      "parameters": [
        {"name": "IN", "type": "REAL/LREAL", "direction": "IN", "description": "Valore floating point"}
      ],
      "return": {"type": "DINT/LINT", "description": "Parte intera (troncata verso zero)"},
      "description": "Tronca la parte decimale, ritorna la parte intera.",
      "example": "intPart := TRUNC(IN := 3.7);  // risultato: 3",
      "mandatory": true,
      "see_also": ["ROUND", "CEIL", "FLOOR"],
      "tia_version": "V20+"
    },
    {
      "name": "ROUND",
      "signature": "ROUND(IN := <value>)",
      "parameters": [
        {"name": "IN", "type": "REAL/LREAL", "direction": "IN", "description": "Valore floating point"}
      ],
      "return": {"type": "DINT/LINT", "description": "Valore arrotondato"},
      "description": "Arrotonda al numero intero più vicino.",
      "example": "rounded := ROUND(IN := 3.7);  // risultato: 4",
      "mandatory": true,
      "see_also": ["TRUNC", "CEIL", "FLOOR"],
      "tia_version": "V20+"
    }
  ]
}
```

---

## Esempio: triggers.json

```json
{
  "category": "Triggers and Timers",
  "description": "Rilevatori di fronte e temporizzatori IEC standard",
  "tia_version": "V20+",
  "source": "TIA Portal Help - SCL Instructions",
  "functions": [
    {
      "name": "R_TRIG",
      "signature": "R_TRIG (istanza function block)",
      "parameters": [
        {"name": "CLK", "type": "BOOL", "direction": "IN", "description": "Segnale da monitorare"},
        {"name": "Q", "type": "BOOL", "direction": "OUT", "description": "TRUE per un ciclo sul fronte di salita"}
      ],
      "return": {"type": "N/A (FB)", "description": "Usare output Q"},
      "description": "Rileva il fronte di salita (0→1) del segnale CLK. Q è TRUE per un solo ciclo.",
      "example": "#risingEdge(CLK := signal);\nIF #risingEdge.Q THEN\n    // Azione sul fronte\nEND_IF;",
      "anti_pattern": "IF NOT #prevSignal AND signal THEN... END_IF;\n#prevSignal := signal;",
      "why_native": "Gestione stato interno automatica, nessun rischio di dimenticare aggiornamento variabile",
      "mandatory": true,
      "notes": "Richiede istanza statica (VAR_STAT o campo di FB)",
      "see_also": ["F_TRIG"],
      "tia_version": "V20+"
    },
    {
      "name": "F_TRIG",
      "signature": "F_TRIG (istanza function block)",
      "parameters": [
        {"name": "CLK", "type": "BOOL", "direction": "IN", "description": "Segnale da monitorare"},
        {"name": "Q", "type": "BOOL", "direction": "OUT", "description": "TRUE per un ciclo sul fronte di discesa"}
      ],
      "return": {"type": "N/A (FB)", "description": "Usare output Q"},
      "description": "Rileva il fronte di discesa (1→0) del segnale CLK. Q è TRUE per un solo ciclo.",
      "example": "#fallingEdge(CLK := signal);\nIF #fallingEdge.Q THEN\n    // Azione sul fronte\nEND_IF;",
      "anti_pattern": "IF #prevSignal AND NOT signal THEN... END_IF;\n#prevSignal := signal;",
      "why_native": "Gestione stato interno automatica, codice più leggibile",
      "mandatory": true,
      "notes": "Richiede istanza statica",
      "see_also": ["R_TRIG"],
      "tia_version": "V20+"
    },
    {
      "name": "TON",
      "signature": "TON (istanza function block)",
      "parameters": [
        {"name": "IN", "type": "BOOL", "direction": "IN", "description": "Segnale di abilitazione"},
        {"name": "PT", "type": "TIME", "direction": "IN", "description": "Tempo di ritardo"},
        {"name": "Q", "type": "BOOL", "direction": "OUT", "description": "Output ritardato"},
        {"name": "ET", "type": "TIME", "direction": "OUT", "description": "Tempo trascorso"}
      ],
      "return": {"type": "N/A (FB)", "description": "Usare output Q e ET"},
      "description": "Timer On-Delay: Q diventa TRUE dopo che IN è stato TRUE per almeno PT.",
      "example": "#delayTimer(IN := startSignal, PT := T#5s);\nIF #delayTimer.Q THEN\n    // Azione dopo 5 secondi\nEND_IF;",
      "mandatory": true,
      "notes": "Reset immediato quando IN torna FALSE",
      "see_also": ["TOF", "TP", "TONR"],
      "tia_version": "V20+"
    },
    {
      "name": "TOF",
      "signature": "TOF (istanza function block)",
      "parameters": [
        {"name": "IN", "type": "BOOL", "direction": "IN", "description": "Segnale di abilitazione"},
        {"name": "PT", "type": "TIME", "direction": "IN", "description": "Tempo di ritardo off"},
        {"name": "Q", "type": "BOOL", "direction": "OUT", "description": "Output con ritardo allo spegnimento"},
        {"name": "ET", "type": "TIME", "direction": "OUT", "description": "Tempo trascorso"}
      ],
      "return": {"type": "N/A (FB)", "description": "Usare output Q e ET"},
      "description": "Timer Off-Delay: Q resta TRUE per PT dopo che IN è diventato FALSE.",
      "example": "#offDelayTimer(IN := signal, PT := T#3s);",
      "mandatory": true,
      "see_also": ["TON", "TP"],
      "tia_version": "V20+"
    },
    {
      "name": "TP",
      "signature": "TP (istanza function block)",
      "parameters": [
        {"name": "IN", "type": "BOOL", "direction": "IN", "description": "Segnale trigger"},
        {"name": "PT", "type": "TIME", "direction": "IN", "description": "Durata impulso"},
        {"name": "Q", "type": "BOOL", "direction": "OUT", "description": "Impulso output"},
        {"name": "ET", "type": "TIME", "direction": "OUT", "description": "Tempo trascorso"}
      ],
      "return": {"type": "N/A (FB)", "description": "Usare output Q e ET"},
      "description": "Pulse Timer: genera un impulso di durata PT sul fronte di salita di IN.",
      "example": "#pulseTimer(IN := trigger, PT := T#500ms);",
      "mandatory": true,
      "notes": "Non retriggerable durante l'impulso",
      "see_also": ["TON", "TOF"],
      "tia_version": "V20+"
    }
  ]
}
```

---

## Esempio: date_time.json

```json
{
  "category": "Date and Time Functions",
  "description": "Funzioni per manipolazione di date, orari e timestamp",
  "tia_version": "V20+",
  "source": "TIA Portal Help - Extended Instructions",
  "functions": [
    {
      "name": "T_ADD",
      "signature": "T_ADD(IN1 := <time1>, IN2 := <duration>)",
      "parameters": [
        {"name": "IN1", "type": "DATE/TOD/DT/DTL/LDT", "direction": "IN", "description": "Tempo base"},
        {"name": "IN2", "type": "TIME/LTIME", "direction": "IN", "description": "Durata da aggiungere"}
      ],
      "return": {"type": "Same as IN1", "description": "Tempo risultante"},
      "description": "Aggiunge una durata a un valore di tempo/data.",
      "example": "newTime := T_ADD(IN1 := currentDT, IN2 := T#1h30m);",
      "anti_pattern": "Calcolo manuale con conversioni e somme",
      "why_native": "Gestisce automaticamente overflow giorni/mesi/anni",
      "mandatory": true,
      "see_also": ["T_SUB", "T_DIFF"],
      "tia_version": "V20+"
    },
    {
      "name": "T_SUB",
      "signature": "T_SUB(IN1 := <time1>, IN2 := <duration>)",
      "parameters": [
        {"name": "IN1", "type": "DATE/TOD/DT/DTL/LDT", "direction": "IN", "description": "Tempo base"},
        {"name": "IN2", "type": "TIME/LTIME", "direction": "IN", "description": "Durata da sottrarre"}
      ],
      "return": {"type": "Same as IN1", "description": "Tempo risultante"},
      "description": "Sottrae una durata da un valore di tempo/data.",
      "example": "previousTime := T_SUB(IN1 := currentDT, IN2 := T#2d);",
      "mandatory": true,
      "see_also": ["T_ADD", "T_DIFF"],
      "tia_version": "V20+"
    },
    {
      "name": "T_DIFF",
      "signature": "T_DIFF(IN1 := <time1>, IN2 := <time2>)",
      "parameters": [
        {"name": "IN1", "type": "DATE/TOD/DT/DTL/LDT", "direction": "IN", "description": "Primo tempo"},
        {"name": "IN2", "type": "DATE/TOD/DT/DTL/LDT", "direction": "IN", "description": "Secondo tempo"}
      ],
      "return": {"type": "TIME/LTIME", "description": "Differenza tra i due tempi"},
      "description": "Calcola la differenza tra due valori di tempo/data.",
      "example": "elapsed := T_DIFF(IN1 := endTime, IN2 := startTime);",
      "anti_pattern": "Sottrazione manuale di componenti DTL",
      "why_native": "Gestisce correttamente giorni diversi, mesi, anni bisestili",
      "mandatory": true,
      "see_also": ["T_ADD", "T_SUB"],
      "tia_version": "V20+"
    },
    {
      "name": "T_COMBINE",
      "signature": "T_COMBINE(IN1 := <date>, IN2 := <time_of_day>)",
      "parameters": [
        {"name": "IN1", "type": "DATE", "direction": "IN", "description": "Data"},
        {"name": "IN2", "type": "TOD/LTOD", "direction": "IN", "description": "Ora del giorno"}
      ],
      "return": {"type": "DT/LDT", "description": "Data e ora combinati"},
      "description": "Combina una data e un'ora in un singolo timestamp.",
      "example": "timestamp := T_COMBINE(IN1 := myDate, IN2 := myTime);",
      "mandatory": true,
      "see_also": ["T_CONV"],
      "tia_version": "V20+"
    },
    {
      "name": "RD_SYS_T",
      "signature": "RD_SYS_T(OUT := <dtl_var>)",
      "parameters": [
        {"name": "OUT", "type": "DTL", "direction": "OUT", "description": "Variabile DTL per output"}
      ],
      "return": {"type": "INT", "description": "Codice errore (0 = OK)"},
      "description": "Legge l'ora di sistema della CPU (UTC).",
      "example": "retVal := RD_SYS_T(OUT := systemTime);",
      "mandatory": true,
      "notes": "Restituisce ora UTC, usare RD_LOC_T per ora locale",
      "see_also": ["WR_SYS_T", "RD_LOC_T"],
      "tia_version": "V20+"
    },
    {
      "name": "WR_SYS_T",
      "signature": "WR_SYS_T(IN := <dtl_var>)",
      "parameters": [
        {"name": "IN", "type": "DTL", "direction": "IN", "description": "Nuovo valore data/ora"}
      ],
      "return": {"type": "INT", "description": "Codice errore (0 = OK)"},
      "description": "Imposta l'ora di sistema della CPU.",
      "example": "retVal := WR_SYS_T(IN := newSystemTime);",
      "mandatory": true,
      "notes": "Richiede permessi appropriati",
      "see_also": ["RD_SYS_T", "WR_LOC_T"],
      "tia_version": "V20+"
    }
  ]
}
```

---

## Istruzioni per l'AI Agent

### Metodologia di lavoro

**La documentazione NON viene fornita direttamente.** L'agent deve:

1. **Cercare autonomamente** le informazioni sulle funzioni SCL
2. **Usare fonti online** affidabili (vedi elenco sotto)
3. **Documentare ogni fonte** utilizzata
4. **Segnalare lacune** se non trova informazioni complete

### Fonti da consultare (in ordine di priorità)

| Priorità | Fonte | URL base | Note |
|----------|-------|----------|------|
| 1 | **Siemens TIA Portal Information System (Online Help)** | https://docs.tia.siemens.cloud | Documentazione ufficiale V20, richiede navigazione JS |
| 2 | **Siemens Industry Support (PDF Manuals)** | https://support.industry.siemens.com | Cercare per numero documento o product ID |
| 3 | **Siemens Cache (PDF diretti)** | https://cache.industry.siemens.com | PDF scaricabili direttamente |
| 4 | **Comparison List S7-1200/1500** | cache.industry.siemens.com/dl/files/648/109797648/ | Documento A5E33285102 - Lista completa istruzioni |
| 5 | **Programming Guideline** | cache.industry.siemens.com/dl/files/040/90885040/ | Best practices SCL |
| 6 | Siemens Forum | https://support.industry.siemens.com/forum | Discussioni tecniche |
| 7 | PLC Academy / SolisPLC | https://www.solisplc.com | Tutorial ed esempi |
| 8 | Stack Overflow (tag: tia-portal, siemens, scl) | stackoverflow.com | Soluzioni community |

**Documenti chiave da scaricare:**
- `s71500_compare_table_en.pdf` - Lista completa istruzioni con compatibilità
- `81318674_Programming_guideline_DOC_v16_en.pdf` - Linee guida programmazione
- Manuals S7-1500 Automation System
- Function Manual PID Control, Motion Control

### Query di ricerca suggerite

Per ogni funzione, usare queste query in ordine:

```
1. site:cache.industry.siemens.com "<FUNCTION_NAME>" SCL S7-1500 PDF
2. site:support.industry.siemens.com "<FUNCTION_NAME>" TIA Portal instruction
3. "<FUNCTION_NAME>" SCL syntax parameters S7-1500
4. TIA Portal V20 "<FUNCTION_NAME>" example
```

**Esempi specifici:**
- Per LIMIT: `site:cache.industry.siemens.com "LIMIT" SCL math instruction`
- Per R_TRIG: `site:support.industry.siemens.com "R_TRIG" edge detection SCL`
- Per T_CONV: `TIA Portal "T_CONV" date time conversion S7-1500`

### REGOLA FONDAMENTALE

⛔ **VIETATO INVENTARE**

- Se non trovi la signature esatta di una funzione → **NON inventarla**
- Se non trovi i parametri → **segna come incompleto**
- Se non sei sicuro al 100% → **indica il livello di confidenza**
- Meglio un JSON incompleto che uno con informazioni false

### Output da produrre

1. Un file JSON per ogni categoria (schema sopra)
2. Un file `index.json` con mapping nome → file
3. Un file `SKILL.md` con template fornito (personalizzare se necessario)
4. **Un file `sources.md`** con tutte le fonti consultate
5. **Un file `incomplete.md`** (se necessario) con le funzioni non trovate

### Formato sources.md

```markdown
# Fonti Documentazione SCL

## Fonti principali utilizzate
- [Titolo pagina](URL completo) - Funzioni documentate: X, Y, Z
- [Titolo pagina](URL completo) - Funzioni documentate: A, B, C

## Data consultazione
YYYY-MM-DD

## Note
Eventuali osservazioni sulla qualità/completezza delle fonti
```

### Formato incomplete.md (se necessario)

```markdown
# Funzioni Non Documentate

## Funzioni mancanti per categoria

### math.json
- `NOME_FUNZIONE` - Motivo: non trovata documentazione ufficiale

### string.json
- `NOME_FUNZIONE` - Motivo: signature incerta, trovate versioni contrastanti

## Richiesta
Per completare la documentazione, fornire manuale/help per:
- Lista funzioni mancanti
```

### Regole di generazione

1. **Completezza**: ogni funzione deve avere almeno i campi obbligatori
2. **Anti-pattern**: identificare e documentare per tutte le funzioni dove esiste un'alternativa IF/THEN comune
3. **Esempi**: devono essere codice SCL valido e compilabile - **verificare sintassi da fonti ufficiali**
4. **Consistenza**: usare sempre parametri nominati (`:=`) negli esempi
5. **Tipi**: usare i nomi tipo TIA (INT, DINT, REAL, LREAL, ANY_NUM, ecc.)
6. **Citazione**: per ogni funzione, la fonte deve essere tracciabile

### Livello di impegno richiesto

L'agent deve **impegnarsi al massimo** per completare tutti i JSON:

- ✅ Cercare ogni funzione su **almeno 2-3 fonti diverse**
- ✅ Se una fonte non ha info, **cercare su altre**
- ✅ Usare **query di ricerca multiple** (es: "SCL LIMIT function", "TIA Portal LIMIT instruction", "S7-1500 LIMIT")
- ✅ Consultare **forum e discussioni** se la documentazione ufficiale è incompleta
- ✅ **Non arrendersi** alla prima ricerca fallita

### Validazione output

- [ ] Ogni JSON è valido (parsabile)
- [ ] Ogni funzione ha `name`, `signature`, `description`, `example`
- [ ] `index.json` contiene tutte le funzioni di tutti i file
- [ ] `SKILL.md` contiene la tabella indice aggiornata
- [ ] Nessun esempio contiene anti-pattern
- [ ] **`sources.md` presente con tutte le fonti**
- [ ] **Nessuna informazione inventata**
- [ ] **`incomplete.md` presente se ci sono lacune**

---

## Note Finali

Questa documentazione sarà usata da un AI per generare codice PLC di produzione. La qualità e precisione della sintassi sono critiche:
- Un errore nella signature = errore di compilazione per l'utente
- Un anti-pattern non documentato = codice subottimale generato

Priorità: **correttezza > completezza**. Meglio documentare meno funzioni correttamente che molte con errori.
