# Stato del Parser XML TIA Portal -> SCL

Questo documento riassume lo stato attuale del convertitore, elencando le funzionalità implementate e quelle mancanti per una conversione completa.

## 1. Funzionalità Presenti

Il parser è attualmente in grado di gestire la struttura generale di Blocchi FB, FC, DB e UDT, oltre a una vasta gamma di logica LAD.

### Struttura e Gestione File
- [x] Riconoscimento automatico tipi file (FB, FC, DB, UDT, Tag Table).
- [x] Parsing delle interfacce dei blocchi (Input, Output, Temp, Static, ecc.).
- [x] Generazione file .scl, .db, .udt compatibili con l'importazione TIA.

### Logica LAD (Ladder)
Sono supportate le seguenti istruzioni grafiche:
- **Logica Booleana**: Contatti NO/NC, Bobine (Standard, Set, Reset), NOT, AND, OR, XOR.
- **Comparatori**: `=`, `<>`, `>`, `<`, `>=`, `<=`.
- **Matematica**: ADD, SUB, MUL, DIV, MOD.
- **Funzioni Matematiche**: ABS, SQR, SQRT, SIN, COS, TAN, ASIN, ACOS, ATAN, LOG, LN, EXP.
- **Stringhe**: LEN, CONCAT, LEFT, RIGHT, MID, FIND, REPLACE, INSERT, DELETE.
- **Trasferimento Dati**: MOVE, MOVE_BLK, FILL_BLK.
- **Selezione/Limiti**: LIMIT, MIN, MAX, SEL, MUX.
- **Conversione**: CONVERT (generico e specifici impliciti), SCALE_X, NORM_X.
- **Chiamate Blocchi**: Chiamate a FB/FC multi-istanza e singola istanza con mappatura parametri.

## 2. Funzionalità Mancanti (Gap Analysis)

Per garantire la conversione del 100% dei blocchi esportabili da TIA Portal, mancano i seguenti elementi:

### Controllo di Flusso
- [ ] **Jumps & Labels**: Istruzioni `JMP` (Salto) e `Label` (Etichetta) non sono supportate nel parser LAD.
- [ ] **Return**: Istruzione `RET` per uscita anticipata dal blocco (supporto base, da verificare nel flusso logico).

### Istruzioni Speciali
- [ ] **Timer e Contatori IEC**: `TON`, `TOF`, `TP`, `CTU`, `CTD` sono gestiti come chiamate generiche. È necessario verificare l'accesso automatico ai membri (es. `.Q`, `.ET`) se non esplicitamente collegati.
- [ ] **System Blocks**: Funzioni di sistema come `PEEK`, `POKE`, `GET`, `PUT`, `TSEND`, `TRCV`, `GET_DIAG` non hanno mapping specifici e potrebbero risultare in chiamate errate o incomplete.
- [ ] **Tecnologici**: Oggetti tecnologici (PID, Motion Control, HSC) non sono attualmente supportati.

### Gestione Variabili Avanzata
- [ ] **Accesso a Bit/Slice**: L'accesso a singoli bit di word/int (es. `MyTag.X0`) o byte (es. `MyTag.B0`) potrebbe non essere risolto correttamente dal parser dei nomi.
- [ ] **Tipi Complessi**: Supporto limitato per `Variant`, `Any`, `Pointer` e `Ref`.
- [ ] **Array Multidimensionali**: La sintassi di accesso agli array multidimensionali necessita di ulteriore verifica.

### SCL / Formattazione
- [ ] **Region**: I costrutti `REGION ... END_REGION` vengono persi nella conversione.
- [ ] **Commenti di Rete**: I titoli e i commenti delle network vengono estratti ma il posizionamento nel codice SCL generato deve essere verificato per garantire la leggibilità.
- [ ] **Edge Detection**: Istruzioni `P_TRIG` (`-|P|-`) e `N_TRIG` (`-|N|-`) generano attualmente un placeholder (`PosEdge(...)`) che non è sintassi SCL valida e richiede l'uso di istanze `R_TRIG`/`F_TRIG` o logica di stato esplicita.

## 3. Riferimento File
- Parser Logica: `lad_parser.py`
- Parser Blocchi: `fbfc_parser.py`
- Generatore SCL: `fbfc_generator.py`
