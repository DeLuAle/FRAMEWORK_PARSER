# Batch Conversion Script - Guida Completa

## Panoramica

Lo script `batch_convert_project.py` processa **interi progetti TIA Portal**, mantenendo la struttura delle cartelle, e genera un report completo degli errori.

**Caratteristiche principali:**
- ✅ Ricrea struttura cartelle identica al progetto originale
- ✅ Processa tutti i tipi di file (FB, FC, DB, UDT, Tags)
- ✅ Valida output per placeholder `???`
- ✅ Crea file `.error` per conversioni fallite
- ✅ Genera report CSV Excel-friendly con statistiche complete
- ✅ Mostra progresso in tempo reale con ETA
- ✅ Compatibile con Windows PowerShell

---

## Utilizzo di Base

### Sintassi

```powershell
python batch_convert_project.py <sorgente> [--output <destinazione>]
```

### Esempi

#### Esempio 1: Conversione con nome automatico

```powershell
cd c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\xml_to_scl

# Output: PLC_410D1_Parsed nella stessa cartella madre
python batch_convert_project.py "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1"
```

#### Esempio 2: Specifichiare cartella output

```powershell
python batch_convert_project.py "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1" --output "C:\Conversioni\PLC_410D1_Parsed"
```

#### Esempio 3: Test su sottocartella

```powershell
# Test su una singola software unit
python batch_convert_project.py "C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\Software units\1_Orchestrator_Safety" --output "C:\Test_Output"
```

---

## Output

### Struttura Cartelle

```
PLC_410D1_Parsed/
├── Software units/
│   ├── 1_Orchestrator_Safety/
│   │   ├── PLC data types/
│   │   │   ├── Motor.udt
│   │   │   └── Config.udt
│   │   ├── PLC tags/
│   │   │   └── SafetyTags.csv
│   │   └── Program blocks/
│   │       ├── Motor_FB.xml.error  (fallito)
│   │       ├── Valve_FC.scl
│   │       └── Init_FB.scl
│   ├── 31_Area01/
│   │   ├── ... (struttura identica)
│   └── ...
├── Program blocks/
│   ├── ...
├── PLC tags/
│   └── ...
└── batch_conversion_report.csv  (REPORT COMPLETO)
```

### File Generati

#### File Convertiti (per tipo)
- **FB/FC** → `.scl` (Structured Control Language)
- **DB** → `.db` (Database definition)
- **UDT** → `.udt` (User Defined Type)
- **Tags** → `.csv` (PLC tag table)

#### File di Errore
- **Nome**: `{original_name}.xml.error`
- **Ubicazione**: Stessa cartella del file originale
- **Contenuto**: Dettagli errore, traceback, timestamp

**Esempio di file .error:**
```
ERROR REPORT
============
File: Motor.xml
Source Path: c:\Projects\...\Motor.xml
Timestamp: 2025-12-26 14:30:15
Status: FAILED

Error Type: PARSE_ERROR
Error Message: XML parse error at line 47

Exception Details:
------------------
[Traceback completo]

Additional Information:
-----------------------
File Type: fb
Input Size: 12,456 bytes
Processing Time: 0.85 seconds
```

#### Report CSV
- **Nome**: `batch_conversion_report.csv`
- **Ubicazione**: Cartella radice output
- **Formato**: Multi-sezione, Excel-friendly (UTF-8 con BOM)

---

## Report CSV - Sezioni

### 1. Summary (Riepilogo Generale)
```
Total Files Discovered: 970
Files Processed: 968
Successful Conversions: 850
Failed Conversions: 95
Validation Errors (??? found): 23
Overall Success Rate: 87.8%
```

### 2. File Type Distribution (Distribuzione per Tipo)
```
File Type  | Total | Success | Failed | Validation Errors | Success Rate
FB         | 156   | 145     | 8      | 3                 | 93.0%
FC         | 89    | 82      | 5      | 2                 | 92.1%
DB         | 245   | 238     | 4      | 3                 | 97.1%
UDT        | 387   | 385     | 2      | 0                 | 99.5%
TAGS       | 93    | 0       | 76     | 17                | 0.0%
```

### 3. Performance Metrics (Metriche di Performance)
```
Total Processing Time: 15m 32s
Average Time: 0.96s per file
Median Time: 0.72s
Min Time: 0.05s
Max Time: 12.34s
Slowest File: [percorso file]
```

### 4. File Size Analysis (Analisi Dimensioni)
```
Total Input Size: 125.3 MB
Total Output Size: 87.2 MB
Size Change: -30.4%
Average Input: 132.1 KB
Average Output: 92.5 KB
```

### 5. Directory Breakdown (Breakdown per Directory)
```
Directory                        | Total | Success | Failed | Success Rate
Software units/1_Orchestrator... | 150   | 145     | 3      | 96.7%
Software units/31_Area01         | 220   | 210     | 8      | 95.5%
...
```

### 6. Detailed File Results (Risultati Dettagliati per File)
```
File Path | Relative Path | File Type | Status | Time (s) | Input Size | Output Size | Error Type | Error Message | ...
```

---

## Output Console

Durante l'esecuzione vedrai un output come questo:

```
===============================================================================
TIA Portal XML to SCL Batch Converter
===============================================================================
Source:      C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1
Destination: C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1_Parsed

Discovering XML files...
Found 970 XML files
Organized in 432 directories (max depth: 9 levels)

Creating mirrored directory structure...
Created 432 directories

Starting batch conversion...

[123/970] Software units/1_Orchestrator_Safety/.../Motor.xml
   Type: FB | Size: 12.1 KB | Status: OK SUCCESS (0.85s)

[124/970] Software units/1_Orchestrator_Safety/.../Valve.xml
   Type: FC | Size: 8.6 KB | Status: !! VALIDATION_ERROR (1.23s)
   Warning: Contains 5 '???' placeholder(s)

[125/970] Software units/31_Area01/.../Config.xml
   Type: DB | Size: 5.5 KB | Status: XX FAILED (0.12s)
   Error: XML parse error

Progress: ████████████░░░░░░░░ 12.8% (124/970)
Success: 110 | Failed: 11 | Validation Errors: 3 | Skipped: 0
Rate: 88.7% | ETA: 11m 45s

...

===============================================================================
BATCH CONVERSION COMPLETE
===============================================================================
Total Files:      970
Processed:        968
Successful:       850 (87.8%)
Failed:           95 (9.8%)
Validation Errors: 23 (2.4%)
Skipped:          2 (0.2%)

Total Time:       15m 32s
Average Time:     0.96s per file
===============================================================================

Report saved to: C:\...\PLC_410D1_Parsed\batch_conversion_report.csv
Error files (.error) created in mirrored structure for failed/partial conversions
```

### Simboli di Stato

| Simbolo | Significato |
|---------|------------|
| `OK` | Conversione riuscita |
| `XX` | Conversione fallita |
| `!!` | Errore di validazione (contiene `???`) |
| `--` | File saltato (non XML) |

---

## Validazione e Criteri di Successo

### SUCCESS ✅
File convertito correttamente:
- Identificato tipo file
- Processato senza eccezioni
- Output file creato
- **NESSUN** placeholder `???` nel file

### VALIDATION_ERROR ⚠️
File convertito ma con problemi:
- Output creato
- Contiene uno o più placeholder `???`
- Ancora aperto per miglioramenti
- File `.error` creato con dettagli

### FAILED ❌
Conversione completamente fallita:
- Errore di parsing
- Output non creato
- File `.error` creato con traceback completo

### SKIPPED ⊘
File non elaborato:
- Non è un file XML
- Tipo non riconosciuto

---

## Statistic Raccolte

### Per Tipo di File
- Conteggio totale per tipo
- Successi/Fallimenti/Errori di validazione
- Tasso di successo per tipo

### Performance
- Tempo totale di elaborazione
- Tempo medio per file
- File più lento
- Tempo minimo/massimo/mediano

### Dimensioni
- Dimensione totale input XML
- Dimensione totale output SCL
- Cambio di dimensione (compressione/espansione)
- Media input/output

### Per Directory
- File totali per directory
- Successos/Fallimenti/Errori di validazione per directory
- Tasso di successo per directory

---

## Tempo di Esecuzione Stimato

Per il progetto PLC_410D1 completo (~970 file):

| Fase | Tempo |
|------|-------|
| Discovery | ~5 secondi |
| Creazione struttura | ~2 secondi |
| Processamento 970 file @ 0.96s/file | ~15-16 minuti |
| Generazione report | ~3 secondi |
| **TOTALE** | **~16-17 minuti** |

---

## Troubleshooting

### Il script non si avvia

**Problema**: `ModuleNotFoundError: No module named 'main'`

**Soluzione**:
```powershell
# Assicurati di essere nella cartella xml_to_scl
cd c:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\xml_to_scl

# Avvia da lì
python batch_convert_project.py "C:\...\PLC_410D1"
```

### Errori di encoding (Windows)

**Problema**: `UnicodeEncodeError` nella console

**Soluzione**: Le uscite usano automaticamente encoding UTF-8 di Windows. Se il problema persiste:

```powershell
# Imposta encoding console su UTF-8
chcp 65001
```

### Cartella output già esiste

**Comportamento**: Lo script crea i file nella struttura esistente
- Se cartella output esiste, aggiunge/sovrascrive i file
- Cartelle non vengono eliminate, solo ricreate se necessarie
- File precedenti vengono sovrascritti

### Nessun file XML trovato

**Problema**: "Found 0 XML files"

**Soluzione**:
- Verifica che il percorso sia corretto
- Verifica che contiene file `.xml`
- Prova con un percorso assoluto instead di relativo

### Report CSV non leggibile in Excel

**Soluzione**:
- Il file usa UTF-8 con BOM (dovrebbe auto-detect in Excel)
- Se non funziona: Apri Excel → File → Apri → Seleziona file CSV
- Excel ti chiederà l'encoding, seleziona "UTF-8"

---

## Advanced Usage

### Test su Sottocartella

```powershell
# Test veloce su singola area
python batch_convert_project.py "C:\...\PLC_410D1\Software units\31_Area01" --output "C:\Test_Area01"

# Verifica risultati prima di eseguire su progetto completo
```

### Usando dalla riga di comando di sistema

```powershell
# Potrai lanciare da qualsiasi cartella se aggiungi il path
$env:Path += ";C:\Projects\MODULBLOCK_MBK2\MBK_2\PLC_410D1\xml_to_scl"

python batch_convert_project.py "C:\Progetti\TIA" --output "C:\Risultati"
```

---

## Interpretare i Risultati

### Successo Totale (100%)
```
Successful: 850 (87.8%)
Failed: 0
Validation Errors: 0
```
→ Perfetto! Tutti i file convertiti con successo.

### Errori di Validazione Alti

Se vedi molti errori di validazione:
```
Validation Errors: 150 (15.5%)
```

**Possibili cause**:
- Logica LAD non completamente ricostruita
- Blocchi con logica complessa non supportata
- Funzioni non mappate nei parser

**Soluzione**: Rivedi i file `.error` e `batch_conversion_report.csv` per identificare pattern di errori.

### Tipo di File con 0% di Successo

Se tutti i file di un tipo falliscono:
```
TAGS: 93 | Success: 0 | Failed: 93 | Success Rate: 0.0%
```

**Possibili cause**:
- Parser non implementato per quel tipo
- Formato XML differente da quello atteso
- Problemi di compatibilità

---

## Prossimi Passi dopo la Conversione

1. **Revisione Report**: Apri `batch_conversion_report.csv` in Excel
2. **Analizza Errori**: Controlla file `.error` per capire fallimenti
3. **Quality Check**: Campiona file `.scl` generati per validare qualità
4. **Correzioni**: Se necessario, correggi e ri-esegui il batch

---

## Compatibilità

- ✅ Windows 10/11
- ✅ Python 3.8+
- ✅ PowerShell (tutti gli script)
- ✅ Command Prompt
- ✅ Path con spazi
- ✅ Nomi file Unicode

---

## Performance Tips

1. **Primo run**: Usa cartella piccola per test
2. **SSD**: Esecuzione più veloce su SSD
3. **Background**: Esegui in sessione PowerShell separata se slow
4. **Monitoraggio**: Controlla `batch_conversion_report.csv` per identificare file lenti

---

## Domande Frequenti

### D: Quanto tempo impiega il batch completo?

**R**: ~16-17 minuti per 970 file (0.96s medio per file)

### D: Posso stoppare e riprendere?

**R**: No, ma puoi eseguire di nuovo. Lo script sovrascrive i file esistenti.

### D: Che formato è il report?

**R**: CSV (comma-separated values), direttamente importabile in Excel

### D: Cosa significa il file `.error`?

**R**: Indica che quel file non è stato convertito (o convertito con errori). Apri il file per dettagli.

### D: Posso processare solo certi tipi di file?

**R**: No, il batch processa tutti i `.xml` trovati. Puoi filtrare manualmente i risultati da report.

### D: Che succede se manca dependenza?

**R**: Lo script usa solo `main.py`, `utils.py` e librerie standard Python.

---

## Support

Per problemi:

1. Controlla `batch_conversion_report.csv` per statistiche dettagliate
2. Rivedi file `.error` per specifiche conversioni fallite
3. Verifica che i file XML siano validi (TIA Portal exports corretti)

---

**Versione**: 1.0
**Data**: December 26, 2025
**Compatibilità**: Windows 10/11, Python 3.8+
