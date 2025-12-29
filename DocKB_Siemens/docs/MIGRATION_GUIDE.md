# 🔄 Guida Migrazione - DocKB_Siemens

Come migrare a DocKB_Siemens dalla cartella originale KB_TO_Sinamics

---

## 📋 Checklist Migrazione

### ✅ Fase 1: Preparazione

- [ ] Backup cartella originale
- [ ] Installa dipendenze (poppler, pandoc)
- [ ] Sposta DocKB_Siemens in `c:\Projects\`
- [ ] Esegui `python validate_setup.py`

### ✅ Fase 2: Test Funzionalità

- [ ] Testa estrazione PDF: `python extract_pdf_to_json.py`
- [ ] Testa build KB: `python build_knowledge_base.py`
- [ ] Testa ricerca: `python sinamics_kb_search.py`
- [ ] Verifica file SCL TIA Portal

### ✅ Fase 3: Migrazione Dati (Opzionale)

- [ ] Copia Knowledge Base esistenti (se vuoi mantenerle)
- [ ] Aggiorna percorsi nei tuoi script custom
- [ ] Test workflow completo end-to-end

### ✅ Fase 4: Deploy

- [ ] Archivia cartella originale
- [ ] Aggiorna documentazione interna
- [ ] Comunica cambio al team

---

## 🔍 Differenze Principali

### Struttura Directory

**Prima (KB_TO_Sinamics):**
```
KB_TO_Sinamics/
├── documento.pdf            # PDF nella root
├── kb_axis/                 # KB S7-1500
├── scripts/                 # Script
├── kb_registry.json         # Registry con path hardcoded
└── ...
```

**Dopo (DocKB_Siemens):**
```
DocKB_Siemens/
├── resources/pdfs/          # PDF organizzati
│   ├── sinamics/
│   └── s7_1500/
├── kb/                      # KB organizzate
│   ├── sinamics/
│   ├── s7_1500/
│   └── unified/
├── scripts/                 # Script aggiornati
├── tia_portal/              # File SCL
├── data/                    # Database
├── docs/                    # Documentazione
├── config.py                # Config centralizzato
└── kb_registry.json         # Registry cross-platform
```

---

### Percorsi

**Prima:**
```python
# Hardcoded Linux paths
pdf_path = "/home/user/KB_TO_Sinamics/documento.pdf"
```

**Dopo:**
```python
# Cross-platform con config.py
from config import PDF_DIR
pdf_path = PDF_DIR / "sinamics" / "manual.pdf"
```

---

### Registry

**Prima (kb_registry.json):**
```json
{
  "knowledge_bases": [{
    "pdf_file": "/home/siemensadmin/resources/pdfs/sinamics_s120_communication.pdf"
  }]
}
```

**Dopo:**
```json
{
  "knowledge_bases": [{
    "pdf_file": "resources/pdfs/sinamics/communication.pdf"
  }]
}
```

---

## 🚀 Setup Step-by-Step

### 1. Sposta Cartella

```powershell
# Dal desktop alla posizione finale
cd "c:\Users\PM\Desktop\KB TO\KB_TO_Sinamics-claude-push-files-repo-oQZaz\KB_TO_Sinamics-claude-push-files-repo-oQZaz"
move DocKB_Siemens c:\Projects\
cd c:\Projects\DocKB_Siemens
```

### 2. Verifica Setup

```powershell
python validate_setup.py
```

**Output atteso:**
```
[OK] Python 3.x
[OK] pdftotext installed
[OK] pandoc installed
[OK] Directory structure
[OK] Registry valid
```

### 3. Test Workflow

```powershell
# Test estrazione (su un PDF già copiato)
cd scripts
python extract_pdf_to_json.py --pdf ../resources/pdfs/s7_1500/s71500_s71500t_axis_function_manual_it-IT_it-IT.pdf --output-dir ../output/test

# Test build
python build_knowledge_base.py --input ../output/test --kb-dir ../kb/test

# Test ricerca
python sinamics_kb_search.py --kb ../kb/test --search "fault"
```

---

## 📦 Migrazione Knowledge Base Esistenti (Opzionale)

Se hai già KB generate nella cartella originale e vuoi mantenerle:

### Copia Manuale

```powershell
# Copia KB SINAMICS esistenti
xcopy "c:\Users\PM\Desktop\KB TO\KB_TO_Sinamics-claude-push-files-repo-oQZaz\KB_TO_Sinamics-claude-push-files-repo-oQZaz\kb_axis" "c:\Projects\DocKB_Siemens\kb\s7_1500" /E /I

# Verifica
dir c:\Projects\DocKB_Siemens\kb\s7_1500
```

### Aggiorna Registry

Dopo aver copiato le KB, aggiorna il registry:

```powershell
cd c:\Projects\DocKB_Siemens
python setup.py  # Rigenera registry automaticamente
```

---

## 🔧 Aggiorna Script Custom

Se hai script custom che usano la vecchia struttura:

### Prima:
```python
import sys
sys.path.append('/path/to/KB_TO_Sinamics')
from scripts.sinamics_kb_search import search_kb

results = search_kb(kb_dir="/home/user/kb_axis/axis_function_it")
```

### Dopo:
```python
import sys
sys.path.append('c:/Projects/DocKB_Siemens')
from config import KB_DIR
from scripts.sinamics_kb_search import search_kb

results = search_kb(kb_dir=KB_DIR / "s7_1500" / "axis_function_it")
```

---

## 📊 Verifica Migrazione

### Checklist Validazione

```powershell
# 1. Struttura directory
python -c "from config import PROJECT_ROOT, PDF_DIR, KB_DIR; print(f'ROOT: {PROJECT_ROOT}'); print(f'PDFs: {PDF_DIR}'); print(f'KB: {KB_DIR}')"

# 2. Registry
python -c "import json; from config import KB_REGISTRY; print(json.dumps(json.load(open(KB_REGISTRY)), indent=2))"

# 3. Script
dir scripts\*.py | measure

# 4. Dati
dir data\*.json | measure
```

**Output atteso:**
```
ROOT: c:\Projects\DocKB_Siemens
PDFs: c:\Projects\DocKB_Siemens\resources\pdfs
KB: c:\Projects\DocKB_Siemens\kb

Registry: 8 KB registered
Scripts: 14
Data files: 4
```

---

## 🎯 Best Practices Post-Migrazione

### 1. Documentazione

```powershell
# Leggi documentazione aggiornata
notepad docs\QUICK_START.md
notepad docs\WINDOWS_GUIDE.md
notepad README.md
```

### 2. Backup

```powershell
# Crea backup ZIP
Compress-Archive -Path c:\Projects\DocKB_Siemens -DestinationPath c:\Backup\DocKB_Siemens_$(Get-Date -Format 'yyyyMMdd').zip
```

### 3. Git (Opzionale)

```powershell
cd c:\Projects\DocKB_Siemens
git init
git add .
git commit -m "Initial commit - DocKB_Siemens v2.0"
```

---

## ⚠️ Troubleshooting Migrazione

### "Module not found"

```powershell
# Verifica Python path
python -c "import sys; print(sys.path)"

# Aggiungi manualmente
$env:PYTHONPATH = "c:\Projects\DocKB_Siemens"
```

### "Registry file not found"

```powershell
# Rigenera registry
cd c:\Projects\DocKB_Siemens
python setup.py
```

### "PDFs not found"

```powershell
# Verifica PDF copiati
dir resources\pdfs\sinamics
dir resources\pdfs\s7_1500

# Se mancano, ricopia
python setup.py
```

---

## 📋 Rollback Plan

Se qualcosa va storto:

```powershell
# 1. Torna alla cartella originale
cd "c:\Users\PM\Desktop\KB TO\KB_TO_Sinamics-claude-push-files-repo-oQZaz\KB_TO_Sinamics-claude-push-files-repo-oQZaz"

# 2. Usa i vecchi script
cd scripts
python sinamics_kb_search.py ...

# 3. DocKB_Siemens resta disponibile per debugging
dir c:\Projects\DocKB_Siemens
```

**Nota:** La cartella originale NON è stata modificata durante la migrazione!

---

## ✅ Migrazione Completata!

Quando tutto funziona:

1. ✅ Archivia cartella originale
2. ✅ Aggiorna documentazione team
3. ✅ Aggiorna link/shortcut
4. ✅ Comunica cambio percorsi agli utenti

---

**Versione:** 2.0  
**Aggiornato:** 2025-12-22  
**Supporto:** Vedi README.md per contatti
