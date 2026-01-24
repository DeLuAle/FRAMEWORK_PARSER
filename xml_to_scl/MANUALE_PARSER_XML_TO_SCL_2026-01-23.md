# Manuale tecnico PLC - Parser XML to SCL (TIA Portal)

## 1. Scopo e campo di applicazione
Il modulo **xml_to_scl** esegue l’analisi di esportazioni XML di TIA Portal e genera artefatti SCL/CSV (FB/FC, DB, UDT e Tag Table). Il parser è progettato per:

- Identificare automaticamente il tipo di file XML (FB/FC/DB/UDT/Tag Table).
- Estrarre **interfacce**, **membri UDT**, **variabili DB** e **metadati** (titolo, commento, versione).
- Raccogliere informazioni su **logica grafica** (LAD/FBD) e **SCL** presenti nei CompileUnit.
- Preparare i dati per la generazione di SCL/CSV tramite generatori dedicati.

## 2. Flusso operativo end‑to‑end
1. **Scansione directory**: ricerca dei file XML (opzionale ricorsivo).
2. **Identificazione tipo**: discriminazione per estensione/nome/struttura XML.
3. **Parsing specifico**: istanziazione del parser appropriato (FB/FC, DB, UDT, Tag Table).
4. **Normalizzazione dati**: struttura unificata (dictionary) con attributi comuni e specifici.
5. **Generazione output**: chiamata al generatore SCL/CSV con i dati estratti.

## 3. Struttura del codice e dipendenze

### 3.1 Mappa moduli principali
| Modulo | Ruolo tecnico | Input | Output | Note operative |
|---|---|---|---|---|
| `main.py` | CLI di conversione e routing dei file | Directory o file XML | File `.scl`, `.db`, `.udt`, `.csv` | Se trova `.scl` lo copia senza parsing |
| `xml_parser_base.py` | Base parser XML con logica comune | XML TIA Portal | `parsed_data` normalizzato | Gestisce commenti multilingua e interfacce |
| `fbfc_parser.py` | Parser FB/FC | XML blocchi | Interfacce + reti logiche | Riconosce LAD/FBD/SCL |
| `db_parser.py` | Parser DB | XML Global/Instance DB | Variabili DB | Gestisce `InstanceOfName` |
| `udt_parser.py` | Parser UDT | XML PlcStruct | Membri UDT | Sezione `None` o `Static` |
| `plc_tag_parser.py` | Parser Tag Table | XML Tag Table | Lista Tag/Costanti | Estrae commenti multilingua |
| `utils.py` | Utility di parsing/formatting | Dati XML | Valori normalizzati | Parsing Array, escaping, default value |

### 3.2 Dipendenze esterne e standard
| Libreria | Uso tecnico | Note |
|---|---|---|
| `xml.etree.ElementTree` | Parsing XML | Fallback se `defusedxml` non disponibile |
| `defusedxml.ElementTree` | Mitigazione XXE | Protezione per XML ostili |
| `argparse` | CLI | Parametri conversione |
| `logging` | Tracciamento eventi | Livello configurabile |
| `pathlib` | Gestione path | Cross‑platform |

### 3.3 Dipendenze interne
- `config.py`: mapping datatype, namespace, impostazioni globali.
- `fbfc_generator.py`, `db_generator.py`, `udt_generator.py`, `plc_tag_generator.py`: output SCL/CSV.
- `lad_parser.py`, `scl_token_parser.py`: parsing logiche grafiche e SCL.

## 4. Identificazione del tipo file (routing)
**Regole principali:**
- Estensione `.scl`: copia diretta in output (bypass parser).
- Estensione `.xml`: analisi rapida su nome e tag XML.
- Tag decisivi: `SW.Blocks.FB`, `SW.Blocks.FC`, `SW.Blocks.GlobalDB`, `SW.Types.PlcStruct`, `SW.Tags.PlcTagTable`.

**Impatto di un cambio segnale nel file XML:**
- Se il tag di root cambia (es. da `FB` a `FC`), il routing indirizza un parser diverso e varia la struttura dati prodotta.
- Se il nome del file cambia includendo “Tag Table”, la logica privilegia il parser Tag Table.

## 5. Parser base XML (`XMLParserBase`)

### 5.1 Ciclo di parsing
1. **Parsing sicuro** con `defusedxml`, fallback a `ElementTree`.
2. **Ricerca block element** specifico del tipo (implementato nelle classi figlie).
3. **Attributi comuni**: `name`, `number`, `access`, `programming_language`, `memory_layout`.
4. **Commenti multilingua**: `Comment` e `Title`.
5. **Interfacce**: sezioni `Input`, `Output`, `InOut`, `Static`, `Temp`, `Constant`, `None`.

### 5.2 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT – Mappatura sezioni
| Sezione XML | Interfaccia SCL attesa | Segnale | Uso del segnale | Effetto di cambiamento |
|---|---|---|---|---|
| `Input` | `VAR_INPUT` | `name`, `datatype`, `start_value` | Parametri in ingresso ai blocchi | Un cambio in XML modifica la firma del blocco generato e le chiamate esterne |
| `Output` | `VAR_OUTPUT` | `name`, `datatype`, `start_value` | Uscite del blocco verso logiche esterne | La modifica altera i segnali esposti; necessaria revisione chiamanti |
| `InOut` | `VAR_IN_OUT` | `name`, `datatype` | Parametri pass‑by‑reference | Cambiamento impatta sia chiamante sia FB/FC interno |
| `Static` | `VAR` (FB) / DB statico | `name`, `datatype`, `start_value` | Memoria persistente | Modifica altera lo stato salvato e i dati inizializzati |
| `Temp` | `VAR_TEMP` | `name`, `datatype` | Variabili temporanee | Modifica influenza logica interna ma non interfacce |
| `Constant` | `VAR CONSTANT` | `name`, `datatype`, `start_value` | Costanti di blocco | Cambiamento ridisegna valori fissi usati nella logica |

> Nota di integrazione: le sezioni `Input/Output/InOut` sono il punto di contatto con logiche esterne (OB, altri FB/FC, HMI/SCADA). Ogni variazione di questi segnali comporta la revisione degli interfacciamenti di progetto.

### 5.3 Documentazione di ogni membro UDT (modello dati)
La funzione `_parse_member` genera un dizionario che descrive ogni membro; i campi standard da documentare sono:

| Campo membro | Descrizione tecnica | Uso in generazione | Effetto di cambiamento |
|---|---|---|---|
| `name` | Nome simbolico | Nome variabile UDT | Cambia il simbolo in SCL e nelle chiamate |
| `full_path` | Percorso completo | Riferimenti a struct annidate | Modifica impatta accessi gerarchici |
| `datatype` | Tipo TIA/SCL | Determina dimensione e formato | Cambia mapping di memoria e conversioni |
| `is_array` | Flag array | Decide generazione `ARRAY[...] OF` | Cambia tipo da scalare a vettore |
| `array_bounds` | Limiti array | Dimensionamento indice | Cambia dimensione e offset |
| `base_type` | Tipo base array | Tipo degli elementi | Influenza compatibilità e casting |
| `version` | Versione istanza FB | Allineamento con FB | Cambio = potenziale incompatibilità |
| `start_value` | Valore iniziale | Inizializzazione DB/UDT | Cambia stato iniziale al download |
| `comment` | Commento multilingua | Documentazione SCL | Cambia note operative |
| `attributes` | Attributi aggiuntivi | Flag e proprietà avanzate | Può cambiare comportamento del blocco |
| `members` | Lista membri nidificati | Strutture interne UDT | Cambia layout interno |
| `is_struct` | Flag struttura | Definisce nesting | Cambio influenza accesso a campi |

**Uso segnali e impatto variazioni:**
- Se `start_value` viene aggiornato in XML, l’inizializzazione in SCL/DB viene rigenerata con il nuovo valore.
- Se un `datatype` passa da scalare ad `Array`, il layout memoria e la generazione cambiano in modo deterministico.

## 6. Parser FB/FC (`FBFCParser`)
- Estrae **attributi**: `HeaderAuthor`, `HeaderFamily`, `HeaderVersion`, `MemoryLayout`, `ProgrammingLanguage`.
- Estrae **interfacce** complete (Input/Output/InOut/Static/Temp/Constant).
- Riconosce **logica grafica LAD/FBD** e **SCL** in `CompileUnit`:
  - LAD/FBD: analizza `NetworkSource/FlgNet` e ricava `fb_calls` + `logic_ops`.
  - SCL: analizza `StructuredText` con parser token.

**Segnali e cambiamento:**
- Se `ProgrammingLanguage` è LAD/FBD, il parser attiva la raccolta dei `CompileUnit`; se cambia a SCL, la logica viene letta come testo strutturato.

**Integrazione con logiche esterne (casi d’uso):**
- **FB di comando motore**: ingressi `StartCmd`, `StopCmd`, uscite `Running`, `Fault`.
  - Il parser ricostruisce l’interfaccia e prepara la generazione SCL; i blocchi chiamanti dovranno collegare gli stessi segnali.
- **FC di calcolo**: input parametrici e output risultato; la modifica di un input in XML genera una nuova firma SCL.

## 7. Parser DB (`DBParser`)
- Riconosce DB Global o Instance.
- Se `InstanceDB`, legge `InstanceOfName` per collegamento FB.
- Sezione prioritaria: `Static` (default DB), fallback su prima sezione valida.

**Segnali e cambiamento:**
- Variabili DB sono **segnali persistenti**. Modifiche di `start_value` o `datatype` riflettono variazioni di stato iniziale e layout memoria.

**Casi d’uso:**
- DB di ricetta: modifica tipi o array in XML implica rigenerazione della struttura dati per HMI e ricette.

## 8. Parser UDT (`UDTParser`)
- Estrae struttura dati custom da `PlcStruct`.
- Usa sezione `None` o `Static` come contenitore membri.

**Segnali e cambiamento:**
- Ogni membro UDT rappresenta un segnale strutturato; cambiando il `datatype` o aggiungendo un membro si modifica il layout globale e tutte le istanze del tipo.

**Casi d’uso:**
- UDT `MotorStatus`: se aggiunto un campo `Temperature`, le istanze in DB/FB devono essere aggiornate.

## 9. Parser Tag Table (`PLCTagParser`)
- Estrae **Tag** (`SW.Tags.PlcTag`) e **Costanti** (`SW.Tags.PlcUserConstant`).
- Campi: `name`, `data_type`, `logical_address`, `value`, `comment`.

**Segnali e cambiamento:**
- Cambiando un `logical_address` si riallinea il mapping con l’hardware/IO o indirizzamenti di memoria.

**Casi d’uso:**
- Tabelle di segnali hardware: una modifica indirizzo IO comporta rigenerazione CSV per import in TIA Portal.

## 10. Gestione logging ed errori
- Errori gestiti: `FileNotFoundError`, `ParseError`, `ValueError`.
- `setup_logging` consente tracciabilità industriale con timestamp.

## 11. Integrazione con generatori SCL/CSV
Il parser consegna una struttura dati unificata che i generatori consumano per produrre:
- FB/FC in `.scl`.
- DB in `.db`.
- UDT in `.udt`.
- Tag Table in `.csv`.

**Nota di integrazione:**
Il parsing è progettato per essere indipendente dalla generazione. Questo consente l’uso dei dati per:
- Export/Import TIA Portal.
- Documentazione automatica.
- Validazioni di conformità (naming, datatype, layout).

## 12. Casi d’uso reali (TIA Portal)
| Caso d’uso | Parser coinvolto | Output | Integrazione esterna |
|---|---|---|---|
| Migrazione progetto legacy | FB/FC + DB + UDT | SCL/DB/UDT | Reimport in TIA Portal |
| Documentazione segnali HMI | Tag Table | CSV | Import su HMI/SCADA |
| Normalizzazione strutture dati | UDT/DB | UDT/DB SCL | Allineamento con standard aziendali |

