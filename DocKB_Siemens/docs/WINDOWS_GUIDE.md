# 🪟 Windows Guide - DocKB_Siemens

Guida completa per utenti Windows

---

## 📦 Installazione Dipendenze (Windows)

### Metodo 1: Chocolatey (Raccomandato)

**Installa Chocolatey** (se non già installato):
```powershell
# PowerShell come Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

**Installa poppler e pandoc:**
```powershell
choco install poppler -y
choco install pandoc -y
```

**Verifica installazione:**
```powershell
pdftotext -v
pandoc --version
```

---

### Metodo 2: Scoop

```powershell
# Installa scoop
iwr -useb get.scoop.sh | iex

# Installa tool
scoop install poppler
scoop install pandoc
```

---

### Metodo 3: MSYS2

```powershell
# Installa MSYS2 da https://www.msys2.org/
# Poi nel terminale MSYS2:
pacman -S mingw-w64-x86_64-poppler
pacman -S pandoc
```

---

## 🔧 Setup Progetto (Windows)

### 1. Posiziona DocKB_Siemens

```powershell
# Opzione A: Sposta in c:\Projects
cd "c:\Users\PM\Desktop\KB TO\KB_TO_Sinamics-claude-push-files-repo-oQZaz\KB_TO_Sinamics-claude-push-files-repo-oQZaz"
move DocKB_Siemens c:\Projects\

# Opzione B: Lascia dov'è
cd DocKB_Siemens
```

### 2. Esegui Setup

```powershell
python setup.py
```

### 3. Valida

```powershell
python validate_setup.py
```

---

## 💻 Comandi Windows-Specific

### Navigazione Directory

```powershell
# Cambia directory
cd c:\Projects\DocKB_Siemens

# Lista file
dir

# Lista ricorsiva
dir /s

# Trova file
dir /s *.pdf
```

### Path Windows

In PowerShell, usa `\` o `/`:
```powershell
# Entrambi funzionano
cd scripts
python extract_pdf_to_json.py --pdf ..\resources\pdfs\sinamics\manual.pdf

# Oppure
python extract_pdf_to_json.py --pdf ../resources/pdfs/sinamics/manual.pdf
```

---

## 🐍 Python su Windows

### Verifica Python

```powershell
python --version
# Output: Python 3.x.x

# Se "python" non funziona, prova:
python3 --version
py --version
```

### Encoding

Se vedi errori con caratteri Unicode:
```powershell
# Imposta encoding UTF-8 globale
$env:PYTHONIOENCODING = "utf-8"

# Permanente (aggiungi a profilo PowerShell)
notepad $PROFILE
# Aggiungi: $env:PYTHONIOENCODING = "utf-8"
```

---

## 📂 Gestione File

### Copia File

```powershell
# Copia PDF
copy manuale.pdf c:\Projects\DocKB_Siemens\resources\pdfs\sinamics\

# Copia ricorsiva
xcopy /E /I sorgente destinazione
```

### Elimina File

```powershell
# Elimina file
del file.txt

# Elimina cartella
rmdir /s /q cartella
```

---

## ⚡ PowerShell Tips

### Alias Utili

```powershell
# Crea alias per comandi lunghi
Set-Alias extract "python scripts\extract_pdf_to_json.py"
Set-Alias build "python scripts\build_knowledge_base.py"
Set-Alias search "python scripts\sinamics_kb_search.py"

# Usa alias
extract --pdf resources\pdfs\sinamics\manual.pdf
```

### Script Batch

Crea `estrai_pdf.bat`:
```batch
@echo off
cd c:\Projects\DocKB_Siemens\scripts
python extract_pdf_to_json.py --pdf %1 --output-dir ../output
```

Usa:
```powershell
.\estrai_pdf.bat manual.pdf
```

---

## 🔍 Troubleshooting Windows

### "python not found"

```powershell
# Controlla se Python è nel PATH
$env:PATH

# Aggiungi Python al PATH
$env:PATH += ";C:\Python313"

# Permanente: System Properties > Environment Variables
```

### "pdftotext not found" (dopo install)

```powershell
# Riavvia PowerShell dopo installazione
# Oppure aggiungi manualmente al PATH:
$env:PATH += ";C:\ProgramData\chocolatey\bin"
```

### Permessi Denied

```powershell
# Esegui PowerShell come Administrator
# Oppure:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
```

### Caratteri strani nell'output

```powershell
# Imposta codepage UTF-8
chcp 65001

# Aggiungi al profilo:
notepad $PROFILE
# Aggiungi: chcp 65001
```

---

## 📊 Performance Windows

### SSD vs HDD

Knowledge Base con 28,000 file funziona meglio su SSD:
- **SSD**: ~5 secondi caricamento
- **HDD**: ~30 secondi caricamento

### Antivirus

Windows Defender può rallentare l'accesso a migliaia di file:
```powershell
# Escludi cartella DocKB_Siemens da Windows Defender
Add-MpPreference -ExclusionPath "c:\Projects\DocKB_Siemens"
```

---

## 🔐 Sicurezza

### Firewall

Se usi API REST server:
```powershell
# Apri porta (Administrator)
New-NetFirewallRule -DisplayName "DocKB API" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

---

## 🎯 Workflow Completo (Windows)

```powershell
# 1. Setup iniziale
cd c:\Projects\DocKB_Siemens
python validate_setup.py

# 2. Aggiungi PDF
copy "c:\Users\USER\Downloads\manuale.pdf" resources\pdfs\sinamics\

# 3. Estrai
cd scripts
python extract_pdf_to_json.py --pdf ..\resources\pdfs\sinamics\manuale.pdf

# 4. Build KB
python build_knowledge_base.py

# 5. Cerca
python sinamics_kb_search.py --search "fault F3000"
```

---

## 📱 Integration Windows

### Task Scheduler

Automatizza estrazione PDF settimanale:
```powershell
# Crea task
$action = New-ScheduledTaskAction -Execute "python" -Argument "c:\Projects\DocKB_Siemens\scripts\extract_pdf_to_json.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DocKB Extract"
```

### Windows Explorer Integration

Aggiungi "Extract PDF" al menu contestuale (Registry):
```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\.pdf\shell\ExtractKB]
@="Extract to Knowledge Base"

[HKEY_CLASSES_ROOT\.pdf\shell\ExtractKB\command]
@="python c:\\Projects\\DocKB_Siemens\\scripts\\extract_pdf_to_json.py --pdf \"%1\""
```

---

## 🆘 Supporto

**Forum:** [Link forum]  
**Email:** [support email]  
**Issues:** GitHub Issues

---

**Versione:** 2.0  
**Aggiornato:** 2025-12-22
