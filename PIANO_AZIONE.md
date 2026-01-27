# Piano d'Azione - FRAMEWORK_PARSER

**Ultimo Aggiornamento**: 2026-01-22 19:35 (Fix #1 COMPLETATO)
**Branch Attivo**: claude/verify-scl-parser-rules-HQcqc

---

## 🚨 Criticità Alta (MUST FIX)

### 1. VAR CONSTANT senza inizializzazione ✅ COMPLETATO

**Priorità**: 🔴 CRITICA
**Status**: ✅ **COMPLETATO** (Commit: fd08755)
**Tempo Impiegato**: 3 ore (stimato 4-6h)
**Componente**: xml_to_scl
**File Modificati**:
- `xml_to_scl/xml_parser_base.py` - Fix estrazione StartValue con namespace
- `xml_to_scl/utils.py` - Aggiunta funzione get_default_value_for_type()
- `xml_to_scl/scl_generator_base.py` - Enhanced member declaration con default values
- `xml_to_scl/fbfc_generator.py` - Fix f-string syntax error
- `xml_to_scl/test_var_constant_initialization.py` - Nuovi test (3/3 PASS)

**Problema Originale**:
Le sezioni `VAR CONSTANT` vengono generate senza valori di inizializzazione, violando le regole SCL documentate in `xml_to_scl/docs/KB_SCL/Regole_Creazione_FC_SCL.md`.

**Output Attuale** (Scorretto):
```scl
VAR CONSTANT
   sds : Bool;           // ❌ MANCA := valore
   PI : Real;            // ❌ MANCA := valore
END_VAR
```

**Output Richiesto** (Corretto):
```scl
VAR CONSTANT
   sds : Bool := TRUE;   // ✅ Con inizializzazione
   PI : Real := 3.14159; // ✅ Con inizializzazione
END_VAR
```

**Impatto**: TIA Portal potrebbe rifiutare l'import dei file SCL generati.

**Soluzioni Proposte**:

**Opzione A** (Preferita): Estrarre valori dall'XML
1. Verificare se TIA Portal XML include `start_value` per elementi `VAR CONSTANT`
2. Modificare `fbfc_parser.py` per estrarre questi valori nella sezione `Constant`
3. Assicurare che `include_value=True` funzioni correttamente in `fbfc_generator.py:113`

**Opzione B**: Valori di default per tipo
1. Se `start_value` non disponibile nell'XML, generare valori di default:
   - `Bool` → `FALSE`
   - `Int/DInt/SInt` → `0`
   - `Real/LReal` → `0.0`
   - `Time` → `T#0ms`
   - `String` → `''`
2. Implementare in `scl_generator_base.py:_generate_member_declaration()`

**Opzione C**: Non generare sezione VAR CONSTANT
1. Se non ci sono valori disponibili, omettere completamente `VAR CONSTANT`
2. Aggiungere warning nel batch report: "VAR CONSTANT omitted (no initialization values)"

**Soluzione Implementata**: Ibrida (Opzione A + B)
1. ✅ Fix parser XML per estrarre StartValue con supporto namespace
   - Problema: StartValue era in namespace `{http://www.siemens.com/.../v5}`
   - Soluzione: Cerca con namespace, fallback senza namespace
2. ✅ Aggiunta generazione valori di default per tipo quando StartValue assente
   - `Bool` → `FALSE`, `Int` → `0`, `Real` → `0.0`, `Time` → `T#0ms`, `String` → `''`
3. ✅ Test completi: 3/3 test passano
   - test_constant_with_startvalue_from_xml
   - test_constant_without_startvalue_gets_default
   - test_no_uninitialized_constants

**Risultati**:
```scl
// Prima (ERRATO):
VAR CONSTANT
   "3002_TRASPORTO" : Int;  // ❌ Mancava valore

// Dopo (CORRETTO):
VAR CONSTANT
   "3002_TRASPORTO" : Int := 3002;  // ✅ Da XML StartValue
```

**Test Validazione**:
- ✅ Test suite: 16/24 passano (fallimenti pre-esistenti, non correlati al fix)
- ✅ Nuovi test VAR CONSTANT: 3/3 passano
- ✅ Validato su file reale: HMI_A04_FB.xml (40+ costanti corrette)
- ⏳ Import TIA Portal: Da testare (richiede ambiente TIA Portal)

**Stima vs Reale**: 4-6 ore stimato / 3 ore reale ✅

---

## ⚠️ Criticità Media (SHOULD FIX)

### 2. Header TITLE/AUTHOR/FAMILY/NAME non conformi ✅ COMPLETATO

**Priorità**: 🟡 MEDIA
**Status**: ✅ **COMPLETATO** (Commit: cedd7a6)
**Tempo Impiegato**: 1.5 ore (stimato 3-4h)
**Componente**: xml_to_scl
**File Modificati**:
- `xml_to_scl/fbfc_generator.py` - Nuova _generate_header_metadata()

**Problema Originale**:
Le regole KB_SCL richiedono metadata formattati in modo specifico nell'header del blocco:

**Output Attuale**:
```scl
FUNCTION_BLOCK "SinamicsCU"
VERSION : 0.1
// Info                         ← Solo commento
```

**Output Richiesto**:
```scl
FUNCTION_BLOCK "SinamicsCU"
TITLE = Info per controllo Sinamics CU    ← TITLE senza virgolette
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : Sviluppatore                     ← AUTHOR con :
FAMILY : Drives                           ← FAMILY con :
NAME : 'SinamicsCU_v1'                    ← NAME con virgolette
VERSION : 0.1
```

**Impatto**: Codice compila in TIA Portal, ma non segue le best practice documentate.

**Soluzione Implementata**:
1. ✅ Creata funzione _generate_header_metadata()
   - Genera metadata nell'ordine KB_SCL: TITLE → {Attributes} → AUTHOR → FAMILY → NAME → VERSION
   - Generazione condizionale: solo se dati presenti in XML
2. ✅ Refactoring _generate_attributes()
   - Split in _generate_attributes_braces() (solo S7_Optimized_Access)
   - Rimossi AUTHOR/FAMILY da {...} (vanno fuori)
3. ✅ Formato NAME sempre generato: 'BlockName_vVersion'

**Risultati**:
```scl
// Prima (NON CONFORME):
FUNCTION_BLOCK "HMI_A04_FB"
{ S7_Optimized_Access := 'TRUE'; Author : 'Piemme'; Family : 'System' }
VERSION : 0.1

// Dopo (KB_SCL CONFORME):
FUNCTION_BLOCK "HMI_A04_FB"
{ S7_Optimized_Access := 'TRUE' }
AUTHOR : Piemme
FAMILY : System
NAME : 'HMI_A04_FB_v0.1'
VERSION : 0.1

// Con TITLE (SinamicsCU):
FUNCTION_BLOCK "SinamicsCU"
TITLE = Info
{ S7_Optimized_Access := 'TRUE' }
NAME : 'SinamicsCU_v0.1'
VERSION : 0.1
```

**Test Validazione**:
- ✅ Validato con HMI_A04_FB.xml (ha AUTHOR/FAMILY, no TITLE)
- ✅ Validato con SinamicsCU.xml (ha TITLE, no AUTHOR/FAMILY)
- ✅ Test VAR CONSTANT ancora passano (3/3 OK, non rotti dal refactoring)
- ⏳ Import TIA Portal: Da testare

**Stima vs Reale**: 3-4 ore stimato / 1.5 ore reale ✅

---

## 💡 Criticità Bassa (NICE TO HAVE)

### 3. Indentazione corpo funzione con TAB

**Priorità**: 🟢 BASSA
**Componente**: xml_to_scl
**File Coinvolti**:
- `xml_to_scl/config.py:67`
- `xml_to_scl/scl_generator_base.py:92-96`

**Problema**:
Le regole KB_SCL richiedono TAB per indentazione nel corpo della funzione (BEGIN), ma il parser usa 3 spazi ovunque.

**Output Attuale**:
```scl
BEGIN
   REGION Logic        ← 3 spazi
      #var := 1;       ← 6 spazi (2 livelli × 3)
   END_REGION
END_FUNCTION
```

**Output Richiesto**:
```scl
BEGIN
	REGION Logic        ← TAB
	   #var := 1;       ← TAB + spazi o doppio TAB
	END_REGION
END_FUNCTION
```

**Impatto**: Cosmetico - TIA Portal accetta entrambi.

**Soluzione**:

1. **Aggiungere configurazione separata**:
```python
# config.py
DEFAULT_CONFIG = {
    'scl_indent': '   ',      # 3 spazi per VAR_INPUT/OUTPUT
    'scl_body_indent': '\t',  # TAB per corpo BEGIN
    ...
}
```

2. **Modificare scl_generator_base.py**:
```python
def _add_line(self, line: str = "", context='default'):
    """Add a line with context-aware indentation"""
    if line:
        if context == 'body':
            indent = config.body_indent * self.indent_level
        else:
            indent = config.indent * self.indent_level
        self.scl_lines.append(f"{indent}{line}")
```

3. **Passare context in fbfc_generator.py** per righe dentro BEGIN

**Test Richiesto**:
- Verificare indentazione visivamente in file generati
- Importare in TIA Portal per conferma accettazione

**Stima Effort**: 2-3 ore

---

## 📋 Altre Attività

### 4. Aggiornare Documentazione

**Priorità**: 🟢 BASSA
**File Coinvolti**:
- `xml_to_scl/docs/README.md`
- `CLAUDE.md`

**Azioni**:
- Documentare le fix implementate
- Aggiornare sezione "Known Limitations" con le non-conformità risolte
- Aggiungere riferimento a `KB_SCL/Regole_Creazione_FC_SCL.md`

**Stima Effort**: 1 ora

---

### 5. Test di Integrazione con TIA Portal

**Priorità**: 🟡 MEDIA
**Prerequisito**: Completare Fix #1 e #2

**Azioni**:
1. Generare file SCL con fix implementate
2. Importare in TIA Portal (V17 o superiore)
3. Verificare compilazione senza errori
4. Documentare eventuali problemi residui

**Stima Effort**: 2 ore

---

## 📊 Riepilogo Effort

| Priorità | Attività | Effort Stimato | Effort Reale | Status |
|-----------|----------|----------------|--------------|--------|
| 🔴 CRITICA | #1 VAR CONSTANT fix | 4-6h | 3h | ✅ DONE (fd08755) |
| 🟡 MEDIA | #2 Header metadata | 3-4h | 1.5h | ✅ DONE (cedd7a6) |
| 🟢 BASSA | #3 TAB indentazione | 2-3h | - | ⏸️ TODO (opzionale) |
| 🟢 BASSA | #4 Documentazione | 1h | - | 🔄 IN PROGRESS |
| 🟡 MEDIA | #5 Test TIA Portal | 2h | - | ⏸️ TODO (richiede TIA) |

**Totale Effort Stimato**: 12-16 ore
**Effort Completato**: 4.5 ore / 12-16 ore (28-38%)
**Completamento Fix Prioritari**: 2/2 (100%) ✅
**Prossimo**: Aggiornamento documentazione finale

**Sequenza Consigliata**:
1. Fix #1 (VAR CONSTANT) → Test → Commit
2. Fix #2 (Header metadata) → Test → Commit
3. Test #5 (TIA Portal integration) → Documentare risultati
4. Fix #3 (TAB) se richiesto da utente
5. Aggiornamento documentazione #4

---

## 🔗 Riferimenti

- **Verifica Regole**: `VERIFICA_REGOLE_SCL_KB.md`
- **Regole SCL**: `xml_to_scl/docs/KB_SCL/Regole_Creazione_FC_SCL.md`
- **Parser FB/FC**: `xml_to_scl/fbfc_generator.py`
- **Parser XML**: `xml_to_scl/fbfc_parser.py`
- **Config**: `xml_to_scl/config.py`

---

**Note**:
- Questo piano d'azione deriva dall'analisi di conformità completata il 2026-01-22
- Priorità basate su impatto sulla compatibilità con TIA Portal
- Effort stimati assumono familiarità con codebase esistente

**Prossimi Step**:
1. Review di questo piano con team/owner
2. Creazione issue GitHub per tracking (opzionale)
3. Sviluppo fix in ordine di priorità
