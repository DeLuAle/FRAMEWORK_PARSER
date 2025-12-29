# 📚 DocKB_Siemens

**Documentation Knowledge Base for Siemens PLC & Drive Systems**

Sistema di gestione e ricerca documentazione tecnica per prodotti Siemens (SINAMICS, S7-1500, TIA Portal). Estrae informazioni da manuali PDF e le rende facilmente ricercabili tramite Knowledge Base strutturata in JSON.

---

## 🎯 Cos'è DocKB_Siemens?

DocKB_Siemens è un **sistema di Information Retrieval** che:

1. **Estrae** testo dapid from the provided manuali PDF Siemens
2. **Struttura** le informazioni in formato JSON ricercabile
3. **Indicizza** contenuti per categoria (parametri, fault, allarmi, ecc.)
4. **Permette ricerca rapida** senza dover aprire PDF da 1000+ pagine

### 🔍 Non è un RAG (ma può diventarlo)

- ✅ **Sistema di Retrieval** basato su keyword matching
- ✅ **Knowledge Base strutturata** con metadata e categorie
- ❌ **Non usa AI/LLM** (completamente offline, zero costi)
- ❌ **Non semantic search** (usa pattern di testo)

Vedi [Sistema KB - Spiegazione Dettagliata](#come-funziona-il-sistema) per dettagli tecnici.

---

## ⚡ Quick Start

### 📦 Passo 1: Installa Dipendenze Sistema

Il sistema richiede **Poppler** (per estrazione PDF) e **Pandoc** (per conversione documenti).

#### 🪟 **WINDOWS**

**Metodo A - Chocolatey** (Consigliato ⭐):

1. **Installa Chocolatey** (se non già presente):
   
   Apri **PowerShell come Amministratore** e lancia:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Installa Poppler e Pandoc**:
   ```powershell
   choco install poppler pandoc -y
   ```

3. **Verifica installazione**:
   ```powershell
   pdftotext -v
   pandoc --version
   ```

**Metodo B - Download Manuale**:

1. **Poppler**:
   - Scarica: https://github.com/oschwartz10612/poppler-windows/releases/latest
   - Estrai in: `C:\Program Files\poppler\`
   - Aggiungi al PATH: `C:\Program Files\poppler\Library\bin`

2. **Pandoc**:
   - Scarica installer: https://pandoc.org/installing.html
   - Installa normalmente (aggiungerà automaticamente al PATH)

3. **Aggiungi Poppler al PATH**:
   ```powershell
   # PowerShell come Amministratore
   [Environment]::SetEnvironmentVariable(
       "Path", 
       $env:Path + ";C:\Program Files\poppler\Library\bin", 
       "Machine"
   )
   ```
   **Importante**: Riavvia PowerShell/terminale dopo aver modificato il PATH

4. **Verifica**:
   ```powershell
   # Chiudi e riapri PowerShell, poi:
   pdftotext -v
   pandoc --version
   ```

#### 🐧 **LINUX** (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install poppler-utils pandoc -y
```

**Verifica**:
```bash
pdftotext -v
pandoc --version
```

#### 🍎 **macOS**

```bash
brew install poppler pandoc
```

**Verifica**:
```bash
pdftotext -v
pandoc --version
```

---

### 📂 Passo 2: Posiziona i PDF

Copia i tuoi manuali PDF in:
```
resources/pdfs/sinamics/     ← PDF SINAMICS
resources/pdfs/s7_1500/      ← PDF S7-1500
```

### ⚙️ Passo 3: Estrai e Costruisci la Knowledge Base

La procedura si divide sempre in **due fasi**: 
1. **Estrazione**: Smonta i PDF in file JSON (operazione lenta, si fa una volta sola).
2. **Build**: Crea l'indice di ricerca finale dai file estratti (operazione veloce).

#### 🔵 Esempio per SINAMICS S120/S150
Usa questi comandi se i tuoi PDF sono in `resources/pdfs/sinamics`:

```powershell
# 1. Estrazione (PDF -> JSON)
python scripts/extract_pdf_to_json.py --pdf-dir "resources/pdfs/sinamics" --output-dir "output/sinamics"

# 2. Creazione Database (JSON -> KB)
python scripts/build_knowledge_base.py --input-dir "output/sinamics" --output-dir "kb/sinamics"
```

#### 🟠 Esempio per S7-1500 / Motion Control
Usa questi comandi se i tuoi PDF sono in `resources/pdfs/s7_1500`:

```powershell
# 1. Estrazione (PDF -> JSON)
python scripts/extract_pdf_to_json.py --pdf-dir "resources/pdfs/s7_1500" --output-dir "output/s7_1500"

# 2. Creazione Database (JSON -> KB)
python scripts/build_knowledge_base.py --input-dir "output/s7_1500" --output-dir "kb/s7_1500"
```

**Fatto!** Ora le tue basi di conoscenza sono pronte nelle cartelle `kb/sinamics` e `kb/s7_1500`.

---

## 🔧 Troubleshooting Dipendenze

### ❌ Errore: "Tool mancanti: pdftotext, pdfinfo"

**Causa**: Poppler non è installato o non è nel PATH.

**Soluzione Windows**:
```powershell
# Verifica se poppler è installato
where.exe pdftotext

# Se non trovato, installa con Chocolatey
choco install poppler -y

# Oppure scarica manualmente da:
# https://github.com/oschwartz10612/poppler-windows/releases/
```

**Dopo l'installazione manuale**, aggiungi al PATH e riavvia PowerShell.

### ❌ Errore: "pandoc: command not found"

**Soluzione Windows**:
```powershell
choco install pandoc -y
```

**Soluzione Linux**:
```bash
sudo apt-get install pandoc -y
```

### ⚠️ PATH non aggiornato dopo installazione

**Windows**: Chiudi **completamente** PowerShell/CMD e riaprilo. Se ancora non funziona, riavvia il PC.

**Verifica PATH manualmente**:
```powershell
$env:Path -split ';' | Select-String poppler
```

Deve mostrare: `C:\Program Files\poppler\Library\bin` o simile.

### ✅ Script di Verifica Rapida

Usa lo script fornito per verificare tutte le dipendenze in una volta. Se ricevi un errore di protezione (PSSecurityException), usa il flag `-ExecutionPolicy Bypass`:

```powershell
# Dalla root del progetto
powershell -ExecutionPolicy Bypass -File .\test_dependencies.ps1
```

**Output atteso**:
```
🔍 Verifica Dipendenze DocKB_Siemens
==================================================

Verifica Python... ✓ OK
  → Python 3.11.x

Verifica pdftotext (Poppler)... ✓ OK
  → pdftotext version 24.x.x

Verifica pdfinfo (Poppler)... ✓ OK
  → pdfinfo version 24.x.x

Verifica Pandoc... ✓ OK
  → pandoc 3.x.x

==================================================
✅ TUTTE LE DIPENDENZE SONO INSTALLATE!
```

**In alternativa** (manuale):
```powershell
pdftotext -v
pandoc --version
python --version
```

---

## 📁 Struttura Progetto

```
DocKB_Siemens/
├── resources/               # 📥 INPUT: PDF sorgente
│   └── pdfs/
│       ├── sinamics/       # Manuali SINAMICS
│       └── s7_1500/        # Manuali S7-1500
│
├── kb/                      # 📚 OUTPUT: Knowledge Bases
│   ├── sinamics/
│   ├── s7_1500/
│   └── unified/            # KB unificata
│
├── scripts/                 # 🔧 Script Python
│   ├── extract_pdf_to_json.py
│   ├── build_knowledge_base.py
│   ├── sinamics_kb_search.py
│   └── ...
│
├── tia_portal/             # ⚙️ Integrazione TIA Portal (SCL)
│   ├── SINAMICS_AlarmHandler.scl
│   └── Alarms_Faults.scl
│
├── data/                   # 📊 Database estratti
│   ├── alarms_faults.json
│   ├── mc_functions_list.json
│   └── ...
│
├── docs/                   # 📖 Documentazione
│   ├── QUICK_START.md
│   ├── WINDOWS_GUIDE.md
│   └── ...
│
├── config.py              # ⚙️ Configurazione percorsi
├── validate_setup.py      # ✅ Validazione setup
└── README.md              # 📄 Questo file
```

---

## 💡 Casi d'Uso Pratici

### 1. 📖 **Ricerca Rapida Documentazione**

**Problema:** Hai un manuale PDF di 1200 pagine. Cerchi un parametro specifico.

**Soluzione:**
```bash
python sinamics_kb_search.py --search "p0230"
```

**Output:** Tutte le sezioni che parlano di p0230, istantaneamente.

---

### 2. 🔧 **Supporto Tecnico / Help Desk**

**Scenario:** Operatore segnala allarme `A0681` sul drive.

**Soluzione:**
```python
# Script rapido
from sinamics_kb_search import search_kb
alarm_info = search_kb(category="alarm", code="A0681")
print(f"Descrizione: {alarm_info['description']}")
print(f"Soluzione: {alarm_info['solution']}")
```

**Beneficio:** Risposta immediata senza consultare manuali.

---

### 3. ⚙️ **Integrazione TIA Portal (PLC)**

**Utilizzo:** Interrogare il database direttamente dal PLC.

Usa i file SCL forniti:
```scl
(* Funzione SCL in TIA Portal *)
FUNCTION GetAlarmDescription : String
VAR_INPUT
    AlarmCode : String;
END_VAR

(* Legge da alarms_faults.json *)
Result := LookupAlarm(AlarmCode);
```

**Applicazioni:**
- Mostra descrizioni allarmi su HMI
- Log automatici dettagliati
- Panel operatore intelligente

---

### 4. 📊 **Analisi Documentazione**

**Esempio:** Audit qualità documentazione

```python
# Statistiche
params_count = len(search_index["parameter"])
faults_count = len(search_index["fault"])

print(f"Parametri documentati: {params_count}")
print(f"Fault catalogati: {faults_count}")
```

---

### 5. 🔄 **Migrazione Progetti**

**Scenario:** Upgrade da S7-300 a S7-1500

```python
# Confronta knowledge bases
old_kb = load_kb("s7_300")
new_kb = load_kb("s7_1500")

# Trova parametri deprecati
deprecated = compare_parameters(old_kb, new_kb)
```

---

### 6. 📝 **Generazione Report Automatici**

**Esempio:** Documentazione progetto

```python
# Parametri usati nel progetto
params = ["p0230", "p1234", "p5678"]

# Genera report con descrizioni
for param in params:
    info = search_kb(query=param)
    report.add(f"{param}: {info['description']}")
```

Output: PDF con documentazione completa parametri.

---

### 7. 🎓 **Training / Formazione**

Sistema quiz interattivo basato sulla KB:

```python
# Genera quiz casuale
questions = generate_quiz(category="parameter", count=10)
```

---

### 8. 🔍 **Troubleshooting Guidato**

Albero decisionale automatico:

```python
def diagnose(symptom):
    possible_faults = search_kb(query=symptom, category="fault")
    for fault in possible_faults:
        print(f"Causa: {fault['code']}")
        print(f"Soluzione: {fault['solution']}")
```

---

### 9. 📱 **Chatbot Tecnico Offline**

Bot basato su keyword (nessun LLM):

```python
def tech_bot(question):
    keywords = extract_keywords(question)
    results = search_kb(keywords=keywords)
    return format_answer(results[:3])
```

**Vantaggi:**
- Zero costi API
- Completamente offline
- Velocità immediata

---

### 10. 🔗 **API REST**

Esponi la KB via API:

```python
from flask import Flask, jsonify

@app.route('/api/alarm/<code>')
def get_alarm(code):
    return jsonify(search_kb(category="alarm", code=code))
```

**Applicazioni:**
- App mb tecnici
- Dashboard web
- Integrazione MES/ERP

---

## 🔬 Come Funziona il Sistema

### Fase 1: Estrazione PDF → JSON

**Script:** `extract_pdf_to_json.py`

1. Usa `pdftotext` per estrarre tutto il testo
2. Divide in "sezioni" basandosi su **righe vuote**
3. Salva ciascuna sezione in file JSON separati

**Input:** `manuale.pdf` (3.9 MB)  
**Output:** ~28,000 file `sezione_NNN.json`

### Fase 2: Build Knowledge Base

**Script:** `build_knowledge_base.py`

1. Carica tutte le sezioni JSON
2. **Indicizza per 7 categorie**:
   - `parameter` - Parametri configurazione
   - `fault` - Errori e fault
   - `alarm` - Allarmi ed eventi
   - `motor` - Motori e drive
   - `safety` - Sicurezza
   - `function` - Funzionalità
   - `appendix` - Appendici

3. Cerca **keywords** nel contenuto:
   ```python
   se sezione contiene "parameter p0230":
       aggiungi a search_index["parameter"]
   
   se sezione contiene "fault F3000":
       aggiungi a search_index["fault"]
   ```

4. Arricchisce con metadata:
   - Keywords auto-estratte
   - Capitolo di appartenenza
   - Link prev/next
   - Word count, lunghezza

**Output:**
```
knowledge_base/
├── index.json          # Capitoli e struttura
├── search_index.json   # Indice per categorie
├── metadata.json       # Info globali
└── sections/           # Sezioni arricchite
```

### Fase 3: Ricerca

```python
# Carica search index
index = load("knowledge_base/search_index.json")

# Cerca nella categoria fault
faults = index["fault"]

# Carica sezioni specifiche
for ref in faults:
    section = load(f"sections/{ref['section_id']}.json")
    print(section["content"])
```

**Vedi:** [`docs/SISTEMA_KB_SPIEGAZIONE.md`](./docs/SISTEMA_KB_SPIEGAZIONE.md) per dettagli completi.

---

## 🚀 Workflow Completo

### Scenario: Aggiungere un nuovo manuale PDF

```powershell
# 1. Copia PDF
copy nuovo_manuale.pdf resources\pdfs\sinamics\

# 2. Estrazione (Fase 1)
python scripts/extract_pdf_to_json.py --pdf "resources/pdfs/sinamics/nuovo_manuale.pdf" --output-dir "output/nuovo_manuale"

# 3. Costruzione KB (Fase 2)
python scripts/build_knowledge_base.py --input-dir "output/nuovo_manuale" --output-dir "kb/nuovo_manuale"

# 4. Cerca
python scripts/sinamics_kb_search.py --kb "kb/nuovo_manuale" --search "fault F3000"
```

---

## 🛠️ Script Disponibili

| Script | Funzione |
|--------|----------|
| `extract_pdf_to_json.py` | Estrae PDF in JSON |
| `build_knowledge_base.py` | Costruisce KB strutturata |
| `sinamics_kb_search.py` | Ricerca nella KB |
| `unified_kb_manager.py` | Gestisci KB multiple |
| `validate_setup.py` | Valida configurazione |
| `setup.py` | Setup automatico progetto |

### 📝 Dettagli Script extract_pdf_to_json.py

**Sintassi:**
```powershell
# Singolo file PDF
python extract_pdf_to_json.py --pdf <percorso_pdf> [--output-dir <directory>]

# Cartella intera di PDF
python extract_pdf_to_json.py --pdf-dir <percorso_cartella> [--output-dir <directory>]
```

**Parametri:**
- `--pdf` (mutually exclusive con --pdf-dir): Percorso di un singolo file PDF da elaborare
- `--pdf-dir` (mutually exclusive con --pdf): Cartella contenente più file PDF (elabora tutti i *.pdf)
- `--output-dir` (opzionale): Directory di output (default: `output`)

**Comportamento:**
- **Singolo PDF**: Output salvato direttamente nella `output-dir`
- **Multipli PDF**: Ogni PDF viene salvato in una sottocartella `output-dir/<nome_pdf>/`

**Esempi:**

```powershell
# 1. Singolo PDF - output in ./output
python extract_pdf_to_json.py --pdf "manuale.pdf"

# 2. Singolo PDF - directory output personalizzata
python extract_pdf_to_json.py --pdf "resources/pdfs/sinamics/s120.pdf" --output-dir "output/s120"

# 3. Batch processing - tutti i PDF da una cartella
python extract_pdf_to_json.py --pdf-dir "resources/pdfs/sinamics" --output-dir "output/sinamics_all"
# Risultato: output/sinamics_all/manual1/, output/sinamics_all/manual2/, etc.

# 4. Percorsi assoluti Windows
python extract_pdf_to_json.py --pdf "C:\Docs\manuale.pdf" --output-dir "C:\Output\kb"

# 5. Batch su percorso assoluto
python extract_pdf_to_json.py --pdf-dir "C:\Manuals\SINAMICS" --output-dir "C:\KB\extracted"
```

**Output esempio (batch mode):**
```
📁 Trovati 5 file PDF in resources/pdfs/sinamics

============================================================
📄 Elaborazione [1/5]: manual_s120.pdf
============================================================
...
✓ Estrazione completata!

============================================================
📄 Elaborazione [2/5]: manual_s150.pdf
============================================================
...

============================================================
🎯 RIEPILOGO FINALE
============================================================
PDF elaborati: 5/5
Sezioni totali estratte: 127,453
Output directory: output/sinamics_all
✅ Processo completato!
```

---

## 📖 Documentazione

- [`docs/QUICK_START.md`](./docs/QUICK_START.md) - Guida rapida 5 minuti
- [`docs/WINDOWS_GUIDE.md`](./docs/WINDOWS_GUIDE.md) - Guida Windows dettagliata
- [`docs/STRUCTURE.md`](./docs/STRUCTURE.md) - Struttura progetto
- [`docs/API.md`](./docs/API.md) - API per sviluppatori
- [`docs/SISTEMA_KB_SPIEGAZIONE.md`](./docs/SISTEMA_KB_SPIEGAZIONE.md) - Come funziona KB

---

## ✅ Validazione Setup

Verifica che tutto sia configurato correttamente:

```powershell
python validate_setup.py
```

**Output atteso:**
```
✓ Python version: 3.11.x
✓ pdftotext installed
✓ pandoc installed
✓ Project structure OK
✓ Registry files valid
✓ All paths cross-platform
✓ Setup complete!
```

---

## 🎯 Vantaggi

| Feature | DocKB_Siemens |
|---------|---------------|
| **Velocità** | ⚡ Ricerca istantanea |
| **Offline** | 🔒 Nessuna dipendenza internet |
| **Costi** | 💰 Zero (no API, no cloud) |
| **Privacy** | 🛡️ Dati restano locali |
| **Portabilità** | 📦 Funziona ovunque (Win/Linux/Mac) |
| **Leggerezza** | 🪶 No database, no dependencies pesanti |
| **Manutenibilità** | 🛠️ File testuali versionabili (Git) |

---

## 🆚 Confronto con Alternative

| Uso | DocKB_Siemens | RAG con LLM | PDF Manual |
|-----|---------------|-------------|------------|
| Lookup parametri | ✅ Perfetto | ❌ Overkill | ❌ Lento |
| Ricerca fault | ✅ Istantaneo | ❌ Costoso | ❌ Manuale |
| Domande complesse | ⚠️ Limitato | ✅ Ottimo | ❌ Impossibile |
| Offline/Embedded | ✅ Sì | ❌ Difficile | ✅ Sì |
| Costi | ✅ $0 | ❌ API costs | ✅ $0 |
| Setup complexity | ✅ Semplice | ❌ Complesso | ✅ Zero |

---

## 🔄 Roadmap Future

- [ ] Web interface ricerca
- [ ] Vector embeddings (semantic search)
- [ ] LLM integration opzionale
- [ ] REST API server
- [ ] Mobile app per tecnici
- [ ] Integration con TIA Portal Cloud

---

## 📞 Supporto

- **Issues:** Crea issue su GitHub
- **Documentation:** Vedi cartella `docs/`
- **Email:** [inserire contatto]

---

## 📄 Licenza

[MIT License](./LICENSE)

---

## 🙏 Acknowledgments

Basato su documentazione Siemens per prodotti:
- SINAMICS S120/S150
- S7-1500/S7-1500T Motion Control
- TIA Portal

---

**Versione:** 2.0  
**Data:** 2025-12-22  
**Autore:** [Your Name]
