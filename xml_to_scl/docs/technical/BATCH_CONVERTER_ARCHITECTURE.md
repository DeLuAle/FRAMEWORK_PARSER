# Architettura del Batch Converter

Documentazione tecnica per sviluppatori e maintainers.

---

## Panoramica

```
batch_convert_project.py (950 righe)
├── Data Structures (linee 28-116)
│   ├── FileResult
│   ├── DirStats
│   └── BatchSummary
│
├── Helpers (linee 119-200)
│   ├── format_size()
│   ├── format_duration()
│   ├── calculate_eta()
│   ├── extract_placeholder_lines()
│   └── find_output_file()
│
├── FileProcessor (linee 203-275)
│   ├── process_with_tracking()
│   └── validate_output()
│
├── StatisticsCollector (linee 278-350)
│   ├── record_file()
│   └── get_summary()
│
├── Error File Creator (linee 353-395)
│   └── create_error_file()
│
├── CSVReportGenerator (linee 398-550)
│   └── generate()
│
├── ProgressDisplay (linee 553-620)
│   └── update()
│
└── Main Flow (linee 623-750)
    ├── print_header()
    ├── print_final_summary()
    └── main()
```

---

## Data Structures

### FileResult (linee 28-67)

```python
@dataclass
class FileResult:
    source_path: Path          # Path assoluto file XML
    relative_path: Path        # Path relativo da source_root
    file_type: Optional[str]   # 'fb', 'fc', 'db', 'udt', 'tags', None
    status: str                # SUCCESS, FAILED, VALIDATION_ERROR, SKIPPED, IO_ERROR

    start_time: datetime       # Timestamp inizio elaborazione
    processing_time: float     # Tempo in secondi

    input_size: int            # Bytes file XML
    output_size: Optional[int] # Bytes file generato (None se fallito)

    output_path: Optional[Path] # Path file output generato

    error_type: Optional[str]  # PARSE_ERROR, VALIDATION_ERROR, IO_ERROR, etc.
    error_message: Optional[str]
    exception_trace: Optional[str]

    has_placeholders: bool     # True se contiene '???'
    placeholder_count: int
    placeholder_lines: List[Tuple[int, str]]  # [(line_num, line_text), ...]
```

**Uso**: Ogni file elaborato produce un `FileResult` con tutti i metadati

---

### DirStats (linee 70-82)

```python
@dataclass
class DirStats:
    path: Path
    total_files: int = 0
    success_count: int = 0
    failed_count: int = 0
    validation_error_count: int = 0
    skipped_count: int = 0

    @property
    def success_rate(self) -> float:
        # Calcola percentuale (escludendo skipped)
```

**Uso**: Raccoglie statistiche per singola directory

---

### BatchSummary (linee 85-145)

```python
@dataclass
class BatchSummary:
    total_files: int
    files_processed: int
    files_succeeded: int
    files_failed: int
    files_validation_errors: int
    files_skipped: int

    file_type_counts: Dict[str, int]        # {'fb': 50, 'fc': 30, ...}
    success_by_type: Dict[str, int]
    failed_by_type: Dict[str, int]
    validation_errors_by_type: Dict[str, int]

    total_time: float
    total_input_size: int
    total_output_size: int

    processing_times: List[float]           # Tutti i tempi
    directory_stats: Dict[Path, DirStats]   # Stats per ogni dir

    @property
    def success_rate(self) -> float: ...
    @property
    def average_time(self) -> float: ...
    @property
    def min_time(self) -> float: ...
    @property
    def max_time(self) -> float: ...
    @property
    def median_time(self) -> float: ...
```

**Uso**: Aggressione dei dati di batch per report finale

---

## Key Functions

### format_size() - linee 153-162

Converte byte a formato leggibile:
- Input: `12456`
- Output: `"12.2 KB"`

**Unità**: B, KB, MB, GB, TB

---

### format_duration() - linee 165-175

Converte secondi a formato durata:
- Input: `932.5`
- Output: `"15m 32s"`

**Formati**:
- < 60s: `"45.3s"`
- < 60m: `"5m 32s"`
- ≥ 60m: `"1h 5m"`

---

### calculate_eta() - linee 178-188

Calcola tempo rimanente stimato:

```python
eta_seconds = (total - current) / (current / elapsed)
```

**Ritorna**: Stringa formattata tramite `format_duration()`

---

### extract_placeholder_lines() - linee 191-205

Estrae righe contenenti `???`:

```python
# Input: contenuto file SCL
# Output: [(45, "Ctrl.Enable := ???;"), (67, "IF ??? THEN"), ...]
```

**Max linee**: 10 (per evitare output troppo grande)

---

### find_output_file() - linee 208-240

Trova file output generato base a tipo:

```python
# Input: output_dir, stem, file_type='fb'
# Output: Path al file .scl oppure None

# Strategy:
# 1. Prova match diretto {stem}.{ext}
# 2. Se non trova, glob pattern {*}.{ext}
# 3. Ritorna il più recente se multipli match
```

**Eccezioni**: Ritorna None se non trovato, non lancia eccezioni

---

### create_directory_mirror() - linee 243-263

Ricrea struttura cartelle:

```python
# Input: source_root, output_root, xml_files list
# Output: dirs_created count

# Process:
# 1. Itera su xml_files
# 2. Calcola relative_path per ognuno
# 3. Crea directory corrispondere in output_root
# 4. mkdir(parents=True, exist_ok=True)
```

---

## FileProcessor Class (linee 266-395)

### process_with_tracking() - linee 268-350

**Flow completo di processamento:**

```
1. Identifica tipo file con identify_file_type()
   → Se None, return SKIPPED

2. Registra dimensione input
   → xml_file.stat().st_size

3. Start timer
   → start_time = time.time()

4. Chiama process_file(xml_file, output_dir)
   → ZERO MODIFICHE - funzione esistente

5. Cattura eccezioni:
   - FileNotFoundError → IO_ERROR
   - PermissionError → IO_ERROR
   - Exception → FAILED + PARSE_ERROR

6. Stop timer
   → processing_time = time.time() - start_time

7. Cerca file output
   → find_output_file() per trovarlo

8. Se trovato:
   - Registra dimensione output
   - Valida per placeholder '???'
   - Se has_placeholders → VALIDATION_ERROR
   - Altrimenti → SUCCESS

9. Se non trovato:
   - Status = FAILED
   - error_type = NO_OUTPUT

10. Return FileResult con tutti i metadati
```

**Key Point**: Non modifica mai `process_file()`, solo wraps risultato

---

### validate_output() - linee 352-366

```python
# 1. Leggi file con encoding='utf-8', errors='replace'
# 2. Conta '???' nel contenuto
# 3. Se count > 0:
#    - Estrai linee con placeholder
#    - Max 10 linee per report
# 4. Return dict con:
#    {
#        'has_placeholders': bool,
#        'count': int,
#        'lines': List[Tuple[int, str]]
#    }
```

**Sicurezza**: Gestisce encoding errors, non lancia eccezioni

---

## StatisticsCollector Class (linee 399-485)

### record_file() - linee 407-467

Aggiorna **tutti** i contatori da un `FileResult`:

```python
# Aggiorna:
# - Conteggi globali (total, processed, succeeded, failed, ...)
# - Conteggi per tipo file (FB, FC, DB, ...)
# - Tempi di processing
# - Dimensioni (input, output)
# - Directory stats (DirStats)

# Categorizza status:
# SKIPPED → files_skipped
# SUCCESS → files_succeeded, success_by_type
# VALIDATION_ERROR → files_validation_errors
# FAILED/IO_ERROR → files_failed
```

---

### get_summary() - linee 469-471

Ritorna `BatchSummary` finale con tutte le statistiche calcolate.

---

## CSVReportGenerator Class (linee 554-728)

### generate() - linee 556-728

Scrive CSV multi-sezione con `encoding='utf-8-sig'` (BOM per Excel):

**Sezioni:**

1. **Header** (metadati generali)
   - Generated timestamp
   - Source path
   - Output path

2. **Summary** (statistiche generali)
   - Total files, processed, succeeded, failed
   - Success rate, total time, average time

3. **File Type Distribution**
   - Conteggi per tipo (FB, FC, DB, UDT, TAGS)
   - Success/failure rates

4. **Performance Metrics**
   - Total time, average, median, min, max
   - Slowest file

5. **File Size Analysis**
   - Total input/output
   - Size change percentage
   - Average input/output

6. **Directory Breakdown**
   - Stats per directory
   - Success rate per directory

7. **Detailed Results**
   - Una riga per ogni file
   - Tutte le colonne da FileResult

**CSV Writer Settings:**
```python
csv.writer(f, quoting=csv.QUOTE_MINIMAL)
# Solo quote quando necessario (commi nei dati, etc.)
```

---

## Main Flow (linee 731-950)

### main() - linee 831-950

**Phases:**

```
PHASE 1: Discovery (linee 868-881)
├── discover all .xml files: source_root.rglob("*.xml")
├── count unique directories
└── calculate max depth

PHASE 2: Mirror Structure (linee 883-889)
├── create_directory_mirror()
└── print created dirs count

PHASE 3: Initialization (linee 891-896)
├── processor = FileProcessor()
├── stats = StatisticsCollector()
└── progress = ProgressDisplay()

PHASE 4: Batch Processing (linee 898-924)
├── FOR each xml_file in xml_files:
│   ├── calculate output_dir (mirrored path)
│   ├── result = process_with_tracking()
│   ├── stats.record_file(result)
│   ├── create_error_file() if needed
│   └── progress.update()
└── total_time = end - start

PHASE 5: Report Generation (linee 926-929)
├── generate_csv_report()
└── report_path = output_root / "batch_conversion_report.csv"

PHASE 6: Summary (linee 931-932)
└── print_final_summary()
```

---

## Integration Points

### Con main.py Esistente

```python
from main import identify_file_type, process_file

# ONLY queste 2 funzioni importate:
# 1. identify_file_type(file_path) → str or None
# 2. process_file(file_path, output_dir) → None (writes to disk)
```

**Vantaggi**:
- Nessuna modifica a `main.py`
- Utilizza funzioni provate e testate
- Semplice da mantenere

---

## Error Handling Strategy

### Fail-Safe Philosophy

**Un errore non stoppa il batch:**

```python
try:
    process_file(xml_file, output_dir)
    # ... validate output
except Exception as e:
    result.status = 'FAILED'
    result.error_message = str(e)
    # CONTINUE to next file
```

**Implicazioni**:
- Un file corrotto non ferma interi batch
- Tutti i file sono processati anche se alcuni falliscono
- Errori registrati in FileResult e file `.error`

---

## Performance Considerations

### Time Complexity

- **Discovery**: O(n) dove n = numero file
- **Mirror structure**: O(d) dove d = numero directory
- **Processing**: O(n * t) dove t = tempo medio per file
- **Report generation**: O(n) per scrivere righe CSV

**Overall**: O(n * t) dominato dal processing

### Memory Usage

- **FileResult list**: ~1KB per file = ~1MB per 1000 file
- **BatchSummary**: <100KB
- **All results in memory**: OK per progetti fino a 10K file

---

## Extension Points

### Aggiungere Nuove Statistiche

```python
# In StatisticsCollector.record_file():
# Aggiungere nuovi campi a BatchSummary
# Popolare in record_file()
# Usare in generate()
```

### Aggiungere Nuovi Formati Report

```python
# Creare classe ReportGenerator specifica
class JSONReportGenerator:
    def generate(self, report_path, ...):
        # Serializza BatchSummary e all_results come JSON

class HTMLReportGenerator:
    def generate(self, report_path, ...):
        # Genera HTML con tabelle e chart
```

### Aggiungere Parallel Processing

```python
# Usare concurrent.futures.ThreadPoolExecutor:
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(processor.process_with_tracking, ...)
        for xml_file in xml_files
    ]
    results = [f.result() for f in futures]
```

**Nota**: FileProcessor è stateless, sicuro per threading

---

## Testing

### Unit Test Example

```python
def test_format_size():
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024*1024) == "1.0 MB"

def test_file_result_creation():
    result = FileResult(
        source_path=Path("test.xml"),
        relative_path=Path("test.xml"),
        file_type="fb",
        status="SUCCESS"
    )
    assert result.status == "SUCCESS"

def test_stats_aggregation():
    stats = StatisticsCollector()
    result = FileResult(..., status="SUCCESS")
    stats.record_file(result)
    assert stats.summary.files_succeeded == 1
```

---

## Logging

Lo script usa logging standard Python:

```python
logger = logging.getLogger(__name__)

# Livelli usati:
logger.debug()    # Detailed info (error file creation)
logger.info()     # Normal operations (dal main.py)
logger.warning()  # Non-critical issues (file stat errors)
logger.error()    # Processing failures (dal main.py)
```

**Output**: Console + file (configurato da `setup_logging()`)

---

## Compatibility Notes

### Windows Specifics

- `Path` objects gestiscono separatori automaticamente
- UTF-8 con BOM per Excel auto-detect
- Console encoding: managed by `encoding='utf-8-sig'`

### Python Version

- **Minimum**: Python 3.8 (dataclasses, typing)
- **Tested**: Python 3.10+

### Dependencies

- **Standard library only** except:
  - `main.py` (existing converter)
  - `utils.py` (logging setup)

---

## Future Enhancements

1. **Parallel processing** - ProcessPoolExecutor per 4x speedup
2. **Incremental mode** - Skip already converted files
3. **Diff detection** - Only reprocess changed files
4. **Priority queue** - Process large files first
5. **Webhook notifications** - Send completion status to external service
6. **Database logging** - Store results in SQLite
7. **REST API** - Expose as web service
8. **GUI** - tkinter interface per drag-and-drop

---

**Versione**: 1.0
**Ultimo Aggiornamento**: December 26, 2025
**Maintainer**: Development Team
