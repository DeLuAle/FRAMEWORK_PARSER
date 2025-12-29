# FRAMEWORK_PARSER

> **Nota**: Questa repository è stata creata per imparare come funziona il framework PLC e la relativa codebase.

> [!IMPORTANT]
> **Source of Truth & Disclaimer**: Gli artefatti SCL/CSV generati sono il risultato di una conversione automatica eseguita dal modulo `xml_to_scl`. Data la natura euristica del parsing della logica Ladder/FBD, il codice prodotto potrebbe contenere discrepanze o errori di interpretazione. La **Source of Truth (SoT)** definitiva rimane esclusivamente il sorgente XML originale esportato da TIA Portal. La validazione tecnica deve sempre fare riferimento ai file XML per garantire l'integrità delle informazioni.




TIA Portal XML to SCL Converter. This tool allows you to convert PLC blocks (FB, FC, DB, UDT) and Tag Tables exported from TIA Portal in XML format into readable and importable SCL or CSV files.

## 🚀 Quick Start

### Batch Conversion of a PLC Folder

To parse an entire PLC project folder (containing `Program blocks`, `PLC tags`, etc.):

```powershell
python xml_to_scl/batch_convert_project.py "PLC_410D1" --output "PLC_410D1_Parsed"
```

- **Input**: The directory containing your TIA Portal XML exports (e.g., `PLC_410D1`).
- **Output**: A new directory (e.g., `PLC_410D1_Parsed`) where the converted SCL/CSV files will be saved, maintaining the original folder structure.

- **Validation**: Automatically checks for placeholders (`???`) in the generated code and logs them in a detailed report.

---

## 📚 Ecosystem & Components

Oltre al parser principale, la repository include strumenti specializzati per l'ecosistema Siemens:

### 🔍 [DocKB_Siemens](./DocKB_Siemens)
Sistema di **Information Retrieval** e Knowledge Base tecnica.
- **Estrazione**: Smonta manuali PDF (SINAMICS, S7-1500) in database JSON.
- **Ricerca Rapida**: Trova parametri, fault e allarmi istantaneamente senza consultare PDF da 1000+ pagine.
- **Integrazione**: Fornisce script di ricerca CLI e modelli SCL per TIA Portal.

### ✍️ [SKILL_SCL_SYNTAX](./SKILL_SCL_SYNTAX)
Guida di riferimento e assistenza per la programmazione **SCL (Structured Control Language)**.
- **Best Practices**: Regole critiche per TIA Portal V20+ (es. parametri nominati, istanze persistenti).
- **Database Funzioni**: Riferimento per oltre 200 funzioni native Siemens.
- **Anti-Patterns**: Catalogo di errori comuni da evitare durante lo sviluppo.

---

## 📊 Reports

After a batch conversion, a `batch_conversion_report.csv` is generated in the output folder, providing:
- Success rate per file type.
- List of any files that failed to convert.
- Identification of blocks requiring manual review (placeholders found).

## 🛠️ Advanced Usage

For single file conversion or more options:
```powershell
python xml_to_scl/main.py path/to/file.xml --output "output_folder"
```

---
**Author**: [DeLuAle](https://github.com/DeLuAle)
