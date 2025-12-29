# Revisione strutturale â€“ FB SCL riutilizzabili (portabilitÃ  totale)

## Scopo del documento
Questo documento elenca **in modo dettagliato, motivato e operativo** tutte le modifiche da applicare allo **schema JSON**, alle **regole di analisi** e alle **assunzioni di progetto**, partendo dai vincoli dichiarati:

- i blocchi analizzati sono **SCL giÃ  correttamente parsati (AST affidabile)**
- i blocchi devono essere **riutilizzabili da un progetto allâ€™altro**
- **non devono contenere ingressi/uscite fisiche** nÃ© accoppiamenti a progetto/impianto

Obiettivo finale:

> **SCL AST â†’ JSON deterministico â†’ codegen FB macchina / documentazione / quality gate**

---

## Assunzioni consolidate

### A1 â€“ Nessun I/O fisico
Nei FB riutilizzabili **non devono comparire**:
- `%I`, `%Q`, `%M`
- `AT` mapping
- tag di periferia

Motivazione:
- garantisce portabilitÃ 
- separa device logic da impianto

---

### A2 â€“ Nessun DB globale hardcoded
Vietati:
- `DB_xxx.yyy`
- GlobalDB di progetto

Ammessi:
- STAT / instance data
- UDT passati via interfaccia

Motivazione:
- i DB globali sono sempre project-specific

---

### A3 â€“ Interfacce solo logiche
Un FB comunica solo tramite:
- VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT
- UDT (`Cmd`, `Sts`, `Cfg`, `Diag`, `If`)

Motivazione:
- composizione
- testabilitÃ 
- simulazione

---

## Cambiamenti allo schema JSON

### 1. Rimozione I/O fisici dal contract
Da rimuovere completamente:
- `hw_inputs`
- `actor_outputs`
- `other_inputs`
- `other_outputs`

Motivazione:
- conflitto diretto con la portabilitÃ 

---

### 2. Contract basato solo su interfacce logiche
Il contract deve descrivere **solo simboli PLC logici**, mai hardware.

---

### 3. Tipizzazione rigorosa delle variabili PLC
Ogni variabile deve includere:
- direzione (input/output/inout/static/temp)
- datatype reale
- nome qualificato
- attributi (RETAIN, CONSTANT, ecc.)

Motivazione:
- codegen corretto
- analisi deterministica

---

## Evidence e tracciabilitÃ 

### 4. Evidence strutturata
Ogni pattern / anti-pattern / vincolo deve includere:
- file
- range (line/col)
- tipo nodo AST
- simbolo

Motivazione:
- auditabilitÃ 
- regressioni
- quality gate

---

## Confidence

### 5. Confidence numerica
Oltre a HIGH/MEDIUM/LOW aggiungere:
- score 0..1
- features contributive

Motivazione:
- automazione CI
- confronto versioni

---

## State machine

### 6. Stato macchina deterministico
Descrivere esplicitamente:
- variabile di stato
- encoding
- stati
- transizioni con condition + evidence

Motivazione:
- base per codegen
- verifica logica

---

## Anti-pattern e vincoli

### 7. Anti-pattern come fonte unica
Tutte le violazioni sono anti-pattern.
I constraints sono solo un riassunto derivato.

---

### 8. Portability gate (FAIL)
Un FB Ã¨ non valido se:
- usa I/O fisici
- usa AT
- usa DB globali hardcoded

---

## Device type

### 9. Tassonomia estendibile
Separare:
- `device_family`
- `device_type`

Motivazione:
- evoluzione della libreria

---

## Versioning

### 10. Versione schema obbligatoria
Aggiungere:
```json
"schema_version": "1.1.0"
```

Motivazione:
- migrazione controllata
- stabilitÃ  codegen

---

## Conclusione
Queste modifiche rendono il sistema:
- portabile
- deterministico
- industrial-grade

e pronto per:
- generazione automatica FB macchina
- quality gate
- knowledge base tecnica.
