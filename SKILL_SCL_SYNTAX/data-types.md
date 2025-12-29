# SCL Data Types Reference

Riferimento completo tipi di dati SCL / Complete SCL data types reference.

---

## Elementary Types (Tipi Elementari)

### Boolean Types

```scl
VAR
    flag : Bool := FALSE;      // 1 bit: TRUE or FALSE
END_VAR

// Costanti boolean
valve := TRUE;
pump := FALSE;
```

**Range**: `FALSE` (0) o `TRUE` (1)  
**Uso**: Flag, stati, segnali digitali

---

### Integer Types (Tipi Interi)

```scl
VAR
    // Signed integers (con segno)
    tinyNum : SInt := -128;           // -128..127 (8 bit)
    smallInt : Int := 100;            // -32768..32767 (16 bit) 
    mediumInt : DInt := 1000000;      // -2^31..2^31-1 (32 bit)
    bigInt : LInt := 1000000000000;   // -2^63..2^63-1 (64 bit)
    
    // Unsigned integers (senza segno)
    unsignedByte : USInt := 255;      // 0..255 (8 bit)
    unsignedWord : UInt := 65535;     // 0..65535 (16 bit)
    unsignedDWord : UDInt := 4000000; // 0..2^32-1 (32 bit)
    unsignedLWord : ULInt;            // 0..2^64-1 (64 bit)
END_VAR
```

**Range Summary**:
- `SInt`: -128 to 127
- `Int`: -32,768 to 32,767 ← **Più comune**
- `DInt`: -2,147,483,648 to 2,147,483,647
- `LInt`: -9.22×10^18 to 9.22×10^18
- `USInt`: 0 to 255
- `UInt`: 0 to 65,535
- `UDInt`: 0 to 4,294,967,295
- `ULInt`: 0 to 1.84×10^19

**Best Practice**:
- Usa `Int` per contatori, indici, stato (default)
- Usa `DInt` per timestamp, grandi contatori
- Usa `UInt` per valori sempre positivi (velocità, RPM)

---

### Floating Point Types

```scl
VAR
    temperature : Real := 25.5;        // 32-bit IEEE 754 (6-7 cifre)
    preciseValue : LReal := 3.141592;  // 64-bit IEEE 754 (15-16 cifre)
END_VAR

// Notazione scientifica
velocity : Real := 1.5E3;      // 1500.0
smallValue : Real := 2.5E-4;   // 0.00025
```

**Precisione**:
- `Real`: ±1.18×10^-38 to ±3.40×10^38 (6-7 cifre significative)
- `LReal`: ±2.23×10^-308 to ±1.80×10^308 (15-16 cifre significative)

**⚠️ Warning**: Non usare `=` per confrontare float! Usa tolleranza:
```scl
IF ABS(IN := value1 - value2) < 0.001 THEN
    // Values sono "uguali" entro tolleranza
END_IF;
```

---

### Time Types

```scl
VAR
    delay : Time := T#5s;              // 5 secondi
    duration : Time := T#1h30m45s;     // 1 ora, 30 min, 45 sec
    shortPulse : Time := T#100ms;      // 100 millisecondi
    longDelay : LTime := LT#1d2h;      // 1 giorno, 2 ore (64-bit)
END_VAR

// Formati supportati
pause := T#1h30m;          // 1 ora 30 minuti
timeout := T#500ms;        // 500 millisecondi  
cycle := T#10s500ms;       // 10.5 secondi
```

**Formato Time Literal**: `T#[d][h][m][s][ms][us][ns]`

**Esempi**:
- `T#5s` - 5 secondi
- `T#2m30s` - 2 minuti 30 secondi
- `T#1h15m` - 1 ora 15 minuti
- `T#1d` - 1 giorno
- `T#500ms` - 500 millisecondi

**Range**:
- `Time`: -24d20h31m23s648ms a +24d20h31m23s647ms (32-bit)
- `LTime`: ±292 anni (64-bit, raro)

---

### Date and Time of Day

```scl
VAR
    today : Date := D#2024-12-25;              // Solo data
    now : Time_Of_Day := TOD#14:30:00;         // Solo ora
    timestamp : Date_And_Time;                  // Data + ora (deprecato, usa DTL)
    modernTime : DTL;                          // Date Time Long (S7-1500)
END_VAR

// DTL Structure (S7-1500 recommended)
VAR
    currentTime : DTL;
END_VAR

// Accesso campi DTL
year := currentTime.YEAR;      // 1970..2262
month := currentTime.MONTH;    // 1..12
day := currentTime.DAY;        // 1..31
hour := currentTime.HOUR;      // 0..23
minute := currentTime.MINUTE;  // 0..59
second := currentTime.SECOND;  // 0..59
```

**DTL vs DATE_AND_TIME**:
- `DTL`: Moderno, S7-1500, più preciso, facilmente accessibile
- `DATE_AND_TIME`: Legacy, S7-300/400, deprecato

---

### String Types

```scl
VAR
    message : String;                  // Max 254 caratteri
    name : String[20] := 'Motor1';     // Max 20 caratteri
    wideText : WString;                // Unicode (16-bit char)
    fixedName : String[10] := 'Test';  // Lunghezza massima 10
END_VAR

// Operazioni stringhe
length := LEN(IN := message);
result := CONCAT(IN1 := 'Error: ', IN2 := name);
```

**Limiti**:
- `String`: Max 254 caratteri
- `WString`: Max 16383 caratteri Unicode
- Specifica lunghezza massima per allocazione efficiente: `String[N]`

**⚠️ Nota**: SCL NON supporta operatore `+` per concatenazione! Usa `CONCAT()`.

---

### Bit String Types (Tipi Bit)

```scl
VAR
    statusByte : Byte := 16#FF;        // 8 bit
    controlWord : Word := 16#0000;     // 16 bit
    statusDWord : DWord := 16#DEADBEEF;// 32 bit
    statusLWord : LWord;               // 64 bit
END_VAR

// Notazione esadecimale
mask := 16#00FF;     // Hex
bits := 2#11110000;  // Binario
octal := 8#377;      // Ottale
```

**Dimensioni**:
- `Byte`: 8 bit
- `Word`: 16 bit ← **Più comune per I/O**
- `DWord`: 32 bit
- `LWord`: 64 bit

**Uso Tipico**: 
- Status word da drive
- Bit di controllo impacchettati
- Maschere per bitwise operations

---

## Complex Types (Tipi Complessi)

### Arrays (Array)

```scl
VAR
    // Array monodimensionale
    temperatures : Array[0..9] of Real;           // 10 elementi
    sensors : Array[1..5] of Int;                 // 5 elementi (indice 1-based)
    
    // Array multidimensionale
    matrix : Array[1..3, 1..3] of Int;            // Matrice 3x3
    cube : Array[0..9, 0..9, 0..9] of Real;       // 3D array
    
    // Array di stringhe
    messages : Array[0..4] of String[50];
END_VAR

// Accesso array
temperatures[0] := 25.5;
value := sensors[3];
matrix[2, 3] := 100;

// Inizializzazione
temperatures[0] := 20.0;
temperatures[1] := 21.5;
// ... oppure usa FILL_BLK
FILL_BLK(IN := 20.0, COUNT := 10, OUT => temperatures);
```

**Best Practices**:
- Indice tipicamente 0-based: `Array[0..N-1]`
- Dichiara dimensione che userai effettivamente
- Per array grandi (>100 elementi), considera DB globale

---

### Structures (Struct)

```scl
VAR
    // Struct inline (definita nella dichiarazione)
    motorData : Struct
        running : Bool;
        speed : Real;
        current : Real;
        temperature : Real;
        errorCode : Int;
    End_Struct;
    
    // Array di struct
    motors : Array[1..5] of Struct
        id : Int;
        name : String[20];
        status : Bool;
    End_Struct;
END_VAR

// Accesso campi
motorData.running := TRUE;
motorData.speed := 1500.0;
currentValue := motorData.current;

// Struct in array
motors[1].id := 101;
motors[1].name := 'Spindle_Main';
motors[1].status := TRUE;
```

**User-Defined Type (UDT)**:
```scl
// Definisci UDT in PLC Data Types
TYPE "MotorType"
    STRUCT
        running : Bool;
        speed : Real;
        current : Real;
    END_STRUCT;
END_TYPE

// Usa UDT
VAR
    motor1 : "MotorType";
    motor2 : "MotorType";
    motorArray : Array[1..10] of "MotorType";
END_VAR
```

---

### Pointer Types (Raramente Usati)

```scl
VAR
    dataPointer : Pointer;     // Pointer generico
    tempPtr : Variant;         // Variant type
END_VAR
```

**⚠️ Nota**: Pointer sono rari in SCL normale. Usati principalmente per:
- Comunicazione con blocchi sistema
- Funzioni avanzate movimentazione dati
- Interfacce con MOVE_BLK_VARIANT

---

## Type Conversions (Conversioni di Tipo)

### Explicit Conversions (Conversioni Esplicite)

```scl
// Integer ↔ Real
realValue := TO_REAL(intValue);        // Int → Real
intValue := TRUNC(IN := realValue);    // Real → Int (tronca)
intValue := ROUND(IN := realValue);    // Real → Int (arrotonda)

// Integer size conversions
dintValue := TO_DINT(intValue);        // Int → DInt
intValue := TO_INT(dintValue);         // DInt → Int (attenzione overflow!)

// Unsigned ↔ Signed
uintValue := TO_UINT(intValue);
intValue := TO_INT(uintValue);

// Bit string ↔ Integer
wordValue := TO_WORD(intValue);        // Int → Word
intValue := TO_INT(wordValue);         // Word → Int
```

**Funzioni Conversione Comuni**:
- `TO_INT()`, `TO_DINT()`, `TO_REAL()` - Converti a tipo specifico
- `TRUNC()` - Real → Int (tronca verso zero)
- `ROUND()` - Real → Int (arrotonda al più vicino)
- `CEIL()` - Real → Int (arrotonda per eccesso)
- `FLOOR()` - Real → Int (arrotonda per difetto)

---

### Implicit Conversions (Conversioni Implicite)

SCL ha conversioni implicite limitate:

```scl
// ✅ OK: Widening (piccolo → grande) è automatico
VAR
    i : Int := 100;
    d : DInt;
END_VAR
d := i;  // OK: Int → DInt implicito

// ❌ ERRORE: Narrowing (grande → piccolo) richiede conversione esplicita
i := d;              // ERRORE!
i := TO_INT(d);      // OK: conversione esplicita
```

**Regola**:
- Piccolo → Grande (widening): Spesso OK
- Grande → Piccolo (narrowing): Richiede SEMPRE conversione esplicita
- Signed ↔ Unsigned: Richiede conversione esplicita
- Int ↔ Real: Richiede conversione esplicita

---

## Type Selection Guidelines

### Quando Usare Ogni Tipo

**Bool**:
- Stati digitali (valve, pump, motor on/off)
- Flag (error, warning, complete)
- Segnali I/O digitali

**Int**:
- Contatori (pezzi, cicli)
- Stati enumerati (0=Idle, 1=Running, 2=Error)
- Indici array
- Valori che non superano ±32k

**DInt**:
- Timestamp (millisecondi da epoch)
- Contatori grandi (pezzi prodotti totali)
- Calcoli che potrebbero superare ±32k

**Real**:
- Misure analogiche (temperatura, pressione, velocità)
- Calcoli matematici (media, percentuale)
- Setpoint e valori di processo

**String**:
- Nomi (dispositivi, ricette)
- Messaggi HMI
- Logging testo

**Array**:
- Collezioni omogenee (10 temperature, 5 velocità)
- Buffer dati
- Tabelle lookup

**Struct**:
- Gruppi di dati correlati (dati motore, parametri ricetta)
- Dati complessi con tipi misti

---

## Memory Allocation (Allocazione Memoria)

### Size Reference

| Tipo | Size | Note |
|------|------|------|
| Bool | 1 bit* | *Allocato in byte, 8 Bool = 1 byte |
| SInt/USInt | 1 byte | |
| Int/UInt | 2 byte | |
| DInt/UDInt | 4 byte | |
| LInt/ULInt | 8 byte | |
| Real | 4 byte | IEEE 754 single |
| LReal | 8 byte | IEEE 754 double |
| Time | 4 byte | |
| String | 2 + len | 2 byte header + caratteri |
| String[N] | 2 + N | Alloca N byte |

### Ottimizzazione Memoria

```scl
// ❌ Inefficiente (3 byte, ma alloca 6 per allineamento)
VAR
    flag1 : Bool;  // Byte 0
    value : Int;   // Byte 2-3 (allineato)
    flag2 : Bool;  // Byte 4
END_VAR

// ✅ Efficiente (raggruppa Bool insieme)
VAR
    flag1 : Bool;  // Byte 0 bit 0
    flag2 : Bool;  // Byte 0 bit 1
    value : Int;   // Byte 2-3
END_VAR
```

**Best Practice**:
- Raggruppa variabili Bool consecutive (fino a 8 = 1 byte)
- Dichiara variabili grandi (Int, Real) dopo Bool per allineamento
- Usa `String[N]` con N appropriato (non sempre 254)

---

## Constants (Costanti)

```scl
VAR CONSTANT
    MAX_SPEED : Real := 3000.0;
    MIN_TEMP : Real := -40.0;
    PI : Real := 3.14159265;
    BUFFER_SIZE : Int := 100;
    DEVICE_NAME : String := 'MainMotor';
END_VAR

// Uso
IF speed > MAX_SPEED THEN
    alarm := TRUE;
END_IF;
```

**Best Practice**:
- Usa costanti per valori "magic number"
- Nomi in UPPER_CASE per convenzione
- Facilita manutenzione (cambi in un posto solo)

---

## Enumerations (S7-1500)

```scl
// Definisci in PLC Data Types
TYPE "MotorState"
    (
        IDLE := 0,
        STARTING := 1,
        RUNNING := 2,
        STOPPING := 3,
        ERROR := 4
    );
END_TYPE

// Uso
VAR
    currentState : "MotorState";
END_VAR

currentState := "MotorState".IDLE;

CASE currentState OF
    "MotorState".IDLE:
        // ...
    "MotorState".STARTING:
        // ...
END_CASE;
```

**Vantaggi**:
- Codice più leggibile
- Type-safe (previene assegnazione valori invalidi)
- Autocomplete in TIA Portal

---

## Special Types (Tipi Speciali)

### ANY Types

```scl
// Per funzioni generiche che accettano qualsiasi tipo
FUNCTION "GenericFunction" : Void
VAR_INPUT
    input : ANY;  // Accetta qualsiasi tipo
END_VAR
```

Usato raramente, principalmente in system function library.

### Variant Type

```scl
VAR
    flexibleData : Variant;
END_VAR
```

Può contenere qualsiasi tipo, usato per comunicazione generica.

---

## Quick Type Selection Flowchart

```
Devo memorizzare...

├─ On/Off, True/False → Bool
├─ Intero -32k..+32k → Int
├─ Intero più grande → DInt
├─ Sempre positivo → UInt/UDInt
├─ Decimale, misura analogica → Real
├─ Decimale alta precisione → LReal
├─ Durata, delay → Time
├─ Testo, nome → String
├─ Collezione valori → Array[...]
└─ Gruppo dati correlati → Struct
```

