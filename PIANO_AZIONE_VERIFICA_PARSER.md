# Piano di Azione - Verifica e Pulizia Parser XML to SCL

**Data Inizio:** 2026-01-21  
**Branch:** `claude/verify-xml-parser-cleanup-jmpca`  
**Obiettivo Operativo:** Verificare risoluzione debolezze parser, eliminare documentazione obsoleta e mantenere tracciabilità tecnica in stile PLC industriale.

---

## 1. Sintesi Esecutiva

| ID | Area | Stato | Nota Operativa | Priorità |
| --- | --- | --- | --- | --- |
| N2 | Gestione fallback `???` | ❌ Da fixare | Logica non risolta eseguita senza protezione | 🔴 Critica |
| N1 | Expression Builder | ✅ Risolto | Abilitato condizionalmente | 🟡 Alta |
| W4 | FB Signatures | ✅ Risolto | Caricato da JSON + fallback hardcoded | 🟡 Alta |
| W5 | Cross-file UID | ❌ Non risolto | Parser single-file | 🟢 Bassa |
| W7 | Default Timer/Counter | ✅ Risolto | Inject default da FB_SIGNATURES | 🟡 Alta |
| W1 | UDT Incomplete | ⚠️ Parziale | Array/circolari non testati | 🟢 Bassa |
| W3 | Type Casting | ⚠️ Parziale | AutomaticTyped mancante | 🟢 Bassa |
| W6 | Formattazione SCL | ⚠️ Parziale | Edge cases non verificati | 🟢 Bassa |
| W2 | Wire Branching | ✅ Risolto | Iterazione children[1:] | 🟡 Media |

---

## 2. Fase 1 - Analisi Debolezze Identificate

### 2.1 Debolezze Critiche

| ID | File | Stato | Evidenza | Azione |
| --- | --- | --- | --- | --- |
| N2 | `lad_parser.py`, `fbfc_generator.py` | ❌ Presente | `???` in più punti | Fix urgente |

### 2.2 Debolezze Confermate

| ID | File | Stato | Evidenza | Azione |
| --- | --- | --- | --- | --- |
| W4 | `config.py` | ✅ Risolto | `FB_SIGNATURES` dinamico | Nessuna |
| W5 | `xml_parser_base.py`, `main.py` | ❌ Presente | Manca project context | Valutare |
| W7 | `lad_parser.py` | ✅ Risolto | Default parametri | Nessuna |

### 2.3 Debolezze Parziali

| ID | File | Stato | Nota Tecnica | Azione |
| --- | --- | --- | --- | --- |
| W1 | `udt_generator.py` | ⚠️ Parziale | Nesting OK, array non testati | Test futuri |
| W3 | `lad_parser.py` | ⚠️ Parziale | Convert OK, AutomaticTyped mancante | Valutare |
| W6 | N/A | ⚠️ Parziale | Formattazione SCL non verificata | Test estesi |

### 2.4 Debolezze Risolte

| ID | File | Stato | Implementazione |
| --- | --- | --- | --- |
| W2 | `lad_parser.py` | ✅ Confermato | Iterazione `children[1:]` |

---

## 3. Fase 2 - Verifica Codice Attuale

### 3.1 Verifica N2 - Problema `???`

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Contare occorrenze in `lad_parser.py` | ☐ | Uso `rg "\?\?\?"` |
| Verificare `fbfc_generator.py` | ☐ | Blocco generazione FB/FC |
| Scegliere strategia A/B/C | ☐ | Preferenza: Fail Fast |

### 3.2 Verifica N1 - Expression Builder

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Verificare `EXPRESSION_BUILDER_AVAILABLE` | ☐ | In `lad_parser.py` |
| Verificare `expression_builder.py` | ☐ | Stabilità parsing |

### 3.3 Verifica W4 - FB Signatures

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Verificare `FB_SIGNATURES` | ☐ | `config.py` |
| Verificare `SYSTEM_BLOCK_PARAMS` | ☐ | `config.py` |

### 3.4 Verifica W5 - Cross-file Resolution

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Verificare `xml_parser_base.py` | ☐ | Input `xml_path` solo file |
| Verificare `main.py` | ☐ | Symbol table globale |

### 3.5 Verifica W7 - Timer/Counter Defaults

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Verificare injection defaults | ☐ | `lad_parser.py` |

---

## 4. Fase 3 - Implementazione Fix

### 4.1 Fix Critici (Priorità Alta)

| Fix | Stato | Strategia Operativa |
| --- | --- | --- |
| N2 - Gestione `???` | ☐ | A: Fail Fast / B: Commento / C: Default FALSE |
| N1 - Expression Builder | ☐ | Abilitare se stabile |

### 4.2 Fix Importanti (Priorità Media)

| Fix | Stato | Strategia Operativa |
| --- | --- | --- |
| W4 - FB Signatures | ☐ | Dizionario `FB_SIGNATURES` |
| W7 - Timer/Counter Defaults | ☐ | Default da `FB_SIGNATURES` |

### 4.3 Fix Opzionali (Priorità Bassa)

| Fix | Stato | Strategia Operativa |
| --- | --- | --- |
| W5 - Cross-file UID | ☐ | ProjectContext |
| W3 - AutomaticTyped | ☐ | Gestione conversione |
| W1 - UDT complessi | ☐ | Test array/circolari |

---

## 5. Fase 4 - Test e Validazione

| Test | Stato | Note Operative |
| --- | --- | --- |
| `run_all_tests.py` | ☐ | Suite completa |
| `test_security_xxe.py` | ☐ | Security |
| `test_region_nesting.py` | ☐ | REGION nesting |
| `test_boolean_expression_builder.py` | ☐ | Boolean expression |
| `test_fb_parameters.py` | ☐ | FB params |
| `test_integration_suite.py` | ☐ | Integrazione |
| `batch_convert_project.py` (PLC_410D1) | ☐ | Conversione progetto |

---

## 6. Fase 5 - Identificazione File Obsoleti

### 6.1 File Root - Da Eliminare

| File | Stato | Azione |
| --- | --- | --- |
| `VERIFICATION_REPORT_v2_EVIDENCE.md` | ✅ | Eliminare |
| `VERIFICATION_EXECUTIVE_SUMMARY.txt` | ✅ | Eliminare |
| `VERIFICATION_MANIFEST.txt` | ✅ | Eliminare |
| `QUICK_START.txt` | ✅ | Eliminare |

### 6.2 File Docs - Da Archiviare

| File | Stato | Azione |
| --- | --- | --- |
| `xml_to_scl/docs/analisi_debolezze_parser_v2_EVIDENCE.md` | ✅ | Spostare in `xml_to_scl/docs/archive/` |

---

## 7. Fase 6 - Pulizia e Commit

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Eliminare file obsoleti | ☐ | `git rm` |
| Archiviare doc | ☐ | `git mv` |
| Commit fix | ☐ | Messaggio dettagliato |
| Commit pulizia doc | ☐ | Separato se necessario |
| Push branch | ☐ | `git push -u origin` |

---

## 8. Fase 7 - Documentazione Finale

| Attività | Stato | Nota Operativa |
| --- | --- | --- |
| Aggiornare piano | ☐ | Allineare stato reale |
| Creare `SUMMARY_VERIFICA_PARSER.md` | ☐ | Manuale finale |

---

## 9. Metriche di Progresso

| Metrica | Valore |
| --- | --- |
| Debolezze Totali Identificate | 9 (W1-W7, N1-N2) |
| Risolte | 5/9 |
| Da Verificare | 1/9 (W5) |
| Parziali | 3/9 (W1, W3, W6) |

---

## 10. Strategia per `???`

| Opzione | Descrizione | Nota Operativa |
| --- | --- | --- |
| A | Fail Fast | `raise LogicResolutionError(...)` |
| B | Commento esplicito | `/* UNRESOLVED */ TRUE` |
| C | Default FALSE | `logger.error(...); en = 'FALSE'` |

---

## 11. Raccomandazioni Future

| Priorità | Attività | Nota Operativa |
| --- | --- | --- |
| Alta | Fix test failures pre-esistenti | Boolean expression, FB params |
| Media | Validare su progetti reali | `PLC_410D1` |
| Bassa | W5/W3/W1 | Valutazione tecnica |

---

## 12. Conclusione Operativa

**Obiettivo Attuale:** Avvio fase di pulizia e fix critici, con tracciabilità completa in stile PLC industriale.  
**Nota Tecnica:** Tutti i nomi simbolici restano invariati per garantire compatibilità con logiche esterne e con configurazioni TIA Portal.
