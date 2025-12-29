# 📋 Piano d'Azione Multi-Sessione per Correzione xml_to_scl

**Data Inizio**: 2025-12-24
**Stato**: 🔴 IN ELABORAZIONE
**Priorità Globale**: CRITICO (55% output corrotto)

---

## 📊 Panoramica

| Sessione | Focus | Durata | Priorità | Complessità |
|----------|-------|--------|----------|-------------|
| **#1** | Sicurezza XXE + Error Handling | 2-3h | 🔴 CRITICO | Bassa |
| **#2** | Fix REGION Nesting | 3-4h | 🔴 CRITICO | Media |
| **#3** | Implementare Boolean Expression Builder | 4-6h | 🔴 CRITICO | Alta |
| **#4** | Fix Duplicazione + FB Parameters | 2-3h | 🟠 ALTA | Media |
| **#5** | Testing + Validation | 3-4h | 🟠 ALTA | Media |
| **#6** | Documentazione + Rollout | 2h | 🟡 MEDIA | Bassa |

**Tempo Totale Stimato**: 16-23 ore (spread su 3-4 giorni)

---

# 🎯 SESSIONE #1: Sicurezza XXE e Error Handling

**Durata**: 2-3 ore
**Priorità**: 🔴 CRITICO
**Complessità**: Bassa
**Prerequisiti**: Nessuno

## Obiettivi
- [x] Aggiungere protezione XXE
- [x] Migliorare gestione errori specifica
- [x] Fix encoding error handling

## Task

### Task 1.1: Protezione XXE in xml_parser_base.py
**File**: `xml_parser_base.py:45`
**Tempo**: 30 min

```python
# PRIMA (VULNERABILE):
self.tree = ET.parse(self.xml_path)

# DOPO (SICURO):
try:
    # Metodo 1: Disabilitare entity resolution in ElementTree
    parser = ET.XMLParser()
    parser.entity = {}  # Disabilita entità externe
    self.tree = ET.parse(self.xml_path, parser=parser)
except ET.ParseError as e:
    logger.error(f"XXE protection: Failed to create parser: {e}")
    raise
```

**Checklist**:
- [ ] Importare ET.XMLParser
- [ ] Creare parser con entity disabled
- [ ] Testare su Positioning_MOL_Machine_FB.xml
- [ ] Verificare nessun side effect

---

### Task 1.2: Protezione XXE in utils.py
**File**: `utils.py:214` (in `validate_xml_file()`)
**Tempo**: 20 min

Stessa patch come Task 1.1, applicare in:
- [ ] `validate_xml_file()` linea 214
- [ ] Testare con file corrupto

---

### Task 1.3: Protezione XXE in plc_tag_parser.py
**File**: `plc_tag_parser.py:23` (in `parse()`)
**Tempo**: 20 min

Stessa patch come Task 1.1, applicare a:
- [ ] Parsing tag table
- [ ] Testare su tag XML

---

### Task 1.4: Migliorare Error Handling in xml_parser_base.py
**File**: `xml_parser_base.py:62-64`
**Tempo**: 30 min

```python
# PRIMA (GENERICO):
except Exception as e:
    logger.error(f"Error parsing {self.xml_path}: {e}")
    raise

# DOPO (SPECIFICO):
except ET.ParseError as e:
    logger.error(f"XML parsing error in {self.xml_path}: {e}")
    raise ValueError(f"Invalid XML: {e}")
except FileNotFoundError as e:
    logger.error(f"File not found: {self.xml_path}")
    raise
except PermissionError as e:
    logger.error(f"Permission denied reading {self.xml_path}: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error parsing {self.xml_path}: {e}")
    raise
```

**Checklist**:
- [ ] Separare ET.ParseError
- [ ] Aggiungere FileNotFoundError
- [ ] Aggiungere PermissionError
- [ ] Mantenere Exception come catch-all finale
- [ ] Testare ogni path di errore

---

### Task 1.5: Fix Encoding Error Handling in main.py
**File**: `main.py:88`
**Tempo**: 20 min

```python
# PRIMA:
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:

# DOPO:
try:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        # Segnalare se ci sono errori
        content = f.read()
        if content.count('\ufffd'):  # Carattere replacement
            logger.warning(f"Encoding errors in {file_path}, used replacement")
except UnicodeDecodeError as e:
    logger.error(f"Cannot decode {file_path}: {e}")
    return
```

**Checklist**:
- [ ] Cambiare errors='ignore' in errors='replace'
- [ ] Aggiungere try/except UnicodeDecodeError
- [ ] Aggiungere warning per replacement chars
- [ ] Testare su file con bad encoding

---

### Task 1.6: Unit Test per Sicurezza
**File**: `tests/test_security.py` (NUOVO)
**Tempo**: 30 min

Creare test per:
- [ ] XXE attack test (fallisca se senza protezione)
- [ ] File permission test
- [ ] Bad encoding test

---

## Checkpoint 1: Sessione #1 Completata?

```bash
# Eseguire questi comandi per verificare:
python -m pytest tests/test_security.py -v
python main.py tests/fixtures/ --output tests/output/

# Verificare nel log:
grep -i "parse error\|XXE\|permission" tests/output/*.log
```

✅ **Success Criteria**:
- Nessun warning XXE
- Errori specifici nel log (non "Exception")
- Encoding errors segnalati come warning
- All test pass

---

---

# 🎯 SESSIONE #2: Fix REGION Nesting Architecture

**Durata**: 3-4 ore
**Priorità**: 🔴 CRITICO
**Complessità**: Media
**Prerequisiti**: Sessione #1 completata

## Obiettivi
- [x] Ridisegnare struttura REGION in fbfc_generator.py
- [x] Collassare networks annidate in sequenza parallela
- [x] Testare su Positioning_MOL_Machine_FB.xml

## Root Cause Analysis

**File interessato**: `fbfc_generator.py` (linea ~150-250)

**Il Problema**:
```python
# Attuale (SBAGLIATO):
def generate_logic(self, networks):
    for network in networks:
        indent_level += 1  # ⚠️ Incrementa e non resetta!
        self.add_region(network.title, indent_level)
        # Genera istruzioni
        # ⚠️ Non chiude la REGION, rimane aperta!
```

**Risultato**: Ogni network annida il successivo

---

## Task

### Task 2.1: Analizzare Struttura Attuale fbfc_generator.py
**Tempo**: 30 min

```bash
# Leggere:
1. fbfc_generator.py:150-250  (metodo generate_logic)
2. fbfc_generator.py:50-100   (metodo add_region, indent, dedent)
3. fbfc_generator.py:30-50    (costruttore e init)

# Domande da farsi:
- Dove viene chiamato generate_logic()?
- Come gestisce l'indentazione?
- Come chiude le REGION?
```

**Checklist**:
- [ ] Comprendere flusso attuale
- [ ] Identificare esatta linea di bug
- [ ] Verificare quanti networks vengono processati

---

### Task 2.2: Redesign Architettura REGION
**Tempo**: 1 ora

```python
# NUOVO DESIGN:
class FBFCGenerator:

    def generate_body(self, interface_data, lad_networks, scl_code):
        """
        Genera il BEGIN/END del blocco con REGION sequenziali.

        Struttura output:
        BEGIN
           REGION "Network 1: ..."
              ...
           END_REGION

           REGION "Network 2: ..."
              ...
           END_REGION

           ... (no nesting!)
        END
        """
        self.add_line('BEGIN')
        self.indent()

        # Genera ogni network come REGION indipendente
        for i, network in enumerate(lad_networks, 1):
            self._generate_network_region(i, network)
            self.add_blank_line()  # Separazione visuale

        # Genera SCL code blocks se presenti
        if scl_code:
            for i, code in enumerate(scl_code, 1):
                self._generate_scl_region(i, code)
                self.add_blank_line()

        self.dedent()
        self.add_line('END')

    def _generate_network_region(self, network_num, network):
        """Genera una singola REGION per un network LAD."""
        title = f"Network {network_num}: {network.title}"

        self.add_line(f'REGION "{title}"')
        self.indent()

        # Genera istruzioni del network
        for instr in network.instructions:
            self.add_line(instr)

        self.dedent()
        self.add_line('END_REGION')

    def _generate_scl_region(self, code_num, scl_code):
        """Genera una REGION per blocco SCL."""
        self.add_line(f'REGION "SCL Code Block {code_num}"')
        self.indent()

        # Aggiungi codice SCL così com'è
        self.add_raw_lines(scl_code)

        self.dedent()
        self.add_line('END_REGION')
```

**Checklist**:
- [ ] Creare nuovo metodo `generate_body()`
- [ ] Refactor `_generate_network_region()` (nuovo)
- [ ] Refactor `_generate_scl_region()` (nuovo)
- [ ] Verificare that indentation level è **sempre** 1 dentro REGION
- [ ] Documentare la nuova struttura

---

### Task 2.3: Integrare Nuovo Design
**Tempo**: 45 min

1. **Backup versione attuale**:
   ```bash
   cp fbfc_generator.py fbfc_generator.py.backup
   ```

2. **Modificare `generate()` principale**:
   ```python
   def generate(self, output_file):
       """Genera file SCL completo."""
       # ... header ...
       self.generate_body(
           self.data.get('interface', {}),
           self.data.get('lad_networks', []),
           self.data.get('scl_code', [])
       )
       # ... write file ...
   ```

3. **Testare**:
   ```bash
   python main.py path/to/Positioning_MOL_Machine_FB.xml --output test/
   ```

**Checklist**:
- [ ] Backup creato
- [ ] Metodo generate() aggiornato
- [ ] Integrazione testata
- [ ] Output non contiene nesting

---

### Task 2.4: Validare Output
**Tempo**: 30 min

**Test file**: `Positioning_MOL_Machine_FB.scl`

```bash
# Verifiche:
1. grep -c "REGION \"Network" output.scl
   # Dovrebbe essere 31 (un per network)

2. grep "REGION.*REGION" output.scl
   # Dovrebbe restituire NULLA (zero nesting)

3. python -c "
   with open('output.scl') as f:
       content = f.read()
       # Conta REGION aperti/chiusi
       opens = content.count('REGION')
       closes = content.count('END_REGION')
       print(f'REGION opens: {opens}, closes: {closes}')
       assert opens == closes, 'Mismatch!'
   "

4. Aprire file e verificare visivamente struttura
```

**Checklist**:
- [ ] 31 REGION generate
- [ ] Nessun nesting REGION
- [ ] REGION/END_REGION bilanciate
- [ ] Output formattato correttamente

---

## Checkpoint 2: Sessione #2 Completata?

✅ **Success Criteria**:
- Output SCL ha 31 REGION sequenziali
- Nessun nesting di REGION
- REGION/END_REGION bilanciate
- File è valido dal punto di vista sintattico SCL

```bash
# Final test
python main.py tests/fixtures/Positioning_MOL_Machine_FB.xml --output tests/output/
grep "REGION.*REGION" tests/output/Positioning_MOL_Machine_FB.scl
# Output dovrebbe essere vuoto
```

---

---

# 🎯 SESSIONE #3: Boolean Expression Builder (LAD Logic)

**Durata**: 4-6 ore
**Priorità**: 🔴 CRITICO
**Complessità**: Alta
**Prerequisiti**: Sessione #1 e #2 completate

## Obiettivi
- [x] Implementare `_build_expression_from_wires()`
- [x] Mappare contatti/bobine a variabili
- [x] Ricostruire logica booleana dalle Wires
- [x] Convertire in notazione infixa SCL

## Background Tecnico

### Struttura LAD nel XML

```xml
<Parts>
  <!-- Variabili/costanti accessibili -->
  <Access UId="21">TON_NoPendingCmd.Q</Access>
  <Access UId="22">Sts.Standstill</Access>

  <!-- Contatti (rappresentano condizioni) -->
  <Part Name="Contact" UId="28" />
  <Part Name="Contact" UId="29" />

  <!-- Gate logici -->
  <Part Name="O" UId="31"><TemplateValue Name="Card">2</TemplateValue></Part>
  <!-- O = OR, A = AND, X = XOR, etc. -->

  <!-- Output (assegnazione) -->
  <Part Name="Coil" UId="35" />
</Parts>

<Wires>
  <!-- Powerrail è il "vero" della rete -->
  <Wire UId="36">
    <Powerrail />
    <NameCon UId="28" Name="in" />
  </Wire>

  <!-- Collegamento variabile a contatto -->
  <Wire UId="37">
    <IdentCon UId="21" />
    <NameCon UId="28" Name="operand" />
  </Wire>

  <!-- Cascata di contatti -->
  <Wire UId="38">
    <NameCon UId="28" Name="out" />
    <NameCon UId="29" Name="in" />
  </Wire>

  <!-- Collegamento a output -->
  <Wire UId="49">
    <NameCon UId="34" Name="out" />
    <NameCon UId="35" Name="in" />
  </Wire>
</Wires>
```

### Algoritmo di Ricostruzione

```
1. Trova la bobina (Coil) - target output
2. Traccia l'ingresso della bobina all'indietro tramite wires
3. Segui la catena:
   - Se trovi Powerrail -> fine della logica seriale
   - Se trovi gate logico (O/A/X) -> ricostruisci con operazione
   - Se trovi Access -> sostituisci con variabile reale
   - Se trovi Contact negato -> aggiungi NOT
4. Costruisci espressione in formato infixa
5. Semplifica e converti a SCL
```

---

## Task

### Task 3.1: Analizzare Struttura lad_parser.py Attuale
**Tempo**: 45 min

```bash
# Leggere e capire:
1. lad_parser.py:12-65       (parse() - entry point)
2. lad_parser.py:66-197      (_parse_parts - estrae nomi variabili)
3. lad_parser.py:199-297     (_parse_wires - mappa connessioni)
4. lad_parser.py:298-350     (_extract_fb_calls - INCOMPLETO)

# Domande:
- Come vengono estratte le Access (variabili)?
- Come vengono mappate le Wires?
- Perché _extract_fb_calls() non ricostruisce la logica?
```

**Checklist**:
- [ ] Comprendere struttura dati `self.parts` (dict UId -> data)
- [ ] Comprendere struttura `self.connections` (dict destination -> source)
- [ ] Identificare dove manca la ricostruzione booleana

---

### Task 3.2: Creare Classe per Espressione Booleana
**Tempo**: 1 ora

**Nuovo file**: `lad_expression_builder.py`

```python
"""
Boolean expression builder per LAD logic reconstruction.
Converte una topologia ladder in espressione booleana SCL.
"""

class LadExpression:
    """Rappresenta un'espressione booleana LAD."""

    def __init__(self, expr_type, left=None, right=None, operand=None):
        """
        expr_type: 'var', 'not', 'and', 'or', 'xor', 'nand', 'nor'
        left/right: subexpressions
        operand: variable name (per type='var')
        """
        self.type = expr_type
        self.left = left
        self.right = right
        self.operand = operand

    def to_scl(self):
        """Converte a notazione SCL."""
        if self.type == 'var':
            return self.operand
        elif self.type == 'not':
            return f"NOT ({self.left.to_scl()})"
        elif self.type == 'and':
            return f"({self.left.to_scl()} AND {self.right.to_scl()})"
        elif self.type == 'or':
            return f"({self.left.to_scl()} OR {self.right.to_scl()})"
        # ... altri gate ...

    def simplify(self):
        """Semplifica l'espressione (opcional)."""
        # Es: NOT NOT x -> x
        pass


class LadExpressionBuilder:
    """Ricostruisce un'espressione booleana da Parts/Wires."""

    def __init__(self, parts, wires):
        """
        parts: dict di {uid -> part_data}
        wires: dict di connections {(dest_uid, pin) -> source_info}
        """
        self.parts = parts
        self.connections = wires

    def build_expression(self, coil_uid):
        """
        Ricostruisce l'espressione per una bobina (coil).

        Args:
            coil_uid: UId del Coil (output)

        Returns:
            LadExpression
        """
        # Inizia dal Coil e traccia all'indietro
        return self._trace_from_coil(coil_uid)

    def _trace_from_coil(self, coil_uid):
        """Traccia da bobina all'indietro per ricostruire logica."""
        # Trova il wire che entra nel coil
        source = self.connections.get((coil_uid, 'in'))
        if not source:
            return LadExpression('var', operand='???')

        # Traccia dal source
        return self._trace_from_source(source['uid'])

    def _trace_from_source(self, uid):
        """Traccia da un elemento della logica."""
        part = self.parts.get(uid)
        if not part:
            return LadExpression('var', operand='???')

        part_type = part.get('type')

        if part_type == 'Access':
            # È una variabile - fine della traccia
            var_name = part.get('name', '???')
            negated = part.get('negated', False)

            expr = LadExpression('var', operand=var_name)
            if negated:
                expr = LadExpression('not', left=expr)
            return expr

        elif part_type == 'Part':
            part_name = part.get('part_type')

            if part_name == 'Contact':
                # Contatto - accedi alla variabile collegata
                source = self.connections.get((uid, 'operand'))
                if source:
                    expr = self._trace_from_source(source['uid'])
                    if part.get('negated'):
                        expr = LadExpression('not', left=expr)
                    return expr
                return LadExpression('var', operand='???')

            elif part_name == 'Coil':
                # Bobina - accedi a cosa la comanda
                source = self.connections.get((uid, 'in'))
                if source:
                    return self._trace_from_source(source['uid'])
                return LadExpression('var', operand='???')

            elif part_name in ['O', 'A', 'X', 'O_N', 'A_N', 'X_N']:
                # Gate logico - accedi ai due ingressi
                left = self.connections.get((uid, 'in1'))
                right = self.connections.get((uid, 'in2'))

                if left and right:
                    left_expr = self._trace_from_source(left['uid'])
                    right_expr = self._trace_from_source(right['uid'])

                    gate_map = {
                        'O': 'or', 'A': 'and', 'X': 'xor',
                        'O_N': 'nor', 'A_N': 'nand', 'X_N': 'xnor'
                    }
                    op_type = gate_map.get(part_name, 'or')

                    return LadExpression(op_type, left=left_expr, right=right_expr)

                return LadExpression('var', operand='???')

        return LadExpression('var', operand='???')
```

**Checklist**:
- [ ] Creare `lad_expression_builder.py`
- [ ] Implementare classe `LadExpression`
- [ ] Implementare classe `LadExpressionBuilder`
- [ ] Metodo `build_expression()` funzionale
- [ ] Metodo `to_scl()` per output

---

### Task 3.3: Integrare Expression Builder in lad_parser.py
**Tempo**: 1 ora

```python
# In lad_parser.py, aggiungi:

from lad_expression_builder import LadExpressionBuilder

class LADLogicParser:
    # ... codice esistente ...

    def _extract_lad_operations(self) -> List[Dict[str, str]]:
        """
        Estrae operazioni LAD ricostruendo espressioni booleane.

        Returns:
            Lista di {dest: variable, expr: expression_scl}
        """
        operations = []
        builder = LadExpressionBuilder(self.parts, self.connections)

        # Trova tutti i Coil (output)
        for uid, part in self.parts.items():
            if part.get('type') == 'Part' and part.get('part_type') == 'Coil':
                # Ricostruisci l'espressione per questo coil
                expr = builder.build_expression(uid)

                # Trova a quale variabile assegna
                dest_source = self.connections.get((uid, 'operand'))
                if dest_source:
                    dest_var = self.parts[dest_source['uid']].get('name', '???')
                    operations.append({
                        'dest': dest_var,
                        'expr': expr.to_scl()
                    })

        return operations

    def parse(self) -> Dict[str, Any]:
        """Parse FlgNet e ritorna operations ricostrutte."""
        # ... codice esistente per parts/wires ...

        # Nuovo: estrai operazioni LAD
        lad_operations = self._extract_lad_operations()

        return {
            'fb_calls': self._extract_fb_calls(),
            'lad_operations': lad_operations  # NUOVO
        }
```

**Checklist**:
- [ ] Import `LadExpressionBuilder`
- [ ] Metodo `_extract_lad_operations()` implementato
- [ ] Integration in `parse()`
- [ ] Return lad_operations nel result

---

### Task 3.4: Aggiornare fbfc_generator.py per Usare Operazioni LAD
**Tempo**: 1 ora

```python
# In fbfc_generator.py:

def _generate_network_region(self, network_num, network):
    """Genera REGION per network LAD con operazioni ricostruite."""
    title = f"Network {network_num}: {network.get('title', 'Unnamed')}"

    self.add_line(f'REGION "{title}"')
    self.indent()

    # Genera le operazioni LAD
    for operation in network.get('lad_operations', []):
        dest = operation['dest']
        expr = operation['expr']
        self.add_line(f"{dest} := {expr};")

    # Genera le chiamate FB se presenti
    for fb_call in network.get('fb_calls', []):
        self._generate_fb_call(fb_call)

    self.dedent()
    self.add_line('END_REGION')

def _generate_fb_call(self, fb_call):
    """Genera una chiamata FB."""
    instance = fb_call.get('instance_name', '???')
    name = fb_call.get('name', '???')

    self.add_line(f"#{instance}(")
    self.indent()

    # Parametri (completa quelli mancanti)
    params = fb_call.get('parameters', {})
    for param_name, param_value in params.items():
        self.add_line(f"{param_name} := {param_value},")

    self.dedent()
    self.add_line(");")
```

**Checklist**:
- [ ] Aggiornare `_generate_network_region()`
- [ ] Aggiungere metodo `_generate_fb_call()`
- [ ] Testare generazione operazioni LAD
- [ ] Verificare output non ha più `???` (o solo fallback)

---

### Task 3.5: Unit Test per Boolean Expression Builder
**Tempo**: 1 hora

**Nuovo file**: `tests/test_lad_expression_builder.py`

```python
import pytest
from lad_expression_builder import LadExpression, LadExpressionBuilder

def test_simple_variable():
    """Test semplice variabile."""
    expr = LadExpression('var', operand='MyVar')
    assert expr.to_scl() == 'MyVar'

def test_not_expression():
    """Test NOT."""
    inner = LadExpression('var', operand='MyVar')
    expr = LadExpression('not', left=inner)
    assert expr.to_scl() == 'NOT (MyVar)'

def test_and_expression():
    """Test AND."""
    left = LadExpression('var', operand='A')
    right = LadExpression('var', operand='B')
    expr = LadExpression('and', left=left, right=right)
    assert '(A AND B)' in expr.to_scl()

def test_complex_expression():
    """Test espressione complessa."""
    a = LadExpression('var', operand='A')
    b = LadExpression('var', operand='B')
    c = LadExpression('var', operand='C')

    # (A OR B) AND C
    or_expr = LadExpression('or', left=a, right=b)
    final = LadExpression('and', left=or_expr, right=c)

    scl = final.to_scl()
    assert 'A' in scl and 'B' in scl and 'C' in scl
    assert 'OR' in scl and 'AND' in scl

def test_builder_with_actual_network():
    """Test builder con network reale da Positioning_MOL_Machine_FB.xml."""
    # Parts e Wires dal Network 6 del file reale
    parts = {
        '21': {'type': 'Access', 'name': 'TON_NoPendingCmd.Q', 'scope': 'LocalVariable'},
        '22': {'type': 'Access', 'name': 'Sts.Standstill', 'scope': 'LocalVariable'},
        '28': {'type': 'Part', 'part_type': 'Contact'},
        '29': {'type': 'Part', 'part_type': 'Contact'},
        '31': {'type': 'Part', 'part_type': 'O', 'template_values': {'Card': '2'}},
        '35': {'type': 'Part', 'part_type': 'Coil'},
    }

    connections = {
        ('28', 'operand'): {'type': 'IdentCon', 'uid': '21'},
        ('28', 'out'): {'type': 'NameCon', 'uid': '29', 'name': 'in'},
        ('29', 'operand'): {'type': 'IdentCon', 'uid': '22'},
        ('29', 'out'): {'type': 'NameCon', 'uid': '31', 'name': 'in1'},
        ('35', 'in'): {'type': 'NameCon', 'uid': '31', 'name': 'out'},
    }

    builder = LadExpressionBuilder(parts, connections)
    expr = builder.build_expression('35')
    scl = expr.to_scl()

    # Dovrebbe contenere le variabili
    assert 'TON_NoPendingCmd.Q' in scl
    assert 'Sts.Standstill' in scl
```

**Checklist**:
- [ ] Creare `tests/test_lad_expression_builder.py`
- [ ] Test semplici variabili
- [ ] Test operazioni NOT/AND/OR
- [ ] Test espressioni complesse
- [ ] Test con network reale
- [ ] Tutti test passano

---

## Checkpoint 3: Sessione #3 Completata?

```bash
# Eseguire questi test:
pytest tests/test_lad_expression_builder.py -v
python main.py tests/fixtures/Positioning_MOL_Machine_FB.xml --output tests/output/

# Verificare nel file output:
grep "???" tests/output/Positioning_MOL_Machine_FB.scl
# Dovrebbe avere MENO di 20 occorrenze di ???
```

✅ **Success Criteria**:
- Boolean expression builder funzionante
- Operazioni LAD generate senza `???`
- Test su network reale passano
- Output SCL ha logica ricostruita

---

---

# 🎯 SESSIONE #4: Fix Duplicazione e FB Parameters

**Durata**: 2-3 ore
**Priorità**: 🟠 ALTA
**Complessità**: Media
**Prerequisiti**: Sessione #1-3 completate

## Task

### Task 4.1: Identify e Fix Duplicazione Istruzioni
**Tempo**: 45 min

**Problema**: Righe 217-218, 223-224 duplicano istruzioni

```bash
# Trovare cause nel codice:
grep -n "PosEdge\|PE\." fbfc_generator.py lad_parser.py
# Cercare dove viene aggiunta due volte la stessa istruzione
```

Ipotesi: La funzione che genera istruzioni iterates due volte la stessa lista.

```python
# Fix: Deduplica prima di generare
def _generate_instructions(self, instructions):
    """Genera istruzioni deduplicando."""
    seen = set()
    for instr in instructions:
        instr_str = str(instr)
        if instr_str not in seen:
            self.add_line(instr_str)
            seen.add(instr_str)
```

**Checklist**:
- [ ] Trovare causa duplicazione
- [ ] Aggiungere deduplica
- [ ] Testare su network
- [ ] Verif icare ogni riga appare una sola volta

---

### Task 4.2: Completare Estrazione Parametri FB Call
**Tempo**: 1 ora

**Problema**: Parametri `en`, `AxisCtrl`, `Config` sono `???`

```python
# In lad_parser.py:

def _extract_fb_calls(self) -> List[Dict[str, Any]]:
    """Extract FB calls with complete parameter mapping."""
    fb_calls = []

    # Trova tutti i Call elements
    for uid, part in self.parts.items():
        if part.get('type') != 'Part' or 'FB' not in part.get('part_type', ''):
            continue

        instance_name = part.get('instance_name', '???')
        part_type = part.get('part_type', '???')

        # Estrai TUTTI i parametri mappati
        parameters = self._extract_fb_parameters(uid, part_type)

        fb_calls.append({
            'instance': instance_name,
            'block_type': part_type,
            'parameters': parameters
        })

    return fb_calls

def _extract_fb_parameters(self, fb_uid, block_type):
    """Estrae parametri di una FB collegati via wires."""
    parameters = {}

    # Standard FB ports basate sul block_type
    ports = self._get_block_ports(block_type)

    for port_name in ports:
        # Cerca il wire collegato a questo ingresso
        source = self.connections.get((fb_uid, port_name))
        if source:
            # Traccia la fonte
            source_uid = source['uid']
            source_part = self.parts.get(source_uid)
            parameters[port_name] = source_part.get('name', '???')
        else:
            parameters[port_name] = '???'  # Fallback

    return parameters

def _get_block_ports(self, block_type):
    """Ritorna i nomi dei port standard per un block type."""
    # Questo va mappato da schema TIA Portal
    standard_ports = {
        'Ax': ['en', 'AxisCtrl', 'Config', 'HwLsMinus', 'HwLsPlus', ...],
        'Motor': ['en', 'MotorCtrl', 'ThermalProtectionA', ...],
        'TON': ['IN', 'PT', 'Q', 'ET'],
        # ... altri blocchi ...
    }
    return standard_ports.get(block_type, [])
```

**Checklist**:
- [ ] Metodo `_extract_fb_parameters()` implementato
- [ ] Metodo `_get_block_ports()` implementato
- [ ] Mappare port standard per blocchi comuni
- [ ] Testare su rete con FB call

---

### Task 4.3: Test Sessione #4
**Tempo**: 30 min

```bash
# Verificare output:
1. grep "???" tests/output/Positioning_MOL_Machine_FB.scl | wc -l
   # Dovrebbe essere < 5 (solo fallback)

2. grep -n "PE.PB_Minus := PosEdge" tests/output/*.scl
   # Dovrebbe apparire UNA VOLTA, non due

3. grep "#Ax(" tests/output/*.scl -A 3
   # I parametri dovrebbero avere valori, non ???

4. grep "#TON_" tests/output/*.scl -A 2
   # I parametri dovrebbero essere mappati
```

**Checklist**:
- [ ] ??? ridotti drasticamente
- [ ] Nessuna duplicazione
- [ ] Parametri FB mappati
- [ ] Output leggibile

---

## Checkpoint 4: Sessione #4 Completata?

✅ **Success Criteria**:
- Meno di 5 `???` restanti (solo fallback)
- Zero duplicazioni di istruzioni
- Parametri FB mappati correttamente
- Output SCL quasi pronto per uso

---

---

# 🎯 SESSIONE #5: Testing Completo + Validation

**Durata**: 3-4 ore
**Priorità**: 🟠 ALTA
**Complessità**: Media
**Prerequisiti**: Sessione #1-4 completate

## Task

### Task 5.1: Suite di Unit Test Completa
**Tempo**: 1 ora

Creare test per ogni componente:
- [ ] Security tests (XXE, encoding)
- [ ] Parser tests (XML parsing)
- [ ] LAD expression tests
- [ ] Generator tests (output format)
- [ ] Integration tests (full pipeline)

```bash
pytest tests/ -v --cov=xml_to_scl
```

**Checklist**:
- [ ] Copertura test > 80%
- [ ] Tutti test passano
- [ ] Coverage report generato

---

### Task 5.2: Confronto Output Prima/Dopo
**Tempo**: 1 ora

```bash
# Convertire con versione backup
cp fbfc_generator.py.backup fbfc_generator.py
python main.py tests/fixtures/Positioning_MOL_Machine_FB.xml --output tests/output/old/

# Convertire con versione corretta
cp fbfc_generator.py.fixed fbfc_generator.py
python main.py tests/fixtures/Positioning_MOL_Machine_FB.xml --output tests/output/new/

# Confrontare
diff -u tests/output/old/Positioning_MOL_Machine_FB.scl \
          tests/output/new/Positioning_MOL_Machine_FB.scl > /tmp/diff.patch

# Analizzare diff
```

**Checklist**:
- [ ] Diff generato
- [ ] Analizzare cambiamenti principali
- [ ] Verificare che nuova versione migliore

---

### Task 5.3: Validazione SCL Syntax
**Tempo**: 1.5 ore

```bash
# Validare output SCL contro TIA Portal syntax
# (Usando regex o parser custom per IEC 61131-3)

python -m pytest tests/test_scl_syntax_validation.py -v
```

**Cosa validare**:
- [ ] Blocchi BEGIN/END bilanciate
- [ ] REGION/END_REGION bilanciate
- [ ] Indentazione consistente
- [ ] Dichiarazioni VAR valide
- [ ] Operatori riconosciuti
- [ ] Funzioni SCL valide

**Checklist**:
- [ ] Scrivere validator SCL
- [ ] Tutti output passano validation
- [ ] Errori di syntax riportati

---

### Task 5.4: Performance Test
**Tempo**: 1 hora

```bash
# Testare conversione su file grande
time python main.py /path/to/large/project.xml --output tests/output/

# Monitorare memoria
python -m memory_profiler main.py /path/to/large/project.xml --output tests/output/
```

**Checklist**:
- [ ] Conversione < 5 sec per file medio (< 10MB XML)
- [ ] Memoria < 500MB
- [ ] Nessun memory leak

---

## Checkpoint 5: Sessione #5 Completata?

✅ **Success Criteria**:
- Test coverage > 80%
- Tutti test passano
- Output valida sintassi SCL
- Performance accettabile

---

---

# 🎯 SESSIONE #6: Documentazione + Rollout

**Durata**: 2 ore
**Priorità**: 🟡 MEDIA
**Complessità**: Bassa
**Prerequisiti**: Sessione #1-5 completate

## Task

### Task 6.1: Aggiornare README e Documentazione
**Tempo**: 45 min

- [ ] Aggiornare `README.md` con nuove capacità
- [ ] Documentare bug fixes in `CHANGELOG.md`
- [ ] Creare guide per:
  - [ ] Usando Boolean Expression Builder
  - [ ] Troubleshooting output
  - [ ] Performance optimization

### Task 6.2: Code Cleanup
**Tempo**: 30 min

- [ ] Rimuovere file `.backup`
- [ ] Rimuovere commenti debug
- [ ] Aggiornare docstring
- [ ] Black formatting

```bash
black xml_to_scl/ --line-length 100
```

### Task 6.3: Release e Deployment
**Tempo**: 45 min

```bash
# Creare versione
git tag v1.1.0-fixed
git push origin v1.1.0-fixed

# Deploy to production
# ... procedure deployment ...
```

- [ ] Git commit per ogni sessione
- [ ] Tag di versione creato
- [ ] Documentazione publicata
- [ ] Release notes scritti

## Checkpoint 6: Completato!

✅ **Final Success Criteria**:
- ✅ Tutti 4 bug critici risolti
- ✅ Test coverage > 80%
- ✅ Documentazione aggiornata
- ✅ Code clean e pronto per production

---

---

# 📈 Tracking Progress

## Metriche di Completamento

| Sessione | Status | % Completamento | Bugs Risolti |
|----------|--------|-----------------|--------------|
| #1 | 🟡 In Progress | 0% | XXE, ErrorHandling |
| #2 | ⬜ Pending | 0% | REGION Nesting |
| #3 | ⬜ Pending | 0% | Boolean Expressions |
| #4 | ⬜ Pending | 0% | Dedup, FB Params |
| #5 | ⬜ Pending | 0% | Testing |
| #6 | ⬜ Pending | 0% | Docs, Rollout |

## Tempo Tracato

```
Sessione #1: ___ / 2-3h
Sessione #2: ___ / 3-4h
Sessione #3: ___ / 4-6h
Sessione #4: ___ / 2-3h
Sessione #5: ___ / 3-4h
Sessione #6: ___ / 2h

TOTALE: ___ / 16-23h
```

---

---

# 🎯 Note Importanti

## Dipendenze tra Sessioni

```
#1 (Security) ──┐
                ├──> #2 (Architecture) ──┐
#2 completata ──┘                        ├──> #3 (LAD Logic)
                                         │
                                         ├──> #4 (Polish)
                                         │
                                         ├──> #5 (Testing)
                                         │
                                         └──> #6 (Release)
```

## Backout Plan

Se una sessione fallisce:
1. **Sessione #1**: Riprovare, è semplice
2. **Sessione #2**: Usare `fbfc_generator.py.backup`
3. **Sessione #3**: Eliminare `lad_expression_builder.py`, revertare parser
4. **Sessione #4**: Simpler fix, riprovare
5. **Sessione #5**: Skippa test falliti, vai a #6
6. **Sessione #6**: Ricomincia da #5

## Validazione tra Sessioni

Dopo **ogni** sessione:
```bash
# Verificare che non sia peggiorato
python main.py tests/fixtures/MotorS.xml --output tests/output/test.scl
grep "???" tests/output/test.scl
# Dovrebbe avere MENO ??? della sessione precedente
```

---

Questo piano è pronto per l'esecuzione. Puoi iniziare dalla **Sessione #1** quando sei pronto!

