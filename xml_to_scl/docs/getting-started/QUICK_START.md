# Quick Start - Batch Converter

## 60 Secondi per Iniziare

### Step 1: Posizionati nella Cartella Script

```powershell
cd C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\xml_to_scl
```

### Step 2: Lancia il Batch Converter

```powershell
# Opzione A: Output automatico (PLC_410D1_Parsed)
python batch_convert_project.py "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1"

# Opzione B: Specifica cartella output
python batch_convert_project.py "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1" --output "C:\Risultati\PLC_410D1_Parsed"
```

### Step 3: Attendi il Completamento

Vedrai output in tempo reale con progresso, ETA e statistiche running.

### Step 4: Esamina Risultati

**Apri il report:**
```powershell
# Windows
Invoke-Item "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1_Parsed\batch_conversion_report.csv"

# Oppure manualmente in Excel
```

---

## Test Veloce su Sottocartella (5 minuti)

```powershell
python batch_convert_project.py "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety" --output "C:\Test_Output"
```

---

## Output Atteso

### Console
```
===============================================================================
TIA Portal XML to SCL Batch Converter
===============================================================================
Source:      C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1
Destination: C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1_Parsed

Found 970 XML files in 432 directories

Created 432 directories

Starting batch conversion...

[1/970] Software units/1_Orchestrator_Safety/.../Motor.xml
   Type: FB | Size: 12.1 KB | Status: OK SUCCESS (0.85s)

Progress: ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0.1% (1/970)
Success: 1 | Failed: 0 | Validation Errors: 0 | Skipped: 0
Rate: 100.0% | ETA: 16m 02s
...

===============================================================================
BATCH CONVERSION COMPLETE
===============================================================================
Total Files: 970
Processed: 968
Successful: 850 (87.8%)
Failed: 95 (9.8%)
Validation Errors: 23 (2.4%)
Skipped: 2 (0.2%)

Total Time: 15m 32s
Average Time: 0.96s per file
===============================================================================

Report saved to: C:\...\PLC_410D1_Parsed\batch_conversion_report.csv
```

### Cartelle Create

```
PLC_410D1_Parsed/
├── Software units/
│   ├── 1_Orchestrator_Safety/
│   │   ├── PLC data types/
│   │   │   ├── Motor.udt
│   │   │   └── Config.udt
│   │   ├── Program blocks/
│   │   │   ├── Motor_FB.scl
│   │   │   └── Valve_FC.xml.error (fallito)
│   ├── 31_Area01/
│   └── ...
├── Program blocks/
├── PLC tags/
└── batch_conversion_report.csv  ← APRI QUESTO IN EXCEL
```

### Report CSV (in Excel)

| Sezione | Contenuto |
|---------|----------|
| Summary | Statistiche generali (total, successi, fallimenti, rate) |
| File Type Distribution | Conteggi per tipo (FB, FC, DB, UDT, Tags) |
| Performance Metrics | Tempi (total, avg, min, max, file più lento) |
| File Size Analysis | Dimensioni (input, output, cambio %) |
| Directory Breakdown | Statistiche per directory |
| Detailed Results | Elenco di tutti i 970 file con status |

---

## File di Errore (.error)

Se un file fallisce, troverai un file `.error` nella stessa posizione con contenuto tipo:

```
ERROR REPORT
============
File: Valve.xml
Source Path: C:\...\Valve.xml
Timestamp: 2025-12-26 14:15:25
Status: VALIDATION_ERROR

Error Type: PLACEHOLDER_ERROR
Error Message: Contains 5 '???' placeholder(s)

Placeholder Locations (5 found):
Line 45: Ctrl.Enable := ???;
Line 67: IF ??? THEN
Line 89: Motor.Speed := ???;

Additional Information:
-----------------------
File Type: fc
Input Size: 8,765 bytes
Processing Time: 1.23 seconds
Output File: C:\...\PLC_410D1_Parsed\Software units\.../Valve.scl
```

---

## Interpretare Status

| Status | Significato | Azione |
|--------|------------|--------|
| `OK SUCCESS` | ✅ Convertito correttamente | Nessuna |
| `XX FAILED` | ❌ Conversione fallita | Revedi file `.error` |
| `!! VALIDATION_ERROR` | ⚠️ Ha placeholder `???` | Rivedi file output |
| `-- SKIPPED` | ⊘ Non XML/non supportato | Nessuna |

---

## Comandi Utili

```powershell
# Visualizza cartella output
explorer "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1_Parsed"

# Apri report in Excel
start "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1_Parsed\batch_conversion_report.csv"

# Conta file convertiti
(Get-ChildItem -Recurse -Filter "*.scl" | Measure-Object).Count

# Conta errori
(Get-ChildItem -Recurse -Filter "*.error" | Measure-Object).Count

# Vedi file più grandi
Get-ChildItem -Recurse -Filter "*.scl" | Sort-Object Length -Descending | Select-Object -First 5 FullName, @{Name="Size";Expression={"{0:N0} KB" -f ($_.Length/1KB)}}
```

---

## Prossimi Passi

1. **Revisione Report**: Aprilo in Excel e analizza statistiche
2. **Errori da Risolvere**: Controlla file `.error` per fallimenti
3. **Campionamento**: Apri alcuni file `.scl` per verificare qualità
4. **Iterazione**: Se necessario, correggi problemi e ri-esegui

---

## Troubleshooting Veloce

### Errore "Module not found"
```powershell
# Soluzioni: Assicurati di eseguire da cartella xml_to_scl
cd C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\xml_to_scl
python batch_convert_project.py "C:\..."
```

### Nessun file trovato
```
# Verifica che il percorso contenga file .xml
Get-ChildItem "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1" -Recurse -Filter "*.xml" | Measure-Object
```

### Report non si apre in Excel
```powershell
# Il file CSV usa UTF-8. Apertura manuale:
# 1. Apri Excel
# 2. File → Apri
# 3. Seleziona batch_conversion_report.csv
# 4. Scegli UTF-8 come encoding
```

---

## Tempo Stimato

- **Discovery + Setup**: 7 secondi
- **Processing 970 file @ 0.96s/file**: ~15-16 minuti
- **Report Generation**: 3 secondi
- **TOTALE**: ~16-17 minuti

---

**Pronto a iniziare? Esegui il comando Step 2 sopra!**
