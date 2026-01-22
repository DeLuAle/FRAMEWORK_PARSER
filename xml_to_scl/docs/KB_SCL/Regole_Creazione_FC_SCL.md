# Regole per la Creazione di Function Block (FC) in SCL - TIA Portal

## Introduzione
Questo documento elenca le regole fondamentali per la creazione di file SCL (Structured Control Language) esportabili e importabili in TIA Portal senza errori di compilazione.

---

## 1. Struttura Header della Funzione

### Formato Corretto
```scl
FUNCTION "NomeFunzione" : TipoRitorno
TITLE = Descrizione Funzione
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : NomeAutore
FAMILY : CategoriaFunzione
NAME : 'ID_Funzione'
VERSION : 1.0
//Commento descrittivo singola riga
```

### Regole Header
- **TITLE**: SENZA virgolette singole. Sintassi: `TITLE = Testo` (NON `TITLE = 'Testo'`)
- **Attributi**: Racchiudere in parentesi graffe con spazio: `{ S7_Optimized_Access := 'TRUE' }`
- **AUTHOR**: Nome dell'autore con due punti `:` come separatore
- **FAMILY**: Categoria/famiglia della funzione
- **NAME**: Identificatore univoco tra virgolette singole
- **VERSION**: Numero versione (es. 1.0, 0.1)
- **Commenti**: Utilizzare `//` per commenti sulla riga successiva all'header

---

## 2. Dichiarazione Variabili di Input/Output

### Formato Corretto
```scl
   VAR_INPUT
      variabile1 : REAL;
      variabile2 : BOOL;
   END_VAR

   VAR_OUTPUT
      risultato : REAL;
      errore : BOOL;
   END_VAR
```

### Regole Variabili I/O
- Indentare con **3 spazi** (o 1 tab)
- Uno spazio dopo `VAR_INPUT` e prima di `END_VAR`
- Ogni variabile con tipo e punto e virgola `;`
- Supportati: `REAL`, `INT`, `BOOL`, `STRING[n]`, etc.

### Tipi Speciali
- **VAR_IN_OUT**: Per variabili bidirezionali (passate per riferimento)
- **VAR_TEMP**: Per variabili temporanee (visibilità locale)
- **VAR CONSTANT**: Per costanti con valori iniziali

---

## 3. Dichiarazione Variabili Temporanee

### VAR_TEMP - Senza Inizializzazione
```scl
   VAR_TEMP
      contatore : INT;
      valore : REAL;
      flag : BOOL;
   END_VAR
```

### VAR CONSTANT - Con Inizializzazione
```scl
   VAR CONSTANT
      PI : REAL := 3.14159265;
      FATTORE_SICUREZZA : REAL := 1.0;
      DIAMETER : REAL := 80.0;
   END_VAR
```

### Regole
- **VAR_TEMP**: NON consentito utilizzare `:=` nella dichiarazione
- **VAR CONSTANT**: Consente `:=` per inizializzare valori costanti
- Scelta: Se una variabile non cambia mai, metterla in `VAR CONSTANT`

---

## 4. Corpo della Funzione (BEGIN...END_FUNCTION)

### Formato Generale
```scl
BEGIN

	REGION NOME_REGIONE

	    // Codice qui

	END_REGION

END_FUNCTION
```

### Regole BEGIN
- Utilizzare **TAB** per indentazione (non spazi)
- Organizzare il codice in **REGION...END_REGION** (logiche funzionali)
- Prefisso `#` per tutte le variabili: `#variabile`
- Commenti inline con `//` o multi-riga con `(* ... *)`

---

## 5. Uso del Prefisso # sulle Variabili

### Regola Fondamentale
**Tutte le variabili devono essere precedute dal prefisso `#`**

### Esempi Corretti
```scl
IF #lunghezza <= 0.0 OR #altezza <= 0.0 THEN
    #errore := TRUE;
    #codice_errore := 1;
    FC_Funzione := 0.0;
    RETURN;
END_IF;

#pressione := 10.0 * #carico / #area;
```

### Eccezioni
- **Nomi di funzione di ritorno**: NON usa `#` → `FC_Funzione := valore`
- **Funzioni di sistema**: NON usano `#` → `SQRT()`, `ABS()`, `INT_TO_REAL()`

---

## 6. Struttura con REGION

### Organizzazione Logica
```scl
BEGIN

	REGION VALIDAZIONE_INPUT
	    // Controlli input
	END_REGION

	REGION LOOKUP_TABLE
	    // Ricerca modello
	END_REGION

	REGION CALCOLI
	    // Calcoli principali
	END_REGION

	REGION OUTPUT
	    // Assegnazione risultati
	END_REGION

END_FUNCTION
```

### Vantaggi
- Codice più leggibile e organizzato
- Facilita il mantenimento e il debugging
- TIA Portal collassa/espande automaticamente le REGION

---

## 7. Tipo di Dato Ritorno

### Esempi Validi
```scl
FUNCTION "FC_CalcolaRisultato" : REAL      // Ritorna numero reale
FUNCTION "FC_Controllo" : BOOL             // Ritorna booleano
FUNCTION "FC_Messaggio" : STRING[50]       // Ritorna stringa max 50 caratteri
FUNCTION "FC_Elabora" : INT                // Ritorna intero
```

### Regole
- Dichiarare il tipo di ritorno subito dopo il nome della funzione: `FUNCTION "Nome" : Tipo`
- Il valore di ritorno si assegna con il nome della funzione: `FC_CalcolaRisultato := valore`

---

## 8. Gestione Errori

### Pattern Consigliato
```scl
VAR_OUTPUT
    errore : BOOL;
    codice_errore : INT;
END_VAR

VAR CONSTANT
    ERRORE_INPUT_INVALIDO : INT := 1;
    ERRORE_MODELLO_SCONOSCIUTO : INT := 2;
    ERRORE_CALCOLO : INT := 3;
END_VAR

BEGIN
    IF #input <= 0.0 THEN
        #errore := TRUE;
        #codice_errore := ERRORE_INPUT_INVALIDO;
        FC_Funzione := 0.0;
        RETURN;
    END_IF;

    #errore := FALSE;
    #codice_errore := 0;
END_FUNCTION
```

### Convenzioni
- Output BOOL `errore`: indica se si è verificato un errore
- Output INT `codice_errore`: specifica il tipo di errore (0 = OK)
- Utilizzare costanti nominative per i codici errore
- Utilizzare `RETURN;` per uscire anticipatamente

---

## 9. Commenti

### Stili Supportati
```scl
// Commento su singola riga
// Più righe di commento
// su linee separate

(* Commento multi-riga
   può estendersi
   su più righe *)

(* Commento
   inline /* annidato */ supportato *)
```

### Regole
- Preferire `//` per commenti brevi
- Usare `(* *)` per commenti lunghi o multi-riga
- I commenti `//` possono essere inline: `#valore := 10.0; // Inizializzazione`

---

## 10. Checklist Pre-Esportazione

Prima di esportare il file SCL, verificare:

- [ ] **Header**: `TITLE` senza virgolette, attributi corretti
- [ ] **Variabili**: Tutte le variabili nel codice hanno prefisso `#`
- [ ] **Indentazione**: VAR_* con 3 spazi, codice con TAB
- [ ] **Inizializzazioni**: Variabili VAR_TEMP senza `:=`, costanti in VAR CONSTANT
- [ ] **REGION**: Codice organizzato in blocchi logici
- [ ] **Tipo Ritorno**: Dichiarato correttamente
- [ ] **Errori**: Gestiti con OUTPUT BOOL e INT
- [ ] **Funzioni di Sistema**: Senza prefisso `#`
- [ ] **Commenti**: Sintassi valida con `//` o `(* *)`
- [ ] **Parentesi**: Bilanciate e corrette
- [ ] **Punto e Virgola**: Tutti gli statement terminano con `;`

---

## 11. Esempio Completo Minimalista

```scl
FUNCTION "FC_Esempio" : REAL
TITLE = Funzione Esempio Minimal
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : Sviluppatore
FAMILY : Utilita
NAME : 'FC_Esempio_v1'
VERSION : 1.0
//Funzione di esempio con regole corrette

   VAR_INPUT
      valore : REAL;
   END_VAR

   VAR_OUTPUT
      risultato : REAL;
      errore : BOOL;
   END_VAR

   VAR CONSTANT
      FATTORE : REAL := 2.5;
   END_VAR

BEGIN

	REGION VALIDAZIONE
	    IF #valore < 0.0 THEN
	        #errore := TRUE;
	        FC_Esempio := 0.0;
	        RETURN;
	    END_IF;
	END_REGION

	REGION CALCOLO
	    #risultato := #valore * FATTORE;
	    #errore := FALSE;
	END_REGION

END_FUNCTION
```

---

## 12. Errori Comuni da Evitare

| Errore | ❌ Sbagliato | ✅ Corretto |
|--------|------------|-----------|
| TITLE con virgolette | `TITLE = 'Testo'` | `TITLE = Testo` |
| Variabile senza # | `IF lunghezza <= 0.0` | `IF #lunghezza <= 0.0` |
| VAR_TEMP con := | `var : REAL := 5.0;` | Usare `VAR CONSTANT` |
| Attributo scorretto | `{S7.extern := 'true'}` | `{ S7_Optimized_Access := 'TRUE' }` |
| Indentazione spazi | `FUNCTION "Nome"` | 3 spazi in VAR_INPUT |
| Mancanza REGION | Codice diretto in BEGIN | `REGION Nome...END_REGION` |
| Inizializzazione nel BEGIN | `#k := 0.5;` (per costanti) | Mettere in `VAR CONSTANT` |

---

## 13. Riferimenti

- **TIA Portal**: Siemens STEP 7 Versione 17 e successive
- **Linguaggio**: SCL (Structured Control Language) conforme IEC 61131-3
- **Formato Export**: File `.scl` importabile/esportabile da TIA Portal

---

## Note Finali

Seguire rigorosamente queste regole garantisce:
✅ Compilazione senza errori di sintassi
✅ Import/Export corretto da TIA Portal
✅ Codice leggibile e manutenibile
✅ Coerenza tra progetti e sviluppatori
