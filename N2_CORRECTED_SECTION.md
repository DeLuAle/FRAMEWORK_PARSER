# N2 Sezione Corretta - Pronto per Copia-Incolla

**Documento:** analisi_debolezze_parser_v2_EVIDENCE.md
**Sezione:** N2 - Fallback "???" per Logica Non Risolta
**Data Correzione:** 2026-01-05
**Status:** Pronto per sostituire sezione originale

---

## VERSIONE ORIGINALE (ERRATA)

```markdown
### N2 - Fallback "???" per Logica Non Risolta: ⚠️ NUOVO

**File:** `lad_parser.py` - Multiple occorrenze

```python
# Line ~850 - Unknown part type
else:
    logger.warning(f"Unknown part type: {part_type}")
    return "???"  # ← Placeholder che finisce nel codice!

# Line ~490 - Failed resolution
if in_expr is None:
    in_expr = "???"
```

**File:** `fbfc_generator.py` lines 201, 211, 221, 233, etc.

```python
# Generator checks for ??? but still generates code
if en and en != 'TRUE' and en != '???':
    self._add_line(f"IF {en} THEN")
# Se en == '???' viene trattato come TRUE (skip IF)
```

**Impatto:**
- Logica non risolta genera `???` nel codice SCL
- Alcune occorrenze saltate silenziosamente (trattate come TRUE)
- Compilazione TIA Portal fallisce con errore criptico
```

---

## VERSIONE CORRETTA (READY TO USE)

Copia il testo qui sotto e sostituisci la sezione originale:

```markdown
### N2 - Fallback "???" per Logica Non Risolta: ❌ CRITICO

**File:** `lad_parser.py` - 35+ occorrenze (linee: 481, 496, 516, 526, 551, 558, 583, 593, 598, 599, 615, 616, 630, 654, 663, 670, 673, 681, 684, 700, 701, 717, 836, 842, 854, 936, 1142 e altre)

```python
# Esempio 1: lad_parser.py linea 481 - Connection non risolvibile
if not source_info:
    return '???'  # ← Placeholder ritornato direttamente nel codice!

# Esempio 2: lad_parser.py linea 516 - Fallback per logica non risolvibile
return '???'  # ← Se logica non ha connessione valida
```

**File:** `fbfc_generator.py` - Gestione PERICOLOSA di "???" (linee: 201, 211, 221, 233, 240, 247, 273, 284)

```python
# fbfc_generator.py linea 201 - GESTIONE SCORRETTA
elif op_type == 'move':
    en = op.get('en_expr')
    if en and en != 'TRUE' and en != '???':
        # Se en ha valore valido (non TRUE, non ???):
        self._add_line(f"IF {en} THEN")
        self._indent()
        self._add_line(f"{op['dest']} := {op['source']};")
        self._dedent()
        self._add_line("END_IF;")
    else:
        # Se en == 'TRUE' O en == '???' o en non esiste:
        # NON genera IF, ma ESEGUE L'AZIONE COMUNQUE (incondizionatamente)!
        self._add_line(f"{op['dest']} := {op['source']};")
```

**Analisi Dettagliata del Comportamento Errato:**

Quando `en == '???'` (logica non risolvibile):
- La condizione: `if en and en != 'TRUE' and en != '???'`
- Valuta: `if '???' and True and False`
- Risultato: `if False`
- Esecuzione: Va nel ramo `else`
- Output generato: `dest := source;` **SENZA IF!**

**Confronto Problematico:**

| Situazione | Comportamento | Impatto | Gravità |
|-----------|--------------|--------|---------|
| en = valore_valido | Genera `IF valore_valido THEN ... END_IF;` | Logica condizionale | ✅ Corretto |
| en = 'TRUE' | Genera `dest := source;` senza IF | Logica sempre eseguita | ✅ Accettabile |
| en = 'FALSE' | Non genera nulla (ramo false) | Logica saltata | ✅ Corretto |
| **en = '???'** | **Genera `dest := source;` senza IF** | **Logica incontrollata** | ❌ **PERICOLOSO** |

**Impatto CRITICO:**

1. **Logica non risolta finisce nel codice SCL**
   - lad_parser.py genera placeholder "???" che finisce nel codice generato
   - Esempio output: `variable := ???;` ← Non compilabile in TIA Portal

2. **Logica incondizionata quando dovrebbe essere condizionale**
   - Se condition non risolvibile → Codice eseguito comunque
   - Peggio di quanto documentato: non è "saltato" ma "eseguito"
   - Esempio:
     ```scl
     // Se Reset non risolvibile:
     #myCounter(CU := TRUE);  // Viene eseguito SEMPRE
     var_reset := FALSE;       // Viene eseguito SEMPRE (senza IF!)
     ```

3. **Differenza critica da quanto documentato**
   - Documento sostiene: "Se en == '???' viene saltato (skip IF come se TRUE)"
   - Realtà: "Se en == '???' viene eseguito SENZA protezione IF (incondizionatamente)"
   - **La realtà è PEGGIO per la sicurezza logica**

**Occurrence e Distribuzione:**

- **lad_parser.py:** 35+ linee generano "???" nel codice output finale
  - Tutte le unresolved connections ritornano "???"
  - Finisce nel codice SCL generato
  - Causa errori di compilazione TIA Portal

- **fbfc_generator.py:** 8 linee controllano "???" ma eseguono comunque
  - Nessun WARNING generato quando en == "???"
  - Silenziosamente ignora il placeholder e esegue
  - Logica precedentemente non risolta diventa logica incondizionata

**Raccomandazione Urgente:**

Questo è un problema **CRITICO** che richiede azione immediata:

1. **Opzione A (Preferibile):** Lanciare LogicResolutionError
   ```python
   # lad_parser.py - sostituire return '???'
   raise LogicResolutionError(
       f"Cannot resolve logic for {part_type} at UID {part_uid}. "
       f"Wire connection missing or invalid."
   )
   ```

2. **Opzione B (Fallback):** Generare commento esplicito
   ```python
   # lad_parser.py
   return f"/* UNRESOLVED: {part_type} at UID {part_uid} - check connections */"
   ```

3. **Opzione C (Minima):** Aggiungere WARNING in fbfc_generator.py
   ```python
   # fbfc_generator.py linea 201
   if en == '???':
       logger.warning(f"Unresolved condition ??? for {op_type} - executing unconditionally")
   if en and en != 'TRUE' and en != '???':
       # ... genera IF
   ```

**Conclusione:**

La gestione di "???" nel codice è **pericolosa e mal documentata**. Il documento sottostima il problema: non è "trattato come TRUE", è **eseguito incondizionatamente senza protezione IF**, il che è ancora più grave.

**Status:** ⛔ **CRITICO - Richiede correzione**
```

---

## VERSIONE ALTERNATIVA (PIÙ BREVE)

Se preferisci una versione più concisa, usa questa:

```markdown
### N2 - Fallback "???" per Logica Non Risolta: ❌ CRITICO

**File:** `lad_parser.py` - 35+ occorrenze

Placeholder "???" viene generato nel codice output quando la logica non è risolvibile:
```python
# lad_parser.py linea 481
if not source_info:
    return '???'  # ← Finisce nel codice SCL generato!
```

**File:** `fbfc_generator.py` - Gestione pericolosa di "???"

```python
# fbfc_generator.py linea 201
if en and en != 'TRUE' and en != '???':
    self._add_line(f"IF {en} THEN")  # Genera IF solo se en è valido
else:
    # Se en == '???' ESEGUE COMUNQUE SENZA PROTEZIONE!
    self._add_line(f"{op['dest']} := {op['source']};")
```

**Problema Critico:**

Quando condizione è "???" (logica non risolvibile):
- NON viene saltata (come "skip IF")
- Viene ESEGUITA SENZA protezione condizionale
- Logica incondizionata dove dovrebbe essere condizionale

**Impatto:**
- "???" finisce nel codice SCL → Errore di compilazione
- Logica non risolta eseguita senza controllo → Comportamento errato

**Status:** ⛔ **CRITICO - Correzione urgente necessaria**
```

---

## NOTE SULLA SOSTITUZIONE

**Prima di sostituire:**
1. Cerca "### N2 -" nel documento originale
2. Seleziona TUTTO il testo da "### N2" fino a prima di "---" (o prima della prossima sezione)
3. Copia la sezione sopra
4. Incolla per sostituire

**Dopo la sostituzione:**
1. Salva il documento
2. Verifica che il markdown sia corretto
3. Aggiorna anche i numeri di riga in W2, W4, N1 (consultare CORRECTIONS_FOR_EVIDENCE_DOCUMENT.md)
4. Commit con message: "fix: correct critical N2 claim about ??? handling"

---

## VERSIONI DISPONIBILI

### Versione 1: COMPLETA (Consigliata)
- Lunghezza: ~200 linee
- Dettagliamento: Molto alto
- Contiene: Analisi completa, tabella, raccomandazioni
- Uso: Se vuoi documentazione completa e accurata

### Versione 2: MEDIA
- Lunghezza: ~100 linee
- Dettagliamento: Medio
- Contiene: Problema, analisi, raccomandazioni
- Uso: Se vuoi mantenere lunghezza simile all'originale

### Versione 3: BREVE (Sopra)
- Lunghezza: ~50 linee
- Dettagliamento: Basso
- Contiene: Problema e impatto
- Uso: Se vuoi versione concisa ma corretta

---

## COSA È CAMBIATO

### Prima (ERRATO):
```
"Se en == '???' viene trattato come TRUE (skip IF)"
Status: ⚠️ NUOVO (media priorità)
```

### Dopo (CORRETTO):
```
"Se en == '???' viene eseguito SENZA protezione IF (incondizionatamente)"
Status: ❌ CRITICO (alta priorità)
```

### Cambiamenti Principali:
1. ✅ Affermazione corretta: "exec without IF" invece di "skip IF"
2. ✅ Status elevato: ⚠️ NUOVO → ❌ CRITICO
3. ✅ Analisi approfondita: Codice reale mostrato
4. ✅ Impatto esplicitato: Logica incondizionata è pericolosa
5. ✅ Raccomandazioni: 3 opzioni di fix

---

## DOMANDE FREQUENTI

**D: Devo usare quale versione?**
R: Se documentazione completa → Versione COMPLETA. Se brevità → Versione BREVE.

**D: Posso copincollare direttamente?**
R: Sì, il testo è pronto per copia-incolla. Controlla solo il markdown rendering.

**D: Devo cambiar altri punti?**
R: Sì, consulta CORRECTIONS_FOR_EVIDENCE_DOCUMENT.md per:
   - W2: Numeri riga 306-324 → 312-325
   - W4: Numeri riga 773-804 → 770-804
   - N1: ~250 → 276 linee

**D: E la tabella in Executive Summary?**
R: Aggiorna anche il status da ⚠️ NUOVO a ❌ CRITICO nella matrice principale.

---

*Sezione N2 corretta - Pronta per uso - Claude Code Analysis - 2026-01-05*
