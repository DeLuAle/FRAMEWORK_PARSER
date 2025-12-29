# SCL Core 30 Functions Reference

Funzioni native Siemens più utilizzate con esempi pratici.

---

## MATH FUNCTIONS (6 funzioni)

### 1. LIMIT - Limitazione Valore / Value Limiting

**Firma / Signature**: `result := LIMIT(MN := <min>, IN := <value>, MX := <max>);`

**Parametri / Parameters**:
- `MN` (IN: ANY_NUM) - Valore minimo / Minimum value
- `IN` (IN: ANY_NUM) - Valore da limitare / Value to limit
- `MX` (IN: ANY_NUM) - Valore massimo / Maximum value
- **Ritorno / Return**: ANY_NUM - Valore limitato tra [MN, MX]

**Descrizione / Description**:
Limita il valore IN nell'intervallo [MN, MX]. Se IN < MN ritorna MN, se IN > MX ritorna MX, altrimenti ritorna IN.

**Esempio / Example**:
```scl
// Limita velocità tra 0 e 100 RPM / Limit speed between 0-100 RPM
speed := LIMIT(MN := 0.0, IN := rawSpeed, MX := 100.0);
```

**Anti-Pattern**:
```scl
// ❌ NON FARE / DON'T DO:
IF val < min THEN
    val := min;
ELSIF val > max THEN
    val := max;
END_IF;

// ✅ USARE / USE:
val := LIMIT(MN := min, IN := val, MX := max);
```

**Perché Nativa / Why Native**: Singola istruzione CPU, più efficiente che 3 condizioni.

---

### 2. MIN - Valore Minimo / Minimum Value

**Firma / Signature**: `minValue := MIN(IN1 := <v1>, IN2 := <v2>, ...);`

**Parametri / Parameters**:
- `IN1..IN32` (IN: ANY_NUM) - Valori da confrontare (min 2, max 32) / Values to compare
- **Ritorno / Return**: ANY_NUM - Valore minimo tra tutti gli input

**Descrizione / Description**:
Ritorna il valore più piccolo tra 2-32 input. Supporta Int, DInt, Real, LReal.

**Esempio / Example**:
```scl
// Trova temperatura minima tra 3 sensori
tempMin := MIN(IN1 := sensor1, IN2 := sensor2, IN3 := sensor3);
```

---

### 3. MAX - Valore Massimo / Maximum Value

**Firma / Signature**: `maxValue := MAX(IN1 := <v1>, IN2 := <v2>, ...);`

**Parametri / Parameters**:
- `IN1..IN32` (IN: ANY_NUM) - Valori da confrontare (min 2, max 32) / Values to compare
- **Ritorno / Return**: ANY_NUM - Valore massimo tra tutti gli input

**Descrizione / Description**:
Ritorna il valore più grande tra 2-32 input. Complementare a MIN.

**Esempio / Example**:
```scl
// Trova pressione massima tra 4 sensori
pressMax := MAX(IN1 := p1, IN2 := p2, IN3 := p3, IN4 := p4);
```

---

### 4. ABS - Valore Assoluto / Absolute Value

**Firma / Signature**: `absValue := ABS(IN := <value>);`

**Parametri / Parameters**:
- `IN` (IN: ANY_NUM) - Valore da cui calcolare valore assoluto
- **Ritorno / Return**: ANY_NUM - Valore assoluto di IN

**Descrizione / Description**:
Ritorna |IN|. Se IN >= 0 ritorna IN, altrimenti ritorna -IN.

**Esempio / Example**:
```scl
// Calcola errore assoluto
error := ABS(IN := setpoint - actualValue);
```

---

### 5. SQRT - Radice Quadrata / Square Root

**Firma / Signature**: `sqrtValue := SQRT(IN := <value>);`

**Parametri / Parameters**:
- `IN` (IN: Real/LReal) - Valore da cui estrarre radice (deve essere >= 0)
- **Ritorno / Return**: Real/LReal - Radice quadrata di IN

**Descrizione / Description**:
Calcola √IN. Se IN < 0, ritorna 0 e setta bit di errore.

**Esempio / Example**:
```scl
// Calcola distanza euclidea
distance := SQRT(IN := dx*dx + dy*dy);
```

---

### 6. SQR - Quadrato / Square

**Firma / Signature**: `sqrValue := SQR(IN := <value>);`

**Parametri / Parameters**:
- `IN` (IN: ANY_NUM) - Valore da elevare al quadrato
- **Ritorno / Return**: ANY_NUM - IN²

**Descrizione / Description**:
Calcola IN². Più efficiente di `IN * IN`.

**Esempio / Example**:
```scl
// Calcola energia cinetica: E = (m * v²) / 2
energy := (mass * SQR(IN := velocity)) / 2.0;
```

---

## TIMER FUNCTIONS (3 funzioni)

### 7. TON - Timer On-Delay

**Firma / Signature**: `#myTimer(IN := <trigger>, PT := <preset>);`

**Parametri / Parameters**:
- `IN` (IN: Bool) - Segnale di start timer
- `PT` (IN: Time) - Preset time (es. T#5s)
- `Q` (OUT: Bool) - Output timer (TRUE quando elapsed >= PT)
- `ET` (OUT: Time) - Tempo trascorso / Elapsed time

**Descrizione / Description**:
Timer con ritardo all'attivazione. Q diventa TRUE dopo PT millisecondi da quando IN diventa TRUE.

**Esempio / Example**:
```scl
VAR
    startTimer : TON;  // DEVE essere in VAR!
END_VAR

// Avvia motore dopo 2 secondi da comando start
#startTimer(IN := startButton, PT := T#2s);
IF #startTimer.Q THEN
    motorRunning := TRUE;
END_IF;
```

**Timing Diagram**:
```
IN:  ___/‾‾‾‾‾‾‾‾‾‾\___
Q:   _______/‾‾‾‾‾‾\___
        |<-PT->|
```

---

### 8. TOF - Timer Off-Delay

**Firma / Signature**: `#myTimer(IN := <trigger>, PT := <preset>);`

**Parametri / Parameters**:
- `IN` (IN: Bool) - Segnale di controllo
- `PT` (IN: Time) - Preset time
- `Q` (OUT: Bool) - Output timer
- `ET` (OUT: Time) - Tempo trascorso

**Descrizione / Description**:
Timer con ritardo alla disattivazione. Q rimane TRUE per PT millisecondi dopo che IN diventa FALSE.

**Esempio / Example**:
```scl
// Mantieni ventola attiva 30s dopo spegnimento riscaldatore
#fanOffDelay(IN := heaterOn, PT := T#30s);
fanRunning := #fanOffDelay.Q;
```

**Timing Diagram**:
```
IN:  ‾‾‾\___________/‾‾
Q:   ‾‾‾‾‾‾‾\________/‾
          |<-PT->|
```

---

### 9. TP - Timer Pulse

**Firma / Signature**: `#myTimer(IN := <trigger>, PT := <preset>);`

**Parametri / Parameters**:
- `IN` (IN: Bool) - Segnale di trigger (fronte salita)
- `PT` (IN: Time) - Durata impulso
- `Q` (OUT: Bool) - Output impulso
- `ET` (OUT: Time) - Tempo trascorso

**Descrizione / Description**:
Genera impulso di durata fissa PT sul fronte di salita di IN. Q è TRUE per PT millisecondi.

**Esempio / Example**:
```scl
// Impulso 500ms su pressione pulsante
#buttonPulse(IN := buttonPressed, PT := T#500ms);
IF #buttonPulse.Q THEN
    incrementCounter();
END_IF;
```

**Timing Diagram**:
```
IN:  ___/‾‾‾‾‾‾‾‾‾‾‾‾‾\___
Q:   ___/‾‾‾‾\__________
        |<-PT->|
```

---

## COUNTER FUNCTIONS (3 funzioni)

### 10. CTU - Count Up

**Firma / Signature**: `#myCounter(CU := <pulse>, R := <reset>, PV := <preset>);`

**Parametri / Parameters**:
- `CU` (IN: Bool) - Count up input (conta sul fronte salita)
- `R` (IN: Bool) - Reset counter (azzera CV)
- `PV` (IN: Int) - Preset value (valore target)
- `Q` (OUT: Bool) - TRUE quando CV >= PV
- `CV` (OUT: Int) - Current value (conteggio attuale)

**Descrizione / Description**:
Conta fronti di salita su CU. Q diventa TRUE quando CV >= PV.

**Esempio / Example**:
```scl
VAR
    pieceCounter : CTU;  // Memoria persistente
END_VAR

// Conta 100 pezzi prodotti
#pieceCounter(
    CU := pieceSensor,
    R := resetButton,
    PV := 100
);

IF #pieceCounter.Q THEN
    batchComplete := TRUE;
END_IF;
```

---

### 11. CTD - Count Down

**Firma / Signature**: `#myCounter(CD := <pulse>, LD := <load>, PV := <preset>);`

**Parametri / Parameters**:
- `CD` (IN: Bool) - Count down input (conta sul fronte salita)
- `LD` (IN: Bool) - Load preset (carica PV in CV)
- `PV` (IN: Int) - Preset value
- `Q` (OUT: Bool) - TRUE quando CV <= 0
- `CV` (OUT: Int) - Current value

**Descrizione / Description**:
Conta alla rovescia da PV. Q diventa TRUE quando CV <= 0.

**Esempio / Example**:
```scl
// Countdown da 50
#countdown(
    CD := decrementPulse,
    LD := loadPreset,
    PV := 50
);

IF #countdown.Q THEN
    timeExpired := TRUE;
END_IF;
```

---

### 12. CTUD - Count Up/Down

**Firma / Signature**: `#myCounter(CU := <up>, CD := <down>, R := <reset>, LD := <load>, PV := <preset>);`

**Parametri / Parameters**:
- `CU` (IN: Bool) - Count up input
- `CD` (IN: Bool) - Count down input
- `R` (IN: Bool) - Reset (CV := 0)
- `LD` (IN: Bool) - Load (CV := PV)
- `PV` (IN: Int) - Preset value
- `QU` (OUT: Bool) - TRUE quando CV >= PV
- `QD` (OUT: Bool) - TRUE quando CV <= 0
- `CV` (OUT: Int) - Current value

**Descrizione / Description**:
Contatore bidirezionale. Combina CTU e CTD.

**Esempio / Example**:
```scl
// Magazzino con entrate/uscite
#warehouseCounter(
    CU := itemEntered,
    CD := itemExited,
    R := resetInventory,
    LD := FALSE,
    PV := 1000
);

IF #warehouseCounter.QU THEN
    warehouseFull := TRUE;
ELSIF #warehouseCounter.QD THEN
    warehouseEmpty := TRUE;
END_IF;
```

---

## EDGE DETECTION (2 funzioni)

### 13. R_TRIG - Rising Edge Trigger

**Firma / Signature**: `#myTrigger(CLK := <signal>);`

**Parametri / Parameters**:
- `CLK` (IN: Bool) - Segnale da monitorare
- `Q` (OUT: Bool) - TRUE per un ciclo sul fronte di salita

**Descrizione / Description**:
Rileva transizione 0→1. Q è TRUE per esattamente un ciclo PLC.

**Esempio / Example**:
```scl
VAR
    startEdge : R_TRIG;
END_VAR

#startEdge(CLK := startButton);
IF #startEdge.Q THEN
    // Eseguito UNA VOLTA sul fronte
    cycleCounter := cycleCounter + 1;
END_IF;
```

**Timing Diagram**:
```
CLK: ___/‾‾‾‾‾‾‾‾‾‾\___
Q:   ___/‾\_________    (un ciclo)
```

---

### 14. F_TRIG - Falling Edge Trigger

**Firma / Signature**: `#myTrigger(CLK := <signal>);`

**Parametri / Parameters**:
- `CLK` (IN: Bool) - Segnale da monitorare
- `Q` (OUT: Bool) - TRUE per un ciclo sul fronte di discesa

**Descrizione / Description**:
Rileva transizione 1→0. Complementare a R_TRIG.

**Esempio / Example**:
```scl
#stopEdge(CLK := runSignal);
IF #stopEdge.Q THEN
    // Eseguito quando runSignal passa da TRUE a FALSE
    saveDataToLog();
END_IF;
```

---

## COMPARISON & SELECTION (5 funzioni)

### 15. SEL - Select Binary

**Firma / Signature**: `result := SEL(G := <selector>, IN0 := <value0>, IN1 := <value1>);`

**Parametri / Parameters**:
- `G` (IN: Bool) - Selettore (FALSE=IN0, TRUE=IN1)
- `IN0` (IN: ANY) - Valore se G=FALSE
- `IN1` (IN: ANY) - Valore se G=TRUE
- **Ritorno / Return**: ANY - IN0 o IN1 a seconda di G

**Descrizione / Description**:
Selettore binario: ritorna IN0 se G=FALSE, IN1 se G=TRUE.

**Esempio / Example**:
```scl
// Seleziona setpoint manuale o automatico
activeSetpoint := SEL(
    G := autoMode,
    IN0 := manualSetpoint,
    IN1 := autoSetpoint
);
```

---

### 16. MUX - Multiplexer

**Firma / Signature**: `result := MUX(K := <index>, IN0 := <v0>, IN1 := <v1>, ...);`

**Parametri / Parameters**:
- `K` (IN: Int) - Indice input da selezionare (0..N-1)
- `IN0..IN31` (IN: ANY) - Valori tra cui selezionare (max 32)
- **Ritorno / Return**: ANY - INK (o IN0 se K fuori range)

**Descrizione / Description**:
Selettore multi-ingresso. Ritorna INK. Se K<0 o K>=N, ritorna IN0.

**Esempio / Example**:
```scl
// Seleziona tra 4 ricette
activeRecipe := MUX(
    K := recipeNumber,
    IN0 := recipe1,
    IN1 := recipe2,
    IN2 := recipe3,
    IN3 := recipe4
);
```

---

### 17. ROL - Rotate Left

**Firma / Signature**: `result := ROL(IN := <value>, N := <count>);`

**Parametri / Parameters**:
- `IN` (IN: Bit String) - Valore da ruotare (Byte/Word/DWord)
- `N` (IN: UInt) - Numero posizioni da ruotare
- **Ritorno / Return**: Bit String - Valore ruotato

**Descrizione / Description**:
Ruota bit verso sinistra. Bit MSB ritorna in LSB.

**Esempio / Example**:
```scl
// Ruota pattern bit 3 posizioni a sinistra
pattern := ROL(IN := 16#0F, N := 3);  // 16#0F → 16#78
```

---

### 18. ROR - Rotate Right

**Firma / Signature**: `result := ROR(IN := <value>, N := <count>);`

**Parametri / Parameters**:
- `IN` (IN: Bit String) - Valore da ruotare
- `N` (IN: UInt) - Numero posizioni
- **Ritorno / Return**: Bit String - Valore ruotato

**Descrizione / Description**:
Ruota bit verso destra. Complementare a ROL.

**Esempio / Example**:
```scl
pattern := ROR(IN := 16#F0, N := 4);  // 16#F0 → 16#0F
```

---

### 19. SHL - Shift Left

**Firma / Signature**: `result := SHL(IN := <value>, N := <count>);`

**Parametri / Parameters**:
- `IN` (IN: Bit String) - Valore da shiftare
- `N` (IN: UInt) - Numero posizioni
- **Ritorno / Return**: Bit String - Valore shiftato (riempie con 0)

**Descrizione / Description**:
Shift logico a sinistra. Inserisce 0 a destra. Equivale a moltiplicazione per 2^N.

**Esempio / Example**:
```scl
// Moltiplica per 8 (2^3)
result := SHL(IN := 5, N := 3);  // 5 * 8 = 40
```

---

## CONVERSION FUNCTIONS (5 funzioni)

### 20. TRUNC - Tronca a Intero / Truncate to Integer

**Firma / Signature**: `intValue := TRUNC(IN := <real>);`

**Parametri / Parameters**:
- `IN` (IN: Real/LReal) - Valore floating point da troncare
- **Ritorno / Return**: DInt - Parte intera (senza arrotondamento)

**Descrizione / Description**:
Tronca verso zero. 3.7 → 3, -2.9 → -2.

**Esempio / Example**:
```scl
// Estrai parte intera
whole := TRUNC(IN := 45.89);  // = 45
```

---

### 21. ROUND - Arrotonda / Round

**Firma / Signature**: `rounded := ROUND(IN := <real>);`

**Parametri / Parameters**:
- `IN` (IN: Real/LReal) - Valore da arrotondare
- **Ritorno / Return**: DInt - Valore arrotondato al più vicino

**Descrizione / Description**:
Arrotonda al numero intero più vicino. .5 arrotonda verso l'alto.

**Esempio / Example**:
```scl
// Arrotonda a intero più vicino
count := ROUND(IN := 7.4);  // = 7
count := ROUND(IN := 7.6);  // = 8
```

---

### 22. CEIL - Arrotonda per Eccesso / Ceiling

**Firma / Signature**: `ceiling := CEIL(IN := <real>);`

**Parametri / Parameters**:
- `IN` (IN: Real/LReal) - Valore input
- **Ritorno / Return**: DInt - Intero superiore

**Descrizione / Description**:
Arrotonda sempre verso l'alto. 3.1 → 4, -2.9 → -2.

**Esempio / Example**:
```scl
// Calcola numero batch necessari (arrotonda per eccesso)
batches := CEIL(IN := totalPieces / TO_REAL(batchSize));
```

---

### 23. FLOOR - Arrotonda per Difetto / Floor

**Firma / Signature**: `floor := FLOOR(IN := <real>);`

**Parametri / Parameters**:
- `IN` (IN: Real/LReal) - Valore input
- **Ritorno / Return**: DInt - Intero inferiore

**Descrizione / Description**:
Arrotonda sempre verso il basso. 3.9 → 3, -2.1 → -3.

**Esempio / Example**:
```scl
batches := FLOOR(IN := ratio);
```

---

### 24. TO_REAL - Converti a Real

**Firma / Signature**: `realValue := TO_REAL(<int_value>);`

**Uso / Usage**: Converte Int/DInt/UInt a Real per calcoli floating point.

**Esempio / Example**:
```scl
average := TO_REAL(sum) / TO_REAL(count);
```

---

## STRING FUNCTIONS (3 funzioni)

### 25. CONCAT - Concatena Stringhe / String Concatenation

**Firma / Signature**: `result := CONCAT(IN1 := <str1>, IN2 := <str2>);`

**Parametri / Parameters**:
- `IN1` (IN: String) - Prima stringa
- `IN2` (IN: String) - Seconda stringa
- **Ritorno / Return**: String - Concatenazione IN1 + IN2

**Descrizione / Description**:
Unisce due stringhe. SCL non supporta operatore `+` per stringhe.

**Esempio / Example**:
```scl
// Crea messaggio diagnostico
message := CONCAT(IN1 := 'Error on ', IN2 := deviceName);
// Risultato: "Error on Motor_1"
```

---

### 26. LEN - Lunghezza Stringa / String Length

**Firma / Signature**: `length := LEN(IN := <string>);`

**Parametri / Parameters**:
- `IN` (IN: String) - Stringa da misurare
- **Ritorno / Return**: Int - Numero caratteri (escluso terminatore)

**Esempio / Example**:
```scl
nameLength := LEN(IN := userName);
IF nameLength > 20 THEN
    // Nome troppo lungo
END_IF;
```

---

### 27. LEFT - Sottostringa Sinistra / Left Substring

**Firma / Signature**: `result := LEFT(IN := <string>, L := <length>);`

**Parametri / Parameters**:
- `IN` (IN: String) - Stringa sorgente
- `L` (IN: Int) - Numero caratteri da estrarre
- **Ritorno / Return**: String - Primi L caratteri

**Esempio / Example**:
```scl
// Estrai prefisso (primi 3 caratteri)
prefix := LEFT(IN := 'MOTOR_001', L := 5);  // = "MOTOR"
```

---

## MOVE FUNCTIONS (3 funzioni)

### 28. MOVE - Sposta Valore / Move Value

**Firma / Signature**: `MOVE(IN := <source>, OUT => <destination>);`

**Parametri / Parameters**:
- `IN` (IN: ANY) - Valore sorgente
- `OUT` (OUT: ANY) - Destinazione (deve essere stesso tipo)

**Descrizione / Description**:
Copia valore da IN a OUT. Equivale a `OUT := IN` ma esplicito.

**Esempio / Example**:
```scl
MOVE(IN := sensorValue, OUT => processValue);
```

---

### 29. MOVE_BLK - Sposta Blocco / Move Block

**Firma / Signature**: `MOVE_BLK(IN := <source>, COUNT := <n>, OUT => <dest>);`

**Parametri / Parameters**:
- `IN` (IN: Variant) - Array sorgente
- `COUNT` (IN: UDInt) - Numero elementi
- `OUT` (OUT: Variant) - Array destinazione

**Descrizione / Description**:
Copia COUNT elementi da array sorgente a destinazione. Molto più veloce di loop FOR.

**Esempio / Example**:
```scl
// Copia 100 valori
MOVE_BLK(IN := sourceArray, COUNT := 100, OUT => destArray);
```

---

### 30. FILL_BLK - Riempi Blocco / Fill Block

**Firma / Signature**: `FILL_BLK(IN := <value>, COUNT := <n>, OUT => <array>);`

**Parametri / Parameters**:
- `IN` (IN: ANY) - Valore da replicare
- `COUNT` (IN: UDInt) - Numero elementi
- `OUT` (OUT: Variant) - Array destinazione

**Descrizione / Description**:
Riempie array con lo stesso valore ripetuto COUNT volte.

**Esempio / Example**:
```scl
// Azzera array (riempi con 0)
FILL_BLK(IN := 0, COUNT := 100, OUT => dataBuffer);

// Inizializza con valore default
FILL_BLK(IN := 25.0, COUNT := 50, OUT => temperatures);
```

---

## Note d'Uso / Usage Notes

- **Parametri Nominati Obbligatori**: Tutte queste funzioni richiedono parametri nominati (`:=` e `=>`).
- **Performance**: Funzioni native sono ottimizzate a livello firmware, molto più veloci delle implementazioni manuali.
- **Tipo Safety**: Il compilatore verifica compatibilità tipi - errori a compile-time, non runtime.
- **Function vs Function Block**: Funzioni ritornano valore singolo, FB hanno stato interno persistente.

Per funzioni oltre queste 30, consultare automaticamente il database JSON (`scl-reference/functions/`).
