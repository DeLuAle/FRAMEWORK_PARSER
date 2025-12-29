---
name: scl-syntax
description: |
  SCL (Structured Control Language) syntax assistance for Siemens TIA Portal V20+ PLC programming.
  Generates error-free SCL code using native functions from a 222-function database.
  Bilingual support (Italian/English). Works with S7-1200/S7-1500 controllers.
  
  Use this skill when:
  - Generating SCL code for Siemens PLCs
  - Creating Function Blocks (FB) or Functions (FC)
  - Working with TIA Portal SCL programming
  - Reviewing or debugging SCL code
  - Questions about SCL syntax, functions, or best practices
  - Converting logic to SCL from other languages
  - Implementing timers, counters, state machines in SCL
---

# SCL Syntax Skill

Assistenza sintassi SCL per programmazione PLC Siemens TIA Portal V20+.
SCL syntax assistance for Siemens TIA Portal V20+ PLC programming.

---

## 🚨 REGOLE CRITICHE NON NEGOZIABILI / CRITICAL NON-NEGOTIABLE RULES

### R1: Parametri Nominati SEMPRE / Named Parameters ALWAYS

**IT**: Tutti i parametri di funzioni native DEVONO usare sintassi nominata con `:=` per input e `=>` per output.

**EN**: All native function parameters MUST use named parameter syntax with `:=` for inputs and `=>` for outputs.

```scl
// ✅ CORRETTO / CORRECT
result := LIMIT(MN := 0, IN := value, MX := 100);
#Motor1(Start := signal, Running => output);

// ❌ SBAGLIATO / WRONG - ERRORE COMPILAZIONE!
result := LIMIT(0, value, 100);
#Motor1(signal, output);
```

---

### R2: Istanze Statiche per Timer/Counter/Trigger / Persistent Storage

**IT**: Timer, Counter, Trigger DEVONO essere dichiarati in `VAR` (FB) o `VAR_STAT`, MAI in `VAR_TEMP`. VAR_TEMP si resetta ogni ciclo PLC!

**EN**: Timer, Counter, Trigger MUST be declared in `VAR` (FB) or `VAR_STAT`, NEVER in `VAR_TEMP`. VAR_TEMP resets every PLC cycle!

```scl
// ❌ SBAGLIATO / WRONG
VAR_TEMP
    myTimer : TON;  // ERRORE: timer si resetta ogni ciclo!
END_VAR

// ✅ CORRETTO / CORRECT
VAR
    myTimer : TON;  // OK: memoria persistente tra cicli
END_VAR
```

---

### R3: ELSIF non ELSEIF / Use ELSIF Not ELSEIF

**IT**: In SCL si usa `ELSIF`, non `ELSEIF` come in altri linguaggi.

**EN**: In SCL use `ELSIF`, not `ELSEIF`.

```scl
// ✅ CORRETTO / CORRECT
IF temp < 0 THEN
    state := 'FROZEN';
ELSIF temp < 100 THEN    // ELSIF!
    state := 'LIQUID';
ELSE
    state := 'GAS';
END_IF;
```

---

### R4: Assegnazione := vs Output =>

**IT**: Usa `:=` per input, `=>` per output quando chiami Function Block.

**EN**: Use `:=` for inputs, `=>` for outputs when calling Function Block.

```scl
// ✅ CORRETTO / CORRECT
#Motor1(
    Start := startButton,      // IN: usa :=
    Speed := speedValue,       // IN: usa :=
    Running => motorStatus,    // OUT: usa =>
    Error => errorFlag         // OUT: usa =>
);
```

---

### R5: FC vs FB / Functions vs Function Blocks

**IT**:
- **FC (Function)**: Per logica stateless (calcoli, trasformazioni)
- **FB (Function Block)**: Per logica stateful con memoria persistente (motori, valvole, sequenze)

**EN**:
- **FC (Function)**: For stateless logic (calculations, transformations)
- **FB (Function Block)**: For stateful logic with persistent memory (motors, valves, sequences)

---

## Decision Tree: FC vs FB

```
Hai bisogno di memoria persistente? / Need persistent memory?
├─ NO → Usa FC / Use FC
│  └─ Esempi: calcoli, conversioni, media, controlli
│     Examples: calculations, conversions, averaging, validations
│
└─ SI → Usa FB / Use FB
   └─ Esempi: motori, timer, sequenze, state machine
      Examples: motors, timers, sequences, state machines
```

---

## Workflow in 3 Passi / 3-Step Workflow

**STEP 1**: Identifica tipo blocco / Identify block type
- Logica ciclica senza stato → FC (Function) / Stateless logic → FC
- Controllo con memoria (motori, valvole, sequenze) → FB (Function Block) / Stateful control → FB
- Dati globali → DB (Data Block) o PLC Tags

**STEP 2**: Consulta funzioni native / Check native functions
- **Core Functions**: Per funzioni comuni (LIMIT, MIN, MAX, TON, CONCAT, ecc.), consulta `scl-reference/core-functions.md`
- **Extended Functions**: Per 192 funzioni aggiuntive, Claude legge automaticamente JSON database in `scl-reference/functions/`
- **Usage Examples**: Vedi `scl-reference/USAGE_EXAMPLE.md` per esempi pratici

**STEP 3**: Valida con checklist / Validate with checklist
- Parametri nominati ✓
- Timer in VAR (non VAR_TEMP) ✓
- ELSIF (non ELSEIF) ✓
- Consulta `scl-reference/anti-patterns.md` per errori comuni da evitare

---

## 📋 Template Blocchi Standard / Standard Block Templates

### Template FC (Function)

```scl
FUNCTION "Calculate_Average" : REAL
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_INPUT
    values : Array[0..9] of Real;    // Array di valori
    count : Int;                      // Numero elementi
END_VAR

VAR_TEMP
    sum : Real;                       // Somma temporanea
    i : Int;                          // Indice loop
END_VAR

BEGIN
    // Validazione input / Input validation
    IF count <= 0 OR count > 10 THEN
        #Calculate_Average := 0.0;
        RETURN;
    END_IF;

    // Calcolo media / Calculate average
    sum := 0.0;
    FOR i := 0 TO count - 1 DO
        sum := sum + values[i];
    END_FOR;

    // Ritorna risultato / Return result
    #Calculate_Average := sum / TO_REAL(count);
END_FUNCTION
```

---

### Template FB (Function Block - State Machine)

```scl
FUNCTION_BLOCK "Motor_Control"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 0.1

VAR_INPUT
    Start : Bool;           // Segnale avvio
    Stop : Bool;            // Segnale stop
    SpeedSetpoint : Real;   // Velocità richiesta
END_VAR

VAR_OUTPUT
    Running : Bool;         // Motore in marcia
    ActualSpeed : Real;     // Velocità attuale
    Alarm : Bool;           // Flag allarme
END_VAR

VAR
    State : Int;            // 0=Idle, 1=Starting, 2=Running
    StartTimer : TON;       // Timer avvio (DEVE essere in VAR!)
    ErrorCount : Int;
END_VAR

VAR_TEMP
    tempSpeed : Real;       // Variabile di lavoro temporanea
END_VAR

BEGIN
    // State machine
    CASE State OF
        0: // Idle
            IF Start AND NOT Stop THEN
                State := 1;
                #StartTimer(IN := FALSE, PT := T#0ms);  // Reset timer
            END_IF;
            Running := FALSE;

        1: // Starting
            #StartTimer(IN := TRUE, PT := T#2s);
            IF #StartTimer.Q THEN
                State := 2;
                Running := TRUE;
            END_IF;
            IF Stop THEN
                State := 0;
            END_IF;

        2: // Running
            Running := TRUE;
            // Limita velocità tra 0 e 3000 RPM
            ActualSpeed := LIMIT(
                MN := 0.0,
                IN := SpeedSetpoint,
                MX := 3000.0
            );
            IF Stop THEN
                State := 0;
                Running := FALSE;
            END_IF;
    END_CASE;

    // Gestione allarmi / Alarm handling
    IF ActualSpeed > 3000.0 * 1.1 THEN
        Alarm := TRUE;
        ErrorCount := ErrorCount + 1;
    END_IF;
END_FUNCTION_BLOCK
```

---

## 🔄 Control Structures / Strutture di Controllo

### IF-ELSIF-ELSE Conditional

```scl
// Condizionale semplice / Simple conditional
IF temperature > 100.0 THEN
    alarm := TRUE;
    shutdownHeater();
END_IF;

// Condizionale completo / Full conditional
IF pressure < 1.0 THEN
    status := 'LOW';
ELSIF pressure > 10.0 THEN
    status := 'HIGH';
ELSE
    status := 'NORMAL';
END_IF;

// Condizioni combinate / Combined conditions
IF (temp > 80.0) AND (pressure > 5.0) OR emergencyStop THEN
    shutdown := TRUE;
END_IF;
```

---

### CASE Statement (per State Machine)

```scl
// Ottimo per state machine e selezione multi-valore
CASE state OF
    0: // Idle
        Running := FALSE;
        IF StartCommand THEN
            state := 1;
        END_IF;

    1: // Starting
        Running := TRUE;
        IF startupComplete THEN
            state := 2;
        END_IF;

    2: // Running
        processControl();
        IF StopCommand THEN
            state := 3;
        END_IF;

    3: // Stopping
        IF shutdownComplete THEN
            state := 0;
        END_IF;

    ELSE
        // Stato invalido - vai in error
        state := 99;
        errorFlag := TRUE;
END_CASE;
```

---

### FOR Loop

```scl
// Loop con contatore crescente / Ascending counter loop
FOR i := 0 TO 9 DO
    temperatures[i] := readSensor(i);
END_FOR;

// Loop con contatore decrescente / Descending counter loop
FOR i := 10 DOWNTO 0 DO
    buffer[i] := 0;
END_FOR;

// Loop con incremento custom / Custom increment
FOR i := 0 TO 100 BY 5 DO
    // i = 0, 5, 10, 15, ..., 100
    processValue(i);
END_FOR;

// EXIT per uscita anticipata / Early exit
FOR i := 0 TO 99 DO
    IF data[i] = targetValue THEN
        foundIndex := i;
        EXIT;  // Esce dal loop
    END_IF;
END_FOR;

// CONTINUE per saltare iterazione / Skip iteration
FOR i := 0 TO 99 DO
    IF data[i] < 0 THEN
        CONTINUE;  // Salta al prossimo i
    END_IF;
    processPositiveValue(data[i]);
END_FOR;
```

---

### WHILE Loop

```scl
// Pre-test (condizione prima esecuzione)
WHILE counter < 100 DO
    counter := counter + 1;
    process(counter);
END_WHILE;

// Con EXIT
WHILE TRUE DO
    data := readData();
    IF data = STOP_MARKER THEN
        EXIT;
    END_IF;
    processData(data);
END_WHILE;
```

---

### REPEAT Loop

```scl
// Post-test (esegue almeno una volta)
REPEAT
    counter := counter + 1;
    value := readSensor();
UNTIL (value > threshold) OR (counter >= maxRetries)
END_REPEAT;

// ⚠️ ATTENZIONE / WARNING: REPEAT termina quando condizione è TRUE
// (opposto di WHILE che continua quando TRUE)
```

---

## 📚 Reference Files / File di Riferimento

### Quando Consultare i File / When to Consult Files

**Per funzioni native comuni (LIMIT, MIN, MAX, TON, CONCAT, ecc.)**:
→ Leggi `scl-reference/core-functions.md`
- Contiene le 30 funzioni più usate con esempi pratici
- Firme complete, parametri, use cases

**Per errori comuni da evitare**:
→ Leggi `scl-reference/anti-patterns.md`
- Catalogo di 15+ anti-pattern con soluzioni
- Errori di performance e correttezza
- Comparazioni corretto vs sbagliato

**Per tipi di dati (Int, Real, String, Array, Struct, ecc.)**:
→ Leggi `scl-reference/data-types.md`
- Reference completa tipi elementari e complessi
- Conversioni di tipo
- Best practices allocazione memoria

**Per funzioni oltre le Core 30**:
→ Claude consulta automaticamente i JSON database in `scl-reference/functions/`
- 192 funzioni aggiuntive organizzate per categoria
- Math, Comparison, Conversion, String, Move, Bitwise, Timers, Counters, Triggers
- Lookup automatico via `index.json`

**Per esempi pratici d'uso**:
→ Leggi `scl-reference/USAGE_EXAMPLE.md`
- Esempi completi di FC e FB
- Pattern comuni implementati correttamente

---

## Database Funzioni / Function Database

**Struttura Database**:
```
scl-reference/functions/
├── index.json           # Indice completo 222 funzioni
├── math.json           # Funzioni matematiche avanzate
├── comparison.json     # Comparazioni e selezioni
├── conversion.json     # Conversioni di tipo
├── string.json         # Manipolazione stringhe
├── move.json           # Trasferimento dati
├── bitwise.json        # Operazioni bitwise
├── timers.json         # Timer avanzati
├── counters.json       # Contatori
└── triggers.json       # Trigger eventi
```

**Processo Lookup Automatico**:
1. Claude legge `index.json` per identificare categoria funzione
2. Legge il file JSON specifico della categoria
3. Estrae definizione completa con parametri ed esempi
4. Formatta risposta seguendo stile Core Functions

---

## ✅ Self-Check Pre-Commit / Checklist Validazione

Prima di finalizzare il codice SCL, verifica tutti questi punti:

- [ ] **Parametri Nominati**: Tutti i parametri funzioni native usano `:=` (IN) e `=>` (OUT)
- [ ] **Storage Timer**: Timer/Counter/Trigger sono in `VAR` (FB) o `VAR_STAT`, MAI in `VAR_TEMP`
- [ ] **ELSIF Syntax**: Usato `ELSIF` (non `ELSEIF`) nelle condizioni
- [ ] **Funzioni Native**: Consultate core-functions.md, nessuna reimplementazione di LIMIT, MIN, MAX, ecc.
- [ ] **Edge Detection**: Usato R_TRIG/F_TRIG (non fronte manuale)
- [ ] **Array Operations**: Usato MOVE_BLK/FILL_BLK (non loop FOR per copia/riempimento)
- [ ] **String Operations**: Usato CONCAT (non operatore +)
- [ ] **Input Validation**: Controlli su range input e valori validi
- [ ] **Error Handling**: Gestione allarmi/errori appropriata
- [ ] **Naming**: Variabili con nomi descrittivi (non `i`, `x`, `temp` come nomi finali)
- [ ] **Comments**: Commenti su logica complessa o non ovvia
- [ ] **Block Type**: FC per logica stateless, FB per logica stateful
- [ ] **Anti-Patterns**: Controllato anti-patterns.md per evitare errori comuni

---

## 📝 Quick Reference / Riferimento Rapido

**Keywords SCL**:
- `FUNCTION` / `FUNCTION_BLOCK` - Definisci blocco
- `VAR` / `VAR_INPUT` / `VAR_OUTPUT` / `VAR_TEMP` - Sezioni dichiarazione
- `BEGIN` / `END_FUNCTION` / `END_FUNCTION_BLOCK` - Delimitatori
- `IF` / `ELSIF` / `ELSE` / `END_IF` - Condizionali
- `CASE` / `OF` / `END_CASE` - Switch statement
- `FOR` / `TO` / `DOWNTO` / `BY` / `END_FOR` - Loop enumerativo
- `WHILE` / `END_WHILE` - Loop pre-test
- `REPEAT` / `UNTIL` / `END_REPEAT` - Loop post-test
- `EXIT` / `CONTINUE` - Controllo loop
- `RETURN` - Uscita funzione

**Operators**:
- `:=` - Assignment / Assegnazione input
- `=>` - Output parameter / Parametro output
- `=` - Comparison / Confronto
- `<>` - Not equal / Diverso
- `AND` / `OR` / `NOT` - Logical operators
- `&` / `|` / `XOR` - Bitwise operators

---

**Versione Skill / Skill Version**: 2.0  
**Target**: TIA Portal V20+ / S7-1500 / S7-1200  
**Standard**: IEC 61131-3 SCL  
**Linguaggio / Language**: Bilingual (Italian + English)  
**Architettura / Architecture**: Progressive Disclosure (Core in SKILL.md, Details in references/)
