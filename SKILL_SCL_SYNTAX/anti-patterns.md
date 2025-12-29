# SCL Anti-Pattern Catalog

Errori comuni e come evitarli / Common mistakes and how to avoid them.

---

## AP1: Reimplementazione LIMIT

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
IF val < min THEN
    val := min;
ELSIF val > max THEN
    val := max;
END_IF;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
val := LIMIT(MN := min, IN := val, MX := max);
```

**Perché / Why**: 3x più efficiente, codice più leggibile, ottimizzato dal compilatore.

**Impatto Performance**: Loop di clamping manuale richiede 3 confronti e 2 assegnazioni. LIMIT è singola istruzione CPU.

---

## AP2: Edge Detection Manuale / Manual Edge Detection

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
IF NOT prevSignal AND signal THEN
    // azione sul fronte
END_IF;
prevSignal := signal;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
VAR
    risingEdge : R_TRIG;
END_VAR

#risingEdge(CLK := signal);
IF #risingEdge.Q THEN
    // azione sul fronte
END_IF;
```

**Perché / Why**: 
- R_TRIG/F_TRIG sono native e affidabili
- Non perdono fronti durante scan veloci
- Codice più leggibile e manutenibile
- Gestione automatica dello stato precedente

**Rischio Manuale**: Con scan time variabile, edge detection manuale può perdere fronti rapidi.

---

## AP3: Loop per Copiare Array / Array Copy Loop

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
FOR i := 0 TO 99 DO
    destArray[i] := sourceArray[i];
END_FOR;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
MOVE_BLK(IN := sourceArray, COUNT := 100, OUT => destArray);
```

**Perché / Why**: 
- MOVE_BLK è ottimizzata a livello sistema
- Trasferimento DMA quando disponibile
- ~10-20x più veloce del loop FOR
- Codice più chiaro e intenzionale

**Benchmark**: 
- Loop FOR (1000 elementi): ~2-3 ms
- MOVE_BLK (1000 elementi): ~0.2 ms

---

## AP4: Scaling Manuale / Manual Scaling

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
scaled := (rawValue - rawMin) * (engMax - engMin) / (rawMax - rawMin) + engMin;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
scaled := SCALE_X(MIN := 0.0, VALUE := rawValue, MAX := 100.0);

// O per range custom
scaled := NORM_X(MIN := rawMin, VALUE := rawValue, MAX := rawMax);
scaledEng := SCALE_X(MIN := engMin, VALUE := scaled, MAX := engMax);
```

**Perché / Why**: 
- SCALE_X ottimizzata per ADC/DAC
- Gestisce automaticamente range standard (0-27648 per analogici)
- Riduce errori di calcolo
- Più leggibile

**Nota**: SCALE_X presume input 0-100 (percentuale), NORM_X normalizza range custom.

---

## AP5: Timer in VAR_TEMP / Timer Storage Error

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG - CAUSA ERRORE GRAVE!
VAR_TEMP
    myTimer : TON;  // ERRORE: azzerato ogni ciclo!
END_VAR

BEGIN
    #myTimer(IN := trigger, PT := T#5s);
    // Q non sarà MAI TRUE perché timer si resetta ogni ciclo
END;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
VAR
    myTimer : TON;  // Memoria persistente tra cicli
END_VAR

BEGIN
    #myTimer(IN := trigger, PT := T#5s);
    IF #myTimer.Q THEN
        // Questo funziona correttamente
    END_IF;
END;
```

**Perché / Why**: 
- Timer deve mantenere stato interno (elapsed time, stato IN precedente)
- VAR_TEMP si resetta completamente ogni ciclo PLC (tipicamente 10-100ms)
- Risultato: timer non accumula mai tempo, Q rimane sempre FALSE

**Regola Generale**: Timer, Counter, Trigger, FB instances → VAR o VAR_STAT, MAI VAR_TEMP.

**Stessa regola per**:
- TON, TOF, TP
- CTU, CTD, CTUD
- R_TRIG, F_TRIG
- Istanze di qualsiasi FB custom

---

## AP6: String Concatenation con +

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
result := str1 + str2;  // Errore di compilazione! Non supportato in SCL
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
result := CONCAT(IN1 := str1, IN2 := str2);

// Per concatenare multiple stringhe
result := CONCAT(
    IN1 := CONCAT(IN1 := str1, IN2 := str2),
    IN2 := str3
);
```

**Perché / Why**: 
- SCL non supporta operatore `+` per stringhe (a differenza di linguaggi high-level)
- CONCAT è funzione nativa ottimizzata
- Supporta fino a String[254]

**Alternative per Multiple Stringhe**:
```scl
// Concatenare 4+ stringhe in modo più pulito
temp := CONCAT(IN1 := prefix, IN2 := name);
temp := CONCAT(IN1 := temp, IN2 := suffix);
result := CONCAT(IN1 := temp, IN2 := extension);
```

---

## AP7: Comparazione Float con = / Float Equality Comparison

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
IF temperature = 25.0 THEN
    // Potrebbe non attivarsi mai a causa errori floating point!
END_IF;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
VAR CONSTANT
    TOLERANCE : Real := 0.01;  // 1% tolerance
END_VAR

IF ABS(IN := temperature - 25.0) < TOLERANCE THEN
    // Confronto con tolleranza
END_IF;
```

**Perché / Why**: 
- Floating point ha errori di rappresentazione (IEEE 754)
- 0.1 + 0.2 ≠ 0.3 esattamente
- Confronto diretto con `=` è quasi sempre sbagliato

**Best Practice per Float**:
- Usa `>`, `<`, `>=`, `<=` quando possibile
- Se serve uguaglianza, usa confronto con tolleranza
- Per valori critici, considera usare Int scalati (es. mm invece di metri)

---

## AP8: Parametri Posizionali / Positional Parameters

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
result := LIMIT(0, value, 100);  // Errore compilazione!
#Motor1(startBtn, stopBtn, running);  // Errore compilazione!
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
result := LIMIT(MN := 0, IN := value, MX := 100);
#Motor1(Start := startBtn, Stop := stopBtn, Running => running);
```

**Perché / Why**: 
- SCL richiede sempre parametri nominati per funzioni native e FB
- Aumenta leggibilità: chiaro quale parametro è quale
- Previene errori da ordine sbagliato
- Permette di omettere parametri opzionali

**Nota**: `:=` per input, `=>` per output.

---

## AP9: Divisione Interi Senza Conversione / Integer Division Without Cast

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
VAR
    sum : Int := 100;
    count : Int := 3;
    average : Real;
END_VAR

average := sum / count;  // Risultato: 33.0 (troncato!)
// Divisione intera: 100 / 3 = 33, poi convertito a Real
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
average := TO_REAL(sum) / TO_REAL(count);  // Risultato: 33.333...
```

**Perché / Why**: 
- Divisione tra interi ritorna intero (troncato)
- Conversione a Real dopo divisione è troppo tardi
- Converti a Real PRIMA della divisione

**Regola**: Per divisione con risultato floating point, converti entrambi operandi a Real prima.

---

## AP10: Uso di ELSEIF invece di ELSIF

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
IF temp < 0 THEN
    state := 0;
ELSEIF temp < 100 THEN  // Errore compilazione! ELSEIF non esiste in SCL
    state := 1;
END_IF;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
IF temp < 0 THEN
    state := 0;
ELSIF temp < 100 THEN  // ELSIF! (no E)
    state := 1;
ELSE
    state := 2;
END_IF;
```

**Perché / Why**: 
- SCL usa `ELSIF` (derivato da Pascal/Ada)
- Altri linguaggi (Python, C, JavaScript) usano `ELSEIF` o `ELIF` o `else if`
- Errore comune per programmatori da altri linguaggi

**Reminder**: `ELSIF` in SCL, non `ELSEIF`, `ELIF`, `else if`.

---

## AP11: Modifica Output di FB senza chiamata / Modifying FB Output Without Call

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
VAR
    motor : FB_Motor;
END_VAR

motor.Running := TRUE;  // SBAGLIATO! Non si modifica output direttamente
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
#motor(Start := TRUE, Stop := FALSE);  // Usa input per controllare

IF #motor.Running THEN  // OK: leggere output
    // Motor sta girando
END_IF;
```

**Perché / Why**: 
- Output FB sono READ-ONLY dal chiamante
- Logica interna FB gestisce gli output
- Modificare output direttamente bypassa logica FB

**Regola**: 
- Input FB: scrivi per controllare (`:=`)
- Output FB: leggi per monitorare
- Non modificare mai output FB dall'esterno

---

## AP12: Nested IF invece di CASE / Nested IF Instead of CASE

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG (per state machine)
IF state = 0 THEN
    // Idle
ELSIF state = 1 THEN
    // Starting
ELSIF state = 2 THEN
    // Running
ELSIF state = 3 THEN
    // Stopping
ELSIF state = 4 THEN
    // Error
END_IF;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
CASE state OF
    0: // Idle
        // logica...
    1: // Starting
        // logica...
    2: // Running
        // logica...
    3: // Stopping
        // logica...
    4: // Error
        // logica...
    ELSE
        // Stato invalido
        state := 4;  // Vai in error
END_CASE;
```

**Perché / Why**: 
- CASE è più leggibile per state machine
- Compilatore genera jump table (O(1) invece di O(n))
- Più facile aggiungere/rimuovere stati
- ELSE cattura stati invalidi

**Quando Usare CASE**:
- State machine
- Selezione tra 3+ valori discreti
- Menu o modalità operative

**Quando Usare IF-ELSIF**:
- Condizioni complesse (non singolo valore)
- Range di valori
- Logica booleana combinata

---

## AP13: Reset Manuale Array / Manual Array Reset

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
FOR i := 0 TO 99 DO
    dataArray[i] := 0;
END_FOR;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
FILL_BLK(IN := 0, COUNT := 100, OUT => dataArray);

// O per valori non-zero
FILL_BLK(IN := initialValue, COUNT := 100, OUT => dataArray);
```

**Perché / Why**: 
- FILL_BLK ottimizzata a livello sistema
- ~10-15x più veloce di loop
- Codice più dichiarativo e chiaro

---

## AP14: Calcolo MIN/MAX con IF / Manual MIN/MAX with IF

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
IF sensor1 < sensor2 THEN
    minTemp := sensor1;
ELSE
    minTemp := sensor2;
END_IF;
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
minTemp := MIN(IN1 := sensor1, IN2 := sensor2);

// Per 3+ valori
minTemp := MIN(IN1 := sensor1, IN2 := sensor2, IN3 := sensor3);
```

**Perché / Why**: 
- MIN/MAX sono native e ottimizzate
- Supportano fino a 32 input
- Codice più compatto
- Singola istruzione CPU

---

## AP15: Ignorare Gestione Errori / Ignoring Error Handling

**Problema / Problem**:
```scl
// ❌ SBAGLIATO / WRONG
result := SQRT(IN := userInput);  // Se userInput < 0 → errore silente!
divisione := numerator / denominator;  // Se denominator = 0 → crash!
```

**Soluzione / Solution**:
```scl
// ✅ CORRETTO / CORRECT
IF userInput >= 0.0 THEN
    result := SQRT(IN := userInput);
ELSE
    result := 0.0;
    errorFlag := TRUE;
END_IF;

IF denominator <> 0 THEN
    divisione := numerator / denominator;
ELSE
    divisione := 0.0;
    divisionByZeroError := TRUE;
END_IF;
```

**Perché / Why**: 
- Input validation previene errori runtime
- Comportamento definito in condizioni anomale
- Safety: macchina non crasha su input invalido

**Best Practice Input Validation**:
1. Valida SEMPRE input da HMI/SCADA
2. Valida input da sensori (range fisico)
3. Valida divisori prima divisione
4. Valida array index prima accesso

---

## Quick Reference Anti-Patterns

| Anti-Pattern | Usa Invece | Motivo |
|--------------|------------|--------|
| IF MIN/MAX manual | MIN()/MAX() | Native ottimizzate |
| IF LIMIT manual | LIMIT() | Singola istruzione CPU |
| Edge detection manual | R_TRIG/F_TRIG | Affidabile, non perde fronti |
| Array copy FOR loop | MOVE_BLK | 10-20x più veloce |
| Array fill FOR loop | FILL_BLK | 10-15x più veloce |
| Timer in VAR_TEMP | Timer in VAR | VAR_TEMP si resetta ogni ciclo |
| String + operator | CONCAT() | + non supportato per stringhe |
| Float equality `=` | ABS(a-b) < tol | Floating point impreciso |
| Parametri posizionali | Parametri nominati | Richiesto da SCL |
| Integer division | TO_REAL() prima | Previene troncamento |
| ELSEIF | ELSIF | Sintassi SCL corretta |
| Nested IF (state) | CASE OF | Più leggibile, più veloce |

