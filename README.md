# FRAMEWORK_PARSER

TIA Portal XML to SCL Converter. This tool allows you to convert PLC blocks (FB, FC, DB, UDT) and Tag Tables exported from TIA Portal in XML format into readable and importable SCL or CSV files.

## 🚀 Quick Start

### Batch Conversion of a PLC Folder

To parse an entire PLC project folder (containing `Program blocks`, `PLC tags`, etc.):

```powershell
python xml_to_scl/batch_convert_project.py "PLC_410D1" --output "PLC_410D1_Parsed"
```

- **Input**: The directory containing your TIA Portal XML exports (e.g., `PLC_410D1`).
- **Output**: A new directory (e.g., `PLC_410D1_Parsed`) where the converted SCL/CSV files will be saved, maintaining the original folder structure.

## 📂 Features

- **FB/FC Conversion**: Converts Ladder/FBD logic into structured SCL code.
- **DB Generation**: Converts Global DBs into `.db` files.
- **UDT Support**: Converts PLC User Data Types into `.udt` files.
- **PLC Tags**: Converts Tag Tables into `.csv` files compatible with TIA Portal import.
- **Structure Preservation**: Maintains the original folder hierarchy (Software units, Program blocks, etc.).
- **Validation**: Automatically checks for placeholders (`???`) in the generated code and logs them in a detailed report.

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
