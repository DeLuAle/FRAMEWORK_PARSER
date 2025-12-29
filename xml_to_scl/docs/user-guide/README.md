# TIA Portal XML to SCL Converter

Questo strumento permette di convertire i file XML esportati da TIA Portal (FB, FC, DB, UDT e Tag Table) in file sorgente SCL, DB, UDT o CSV pronti per l'importazione.

## Stato del Progetto
Il convertitore è pronto per l'uso sulla maggior parte della logica LAD standard.

### Funzionalità Supportate
- **Blocchi**: FB, FC, DB, UDT.
- **Tag Table**: Conversione in formato CSV per TIA Portal.
- **Logica LAD**: Operazioni booleane, comparatori, matematica, stringhe, MOVE, conversioni e chiamate a blocchi (FB/FC).

### Limitazioni Note
- **Salti (Jumps)**: `JMP` e `Label` non sono ancora supportati.
- **Timer/Counter IEC**: Supporto base, l'accesso ai membri (es. `.Q`) potrebbe richiedere verifiche manuali.
- **Tipi Complessi**: Supporto preliminare per `Variant` e `Any`.

## Istruzioni per l'Uso

### 1. Requisiti
- Python 3.8 o superiore.
- Nessuna libreria esterna richiesta (usa la libreria standard).

### 2. Conversione
Apri un terminale nella cartella `xml_to_scl` ed esegui:

```powershell
# Converti tutti i file in una cartella
python main.py "percorso/alla/tua/cartella_xml" --output "output"

# Converti un singolo file
python main.py "percorso/al/file.xml" --output "output"
```

### 3. Opzioni Comuni
- `--output` o `-o`: Specifica la cartella di destinazione (default: `output`).
- `--recursive` o `-r`: Scansiona le sottocartelle (attivo di default).
- `--type`: Filtra per tipo (`udt`, `db`, `fb`, `fc`, `tags`).

## Struttura Output
I file generati verranno salvati nella cartella di output specificata:
- `.scl` per FB e FC.
- `.db` per i Data Block.
- `.udt` per i tipi di dati utente.
- `.csv` per le tabelle delle variabili (PLC Tags).
