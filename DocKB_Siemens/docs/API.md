# 🔌 API Documentation - DocKB_Siemens

Documentazione per sviluppatori che vogliono integrare DocKB_Siemens

---

## 📚 Python API

### Importare Moduli

```python
import sys
sys.path.append('c:/Projects/DocKB_Siemens')

from config import PROJECT_ROOT, PDF_DIR, KB_DIR
from scripts.build_knowledge_base import KnowledgeBaseBuilder
from scripts.sinamics_kb_search import search_kb
```

---

## 🔍 Search API

### Funzione `search_kb()`

```python
from scripts.sinamics_kb_search import search_kb

# Ricerca per categoria
results = search_kb(
    kb_dir="kb/sinamics/manual",
    category="fault"
)

# Ricerca testuale
results = search_kb(
    kb_dir="kb/sinamics/manual",
    query="parameter p0230"
)

# Parametri:
# - kb_dir: path alla KB
# - category: 'parameter', 'fault', 'alarm', 'motor', 'safety', 'function', 'appendix'
# - query: testo da cercare
# - max_results: numero massimo risultati (default: 10)

# Returns: List[Dict]
# [
#   {
#     "section_id": "sezione_000123",
#     "content": "...",
#     "keywords": [...],
#     "relevance": 0.8
#   }
# ]
```

---

## 🏗️ Build API

### Classe `KnowledgeBaseBuilder`

```python
from scripts.build_knowledge_base import KnowledgeBaseBuilder

# Inizializza builder
builder = KnowledgeBaseBuilder(json_dir="output/manual")

# Carica sezioni
sections = builder.load_sections()

# Identifica capitoli
chapters = builder.identify_chapters()

# Crea search index
search_index = builder.build_search_index()

# Salva KB
builder.save_knowledge_base(output_dir="kb/sinamics/manual")
```

---

## 📄 PDF Extraction API

### Classe `PDFExtractor`

```python
from scripts.extract_pdf_to_json import PDFExtractor

# Inizializza extractor
extractor = PDFExtractor("resources/pdfs/sinamics/manual.pdf")

# Estrai testo
text = extractor.extract_text()

# Estrai e salva JSON
data = extractor.extract_to_json(output_dir="output/manual")

# Returns: Dict
# {
#   "metadata": {
#     "source": "manual.pdf",
#     "total_lines": 28553,
#     "extraction_method": "pdftotext"
#   },
#   "sezioni": [...],
#   "content": {...}
# }
```

---

## 📊 Registry API

### Leggere Registry

```python
import json
from config import KB_REGISTRY

with open(KB_REGISTRY, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Lista KB disponibili
for kb in registry['knowledge_bases']:
    print(f"{kb['id']}: {kb['name']}")
```

### Aggiungere KB al Registry

```python
new_kb = {
    "id": "new_manual",
    "name": "New Manual",
    "pdf_file": "resources/pdfs/sinamics/new.pdf",
    "kb_directory": "kb/sinamics/new",
    "description": "New SINAMICS manual",
    "status": "active",
    "language": "en"
}

registry['knowledge_bases'].append(new_kb)

with open(KB_REGISTRY, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
```

---

## 🔗 Integration Examples

### Flask REST API

```python
from flask import Flask, jsonify, request
from scripts.sinamics_kb_search import search_kb

app = Flask(__name__)

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    category = request.args.get('category')
    
    results = search_kb(
        kb_dir="kb/unified",
        query=query,
        category=category
    )
    
    return jsonify(results)

@app.route('/api/alarm/<code>', methods=['GET'])
def get_alarm(code):
    results = search_kb(
        kb_dir="kb/unified",
        query=code,
        category="alarm"
    )
    
    if results:
        return jsonify(results[0])
    return jsonify({"error": "Alarm not found"}), 404

if __name__ == '__main__':
    app.run(port=5000)
```

**Usage:**
```bash
curl "http://localhost:5000/api/search?q=fault&category=fault"
curl "http://localhost:5000/api/alarm/A0681"
```

---

### Batch Processing

```python
from pathlib import Path
from scripts.extract_pdf_to_json import PDFExtractor
from scripts.build_knowledge_base import KnowledgeBaseBuilder

def process_all_pdfs(pdf_dir, output_base):
    """Processa tutti i PDF in una directory"""
    pdf_dir = Path(pdf_dir)
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")
        
        # Extract
        output_dir = output_base / pdf_file.stem
        extractor = PDFExtractor(str(pdf_file))
        extractor.extract_to_json(str(output_dir))
        
        # Build KB
        builder = KnowledgeBaseBuilder(str(output_dir))
        builder.load_sections()
        builder.identify_chapters()
        builder.build_search_index()
        builder.build_master_index()
        
        kb_dir = Path("kb") / "batch" / pdf_file.stem
        builder.save_knowledge_base(str(kb_dir))
        
        print(f"  [OK] KB created: {kb_dir}")

# Usage
process_all_pdfs("resources/pdfs/sinamics", Path("output"))
```

---

### Custom Search Index

```python
from collections import defaultdict
from scripts.build_knowledge_base import KnowledgeBaseBuilder

class CustomKBBuilder(KnowledgeBaseBuilder):
    """Estende KnowledgeBaseBuilder con categorie custom"""
    
    def build_custom_search_index(self):
        """Crea indice con categorie personalizzate"""
        search_index = defaultdict(list)
        
        # Categorie custom
        custom_keywords = {
            'profidrive': ['profidrive', 'telegram', 'cyclic'],
            'encoder': ['encoder', 'resolver', 'ssi', 'endat'],
            'safety': ['sto', 'sls', 'sbc', 'safe torque'),
        }
        
        for category, keywords in custom_keywords.items():
            for section_id, section in self.sections.items():
                content = section['content'].lower()
                for keyword in keywords:
                    if keyword in content:
                        search_index[category].append({
                            'section_id': section['id'],
                            'section_num': section_id,
                            'content_preview': content[:100],
                        })
                        break
        
        return dict(search_index)

# Usage
builder = CustomKBBuilder("output/manual")
builder.load_sections()
custom_index = builder.build_custom_search_index()
```

---

### Database Integration

```python
import sqlite3
import json

def export_kb_to_sqlite(kb_dir, db_file):
    """Esporta KB in database SQLite"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Crea tabella
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sections (
            id TEXT PRIMARY KEY,
            chapter TEXT,
            content TEXT,
            keywords TEXT,
            metadata TEXT
        )
    ''')
    
    # Import sezioni
    sections_dir = Path(kb_dir) / "sections"
    for section_file in sections_dir.glob("*.json"):
        with open(section_file, 'r', encoding='utf-8') as f:
            section = json.load(f)
        
        cursor.execute('''
            INSERT OR REPLACE INTO sections VALUES (?, ?, ?, ?, ?)
        ''', (
            section['id'],
            section.get('chapter', ''),
            section['content'],
            json.dumps(section.get('metadata', {}).get('keywords', [])),
            json.dumps(section.get('metadata', {}))
        ))
    
    conn.commit()
    conn.close()
    print(f"Exported to {db_file}")

# Usage
export_kb_to_sqlite("kb/sinamics/manual", "sinamics.db")
```

---

## 🎯 CLI Integration

### Argparse Example

```python
import argparse
from scripts.sinamics_kb_search import search_kb

def main():
    parser = argparse.ArgumentParser(description='Search Knowledge Base')
    parser.add_argument('--kb', required=True, help='KB directory')
    parser.add_argument('--search', help='Search query')
    parser.add_argument('--category', help='Category filter')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    results = search_kb(
        kb_dir=args.kb,
        query=args.search,
        category=args.category
    )
    
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    else:
        for result in results:
            print(f"\n{result['section_id']}:")
            print(result['content'][:200])

if __name__ == '__main__':
    main()
```

---

## 📡 Event-Driven Architecture

### Watcher Example

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFHandler(FileSystemEventHandler):
    """Auto-process new PDFs"""
    
    def on_created(self, event):
        if event.src_path.endswith('.pdf'):
            print(f"New PDF detected: {event.src_path}")
            # Auto-extract
            # Auto-build KB
            # Auto-update registry

observer = Observer()
observer.schedule(PDFHandler(), path='resources/pdfs', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
```

---

## 🔐 Security Best Practices

### Input Validation

```python
from pathlib import Path

def validate_kb_path(kb_path):
    """Valida che il path KB sia sicuro"""
    kb_path = Path(kb_path).resolve()
    
    # Check dentro PROJECT_ROOT
    if not str(kb_path).startswith(str(PROJECT_ROOT)):
        raise ValueError("KB path outside project root")
    
    # Check esiste
    if not kb_path.exists():
        raise FileNotFoundError(f"KB not found: {kb_path}")
    
    return kb_path
```

---

## 📊 Performance Tips

### Lazy Loading

```python
class LazyKB:
    """Carica sezioni solo quando necessario"""
    
    def __init__(self, kb_dir):
        self.kb_dir = Path(kb_dir)
        self._index = None
        self._sections_cache = {}
    
    @property
    def index(self):
        if self._index is None:
            with open(self.kb_dir / "search_index.json") as f:
                self._index = json.load(f)
        return self._index
    
    def get_section(self, section_id):
        if section_id not in self._sections_cache:
            section_file = self.kb_dir / "sections" / f"{section_id}.json"
            with open(section_file) as f:
                self._sections_cache[section_id] = json.load(f)
        return self._sections_cache[section_id]
```

---

## 📝 Type Hints

```python
from typing import List, Dict, Optional
from pathlib import Path

def search_kb(
    kb_dir: str | Path,
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Search Knowledge Base
    
    Args:
        kb_dir: Path to KB directory
        query: Search query string
        category: Category filter
        max_results: Maximum results to return
    
    Returns:
        List of matching sections with metadata
    """
    pass
```

---

**Versione:** 2.0  
**Aggiornato:** 2025-12-22
