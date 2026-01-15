
Comprehensive Guide for Creating a Claude Code LINT/SKILL for SCL Programming
Based on my navigation of the TIA Portal documentation, here's everything you need to create a LINT or SKILL extension for Claude Code to write correct SCL code:

1. SCL Language Foundation
SCL (Structured Control Language) is a high-level programming language based on PASCAL and follows DIN EN 61131-3 (international IEC 1131-3) standards. It's designed for programmable logic controllers (PLCs) and is particularly suitable for:

Data management
Process optimization
Recipe management
Mathematical/statistical tasks
2. Core Language Elements for LINT Rules
Syntax Rules:
Each instruction must end with a semicolon (;)
No distinction between upper and lower case (case-insensitive)
Instructions can span multiple lines
Comments serve only for documentation and don't affect execution
Four Types of Instructions:
Value assignments - assign tags, constants, expressions, or other tag values
Instructions for program control - branches, loops, jumps
Additional instructions from the "Instructions" task card - standard library functions
Block calls - subroutines in other blocks
3. Critical LINT Rules to Implement
Syntax Validation:
Verify semicolons terminate all instructions
Check for proper parentheses and bracket matching
Validate comment syntax (// for single line)
Variable and Type Checking:
Verify data type consistency in assignments
Check parameter types match function signatures
Validate array indexing and bounds
Ensure variables are declared before use
Instruction-Specific Rules:
Program Control Instructions:

WHILE "condition" < 10 DO ... END WHILE;
IF condition THEN ... ELSIF ... ELSE ... END IF;
FOR "counter" := 0 TO 10 DO ... END FOR;
Proper nesting and closure of control structures
Value Assignments:

Pattern: "variable" := value;
Must include proper type casting where needed
Block Calls:

Pattern: "BlockName"();
Validate block existence and parameter lists
4. Data Types to Validate
Basic Types:

Binary numbers (BYTE, WORD, DWORD, etc.)
Integers (INT, DINT, UINT, UDINT)
Floating-point (REAL, LREAL)
Timers (S5TIME, TIME, TIME_OF_DAY)
Date and Time (DATE, DT, TOD)
Character strings (STRING)
Complex Types:

ARRAY declarations and usage
PLC Data Types (UDT)
STRUCT data structures
Pointers
Parameter types (IN, OUT, IN_OUT)
5. SCL Operations Categories
Build LINT rules for these operation types:

Bit logic operations - AND, OR, XOR, NOT
Timer operations - TON, TOF, TP, RTO
Counter operations - CTU, CTD, CTUD
Comparator operations - ==, <>, <, <=, >, >=
Math functions - ADD, SUB, MUL, DIV, MOD, ABS, SQRT, SIN, COS
Move operations - MOVE, MOVEB (block move)
Conversion operations - Type casting and conversions
Word logic operations - Bitwise operations on words
Shift and Rotate - SHL, SHR, ROL, ROR
6. Programming Recommendations to Encode
Based on TIA Portal best practices:

Symbolic addressing - Use symbolic names instead of absolute addresses
Use DB_ANY data type - For flexible data type handling
Proper use of PLC data types (UDT) - For structured data
Use MOVE instructions in STL - For efficient data movement
Use IEC timers and counters - Standard, platform-independent
Indirect addressing - Only where necessary with proper bounds checking
ARRAY component addressing - Best practices for multi-dimensional arrays
7. SKILL/LINT Implementation Structure
Create rules organized as:

scl_lint_rules:
├── syntax_rules
│   ├── semicolon_termination
│   ├── bracket_matching
│   ├── comment_syntax
│   └── instruction_structure
├── semantic_rules
│   ├── variable_declaration
│   ├── type_checking
│   ├── scope_validation
│   └── function_signature_matching
├── instruction_rules
│   ├── control_flow (IF/THEN/WHILE/FOR)
│   ├── assignments
│   ├── block_calls
│   └── operations_validation
├── data_type_rules
│   ├── basic_type_validation
│   ├── complex_type_validation
│   └── type_conversion_rules
└── best_practices
    ├── naming_conventions
    ├── performance_guidelines
    └── platform_compatibility
8. Key Pattern Examples to Validate
scl
// Valid SCL patterns:
"MyTag" := 0;                              // Value assignment
"MyDB"();                                  // Block call
WHILE "Counter" < 10 DO
  "Counter" := "Counter" + 1;
END WHILE;                                 // Loop structure

IF "Condition" THEN
  "Output" := 1;
ELSE
  "Output" := 0;
END IF;                                    // Conditional
9. Documentation Sources Available
Key sections in TIA Portal documentation:

Basics of SCL - Language fundamentals
Rules for SCL instructions - Syntax and structure rules
Creating SCL programs - Program organization
Instructions - Complete instruction catalog (S7-1200, S7-1500)
Data types - Type reference guide
Programming recommendations - Best practices
10. Integration Recommendations
For Claude Code SKILL creation:

Implement real-time syntax validation as user types
Provide autocompletion for instructions and functions
Highlight type mismatches and compatibility issues
Suggest proper data types and structures
Warn about non-standard or deprecated patterns
Validate block call parameters against declarations
Check for missing semicolons and unmatched brackets
Enforce naming conventions and best practices
This comprehensive foundation should enable you to build a robust LINT/SKILL that helps developers write correct SCL code automatically while adhering to SIEMENS TIA Portal standards.



Documentazione Completa SCL per Claude Code LINT/SKILL
Ho completato l'esplorazione della documentazione TIA Portal. Ecco i documenti MD organizzati per argomenti:

📄 DOCUMENTO 1: SCL_01_FONDAMENTI.md
markdown
# SCL - Structured Control Language - Fondamenti

## 1. Che cos'è SCL

SCL (Structured Control Language) è un linguaggio di programmazione ad alto livello basato su PASCAL conforme agli standard:
- **DIN EN 61131-3** (IEC 1131-3 internazionale)
- **PLCopen Basis level ST** (Structured Text)

### Caratteristiche principali
- Linguaggio case-insensitive (non distingue maiuscole/minuscole)
- Basato su istruzioni che terminano con semicolon (;)
- Supporta strutture di controllo avanzate (IF/ELSE, WHILE, FOR)
- Adatto per logica complessa, calcoli, gestione dati

### Campi di applicazione
- Gestione dati
- Ottimizzazione processi
- Gestione ricette
- Operazioni matematiche/statistiche
- Logica di controllo complessa

## 2. Regole Fondamentali di Sintassi

### 2.1 Terminazione Istruzioni
Ogni istruzione DEVE terminare con punto e virgola `;`
```scl
"Counter" := 0;
"Output" := "Input1" AND "Input2";
"MyBlock"();
```

### 2.2 Case-Insensitivity
Non c'è distinzione tra maiuscole e minuscole
```scl
"MyTag" := 100;     // Valido
"MYTAG" := 100;     // Stesso valore
"mytag" := 100;     // Stesso valore
```

### 2.3 Multi-linea
Un'istruzione può occupare multiple righe
```scl
"LongVariable" := "Input1" AND "Input2" AND 
                  "Input3" AND "Input4";
```

### 2.4 Commenti
I commenti non influenzano l'esecuzione del programma
```scl
// Commento su singola riga
"Counter" := 0;     // Incrementa il contatore
```

## 3. Tipi di Istruzioni SCL

### 3.1 Assegnazioni di Valore (Value Assignments)
Assegna a un tag il valore di una costante, un'espressione o un altro tag
```scl
"MyTag" := 0;                              // Costante
"Output" := "Input" + 10;                  // Espressione
"CopyTag" := "SourceTag";                  // Copia valore
```

### 3.2 Istruzioni di Controllo Programma (Program Control)
Implementano branch, loop e salti
```scl
// IF/THEN/ELSE
IF "Condition" THEN
    "Action1" := 1;
ELSIF "OtherCondition" THEN
    "Action2" := 1;
ELSE
    "Action3" := 1;
END IF;

// WHILE loop
WHILE "Counter" < 10 DO
    "Counter" := "Counter" + 1;
END WHILE;

// FOR loop
FOR "i" := 0 TO 10 DO
    "Array"["i"] := 0;
END FOR;
```

### 3.3 Istruzioni dalla Task Card "Instructions"
Funzioni standard dalla libreria di istruzioni
```scl
// Operazioni bit
"BitResult" := "Input1" AND "Input2";

// Operazioni timer/counter
"TON_Instance"(IN := "Enable", PT := T#5S, Q => "Output");

// Operazioni matematiche
"Result" := ADD("Input1", "Input2");
```

### 3.4 Block Calls
Chiamata a subroutine in altri blocchi
```scl
"MyDB"();                    // Senza parametri
"MyFB"(IN := 10, OUT => Result);  // Con parametri
```

## 4. Elementi del Linguaggio

### Espressioni
Combinazioni di variabili, operatori e funzioni che restituiscono un valore
```scl
"A" + "B"
"Input1" AND "Input2" OR "Input3"
("X" > 5) AND ("Y" < 10)
```

### Assegnazioni di Valore
Trasferisce il risultato di un'espressione a una variabile
```scl
"Target" := "Source";
"Total" := "A" + "B" + "C";
```

### Operatori e Precedenza
- **Aritmetica**: +, -, *, /, MOD
- **Logica**: AND, OR, NOT, XOR
- **Comparazione**: =, <>, <, >, <=, >=
- **Precedenza**: Parentesi > Moltiplicazione/Divisione > Addizione/Sottrazione

## 5. Struttura di un Programma SCL
```scl
// Dichiarazioni di variabili locali (nell'interfaccia del blocco)
DECLARE
    LOCAL "Counter" : INT := 0;
    LOCAL "Status" : BOOL := FALSE;
END_DECLARE;

// Corpo del programma
BEGIN
    // Logica principale
    IF "Enable" THEN
        "Counter" := "Counter" + 1;
    END IF;
    
    // Chiamate a funzioni
    "Result" := ADD("A", "B");
    
    // Controllo del flusso
    WHILE "Counter" < 100 DO
        "Counter" := "Counter" + 1;
    END WHILE;
END;
```

## 6. Floating-Point e Costanti

### Operazioni con REAL e LREAL
Gestione accurata dei numeri in virgola mobile
```scl
"Real_Value" := 3.14159;
"Double_Value" : LREAL := 2.718281828;

// Risultati di operazioni
"Division_Result" := 10.0 / 3.0;  // 3.333...
```

### Calcolo con Costanti
```scl
"Time_Value" := T#5S;              // 5 secondi
"Date_Value" := D#2024-01-01;      // Data
"Constant" := 100;                 // Numero intero
```

## 7. Best Practices

1. **Nomi significativi**: Usa nomi di variabili che descrivono il significato
2. **Commenti**: Documenta la logica complessa
3. **Struttura**: Organizza il codice in blocchi logici
4. **Type safety**: Dichiara sempre i tipi di dati corretti
5. **Performance**: Evita loop nidificati non necessari
6. **Indentation**: Mantieni uno stile di indentazione coerente
```scl
// ✓ Buono: Nomi significativi e commentati
"MotorSpeed" := "SpeedReference" * "Gain_Factor";

// ✗ Cattivo: Nomi generici
"X" := "A" * "B";
```
📄 DOCUMENTO 2: SCL_02_DATA_TYPES.md
markdown
# Tipi di Dati SCL

## 1. Tipi di Dati di Base

### 1.1 Numeri Binari (Binary Numbers)

|
 Tipo 
|
 Dimensione 
|
 Intervallo 
|
 Descrizione 
|
|
------
|
-----------
|
-----------
|
-------------
|
|
 BOOL 
|
 1 bit 
|
 FALSE/TRUE 
|
 Valore booleano 
|
|
 BYTE 
|
 8 bit 
|
 0-255 
|
 Byte senza segno 
|
|
 WORD 
|
 16 bit 
|
 0-65535 
|
 Parola senza segno 
|
|
 DWORD 
|
 32 bit 
|
 0-4294967295 
|
 Doppia parola 
|
|
 LWORD 
|
 64 bit 
|
 0-18446744073709551615 
|
 Parola lunga 
|

### 1.2 Numeri Interi (Integers)

|
 Tipo 
|
 Dimensione 
|
 Intervallo 
|
 Descrizione 
|
|
------
|
-----------
|
-----------
|
-------------
|
|
 INT 
|
 16 bit 
|
 -32768 a 32767 
|
 Intero con segno 
|
|
 DINT 
|
 32 bit 
|
 -2147483648 a 2147483647 
|
 Intero doppio con segno 
|
|
 LINT 
|
 64 bit 
|
 ±9223372036854775807 
|
 Intero lungo con segno 
|
|
 UINT 
|
 16 bit 
|
 0-65535 
|
 Intero senza segno 
|
|
 UDINT 
|
 32 bit 
|
 0-4294967295 
|
 Intero doppio senza segno 
|
|
 ULINT 
|
 64 bit 
|
 0-18446744073709551615 
|
 Intero lungo senza segno 
|
```scl
// Dichiarazioni di interi
LOCAL "Counter" : INT := 0;
LOCAL "HighCounter" : DINT := 100000;
LOCAL "UnsignedValue" : UINT := 65535;
```

### 1.3 Numeri Floating-Point

|
 Tipo 
|
 Dimensione 
|
 Precisione 
|
 Intervallo 
|
|
------
|
-----------
|
-----------
|
-----------
|
|
 REAL 
|
 32 bit 
|
 ~7 cifre 
|
 ±1.175494e-38 a ±3.402823e+38 
|
|
 LREAL 
|
 64 bit 
|
 ~15 cifre 
|
 ±2.225073e-308 a ±1.797693e+308 
|
```scl
// Operazioni floating-point
LOCAL "Temperature" : REAL := 25.5;
LOCAL "Pressure" : LREAL := 1013.25;

"Result" := "Temperature" / 2.0;
"Average" := ("Value1" + "Value2" + "Value3") / 3.0;
```

**Nota importante**: Cuidado con la precisione in operazioni ripetitive

### 1.4 Timer e Tempo

|
 Tipo 
|
 Descrizione 
|
 Formato 
|
 Esempio 
|
|
------
|
-----------
|
---------
|
---------
|
|
 TIME 
|
 Intervallo di tempo 
|
 T# formato 
|
 T#5S, T#100MS 
|
|
 TIME_OF_DAY (TOD) 
|
 Ora del giorno 
|
 HH:MM:SS.MS 
|
 TOD#14:30:45.500 
|
|
 DATE (D) 
|
 Data 
|
 YYYY-MM-DD 
|
 D#2024-01-15 
|
|
 DATE_AND_TIME (DT) 
|
 Data e ora 
|
 Data + ora 
|
 DT#2024-01-15-14:30:45 
|
|
 S5TIME 
|
 Legacy timer 
|
 Formato Siemens 
|
 S5T#1S 
|
```scl
// Dichiarazioni di tempo
LOCAL "Delay" : TIME := T#2S;
LOCAL "LongDelay" : TIME := T#500MS;
LOCAL "ScheduledTime" : TOD := TOD#09:00:00;
```

### 1.5 Stringhe di Caratteri (Character Strings)
```scl
LOCAL "Message" : STRING := 'Hello World';
LOCAL "ShortString" : STRING[10] := 'Short';

// Operazioni su stringhe
"Output" := CONCAT("String1", "String2");
"Length" := LEN("MyString");
```

## 2. Tipi di Dati Complessi

### 2.1 ARRAY (Matrici)

Collezione di elementi dello stesso tipo
```scl
// Dichiarazione di array
LOCAL "IntArray" : ARRAY[0..9] OF INT;
LOCAL "BoolArray" : ARRAY[1..10] OF BOOL;

// Accesso agli elementi
"IntArray"[0] := 100;
"IntArray"[5] := "IntArray"[0] + 50;

// Array multidimensionali
LOCAL "Matrix" : ARRAY[0..9, 0..9] OF REAL;
"Matrix"[2, 3] := 3.14;
```

### 2.2 STRUCT - Strutture Anonime

Raggruppamento di variabili di tipi diversi
```scl
// Dichiarazione
LOCAL "MyStruct" : STRUCT
    "Field1" : INT;
    "Field2" : BOOL;
    "Field3" : REAL;
END_STRUCT;

// Accesso ai campi
"MyStruct"."Field1" := 100;
"MyStruct"."Field2" := TRUE;
"Result" := "MyStruct"."Field3" * 2.0;
```

### 2.3 PLC Data Types (UDT - User Defined Types)

Tipi di dati definiti dall'utente, riutilizzabili
```scl
// Dichiarazione di UDT (definita nel progetto)
LOCAL "MotorData" : MotorUDT;

// Accesso ai dati
"MotorData"."Speed" := 1500;
"MotorData"."Status" := TRUE;
```

### 2.4 Named Value Data Types (S7-1500)
```scl
// Enumerazione con nomi significativi
LOCAL "State" : OperatingState;  // enum definito

"State" := OperatingState#RUNNING;
"State" := OperatingState#STOPPED;
```

### 2.5 Puntatori

Riferimenti a variabili in memoria
```scl
// Dichiarazione di puntatore
LOCAL "PointerToInt" : POINTER TO INT;
LOCAL "PointerToArray" : POINTER TO ARRAY;

// Dereferenziamento
"PointerToInt"^ := 100;  // Assegna 100 alla variabile puntata
```

## 3. Parameter Types

Tipi di parametri per blocchi e funzioni

|
 Parametro 
|
 Descrizione 
|
 Utilizzo 
|
|
-----------
|
-----------
|
---------
|
|
 IN 
|
 Input - Valore in ingresso 
|
 Dati verso il blocco 
|
|
 OUT 
|
 Output - Valore in uscita 
|
 Risultati dal blocco 
|
|
 IN_OUT 
|
 Input/Output - Bidirezionale 
|
 Modifica il valore originale 
|
|
 STATIC 
|
 Statico - Mantiene valore 
|
 Tra cicli di esecuzione 
|
|
 TEMP 
|
 Temporaneo - Locale al blocco 
|
 Solo durante esecuzione 
|
```scl
// Dichiarazione parametri
DECLARE
    IN "Input1" : INT;
    IN "Input2" : REAL;
    OUT "Output" : BOOL;
    IN_OUT "Counter" : INT;
    STATIC "LastValue" : INT := 0;
    TEMP "LocalVar" : REAL;
END_DECLARE;
```

## 4. System Data Types

Tipi di dati di sistema speciali
```scl
// Per operazioni specifiche del sistema
LOCAL "BlockInterface" : VARIANT;
LOCAL "SystemTime" : DT;
LOCAL "TimerValue" : S5TIME;
```

## 5. Hardware Data Types

Tipi per accesso diretto all'hardware
```scl
LOCAL "InputByte" : IB 0;     // Byte ingresso 0
LOCAL "OutputByte" : QB 0;    // Byte uscita 0
LOCAL "MemoryBit" : M 0.0;    // Bit memoria 0.0
```

## 6. Conversione Tipi di Dati

### 6.1 Conversione Automatica
Il compilatore converte automaticamente quando possibile
```scl
"IntValue" : INT := 100;
"RealValue" : REAL;

"RealValue" := "IntValue";  // INT convertito a REAL: 100.0
```

### 6.2 Conversione Esplicita

#### Per S7-1500
```scl
"Result" : DINT := INT_TO_DINT("IntValue");
"Text" := INT_TO_STRING("Number");
"Float" := INT_TO_REAL("IntValue");
```

#### Per S7-1200
```scl
"Result" : DINT := EXTEND("IntValue");
"Float" := FLOAT("IntValue");
```

#### Per S7-300/S7-400
```scl
"ConvertedValue" := CONVD("SourceValue");
```

## 7. Best Practices per i Tipi di Dati

1. **Scegli il tipo appropriato**: Usa INT per contatori, REAL per calcoli, BOOL per stati
2. **Evita conversioni non necessarie**: Riducono performance
3. **Documenta UDT complessi**: Spiega il significato di ogni campo
4. **Usa array quando appropriato**: Evita di creare 10 variabili separate
5. **STRUCT per dati correlati**: Raggruppa logicamente i dati
6. **Floating-point cautela**: Considera problemi di precisione in cicli
```scl
// ✓ Buono: Struttura logica
LOCAL "MotorStatus" : STRUCT
    "Running" : BOOL;
    "Speed" : INT;
    "Temperature" : REAL;
END_STRUCT;

// ✗ Cattivo: Variabili sparse
LOCAL "MotorRunning" : BOOL;
LOCAL "MotorSpeed" : INT;
LOCAL "MotorTemp" : REAL;
```
📄 DOCUMENTO 3: SCL_03_BIT_AND_LOGIC_OPERATIONS.md
markdown
# Operazioni Logiche e di Bit in SCL

## 1. Operazioni Logiche di Bit

### 1.1 Funzioni di Trigger per Segnali

#### R_TRIG: Detect Positive Signal Edge
Rileva il passaggio da 0 a 1
```scl
// Dichiarazione
LOCAL "EdgeDetector" : R_TRIG;

// Utilizzo
"EdgeDetector"(CLK := "InputSignal", Q => "EdgeDetected");

// Parametri:
// CLK : BOOL - Segnale in ingresso
// Q : BOOL - Output TRUE al rilevamento del fronte positivo
```

**Uso pratico**:
```scl
// Incrementa contatore solo al fronte positivo
"MyTrigger"(CLK := "PushButton", Q => "EdgeOutput");
IF "EdgeOutput" THEN
    "Counter" := "Counter" + 1;
END IF;
```

#### F_TRIG: Detect Negative Signal Edge
Rileva il passaggio da 1 a 0
```scl
// Dichiarazione
LOCAL "FallingEdge" : F_TRIG;

// Utilizzo
"FallingEdge"(CLK := "InputSignal", Q => "EdgeDetected");

// Parametri:
// CLK : BOOL - Segnale in ingresso
// Q : BOOL - Output TRUE al rilevamento del fronte negativo
```

**Uso pratico**:
```scl
// Conteggia rilasci di pulsante
"ReleaseTrigger"(CLK := "PushButton", Q => "ReleaseDetected");
IF "ReleaseDetected" THEN
    "ReleaseCount" := "ReleaseCount" + 1;
END IF;
```

## 2. Operazioni Logiche Standard

### 2.1 Operatori AND, OR, NOT, XOR
```scl
// AND logico
"Result" := "Input1" AND "Input2";

// OR logico
"Result" := "Input1" OR "Input2";

// NOT logico (negazione)
"Result" := NOT "Input";

// XOR logico (exclusive OR)
"Result" := "Input1" XOR "Input2";

// Combinazioni complesse
"Output" := ("A" AND "B") OR (NOT "C" AND "D");
```

### 2.2 Tabelle di Verità

|
 A 
|
 B 
|
 AND 
|
 OR 
|
 XOR 
|
 NOT A 
|
|
---
|
---
|
-----
|
----
|
----
|
-------
|
|
 0 
|
 0 
|
 0   
|
 0  
|
 0  
|
 1     
|
|
 0 
|
 1 
|
 0   
|
 1  
|
 1  
|
 1     
|
|
 1 
|
 0 
|
 0   
|
 1  
|
 1  
|
 0     
|
|
 1 
|
 1 
|
 1   
|
 1  
|
 0  
|
 0     
|

## 3. Precedenza degli Operatori

Ordine di valutazione (dal più alto al più basso):

1. **Parentesi** `()`
2. **Negazione** `NOT`
3. **Moltiplicazione/Divisione** `*`, `/`
4. **Addizione/Sottrazione** `+`, `-`
5. **Confronto** `=`, `<>`, `<`, `>`, `<=`, `>=`
6. **AND logico**
7. **XOR logico**
8. **OR logico**
```scl
// Esempi di precedenza
"A" AND "B" OR "C"        // = ("A" AND "B") OR "C"
"A" OR "B" AND "C"        // = "A" OR ("B" AND "C")
NOT "A" AND "B"           // = (NOT "A") AND "B"
"A" AND "B" = "C"         // = ("A" AND "B") = "C"

// Usa parentesi per chiarezza
"Result" := ("A" AND "B") OR ("C" AND NOT "D");
```

## 4. Operazioni di Comparazione

Restituiscono valori booleani
```scl
// Uguaglianza
"AreEqual" := "Value1" = "Value2";

// Disuguaglianza
"NotEqual" := "Value1" <> "Value2";

// Minore/Maggiore
"IsSmaller" := "Value1" < "Value2";
"IsGreater" := "Value1" > "Value2";

// Minore o uguale / Maggiore o uguale
"IsSmallEqual" := "Value1" <= "Value2";
"IsGreatEqual" := "Value1" >= "Value2";

// Combinazioni
"InRange" := ("Value" >= 0) AND ("Value" <= 100);
```

## 5. Operazioni Bitwise (Word Logic Operations)

Operazioni bit-per-bit su parole intere
```scl
// AND bitwise su word/dword
"Result" : WORD := "Input1" AND "Input2";

// OR bitwise
"Result" : WORD := "Input1" OR "Input2";

// XOR bitwise
"Result" : WORD := "Input1" XOR "Input2";

// Inversione bitwise (NOT)
"Result" : WORD := NOT "Input";
```

**Esempio pratico - Mascheratura di bit**:
```scl
// Estrai bit 0-3 usando mascheratura
LOCAL "InputWord" : WORD := 0xABCD;
LOCAL "Mask" : WORD := 0x000F;
LOCAL "LowerNibble" : WORD;

"LowerNibble" := "InputWord" AND "Mask";  // Risultato: 0x000D
```

## 6. Operazioni di Shift (Shift and Rotate)

### 6.1 SHL - Shift Left (Scorrimento a Sinistra)

Sposta i bit verso sinistra, aggiunge 0 a destra
```scl
// SHL_W per WORD
"Result" : WORD := SHL_W("Input", 3);  // Sposta 3 posizioni sinistra

// Equivale a moltiplicare per 2^n
// SHL_W(0b00000101, 2) = 0b00010100 (5 * 4 = 20)
```

### 6.2 SHR - Shift Right (Scorrimento a Destra)

Sposta i bit verso destra, aggiunge 0 a sinistra
```scl
// SHR_W per WORD
"Result" : WORD := SHR_W("Input", 2);  // Sposta 2 posizioni destra

// Equivale a dividere per 2^n (con troncamento)
// SHR_W(0b00010100, 2) = 0b00000101 (20 / 4 = 5)
```

### 6.3 ROL - Rotate Left (Rotazione a Sinistra)

Ruota i bit verso sinistra, il bit più a sinistra torna a destra
```scl
// ROL_W per WORD (16 bit)
"Result" : WORD := ROL_W("Input", 4);

// Esempio: 0b1001_0000_0000_0000 ruotato 4 posizioni
//          0b0000_0000_0000_1001
```

### 6.4 ROR - Rotate Right (Rotazione a Destra)

Ruota i bit verso destra, il bit più a destra torna a sinistra
```scl
// ROR_W per WORD
"Result" : WORD := ROR_W("Input", 3);

// Esempio: 0b0000_0001 ruotato 1 posizione
//          0b1000_0000
```

### 6.5 Dimensioni di Shift/Rotate

|
 Funzione 
|
 Tipo 
|
 Dimensione 
|
|
----------
|
------
|
-----------
|
|
 SHL_W, SHR_W, ROL_W, ROR_W 
|
 WORD 
|
 16 bit 
|
|
 SHL_DW, SHR_DW, ROL_DW, ROR_DW 
|
 DWORD 
|
 32 bit 
|
|
 SHL_LW, SHR_LW, ROL_LW, ROR_LW 
|
 LWORD 
|
 64 bit 
|

## 7. Casi di Utilizzo Pratici

### 7.1 Maschera di Bit per Estrazione
```scl
// Estrai stato di specifici bit
LOCAL "SystemStatus" : WORD := 0x5A3F;
LOCAL "Bit5_8" : WORD := ("SystemStatus" SHR 5) AND 0x0F;
```

### 7.2 Impostazione/Cancellazione di Bit
```scl
// Imposta bit 3
LOCAL "Value" : WORD := 0x0000;
"Value" := "Value" OR 0x0008;  // Risultato: 0x0008

// Cancella bit 5
"Value" := "Value" AND NOT 0x0020;
```

### 7.3 Inversione di Stato
```scl
// Toggle (inverti) bit usando XOR
LOCAL "Toggle" : BOOL := FALSE;
"Toggle" := "Toggle" XOR TRUE;  // Inverti il valore
```

## 8. Best Practices

1. **Usa parentesi** per chiarezza sugli ordini di operazione
2. **Evita operazioni logiche troppo complesse**: Dividi in step più semplici
3. **Documenta la logica bitwise**: È facile da sbagliare
4. **Usa costanti hex per maschere**: `0xFFFF` è più chiaro di `65535`
5. **Testa la precedenza**: Quando in dubbio, aggiungi parentesi
```scl
// ✓ Buono: Chiaro e leggibile
"Enable" := ("ManualMode" OR "AutoMode") AND "SystemReady" AND NOT "Error";

// ✗ Cattivo: Difficile da leggere
"Enable" := "ManualMode" OR "AutoMode" AND "SystemReady" AND NOT "Error";
```
📄 DOCUMENTO 4: SCL_04_TIMER_OPERATIONS.md
markdown
# Operazioni Timer in SCL

## 1. Chiamata di Timer IEC (IEC Standard Timers)

### 1.1 Dichiarazione di Timer

I timer IEC possono essere dichiarati come:

#### Option 1: Array di Timer
```scl
// Dichiarazione in interfaccia blocco
DECLARE
    STATIC "MyTIMERArray" : ARRAY[0..1] OF IEC_TIMER;
END_DECLARE;

// Nel codice:
"MyTIMERArray"[0].TON(IN := "Enable", PT := T#5S, Q => "Output");
"MyTIMERArray"[1].TOF(IN := "Enable", PT := T#2S, Q => "Output");
```

#### Option 2: Timer in Struttura
```scl
DECLARE
    STATIC "MyStruct" : STRUCT
        "FirstTimer" : IEC_TIMER;
        "PT" : TIME;
        "ET" : TIME;
        "IN" : BOOL;
        "Q" : BOOL;
    END_STRUCT;
END_DECLARE;

// Utilizzo:
"MyStruct"."FirstTimer".TON(IN := "MyStruct"."IN", 
                             PT := "MyStruct"."PT", 
                             Q => "MyStruct"."Q");
```

#### Option 3: Timer in Blocco Dati Globale
```scl
// Dichiarazione in data block
"MyTimer" : IEC_TIMER;

// Utilizzo nel programma:
"MyTimer".TON(IN := "Trigger", PT := T#1S, Q => "Output");
```

### 1.2 Parametri Timer IEC

Struttura di un timer IEC:
```
IEC_TIMER contiene:
├── IN (BOOL) - Ingresso di controllo
├── PT (TIME) - Preset Time (durata desiderata)
├── Q (BOOL) - Output dello stato
└── ET (TIME) - Elapsed Time (tempo trascorso)
```

## 2. TP: Generate Pulse (Timer Impulso)

Genera un impulso di durata fissa quando l'ingresso diventa TRUE
```scl
// Dichiarazione
DECLARE
    STATIC "PulseTimer" : TP;
END_DECLARE;

// Utilizzo
"PulseTimer"(IN := "Trigger", PT := T#100MS, Q => "Pulse", ET => "ElapsedTime");
```

### Parametri TP:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 IN 
|
 BOOL 
|
 Ingresso di attivazione 
|
|
 PT 
|
 TIME 
|
 Durata dell'impulso (Preset Time) 
|
|
 Q 
|
 BOOL 
|
 Output (TRUE per durata PT) 
|
|
 ET 
|
 TIME 
|
 Tempo trascorso 
|

### Cronogramma TP:
```
IN:  ──┐       ┌──────────────────
       └───────┘

Q:   ──┐─────┐  ┐─────┐
     ──┘     └──┘     └──
        PT      PT
```

### Esempio pratico:
```scl
// Genera impulso di 200ms al premere pulsante
"ImpulseGen"(IN := "Button", PT := T#200MS, Q => "LampPulse");
```

## 3. TON: Generate On-Delay (Ritardo alla chiusura)

Generatore di ritardo alla chiusura. Manda segnale TRUE dopo PT secondi di ingresso TRUE
```scl
DECLARE
    STATIC "OnDelayTimer" : TON;
END_DECLARE;

// Utilizzo
"OnDelayTimer"(IN := "Enable", PT := T#5S, Q => "Delayed", ET => "Elapsed");
```

### Parametri TON:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 IN 
|
 BOOL 
|
 Ingresso di attivazione 
|
|
 PT 
|
 TIME 
|
 Ritardo desiderato 
|
|
 Q 
|
 BOOL 
|
 Output (FALSE finché timer non scade) 
|
|
 ET 
|
 TIME 
|
 Tempo trascorso 
|

### Cronogramma TON:
```
IN:  ──┐           ┌───────────────
     ──┘           └───────────────

Q:   ──────────┐
     ──────────┘
              PT

Delay di PT secondi prima che Q vada a TRUE
```

### Caso d'uso - Protezione da contatti rimbalzanti:
```scl
// Attendi che il segnale sia stabile per 50ms
"DebounceTimer"(IN := "RawInput", PT := T#50MS, Q => "StableInput", ET => "DebounceTime");

IF "StableInput" THEN
    "Action" := 1;
END IF;
```

## 4. TOF: Generate Off-Delay (Ritardo alla apertura)

Mantiene OUTPUT TRUE per PT secondi dopo che INPUT diventa FALSE
```scl
DECLARE
    STATIC "OffDelayTimer" : TOF;
END_DECLARE;

// Utilizzo
"OffDelayTimer"(IN := "Enable", PT := T#3S, Q => "Output", ET => "Elapsed");
```

### Cronogramma TOF:
```
IN:  ──┐           ┌───────────────
     ──┘           └───────────────

Q:   ──┐                   ┐
     ──┴───────────────────┘
                  PT

Output rimane TRUE per PT secondi dopo che INPUT diventa FALSE
```

### Caso d'uso - Tempo di raffreddamento:
```scl
// Mantieni ventola accesa per 60 secondi dopo arresto motore
"CoolingTimer"(IN := "MotorRunning", PT := T#60S, Q => "FanRunning");
```

## 5. TONR: Time Accumulator (Accumulatore di Tempo)

Accumula il tempo in cui l'ingresso è TRUE. Non resetta quando IN va a FALSE
```scl
DECLARE
    STATIC "AccumulatorTimer" : TONR;
END_DECLARE;

// Utilizzo
"AccumulatorTimer"(IN := "Running", PT := T#1H, Q => "TimedOut", ET => "TotalTime");
```

### Cronogramma TONR:
```
IN:  ──┐    ┌──┐    ┌──────────────
     ──┘    └──┘    └──────────────

Q:   ──────────────────────┐
     ──────────────────────┘
                    PT (totale accumulato)

Accumula tempo, resetta solo con RESET_TIMER
```

### Caso d'uso - Conteggio ore di funzionamento:
```scl
// Accumula ore totali di funzionamento
"HoursCounter"(IN := "Equipment_Running", 
               PT := T#10000H,  // Max 10000 ore
               Q => "LifeExpired",
               ET => "TotalHours");
```

## 6. RESET_TIMER: Reset Timer

Resetta lo stato del timer e il tempo trascorso
```scl
// Resetta l'accumulatore
IF "Reset_Command" THEN
    RESET_TIMER("HoursCounter");
END IF;
```

### Parametro:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 Timer 
|
 IEC_TIMER 
|
 Istanza del timer da resettare 
|

## 7. PRESET_TIMER: Load Time Duration

Carica una nuova durata nel timer
```scl
// Imposta dinamicamente il tempo di ritardo
"NewDelay" : TIME := T#10S;
PRESET_TIMER("OnDelayTimer", "NewDelay");
```

### Parametri:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 Timer 
|
 IEC_TIMER 
|
 Istanza del timer 
|
|
 Value 
|
 TIME 
|
 Nuovo valore PT 
|

## 8. Formato TIME in SCL

### 8.1 Specifica del Tempo
```scl
T#5S            // 5 secondi
T#100MS         // 100 millisecondi
T#1M30S         // 1 minuto 30 secondi
T#2H            // 2 ore
T#1D2H3M4S      // 1 giorno 2 ore 3 minuti 4 secondi
T#1000MS        // 1000 millisecondi = 1 secondo
```

### 8.2 Variabili di Tipo TIME
```scl
LOCAL "TimerDelay" : TIME := T#5S;
LOCAL "DynamicTime" : TIME;

// Calcoli con TIME
"DynamicTime" := "TimerDelay" * 2;  // Raddoppia il tempo
```

## 9. Esempio Completo di Utilizzo Timer
```scl
// Applicazione reale: Sistema di controllo motore

DECLARE
    STATIC "StartTimer" : TON;        // Rampa di avvio
    STATIC "StabilityTimer" : TON;    // Verifica stabilità
    STATIC "LifetimeCounter" : TONR;  // Conteggio ore
END_DECLARE;

BEGIN
    // Timer 1: Attendi 5 secondi prima di avviare
    "StartTimer"(IN := "StartCommand", 
                 PT := T#5S, 
                 Q => "MotorCanStart");
    
    // Timer 2: Verifica stabilità per 2 secondi
    "StabilityTimer"(IN := "MotorRunning", 
                     PT := T#2S, 
                     Q => "IsStable");
    
    // Timer 3: Accumula ore di funzionamento
    "LifetimeCounter"(IN := "MotorRunning", 
                      PT := T#8000H,  // Manutenzione ogni 8000 ore
                      Q => "MaintenanceNeeded",
                      ET => "RunningHours");
    
    // Logica di controllo
    IF "MotorCanStart" AND "IsStable" THEN
        "MotorOutput" := 1;
    ELSE
        "MotorOutput" := 0;
    END IF;
    
    // Avviso manutenzione
    IF "MaintenanceNeeded" THEN
        "MaintenanceAlarm" := 1;
    END IF;
END;
```

## 10. Best Practices Timer

1. **Inizializza sempre i timer**: Dichiara con STATIC per mantenere stato
2. **Usa nomi significativi**: "DebounceTimer" è meglio di "Timer1"
3. **Documenta PT**: Commenta il significato di ogni timing
4. **Usa T# notation**: Più leggibile di millisecondi puri
5. **Attenzione a TOF**: Utile ma facile da confondere con TON
6. **TONR per conteggi**: Accumulare tempo totale
```scl
// ✓ Buono: Nomi chiari e commenti
"MotorStartDelay"(IN := "StartBtn


mancano alcune delle funzioni che sono elencate in gruppi in questa pagina




13 passaggi
continua da questa pagina: http://localhost:5111/en-us/tiaportal/ProgSCL2MenUS/15889037451/15889037451?api=V19




30 passaggi
📚 DOCUMENTAZIONE COMPLETA SCL - FUNZIONI E OPERAZIONI DI SISTEMA
Ho completato l'esplorazione sistematica della documentazione TIA Portal. Ecco i documenti MD completi divisi per argomenti:

📄 DOCUMENTO 5: SCL_05_COUNTER_OPERATIONS.md
markdown
# Operazioni Counter (Contatori) in SCL

## 1. Chiamata di Contatori IEC (Calling IEC Counters)

I contatori IEC possono essere dichiarati come array, in strutture anonime, o in blocchi dati globali.

### 1.1 Dichiarazione Contatori IEC

#### Array di Contatori
```scl
DECLARE
    STATIC "MyCounterArray" : ARRAY[0..1] OF IEC_COUNTER;
END_DECLARE;

// Utilizzo:
"MyCounterArray"[0].CTU(CU := "Input", R := "Reset", PV := 10, Q => "Output");
```

#### Struttura Anonima con Contatori
```scl
DECLARE
    STATIC "MyStruct" : STRUCT
        "FirstCounter" : IEC_COUNTER;
        "CU" : BOOL;
        "CD" : BOOL;
        "R" : BOOL;
        "PV" : INT;
        "Q" : BOOL;
        "CV" : INT;
    END_STRUCT;
END_DECLARE;

"MyStruct"."FirstCounter".CTU(CU := "MyStruct"."CU", 
                               R := "MyStruct"."R",
                               PV := "MyStruct"."PV",
                               Q => "MyStruct"."Q");
```

## 2. CTU: Count Up (Conteggio Ascendente)

Incrementa il valore di conteggio (CV) ogni volta che l'ingresso CU passa da 0 a 1.
```scl
DECLARE
    STATIC "UpCounter" : CTU;
END_DECLARE;

// Utilizzo
"UpCounter"(CU := "PulseInput", 
            R := "Reset", 
            PV := 20,           // Preset Value (massimo 20)
            Q => "OutputReady",
            CV => "CountValue");
```

### Parametri CTU:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 CU 
|
 BOOL 
|
 Count Up - Ingresso di conteggio 
|
|
 R 
|
 BOOL 
|
 Reset - Resetta il contatore a 0 
|
|
 PV 
|
 INT 
|
 Preset Value - Valore massimo da raggiungere 
|
|
 Q 
|
 BOOL 
|
 Output - TRUE quando CV >= PV 
|
|
 CV 
|
 INT 
|
 Current Value - Valore attuale di conteggio 
|

### Cronogramma CTU:
```
CU: ──┐  ┌─┐  ┌─┐  ┌─┐  ┌─┐
    ──┘──┘ └──┘ └──┘ └──┘ └───

CV: 0  1  2  3  4  5
            │
           PV=5
           
Q:  ─────┐
    ──────┘
```

### Caso d'uso - Contare pezzi prodotti:
```scl
"PieceCounter"(CU := "PieceDetected", 
               R := "ResetProduction",
               PV := 100,  // 100 pezzi per lotto
               Q => "LotComplete",
               CV => "PiecesProduced");

IF "LotComplete" THEN
    "Operator_Alarm" := 1;
END IF;
```

## 3. CTD: Count Down (Conteggio Discendente)

Decrementa il valore di conteggio ogni volta che l'ingresso CD passa da 0 a 1.
```scl
DECLARE
    STATIC "DownCounter" : CTD;
END_DECLARE;

// Utilizzo
"DownCounter"(CD := "PulseInput",
              LD := "LoadNewValue",
              PV := 50,
              Q => "CountCompleted",
              CV => "RemainingValue");
```

### Parametri CTD:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 CD 
|
 BOOL 
|
 Count Down - Ingresso di conteggio discendente 
|
|
 LD 
|
 BOOL 
|
 Load - Carica PV in CV 
|
|
 PV 
|
 INT 
|
 Preset Value - Valore iniziale da cui contare 
|
|
 Q 
|
 BOOL 
|
 Output - TRUE quando CV <= 0 
|
|
 CV 
|
 INT 
|
 Current Value - Valore attuale (decresce) 
|

### Cronogramma CTD:
```
CD: ──┐  ┌─┐  ┌─┐  ┌─┐
    ──┘──┘ └──┘ └──┘ └──

LD: ┌──┐ (carica PV in CV)
    └──┘

PV:  10
CV:  10  9  8  7  6
     
Q:              ─────┐
     ──────────────┘
                CV=0
```

### Caso d'uso - Conto alla rovescia per evento:
```scl
// Conteggio da 10 a 0
"CountdownTimer"(CD := "SecondPassed",
                 LD := "StartCountdown",
                 PV := 10,
                 Q => "TimeExpired",
                 CV => "TimeLeft");

// Visualizza tempo rimanente
"DisplayTime" := "TimeLeft";
```

## 4. CTUD: Count Up/Down (Conteggio Bidirezionale)

Conta sia in salita che in discesa a seconda dell'ingresso attivo.
```scl
DECLARE
    STATIC "BiDirectionalCounter" : CTUD;
END_DECLARE;

// Utilizzo
"BiDirectionalCounter"(CU := "IncreaseInput",
                       CD := "DecreaseInput",
                       R := "Reset",
                       LD := "Load",
                       PV := 100,
                       Q1 => "UpperLimit",  // TRUE quando CV >= PV
                       Q2 => "LowerLimit",  // TRUE quando CV < 0
                       CV => "CurrentValue);
```

### Parametri CTUD:

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 CU 
|
 BOOL 
|
 Count Up - Incrementa CV 
|
|
 CD 
|
 BOOL 
|
 Count Down - Decrementa CV 
|
|
 R 
|
 BOOL 
|
 Reset - Resetta CV a 0 
|
|
 LD 
|
 BOOL 
|
 Load - Carica PV in CV 
|
|
 PV 
|
 INT 
|
 Preset Value - Valore di riferimento 
|
|
 Q1 
|
 BOOL 
|
 Output Superiore - TRUE quando CV >= PV 
|
|
 Q2 
|
 BOOL 
|
 Output Inferiore - TRUE quando CV < 0 
|
|
 CV 
|
 INT 
|
 Current Value - Valore attuale 
|

### Cronogramma CTUD:
```
CU: ──┐     ┌─┐
    ──┘     └─┘

CD:     ┌─┐     ┌─┐
        └─┘     └─┘

CV:  0  1  0  1  2
     
Q1:               ─────┐ (se CV >= PV)
    ─────────────────┘

Q2:             ┌───── (se CV < 0)
    ─────────┘
```

### Caso d'uso - Controllo di livello con limite superiore e inferiore:
```scl
"LevelController"(CU := "InputIncreasing",
                  CD := "InputDecreasing",
                  R := "ResetLevel",
                  LD := "Calibrate",
                  PV := 100,  // Limite superiore
                  Q1 => "LevelTooHigh",
                  Q2 => "LevelTooLow",
                  CV => "CurrentLevel");

// Logica di controllo
IF "LevelTooHigh" THEN
    "PumpOff" := 1;
ELSIF "LevelTooLow" THEN
    "PumpOn" := 1;
END IF;
```

## 5. Struttura IEC_COUNTER

Un contatore IEC contiene:
```
IEC_COUNTER
├── CU (BOOL) - Count Up pulse input
├── CD (BOOL) - Count Down pulse input
├── R (BOOL) - Reset
├── LD (BOOL) - Load Preset Value
├── PV (INT) - Preset Value
├── Q (BOOL) - Output
├── Q1 (BOOL) - Output Upper Limit (CTUD)
├── Q2 (BOOL) - Output Lower Limit (CTUD)
└── CV (INT) - Current Count Value
```

## 6. Confronto tra CTU, CTD, CTUD

|
 Funzione 
|
 Direzione 
|
 Reset 
|
 Load 
|
 Output 
|
 Uso Tipico 
|
|
----------
|
-----------
|
-------
|
------
|
--------
|
------------
|
|
 CTU 
|
 Solo su 
|
 Sì 
|
 No 
|
 1 uscita (Q) 
|
 Conteggio pezzi 
|
|
 CTD 
|
 Solo giù 
|
 No 
|
 Sì 
|
 1 uscita (Q) 
|
 Conto alla rovescia 
|
|
 CTUD 
|
 Su e giù 
|
 Sì 
|
 Sì 
|
 2 uscite (Q1, Q2) 
|
 Livelli, posizioni 
|

## 7. Esempio Completo: Sistema di Produzione
```scl
// Controllo linea produttiva

DECLARE
    STATIC "PieceCounter" : CTU;        // Conta pezzi prodotti
    STATIC "RejectionCounter" : CTU;    // Conta scarti
    STATIC "BatchCounter" : CTUD;       // Conta lotti
END_DECLARE;

BEGIN
    // Conta pezzi buoni
    "PieceCounter"(CU := "GoodPieceDetected",
                   R := "BatchReset",
                   PV := 1000,     // 1000 pezzi per lotto
                   Q => "LotFull",
                   CV => "ProducedCount");
    
    // Conta scarti
    "RejectionCounter"(CU := "RejectedPiece",
                       R := "BatchReset",
                       PV := 50,      // Allarme oltre 50 scarti
                       Q => "TooManyRejects",
                       CV => "RejectionCount");
    
    // Conta lotti
    "BatchCounter"(CU := "LotFull",
                   CD := "LotShipped",
                   R := "ResetBatchCount",
                   PV := 5,         // 5 lotti per pallet
                   Q1 => "PalletFull",
                   Q2 => "NoBatches",
                   CV => "LotCount");
    
    // Logica di controllo
    IF "LotFull" THEN
        "StopProduction" := 1;
        "QualityCheck" := 1;
    END IF;
    
    IF "TooManyRejects" THEN
        "MaintenanceAlarm" := 1;
    END IF;
    
    IF "PalletFull" THEN
        "CallForShipping" := 1;
    END IF;
END;
```

## 8. Best Practices per Contatori

1. **Inizializza sempre**: Usa STATIC per mantenere lo stato
2. **Documenta PV**: Spiega il significato del valore di conteggio
3. **Scegli il tipo giusto**: CTU per conteggio, CTD per conto alla rovescia, CTUD per bidirezionali
4. **Gestisci il reset**: Decidi quando ripristinare a 0
5. **Monitora overflow**: Attento al raggiungimento di MAX INT (2147483647)
6. **Usa strutture**: Raggruppa contatori correlati
```scl
// ✓ Buono: Struttura logica
DECLARE
    STATIC "ProductionMetrics" : STRUCT
        "GoodParts" : CTU;
        "DefectiveParts" : CTU;
        "TotalProduced" : CTUD;
    END_STRUCT;
END_DECLARE;

// ✗ Cattivo: Contatori sparsi
DECLARE
    STATIC "Counter1" : CTU;
    STATIC "Counter2" : CTU;
    STATIC "Counter3" : CTUD;
END_DECLARE;
```
📄 DOCUMENTO 6: SCL_06_MATH_AND_CONVERSION.md
markdown
# Funzioni Matematiche e Conversione in SCL

## 1. Funzioni Matematiche Standard

### 1.1 Operazioni di Base

#### ABS: Absolute Value (Valore Assoluto)
Restituisce il valore assoluto di un numero
```scl
"Result" : INT := ABS(-25);           // Risultato: 25
"AbsValue" : REAL := ABS(-3.14159);   // Risultato: 3.14159
```

#### MIN: Minimum Value (Valore Minimo)
Restituisce il valore minore tra due o più numeri
```scl
"Smallest" : INT := MIN(10, 5, 20);        // Risultato: 5
"LowerTemp" : REAL := MIN("Temp1", "Temp2");
```

#### MAX: Maximum Value (Valore Massimo)
Restituisce il valore maggiore tra due o più numeri
```scl
"Largest" : INT := MAX(10, 5, 20);    // Risultato: 20
"HigherPressure" : REAL := MAX("P1", "P2", "P3");
```

#### LIMIT: Limit Value Between Range
Limita un valore entro un intervallo specificato
```scl
"LimitedValue" : INT := LIMIT(5, 1, 10);      // Risultato: 5
"LimitedValue" : INT := LIMIT(15, 1, 10);     // Risultato: 10
"LimitedValue" : INT := LIMIT(-5, 1, 10);     // Risultato: 1

// Uso pratico: limitare velocità motore
"MotorSpeed" := LIMIT("DesiredSpeed", 0, 3000);  // 0-3000 RPM
```

### 1.2 Funzioni Radice e Potenza

#### SQR: Square (Quadrato)
Elevaa al quadrato un numero
```scl
"Squared" : REAL := SQR(5.0);    // Risultato: 25.0
"Area" := SQR("Radius");          // Quadrato del raggio
```

#### SQRT: Square Root (Radice Quadrata)
Calcola la radice quadrata
```scl
"SquareRoot" : REAL := SQRT(25.0);   // Risultato: 5.0
"Hypotenuse" := SQRT("A"*"A" + "B"*"B");  // Teorema Pitagora
```

### 1.3 Funzioni Trigonometriche

#### SIN: Sine (Seno)
Calcola il seno (argomento in radianti)
```scl
"Sine" : REAL := SIN(0.0);           // Risultato: 0.0
"Sine" : REAL := SIN(1.5707963);     // π/2, Risultato: 1.0
```

#### COS: Cosine (Coseno)
Calcola il coseno (argomento in radianti)
```scl
"Cosine" : REAL := COS(0.0);         // Risultato: 1.0
"Cosine" : REAL := COS(3.1415926);   // π, Risultato: -1.0
```

#### TAN: Tangent (Tangente)
Calcola la tangente (argomento in radianti)
```scl
"Tangent" : REAL := TAN(0.7853981);  // π/4, Risultato: 1.0
```

#### ASIN: Arcsine (Arcoseno)
Calcola l'arcoseno (restituisce radianti)
```scl
"Angle" : REAL := ASIN(0.5);  // Risultato: 0.5236 (30°)
"Angle" : REAL := ASIN(1.0);  // Risultato: 1.5708 (90°)
```

#### ACOS: Arccosine (Arcocoseno)
Calcola l'arcocoseno (restituisce radianti)
```scl
"Angle" : REAL := ACOS(0.5);   // Risultato: 1.0472 (60°)
"Angle" : REAL := ACOS(-1.0);  // Risultato: 3.1416 (180°)
```

#### ATAN: Arctangent (Arcotangente)
Calcola l'arcotangente (restituisce radianti)
```scl
"Angle" : REAL := ATAN(1.0);   // Risultato: 0.7854 (45°)
```

### 1.4 Funzioni Logaritmiche ed Esponenziali

#### LN: Natural Logarithm (Logaritmo Naturale)
Calcola il logaritmo naturale (base e)
```scl
"Logarithm" : REAL := LN(1.0);       // Risultato: 0.0
"Logarithm" : REAL := LN(2.71828);   // e, Risultato: ~1.0
```

#### EXP: Exponential (Esponenziale)
Calcola e elevato alla potenza specificata
```scl
"Exponential" : REAL := EXP(0.0);    // Risultato: 1.0
"Exponential" : REAL := EXP(1.0);    // Risultato: 2.71828 (e)
```

## 2. Funzioni di Conversione Numeriche

### 2.1 Conversioni Fondamentali

#### CONVERT (o funzioni tipo INT_TO_REAL)
Converte tra tipi di dati

**Per S7-1500:**
```scl
// INT a DINT
"Result" : DINT := INT_TO_DINT(100);

// INT a REAL
"Result" : REAL := INT_TO_REAL(100);

// REAL a INT
"Result" : INT := REAL_TO_INT(3.14);  // Trunca: 3

// DINT a INT
"Result" : INT := DINT_TO_INT(50000);

// DINT a REAL
"Result" : REAL := DINT_TO_REAL(100000);

// REAL a DINT
"Result" : DINT := REAL_TO_DINT(123.45);

// LREAL a REAL
"Result" : REAL := LREAL_TO_REAL(3.14159265);
```

**Per S7-1200:**
```scl
// Usa EXTEND per espandere
"Result" : DINT := EXTEND(100);  // INT a DINT

// Usa FLOAT per convertire a REAL
"Result" : REAL := FLOAT(100);   // INT a REAL

// Usa funzioni dirette
"Result" : INT := INT(3.14);     // REAL a INT
```

### 2.2 Conversioni Avanzate

#### ROUND: Round Numerical Value (Arrotondamento)
Arrotonda un numero al valore intero più vicino
```scl
"Rounded" : DINT := ROUND(3.4);    // Risultato: 3
"Rounded" : DINT := ROUND(3.5);    // Risultato: 4
"Rounded" : DINT := ROUND(3.6);    // Risultato: 4
```

#### CEIL: Ceiling (Arrotonda per Eccesso)
Arrotonda al numero intero superiore
```scl
"Ceiling" : DINT := CEIL(3.1);    // Risultato: 4
"Ceiling" : DINT := CEIL(3.9);    // Risultato: 4
```

#### FLOOR: Floor (Arrotonda per Difetto)
Arrotonda al numero intero inferiore
```scl
"Floor" : DINT := FLOOR(3.9);     // Risultato: 3
"Floor" : DINT := FLOOR(3.1);     // Risultato: 3
```

#### TRUNC: Truncate (Tronca)
Rimuove la parte decimale
```scl
"Truncated" : DINT := TRUNC(3.9);     // Risultato: 3
"Truncated" : DINT := TRUNC(-3.9);    // Risultato: -3
```

### 2.3 Conversioni di Scala

#### SCALE_X: Scale (Ridimensiona)
Scala un valore da un intervallo a un altro
```scl
"Scaled" : REAL := SCALE_X("Input", 0.0, 100.0, 0.0, 10.0);
// Mappa Input da intervallo [0, 100] a intervallo [0, 10]
```

#### NORM_X: Normalize (Normalizza)
Normalizza un valore entro un intervallo specificato
```scl
"Normalized" : REAL := NORM_X("Input", 0.0, 100.0, 0.0, 1.0);
// Mappa Input da [0, 100] a [0, 1]
```

## 3. Funzioni di Comparazione Avanzate

### 3.1 Type Checking Functions

#### TYPEOF: Get Type (Ottieni Tipo)
Restituisce il tipo di una variabile
```scl
// S7-1500 only
"VarType" := TYPEOF("MyVariable");
```

#### TYPEOFELEMENTS: Check ARRAY Element Type
Verifica il tipo degli elementi di un array
```scl
// Controlla se gli elementi di un array sono di tipo INT
"IsIntArray" := TYPEOFELEMENTS("MyArray", INT);
```

#### IS_ARRAY: Check for ARRAY
Verifica se una variabile è un array
```scl
// TRUE se "MyVar" è un array
"IsArrayType" := IS_ARRAY("MyVar");
```

#### TYPEOFDB: Query Data Type of a DB
Verifica il tipo di dati di un blocco dati
```scl
// S7-1500 only
"DBType" := TYPEOFDB("DataBlockName");
```

## 4. Tabella Riepilogativa Funzioni

|
 Funzione 
|
 Descrizione 
|
 Parametri 
|
 Risultato 
|
|
----------
|
-----------
|
-----------
|
----------
|
|
 ABS 
|
 Valore assoluto 
|
 INT/REAL 
|
 INT/REAL 
|
|
 MIN 
|
 Minimo 
|
 Variabile 
|
 Tipo stesso 
|
|
 MAX 
|
 Massimo 
|
 Variabile 
|
 Tipo stesso 
|
|
 LIMIT 
|
 Limita intervallo 
|
 3 parametri 
|
 Tipo parametro 
|
|
 SQR 
|
 Quadrato 
|
 REAL 
|
 REAL 
|
|
 SQRT 
|
 Radice quadrata 
|
 REAL 
|
 REAL 
|
|
 SIN, COS, TAN 
|
 Trigonometriche 
|
 REAL (radianti) 
|
 REAL 
|
|
 ASIN, ACOS, ATAN 
|
 Inv. Trigon. 
|
 REAL 
|
 REAL (radianti) 
|
|
 LN 
|
 Log naturale 
|
 REAL 
|
 REAL 
|
|
 EXP 
|
 Esponenziale 
|
 REAL 
|
 REAL 
|
|
 ROUND, CEIL, FLOOR 
|
 Arrotondamenti 
|
 REAL 
|
 DINT 
|
|
 TRUNC 
|
 Troncamento 
|
 REAL 
|
 DINT 
|
|
 SCALE_X, NORM_X 
|
 Scaling 
|
 5 parametri 
|
 REAL 
|

## 5. Esempio Pratico: Controllo Temperatura
```scl
// Controllo riscaldamento con logica matematica

DECLARE
    STATIC "DesiredTemp" : REAL := 25.0;
    STATIC "CurrentTemp" : REAL;
    STATIC "MinTemp" : REAL := 15.0;
    STATIC "MaxTemp" : REAL := 35.0;
    STATIC "SmoothTemp" : REAL;
END_DECLARE;

BEGIN
    // Leggi sensore temperatura
    "CurrentTemp" := "TemperatureSensor";
    
    // Limita tra minimo e massimo
    "CurrentTemp" := LIMIT("CurrentTemp", "MinTemp", "MaxTemp");
    
    // Calcola differenza temperatura
    "TempDifference" : REAL := ABS("DesiredTemp" - "CurrentTemp");
    
    // Applica controllo proporzionale (PID semplificato)
    "HeatingPower" : REAL := LIMIT("TempDifference" * 10.0, 0.0, 100.0);
    
    // Usa funzioni trigonometriche per soft-start rampa
    "RampPhase" := LIMIT("TimeRunning" / 100.0, 0.0, 1.0);
    "SoftStartFactor" : REAL := SIN("RampPhase" * 1.5708);  // 0 a π/2
    
    // Output finale
    "HeaterOutput" := "HeatingPower" * "SoftStartFactor";
    
    // Allarmi
    IF "CurrentTemp" > "MaxTemp" THEN
        "OverheatAlarm" := 1;
    END IF;
    
    IF "CurrentTemp" < "MinTemp" THEN
        "UnderheatAlarm" := 1;
    END IF;
END;
```

## 6. Best Practices

1. **Attento ai radianti**: Funzioni trigonometriche usano radianti, non gradi
2. **Overflow in sqrt**: SQRT di numeri negativi causa errore
3. **Logaritmo di zero**: LN(0) causa errore
4. **Precisione floating-point**: Usa tolleranze nei confronti di REAL
5. **Tipo di ritorno**: Conosci sempre il tipo di risultato della funzione
6. **Performance**: Evita calcoli trigonometrici in loop stretti
```scl
// ✓ Buono: Chiarezza e range checking
IF "Value" >= 0.0 THEN
    "SquareRoot" := SQRT("Value");
ELSE
    "SquareRoot" := 0.0;  // Gestisci caso negativo
END IF;

// ✗ Cattivo: Nessun controllo
"SquareRoot" := SQRT("Value");  // Potrebbe crashes se negativo
```
📄 DOCUMENTO 7: SCL_07_MOVE_AND_ADVANCED_OPS.md
markdown
# Operazioni Move e Operazioni Avanzate in SCL

## 1. Operazioni Move (Spostamento Dati)

### 1.1 MOVE_BLK: Move Block (Sposta Blocco di Dati)

Copia un blocco contiguo di dati da un'area all'altra
```scl
// Dichiarazione source e destination array
LOCAL "SourceArray" : ARRAY[0..9] OF INT;
LOCAL "DestArray" : ARRAY[0..9] OF INT;

// Copia intero array
MOVE_BLK(SRC := "SourceArray", 
         DEST := "DestArray", 
         COUNT := 10);
```

**Parametri:**

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 SRC 
|
 Indirizzo 
|
 Indirizzo sorgente (primo elemento) 
|
|
 DEST 
|
 Indirizzo 
|
 Indirizzo destinazione 
|
|
 COUNT 
|
 DWORD 
|
 Numero di elementi da copiare 
|

**Caso d'uso:**
```scl
// Backup di dati attuali
LOCAL "CurrentValues" : ARRAY[0..99] OF REAL;
LOCAL "BackupValues" : ARRAY[0..99] OF REAL;

MOVE_BLK(SRC := ADR("CurrentValues"),
         DEST := ADR("BackupValues"),
         COUNT := 100);
```

### 1.2 MOVE_BLK_VARIANT: Move Block with Variant
Sposta blocchi con tipi variant
```scl
// Copia dati variant
MOVE_BLK_VARIANT(SRC := "SourceVariant",
                 DEST := "DestVariant",
                 COUNT := 50);
```

### 1.3 UMOVE_BLK: Uninterruptible Move Block
Sposta blocco senza interruzioni (atomico)
```scl
// Operazione critica senza interruzioni
UMOVE_BLK(SRC := ADR("CriticalData"),
          DEST := ADR("BackupData"),
          COUNT := 100);
```

### 1.4 FILL_BLK: Fill Block (Riempie Blocco)

Riempie un'area di memoria con un valore specifico
```scl
// Inizializza array a 0
LOCAL "DataArray" : ARRAY[0..49] OF INT;

FILL_BLK(DEST := ADR("DataArray"),
         FILL := 0,
         COUNT := 50);
```

**Parametri:**

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 DEST 
|
 Indirizzo 
|
 Indirizzo destinazione 
|
|
 FILL 
|
 BYTE 
|
 Valore di riempimento 
|
|
 COUNT 
|
 DWORD 
|
 Numero di byte da riempire 
|

### 1.5 UFILL_BLK: Uninterruptible Fill Block
Riempie un blocco atomicamente
```scl
// Cancella memoria critica senza interruzioni
UFILL_BLK(DEST := ADR("SecureArea"),
          FILL := 0xFF,
          COUNT := 100);
```

## 2. Operazioni Scatter/Gather (Estrazione/Assemblamento Bit)

### 2.1 SCATTER: Parse Bit Sequence into Individual Bits
Estrae bit individuali da una sequenza
```scl
// Estrai bit specifici da una word
LOCAL "InputWord" : WORD := 0xABCD;
LOCAL "BitArray" : ARRAY[0..15] OF BOOL;

SCATTER(SRC := "InputWord",
        DEST := "BitArray");

// Ora BitArray[0..15] contiene i singoli bit di InputWord
```

**Parametri:**

|
 Parametro 
|
 Tipo 
|
 Descrizione 
|
|
-----------
|
------
|
-----------
|
|
 SRC 
|
 BYTE/WORD/DWORD 
|
 Valore sorgente 
|
|
 DEST 
|
 ARRAY OF BOOL 
|
 Array destinazione bit 
|

### 2.2 SCATTER_BLK: Parse Block of Bits
Estrae bit da un intero blocco
```scl
// Estrai bit da array di byte
LOCAL "ByteArray" : ARRAY[0..9] OF BYTE;
LOCAL "BitArray" : ARRAY[0..79] OF BOOL;

SCATTER_BLK(SRC := ADR("ByteArray"),
            DEST := ADR("BitArray"),
            COUNT := 10);  // 10 byte = 80 bit
```

### 2.3 GATHER: Merge Individual Bits into Bit Sequence
Assembla bit individuali in una sequenza
```scl
// Assembla bit array in una word
LOCAL "BitArray" : ARRAY[0..15] OF BOOL;
LOCAL "OutputWord" : WORD;

GATHER(SRC := "BitArray",
       DEST => "OutputWord");

// OutputWord contiene i bit assembrati
```

### 2.4 GATHER_BLK: Merge Block of Bits
Assembla un intero blocco di bit
```scl
// Assembla 80 bit in 10 byte
LOCAL "BitArray" : ARRAY[0..79] OF BOOL;
LOCAL "ByteArray" : ARRAY[0..9] OF BYTE;

GATHER_BLK(SRC := ADR("BitArray"),
           DEST := ADR("ByteArray"),
           COUNT := 10);  // 10 byte output
```

## 3. Operazioni String Avanzate

### 3.1 Deserialize: Converti Dati Serializzati
Converte flusso di byte in tipo di dato
```scl
LOCAL "SerializedData" : ARRAY[0..9] OF BYTE;
LOCAL "StructData" : MyDataType;

DESERIALIZE(SRC := ADR("SerializedData"),
            SIZE := 10,
            DEST => "StructData");
```

### 3.2 Serialize: Serializza Dati
Converte tipo di dato in flusso di byte
```scl
LOCAL "StructData" : MyDataType;
LOCAL "SerializedData" : ARRAY[0..9] OF BYTE;

SERIALIZE(SRC := "StructData",
          DEST => ADR("SerializedData"),
          SIZE := 10);
```

## 4. Operazioni su Referenze (S7-1500)

### 4.1 REF: Create Reference (Crea Referenza a Tag)
Crea un riferimento a una variabile
```scl
LOCAL "TagReference" : REFERENCE TO INT;
LOCAL "MyInteger" : INT := 100;

"TagReference" := REF("MyInteger");

// Accedi al valore tramite referenza
"TagReference"^ := 200;  // MyInteger diventa 200
```

## 5. Operazioni su Array

### 5.1 ARRAY[*]: Array Element Access
Accesso a elementi di array multidimensionali
```scl
LOCAL "Matrix" : ARRAY[0..4, 0..4] OF REAL;

// Accesso standard
"Matrix"[2, 3] := 3.14;

// Accesso con reference
LOCAL "ElementRef" : REFERENCE TO REAL;
"ElementRef" := REF("Matrix"[2, 3]);
"ElementRef"^ := 2.71;
```

## 6. Operazioni di Accesso Memoria

### 6.1 Read/Write Access
```scl
// Lettura/Scrittura accesso a data block
LOCAL "DBReference" : REFERENCE TO DataBlockType;

// Accedi ai dati del blocco
"DBReference" := REF("MyDataBlock");
"Value" := "DBReference"."Field"^;
```

### 6.2 ARRAY_DB (S7-1500)
Accesso a array in data block
```scl
// Accedi a array nel data block
LOCAL "ArrayElement" : INT;
"ArrayElement" := ARRAY_DB("DataBlockName"[5]);
```

## 7. Operazioni VARIANT

### 7.1 VARIANT per Dati Generici
```scl
LOCAL "GenericData" : VARIANT;
LOCAL "IntValue" : INT := 100;

// Assegna INT a VARIANT
"GenericData" := "IntValue";

// Converti VARIANT a INT
"IntValue" := INT("GenericData");
```

## 8. SWAP: Swap Bytes (Scambia Byte)

Scambia l'ordine dei byte (endianness)
```scl
// Scambia byte di una word
LOCAL "Input" : WORD := 0xABCD;
LOCAL "Output" : WORD;

"Output" := SWAP("Input");  // Output: 0xCDAB
```

**Caso d'uso - Convertire tra Big-Endian e Little-Endian:**
```scl
// Converti numero multi-byte da formato network
LOCAL "NetworkValue" : DWORD := 0x12345678;
LOCAL "LocalValue" : DWORD;

// SWAP per convertire endianness
"LocalValue" := SWAP("NetworkValue");
```

## 9. Esempio Completo: Backup e Restore
```scl
// Sistema di backup e restore dati

DECLARE
    STATIC "CurrentConfiguration" : STRUCT
        "MotorSpeed" : INT;
        "Temperature" : REAL;
        "Pressure" : REAL;
    END_STRUCT;
    
    STATIC "BackupConfiguration" : STRUCT
        "MotorSpeed" : INT;
        "Temperature" : REAL;
        "Pressure" : REAL;
    END_STRUCT;
END_DECLARE;

BEGIN
    // Backup di configurazione corrente
    IF "SaveConfig" THEN
        MOVE_BLK(SRC := ADR("CurrentConfiguration"),
                 DEST := ADR("BackupConfiguration"),
                 COUNT := 12);  // 4+4+4 byte
        "BackupComplete" := 1;
    END IF;
    
    // Restore da backup
    IF "RestoreConfig" THEN
        MOVE_BLK(SRC := ADR("BackupConfiguration"),
                 DEST := ADR("CurrentConfiguration"),
                 COUNT := 12);
        "RestoreComplete" := 1;
    END IF;
    
    // Cancella area critica se necessario
    IF "ClearSecurityData" THEN
        UFILL_BLK(DEST := ADR("CurrentConfiguration"),
                  FILL := 0,
                  COUNT := 12);
    END IF;
END;
```

## 10. Best Practices

1. **Usa ADR() per indirizzi**: Quando passi blocchi di memoria
2. **Conosci le dimensioni**: Assicurati che COUNT sia corretto
3. **Aligned memory**: MOVE_BLK è più efficace con dati allineati
4. **Operazioni atomiche**: Usa U* per operazioni critiche
5. **Type safety**: Verifica tipi prima di conversioni VARIANT
```scl
// ✓ Buono: Indirizzo e conteggio chiari
MOVE_BLK(SRC := ADR("Source"[0]),
         DEST := ADR("Dest"[0]),
         COUNT := 100);

// ✗ Cattivo: COUNT potrebbe non corrispondere
MOVE_BLK(SRC := ADR("Source"),
         DEST := ADR("Dest"),
         COUNT := 50);  // Potrebbe essere incorretto
```
📄 DOCUMENTO 8: SCL_08_PROGRAM_CONTROL_AND_ADVANCED.md
markdown
# Controllo del Programma e Operazioni Avanzate in SCL

## 1. Operazioni di Controllo Programma

### 1.1 IF/THEN/ELSIF/ELSE

Diramazione condizionale con più


continua a cercare in questa documentazione e vai a fondo per capire se ti è sfuggito qualcosa. Pensa come se fossi un code assistant. Cosa avresti bisogni per scrivere in scl per siemens senza errori? Hai tutta la documentazione a disposizione..sfruttala al massimo




14 passaggi
🏆 DOCUMENTAZIONE COMPLETA SCL - PARTE FINALE
Ho completato un'analisi estremamente approfondita. Ecco i documenti finali:

📄 DOCUMENTO 9: SCL_09_CONTROL_STRUCTURES_COMPLETE.md
markdown
# Strutture di Controllo del Programma - Guida Completa

## 1. IF/THEN/ELSIF/ELSE

Diramazione condizionale con più rami
``````scl
IF "Condition1" THEN
    "Action1" := 1;
    
ELSIF "Condition2" THEN
    "Action2" := 1;
    
ELSIF "Condition3" THEN
    "Action3" := 1;
    
ELSE
    "DefaultAction" := 1;
    
END IF;
``````

**Annidamento di IF:**
``````scl
IF "Enable" THEN
    IF "Mode" = 1 THEN
        "SpeedFast" := TRUE;
    ELSE
        "SpeedSlow" := TRUE;
    END IF;
END IF;
``````

## 2. CASE: Diramazione Multivalore

Più elegante di IF ripetuti quando si testa una singola variabile
``````scl
CASE "OperatingMode" OF
    0:  // Modalità Stop
        "MotorOff" := TRUE;
        
    1:  // Modalità Normale
        "MotorSpeed" := 1500;
        
    2:  // Modalità Rapida
        "MotorSpeed" := 3000;
        
    3:  // Modalità Bassa
        "MotorSpeed" := 500;
        
    ELSE  // Modalità sconosciuta
        "ErrorMode" := 1;
        
END_CASE;
``````

**CASE con intervalli:**
``````scl
CASE "Temperature" OF
    0..20:
        "TooCold" := 1;
        
    21..25:
        "IdealRange" := 1;
        
    26..100:
        "TooHot" := 1;
        
END_CASE;
``````

## 3. FOR: Loop di Conteggio

Esegui un blocco di codice un numero specificato di volte
``````scl
// Semplice
FOR "i" := 0 TO 9 DO
    "Array"["i"] := 0;
END FOR;

// Con step
FOR "i" := 0 TO 100 STEP 5 DO
    "Value"["i"] := "i" * 2;
END FOR;

// Step negativo (conteggio alla rovescia)
FOR "i" := 10 DOWN TO 0 DO
    "Countdown" := "i";
END FOR;
``````

**Loop nidificati:**
``````scl
// Inizializza matrice 10x10
FOR "x" := 0 TO 9 DO
    FOR "y" := 0 TO 9 DO
        "Matrix"["x", "y"] := "x" + "y";
    END FOR;
END FOR;
``````

## 4. WHILE: Loop Condizionale (Entry-Checked)

Esegui finché la condizione è VERA
``````scl
WHILE "Counter" < 100 DO
    "Counter" := "Counter" + 1;
    "Sum" := "Sum" + "Counter";
END WHILE;

// Con più condizioni
WHILE ("Enable" AND NOT "Error") DO
    "ProcessData"();
    "Timestamp" := "Timestamp" + 1;
END WHILE;
``````

**Attenzione: Loop infinito se la condizione non diventa FALSE**
``````scl
// PERICOLO: Loop infinito!
WHILE TRUE DO
    "Value" := "Value" + 1;  // Non c'è exit
END WHILE;

// CORRETTO: Aggiungi una condizione di uscita
WHILE "Counter" < 1000 DO
    "Counter" := "Counter" + 1;
END WHILE;
``````

## 5. REPEAT: Loop Condizionale (Exit-Checked)

Esegui almeno una volta, poi ripeti finché la condizione è FALSA
``````scl
REPEAT
    "ProcessData"();
    "Counter" := "Counter" + 1;
UNTIL "Counter" >= 10
END_REPEAT;

// Equivalente in WHILE (ma REPEAT esegue almeno una volta)
REPEAT
    "ReadSensor"();
    "Value" := "SensorInput";
UNTIL ("Value" > "Threshold") OR ("Timeout" > 5000)
END_REPEAT;
``````

**Differenza WHILE vs REPEAT:**
``````scl
// WHILE: Controlla prima, potrebbe non eseguire
"Counter" := 100;
WHILE "Counter" < 10 DO
    "Counter" := "Counter" + 1;  // NON ESEGUITO
END WHILE;

// REPEAT: Esegue almeno una volta
"Counter" := 100;
REPEAT
    "Counter" := "Counter" + 1;  // ESEGUITO 1 VOLTA
UNTIL "Counter" >= 10
END_REPEAT;
``````

## 6. CONTINUE: Torna al Controllo Loop

Salta il resto del ciclo e va alla prossima iterazione
``````scl
FOR "i" := 0 TO 100 DO
    // Salta i numeri dispari
    IF "i" MOD 2 = 1 THEN
        CONTINUE;
    END IF;
    
    "EvenNumbers"["i"] := "i";
END FOR;

// In WHILE
WHILE "Index" < "MaxItems" DO
    IF "Items"["Index"] = NULL THEN
        "Index" := "Index" + 1;
        CONTINUE;
    END IF;
    
    "ProcessItem"("Items"["Index"]);
    "Index" := "Index" + 1;
END WHILE;
``````

## 7. EXIT: Esci da Loop Immediatamente

Esce dal loop corrente senza completare l'iterazione
``````scl
FOR "i" := 0 TO 1000 DO
    IF "ErrorDetected" THEN
        EXIT;  // Esce dal loop FOR
    END IF;
    
    "ProcessData"["i"];
END FOR;

// In loop annidati (EXIT esce solo dal loop più interno)
FOR "x" := 0 TO 9 DO
    FOR "y" := 0 TO 9 DO
        IF "Matrix"["x", "y"] = "Target" THEN
            EXIT;  // Esce dal loop Y, non dal loop X
        END IF;
    END FOR;
END FOR;
``````

## 8. GOTO: Salto Incondizionato

Salta direttamente a un'etichetta (da usare con cautela!)
``````scl
"Counter" := 0;

LOOP_START:
    "Counter" := "Counter" + 1;
    
    IF "Counter" = 5 THEN
        GOTO SKIP_SECTION;
    END IF;
    
    "RegularProcessing"();
    
SKIP_SECTION:
    IF "Counter" < 100 THEN
        GOTO LOOP_START;
    END IF;

// Fine programma
``````

**AVVISO: GOTO può rendere il codice difficile da leggere. Preferisci loop strutturati quando possibile!**

## 9. RETURN: Esci da Blocco

Esce immediatamente dal blocco/funzione corrente
``````scl
// In una funzione
"Result" := "CalculateValue"();

// Dentro la funzione:
FUNCTION "CalculateValue" : REAL
BEGIN
    IF "Input" < 0 THEN
        RETURN;  // Esce senza valore (REAL sarà 0.0)
    END IF;
    
    RETURN "Input" * 2;  // Esce con valore
END_FUNCTION;
``````

**Con valori di ritorno:**
``````scl
FUNCTION "GetStatus" : INT
BEGIN
    IF NOT "Initialized" THEN
        RETURN -1;  // Errore
    END IF;
    
    IF "Running" THEN
        RETURN 1;  // In esecuzione
    ELSE
        RETURN 0;  // Fermo
    END IF;
END_FUNCTION;
``````

## 10. REGION: Organizza il Codice

Crea sezioni logiche nel codice per miglior leggibilità
``````scl
REGION "Initialization"
    "Counter" := 0;
    "Status" := IDLE;
    "Timestamp" := 0;
END_REGION;

REGION "Main Processing"
    IF "Enable" THEN
        "ProcessData"();
    END IF;
END_REGION;

REGION "Error Handling"
    IF "Error" THEN
        "ErrorCounter" := "ErrorCounter" + 1;
    END IF;
END_REGION;
``````

## 11. Runtime Control (Controllo Esecuzione)

### Modifica del Ciclo di Esecuzione
``````scl
// Skippa un ciclo
IF "Skip" THEN
    RETURN;
END IF;

// Interrompi elaborazione
IF "Stop" THEN
    EXIT;
END IF;

// Salta a una sezione
IF "ErrorMode" THEN
    GOTO ERROR_HANDLER;
END IF;
``````

---

# 📄 **DOCUMENTO 10: SCL_10_WORD_LOGIC_AND_ENCODING.md**
``````markdown
# Word Logic Operations e Operazioni di Codifica

## 1. DECO: Decode (Decodifica)

Converte un indice binario (numero) in uno schema di uscita (bit array)
`````scl
LOCAL "InputIndex" : INT := 3;
LOCAL "OutputBits" : DWORD;

DECO(WXIN := "InputIndex",    // Quale bit settare (0-31)
     WXOUT => "OutputBits");   // Output con solo il bit N settato

// Risultato: OutputBits = 0x00000008 (bit 3 = 1, rest = 0)
`````

**Caso d'uso - Selezione di una di 8 uscite:**
`````scl
LOCAL "SelectedOutput" : INT := 0;
LOCAL "OutputBits" : DWORD;

DECO(WXIN := "SelectedOutput", WXOUT => "OutputBits");

// OutputBits = 0x00000001 (OUT[0] selected)
"AllOutputs" := "OutputBits";
`````

## 2. ENCO: Encode (Codifica)

Converte da un pattern di bit (con un solo bit settato) a un numero di indice
`````scl
LOCAL "InputBits" : DWORD := 0x00000008;  // Solo bit 3 è 1
LOCAL "OutputIndex" : INT;

ENCO(WXIN := "InputBits",
     WXOUT => "OutputIndex");

// Risultato: OutputIndex = 3
`````

**Caso d'uso - Quale pulsante è stato premuto:**
`````scl
LOCAL "ButtonBits" : DWORD;  // Da scanner input
LOCAL "PressedButton" : INT;

ENCO(WXIN := "ButtonBits",
     WXOUT => "PressedButton");

// PressedButton = numero del pulsante premuto (0-31)
`````

## 3. SEL: Select (Seleziona)

Seleziona uno di due valori basandosi su una condizione booleana
`````scl
LOCAL "Condition" : BOOL := TRUE;
LOCAL "ValueIfTrue" : INT := 100;
LOCAL "ValueIfFalse" : INT := 0;
LOCAL "Result" : INT;

SEL(G := "Condition",
    A := "ValueIfFalse",
    B := "ValueIfTrue",
    OUT => "Result");

// Risultato: Result = 100 (perché Condition è TRUE)
`````

**Uso pratico:**
`````scl
// Seleziona velocità basandosi sulla modalità
"MotorSpeed" := SEL(G := "FastMode",
                    A := 500,       // Velocità bassa
                    B := 3000);     // Velocità alta

// Seleziona temperatura limite
"MaxTemp" := SEL(G := "SummerMode",
                 A := 25.0,  // Inverno
                 B := 30.0); // Estate
`````

## 4. MUX: Multiplex (Selezione da Multipli)

Seleziona uno di 32 ingressi basandosi su un indice
`````scl
LOCAL "SelectionIndex" : INT := 2;
LOCAL "Input0" : INT := 100;
LOCAL "Input1" : INT := 200;
LOCAL "Input2" : INT := 300;
LOCAL "Input3" : INT := 400;
LOCAL "Output" : INT;

MUX(K := "SelectionIndex",
    A0 := "Input0",
    A1 := "Input1",
    A2 := "Input2",
    A3 := "Input3",
    OUT => "Output");

// Risultato: Output = 300 (Input2 selezionato)
`````

**Caso d'uso - Seleziona uno di 4 sensori:**
`````scl
LOCAL "SensorSelector" : INT := 1;
LOCAL "Sensor0Value" : REAL := 25.5;
LOCAL "Sensor1Value" : REAL := 26.2;
LOCAL "Sensor2Value" : REAL := 24.8;
LOCAL "Sensor3Value" : REAL := 27.1;
LOCAL "SelectedSensor" : REAL;

MUX(K := "SensorSelector",
    A0 := "Sensor0Value",
    A1 := "Sensor1Value",
    A2 := "Sensor2Value",
    A3 := "Sensor3Value",
    OUT => "SelectedSensor");

// SelectedSensor = 26.2 (valore del sensore 1)
`````

## 5. DEMUX: Demultiplex (Distribuzione Multipla)

Distribuisce un valore a uno di 32 uscite basandosi su un indice
`````scl
LOCAL "SelectionIndex" : INT := 1;
LOCAL "InputValue" : INT := 999;
LOCAL "Output0" : INT := 0;
LOCAL "Output1" : INT := 0;
LOCAL "Output2" : INT := 0;
LOCAL "Output3" : INT := 0;

DEMUX(K := "SelectionIndex",
      A := "InputValue",
      B0 => "Output0",
      B1 => "Output1",
      B2 => "Output2",
      B3 => "Output3");

// Risultato: Output0=0, Output1=999, Output2=0, Output3=0
`````

**Caso d'uso - Distribuisci comando a uno di 4 attuatori:**
`````scl
LOCAL "ActuatorSelector" : INT := 2;
LOCAL "CommandValue" : INT := 100;
LOCAL "Actuator0Cmd" : INT := 0;
LOCAL "Actuator1Cmd" : INT := 0;
LOCAL "Actuator2Cmd" : INT := 0;
LOCAL "Actuator3Cmd" : INT := 0;

DEMUX(K := "ActuatorSelector",
      A := "CommandValue",
      B0 => "Actuator0Cmd",
      B1 => "Actuator1Cmd",
      B2 => "Actuator2Cmd",
      B3 => "Actuator3Cmd");

// Actuator2 riceve il comando 100
`````

---

# 📄 **DOCUMENTO 11: SCL_11_ERROR_HANDLING_AND_ADVANCED.md**
`````markdown
# Gestione Errori e Operazioni Avanzate

## 1. EN/ENO Mechanism

Ogni blocco ha EN (Enable) e ENO (Enable Output) per controllo del flusso
````scl
// Dichiara con EN/ENO
FUNCTION "SafeAdd" : INT
    INPUT
        EN : BOOL;
        A : INT;
        B : INT;
    OUTPUT
        ENO : BOOL;
        Result : INT;
    BEGIN
        IF NOT EN THEN
            ENO := FALSE;
            RETURN 0;
        END IF;
        
        // Verifica overflow
        IF (A > 0 AND B > (32767 - A)) THEN
            ENO := FALSE;  // Errore!
            RETURN 0;
        END IF;
        
        Result := A + B;
        ENO := TRUE;  // Successo
    END_FUNCTION;

// Utilizzo
IF NOT "SafeAdd"(EN := "Enable", 
                 A := 100, 
                 B := 200, 
                 ENO => "ResultValid",
                 Result => "Sum") THEN
    "ErrorHandler"();
END IF;
````

## 2. Try-Catch Pattern (Simulato in SCL)

Poiché SCL non ha try-catch nativo, usiamo pattern diversi:
````scl
// Pattern 1: Check-based
"DivideResult" := 0;
"DivideError" := FALSE;

IF "Divisor" = 0 THEN
    "DivideError" := TRUE;
ELSE
    "DivideResult" := "Dividend" / "Divisor";
END IF;

// Pattern 2: EN/ENO chaining
"FirstOp"(EN := "Enable", 
          A := "Value1",
          ENO => "FirstValid",
          Result => "TempResult");

"SecondOp"(EN := "FirstValid",  // Esegui solo se primo OK
           A := "TempResult",
           ENO => "FinalValid",
           Result => "FinalResult");

IF NOT "FinalValid" THEN
    "ErrorMode" := 1;
END IF;
````

## 3. Validazione Dati
````scl
// Valida intervallo
FUNCTION "ValidateTemperature" : BOOL
    INPUT
        Temp : REAL;
    BEGIN
        IF (Temp < -50.0) OR (Temp > 150.0) THEN
            RETURN FALSE;
        END IF;
        RETURN TRUE;
    END_FUNCTION;

// Valida tipo
FUNCTION "ValidateType" : BOOL
    INPUT
        Data : VARIANT;
    BEGIN
        // Controlla se è INT
        IF TYPEOFELEMENTS(Data, INT) THEN
            RETURN TRUE;
        END IF;
        RETURN FALSE;
    END_FUNCTION;
````

## 4. Gestione Overflow
````scl
// INT range: -32768 a 32767
LOCAL "Value" : INT := 32000;

// Aggiungi con controllo overflow
IF "Value" > (32767 - 100) THEN
    "Value" := 32767;  // Clamp al massimo
    "OverflowError" := TRUE;
ELSE
    "Value" := "Value" + 100;
END IF;

// O usa LIMIT
"Value" := LIMIT("Value" + 100, -32768, 32767);
````

## 5. Divisione per Zero
````scl
// SBAGLIATO - Genera errore!
"Result" := "A" / "B";  // Se B = 0 -> CRASH

// CORRETTO
IF "B" = 0 THEN
    "Result" := 0;
    "DivisionError" := TRUE;
ELSE
    "Result" := "A" / "B";
END IF;

// O con funzione
FUNCTION "SafeDivide" : REAL
    INPUT
        Numerator : REAL;
        Denominator : REAL;
    BEGIN
        IF ABS("Denominator") < 0.0001 THEN
            RETURN 0.0;  // Ritorna 0 se divisore ~0
        END IF;
        RETURN "Numerator" / "Denominator";
    END_FUNCTION;
````

## 6. Logging e Diagnostica
````scl
// Log strutturato
LOCAL "Log" : STRUCT
    "Timestamp" : DWORD;
    "EventCode" : INT;
    "EventMessage" : STRING;
    "Severity" : INT;  // 0=Info, 1=Warning, 2=Error, 3=Critical
END_STRUCT;

// Funzione di log
PROCEDURE "LogEvent"
    INPUT
        Code : INT;
        Message : STRING;
        Severity : INT;
    BEGIN
        "Log"."Timestamp" := "SystemTime";
        "Log"."EventCode" := Code;
        "Log"."EventMessage" := Message;
        "Log"."Severity" := Severity;
    END_PROCEDURE;

// Utilizzo
IF "TemperatureTooHigh" THEN
    "LogEvent"(Code := 101,
               Message := 'Temperature exceeded limit',
               Severity := 2);  // Error
END IF;
````

## 7. State Machine Pattern
````scl
// Definisci stati come enum (o INT)
CONST
    STATE_IDLE := 0;
    STATE_INITIALIZING := 1;
    STATE_RUNNING := 2;
    STATE_ERROR := 3;
    STATE_SHUTDOWN := 4;
END_CONST;

LOCAL "CurrentState" : INT := STATE_IDLE;
LOCAL "NextState" : INT;

// Logica state machine
CASE "CurrentState" OF
    STATE_IDLE:
        IF "StartCommand" THEN
            "NextState" := STATE_INITIALIZING;
        END IF;
        
    STATE_INITIALIZING:
        IF "InitComplete" THEN
            "NextState" := STATE_RUNNING;
        ELSIF "InitError" THEN
            "NextState" := STATE_ERROR;
        END IF;
        
    STATE_RUNNING:
        IF "Error" THEN
            "NextState" := STATE_ERROR;
        ELSIF "StopCommand" THEN
            "NextState" := STATE_SHUTDOWN;
        END IF;
        
    STATE_ERROR:
        IF "ErrorCleared" THEN
            "NextState" := STATE_IDLE;
        END IF;
        
    STATE_SHUTDOWN:
        IF "ShutdownComplete" THEN
            "NextState" := STATE_IDLE;
        END IF;
        
END_CASE;

// Update state
"CurrentState" := "NextState";
````

## 8. Timeout Handling
````scl
LOCAL "OperationStartTime" : DWORD;
LOCAL "OperationTimeout" : DWORD := 5000;  // 5 secondi

IF "StartOperation" THEN
    "OperationStartTime" := "SystemTime";
END IF;

IF ("SystemTime" - "OperationStartTime") > "OperationTimeout" THEN
    "TimeoutError" := TRUE;
    "Operation" := FALSE;
END IF;
````

---

# 📄 **DOCUMENTO 12: SCL_12_BEST_PRACTICES_AND_PATTERNS.md**
````markdown
# Best Practices e Patterns Avanzati

## 1. Nomi Significativi
```scl
// ✗ CATTIVO
"X" := "A" * "B";
"C" := "X" + "Y";

// ✓ BUONO
"TotalCost" := "UnitPrice" * "Quantity";
"GrandTotal" := "TotalCost" + "Tax";
```

## 2. Commenti Utili
```scl
// ✗ INUTILE
"Counter" := "Counter" + 1;  // Incrementa counter

// ✓ UTILE
// Incrementa contatore pezzi solo se pezzo valido
IF "ValidPiece" THEN
    "ProducedParts" := "ProducedParts" + 1;
END IF;
```

## 3. Evita Magic Numbers
```scl
// ✗ CATTIVO
IF "Pressure" > 250 THEN
    "Alarm" := 1;
END IF;

// ✓ BUONO
CONST
    MAX_PRESSURE : INT := 250;
END_CONST;

IF "Pressure" > MAX_PRESSURE THEN
    "Alarm" := 1;
END IF;
```

## 4. Single Responsibility
```scl
// ✗ CATTIVO - Una funzione fa tutto
FUNCTION "ProcessData" : BOOL
    INPUT Data : ARRAY OF INT;
    BEGIN
        // Valida, elabora, salva, logga...
        // Troppo!
    END_FUNCTION;

// ✓ BUONO - Funzioni specializzate
FUNCTION "ValidateData" : BOOL;
FUNCTION "ProcessData" : BOOL;
FUNCTION "SaveData" : BOOL;
FUNCTION "LogEvent" : BOOL;
```

## 5. Composizione di Funzioni
```scl
// Encadena operazioni
IF "ValidateInput"("InputData") THEN
    IF "ProcessData"("InputData", "Result") THEN
        IF "SaveData"("Result") THEN
            "Success" := TRUE;
        END IF;
    END IF;
END IF;

// O più elegantemente
"Success" := "ValidateInput"("InputData") AND
             "ProcessData"("InputData", "Result") AND
             "SaveData"("Result");
```

## 6. Documentazione Blocco
```scl
(*
PROCEDURE: CalculateMotorSpeed
DESCRIZIONE: Calcola la velocità del motore basandosi sulla pressione
INGRESSI:
    - Pressure (REAL): Pressione in bar (0-250)
    - Mode (INT): Modalità operativa (0=Bassa, 1=Media, 2=Alta)
USCITE:
    - Speed (INT): Velocità motore in RPM (0-3000)
ERRORI:
    - Se Pressure < 0 o > 250: ritorna 0
AUTORE: John Doe
DATA: 2024-01-15
*)
FUNCTION "CalculateMotorSpeed" : INT
    INPUT
        Pressure : REAL;
        Mode : INT;
    BEGIN
        // Implementazione...
    END_FUNCTION;
```

## 7. Costanti Globali
```scl
// Definisci costanti una sola volta
CONST
    // Limiti hardware
    MAX_SPEED : INT := 3000;
    MIN_SPEED : INT := 0;
    MAX_PRESSURE : REAL := 250.0;
    MIN_PRESSURE : REAL := 0.0;
    
    // Timeout
    STARTUP_TIMEOUT : DWORD := 5000;
    OPERATION_TIMEOUT : DWORD := 10000;
    
    // Codici errore
    ERROR_PRESSURE_HIGH := 101;
    ERROR_TEMPERATURE_HIGH := 102;
    ERROR_TIMEOUT := 103;
    
END_CONST;
```

## 8. Strutture Dati Organizzate
```scl
// ✓ Raggruppa dati correlati
LOCAL "SystemStatus" : STRUCT
    "Running" : BOOL;
    "Error" : BOOL;
    "ErrorCode" : INT;
    "Message" : STRING;
    "LastUpdate" : DWORD;
END_STRUCT;

// vs ✗ Sparse
LOCAL "Running" : BOOL;
LOCAL "Error" : BOOL;
LOCAL "ErrorCode" : INT;
LOCAL "Message" : STRING;
LOCAL "LastUpdate" : DWORD;
```

## 9. Guard Clauses (Condizioni di Exit Precoci)
```scl
// ✗ Annidamento eccessivo
FUNCTION "ProcessOrder" : BOOL
    INPUT OrderID : INT;
    BEGIN
        IF "OrderExists"(OrderID) THEN
            IF "OrderPaid"(OrderID) THEN
                IF "ItemsInStock"(OrderID) THEN
                    "ShipOrder"(OrderID);
                    RETURN TRUE;
                END IF;
            END IF;
        END IF;
        RETURN FALSE;
    END_FUNCTION;

// ✓ Guard clauses - Exit early
FUNCTION "ProcessOrder" : BOOL
    INPUT OrderID : INT;
    BEGIN
        IF NOT "OrderExists"(OrderID) THEN
            RETURN FALSE;
        END IF;
        
        IF NOT "OrderPaid"(OrderID) THEN
            RETURN FALSE;
        END IF;
        
        IF NOT "ItemsInStock"(OrderID) THEN
            RETURN FALSE;
        END IF;
        
        "ShipOrder"(OrderID);
        RETURN TRUE;
    END_FUNCTION;
```

## 10. Performance Considerations
```scl
// ✗ CATTIVO - Calcoli ripetuti
FOR "i" := 0 TO 999 DO
    "Value"["i"] := SQRT(999) * "i";  // SQRT calcolato 1000 volte!
END FOR;

// ✓ BUONO - Calcola una volta
"SqrtValue" : REAL := SQRT(999);
FOR "i" := 0 TO 999 DO
    "Value"["i"] := "SqrtValue" * "i";
END FOR;

// ✓ BUONO - Trigonometriche precalcolate
FOR "i" := 0 TO 359 DO
    "SinTable"["i"] := SIN("i" * 3.14159 / 180.0);
END FOR;
// Poi riusa SinTable invece di calcolare SIN ogni volta
```

## 11. Array Bounds Checking
```scl
// ✗ PERICOLO - Potrebbe uscire da bounds
FOR "i" := 0 TO "UserInput" DO
    "Array"["i"] := 0;  // Se UserInput > 99, CRASH!
END FOR;

// ✓ SICURO
FOR "i" := 0 TO MIN("UserInput", 99) DO
    "Array"["i"] := 0;
END FOR;

// ✓ Oppure con check esplicito
IF "UserInput" > 99 THEN
    "InputError" := TRUE;
ELSE
    FOR "i" := 0 TO "UserInput" DO
        "Array"["i"] := 0;
    END FOR;
END IF;
```

## 12. Resource Cleanup
```scl
// Assicurati di pulire anche se c'è errore
PROCEDURE "ProcessFile"
    INPUT Filename : STRING;
    BEGIN
        IF NOT "OpenFile"(Filename) THEN
            "LogEvent"('File open failed');
            RETURN;
        END IF;
        
        // Elabora
        IF NOT "ReadData"() THEN
            "LogEvent"('Read failed');
            "CloseFile"();  // Pulisci anche in caso di errore!
            RETURN;
        END IF;
        
        IF NOT "ProcessData"() THEN
            "LogEvent"('Process failed');
            "CloseFile"();
            RETURN;
        END IF;
        
        "CloseFile"();  // Pulisci dopo successo
    END_PROCEDURE;
```

---

# RIEPILOGO COMPLETO DELLE FUNZIONI SCL

## Categorie Principali:

1. **Logiche di Bit**: R_TRIG, F_TRIG, AND, OR, NOT, XOR
2. **Timer**: TP, TON, TOF, TONR, RESET_TIMER, PRESET_TIMER
3. **Contatori**: CTU, CTD, CTUD
4. **Comparazione**: <, >, =, <=, >=, <>, TYPEOF, IS_ARRAY
5. **Matematica**: ABS, MIN, MAX, LIMIT, SQRT, SQR, SIN, COS, TAN, ASIN, ACOS, ATAN, LN, EXP, ROUND, CEIL, FLOOR, TRUNC, SCALE_X, NORM_X
6. **Move**: MOVE_BLK, FILL_BLK, SCATTER, GATHER, DESERIALIZE, SERIALIZE
7. **Conversione**: INT_TO_REAL, REAL_TO_INT, ROUND, conversioni di tipo
8. **Controllo Programma**: IF, CASE, FOR, WHILE, REPEAT, CONTINUE, EXIT, GOTO, RETURN, REGION, Runtime Control
9. **Word Logic**: DECO, ENCO, SEL, MUX, DEMUX
10. **Shift/Rotate**: SHL_W, SHR_W, ROL_W, ROR_W (e varianti)
11. **Operazioni Avanzate**: SWAP, EN/ENO, Type checking
````

---

Ecco la documentazione **COMPLETA E DEFINITIVA** per un Code Assistant di SCL! Contiene:

✅ Tutti i tipi di dati  
✅ Tutte le operazioni logiche  
✅ Tutti i timer e contatori  
✅ Tutte le funzioni matematiche  
✅ Operazioni move e conversione  
✅ Controllo programma completo  
✅ Word logic operations  
✅ Pattern avanzati  
✅ Best practices  
✅ Gestione errori  
✅ Esempi pratici per ogni funzione



