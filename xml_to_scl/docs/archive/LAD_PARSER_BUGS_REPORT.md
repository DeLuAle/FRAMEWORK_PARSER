# 🔴 Report: Bug Critici nel LAD Parser

Data: 2025-12-24
File: `Positioning_MOL_Machine_FB.xml` (FB con 31 networks LAD)

---

## 📋 Sommario Esecutivo

Il **LAD Parser** ha **4 bug critici** che causano:
1. **Nesting infinito di REGION** (32+ livelli)
2. **Tutte le espressioni booleane rimpiazzate con `???`**
3. **Duplicazione di istruzioni** (ogni riga x2)
4. **Parametri FB call incompleti**

**Impatto**: ❌ Output SCL **completamente inutilizzabile**

---

## 🐛 Bug #1: NESTING INFINITO DI REGION

### Sintomo
```scl
BEGIN
   REGION "Network 1: Init"
      REGION "Network 2: Reset"
         REGION "Network 3: Actual Position"
            ... 32 livelli di nesting! ...
                                    REGION "Network 45: HMI Status"
                                       IF NOT InitDone THEN ... END_IF;
                                    END_REGION
                                 END_REGION
                              ...
                           END_REGION
                        END_REGION
                     END_REGION
                  END_REGION
               END_REGION
            END_REGION
         END_REGION
      END_REGION
   END_REGION
END
```

### Causa Radice
Nella **fbfc_generator.py** (linea dove genera le REGION):
- Il generatore **NON collassa i networks** in sequenza parallela
- Invece, **annida tutte le REGION** una dentro l'altra
- Ogni network diventa una REGION dentro il network precedente

### Soluzione Richiesta
```python
# SBAGLIATO (Attuale):
for network in networks:
    indent_level += 1
    generate_region(network, indent_level)
    # Non chiude la REGION!

# CORRETTO (Dovrebbe essere):
for network in networks:
    indent_level = 1  # Reset al livello base
    generate_region(network, indent_level)
    # Chiude la REGION prima del prossimo network
```

**File**: `fbfc_generator.py` (linea ~150-200)

---

## 🐛 Bug #2: ESPRESSIONI BOOLEANE DIVENTANO "???"

### Sintomo
```scl
// Linea 169 - Dovrebbe avere la logica LAD
Ctrl.StopDueDoorOpeningRequest := ((((??? OR ???) AND CIn.Manager...

// Linea 174 - IF condition senza operandi
IF ??? THEN
   Ctrl.StopInPhase := FALSE;
```

### Causa Radice
Nel **lad_parser.py**, la funzione `_extract_fb_calls()` non ricostruisce l'espressione booleana dalla struttura Parts/Wires.

**Cosa manca**:
1. **`_build_expression_from_wires()`** - Funzione per ricostruire l'espressione booleana
2. **Mapping dei contatti (Contact)** alle variabili reali
3. **Mapping dei gate logici (O per OR, A per AND)** alle operazioni
4. **Valutazione della topologia del circuito ladder**

### Esempio del Problema
La rete LAD ha questa struttura nel XML (linee 669-743):
```xml
<Parts>
  <Access UId="21">TON_NoPendingCmd.Q</Access>
  <Access UId="22">Sts.Standstill</Access>
  <Access UId="23">Ctrl.StopDueDoorOpeningRequest</Access>
  <Part Name="Contact" UId="28" />         <!-- Contatto 1 -->
  <Part Name="Contact" UId="29" />         <!-- Contatto 2 -->
  <Part Name="O" UId="31">                 <!-- Gate OR con 2 ingressi -->
    <TemplateValue Name="Card">2</TemplateValue>
  </Part>
  <Part Name="Coil" UId="35" />            <!-- Output (assegnazione) -->
</Parts>

<Wires>
  <Wire UId="36">
    <Powerrail />
    <NameCon UId="28" Name="in" />         <!-- Contatto 1 connesso al rail -->
    <NameCon UId="30" Name="in" />         <!-- Contatto 3 connesso al rail -->
  </Wire>
  <Wire UId="37">
    <IdentCon UId="21" />                  <!-- Fonte: TON_NoPendingCmd.Q -->
    <NameCon UId="28" Name="operand" />    <!-- Va a Contact 1 -->
  </Wire>
  <Wire UId="38">
    <NameCon UId="28" Name="out" />        <!-- Output Contact 1 -->
    <NameCon UId="29" Name="in" />         <!-- Input contatto 2 -->
  </Wire>
  ...
  <Wire UId="49">
    <NameCon UId="34" Name="out" />        <!-- Output contatto finale -->
    <NameCon UId="35" Name="in" />         <!-- Input della bobina (assignment) -->
  </Wire>
</Wires>
```

**La logica dovrebbe essere**:
```scl
Ctrl.StopDueDoorOpeningRequest :=
    (TON_NoPendingCmd.Q AND Sts.Standstill AND Ctrl.StopDueDoorOpeningRequest) OR
    (CIn.Manager.EnableStopDoorOpeningReq AND ZSI.Door_NormalStop AND NOT ZSI.Door_Opened)
```

**Cosa fa il parser attualmente**: Estrae solo i nomi delle variabili, NON ricostruisce l'espressione dai wires.

**File**: `lad_parser.py` (linea 298+, la funzione `_extract_fb_calls()` è INCOMPLETA)

---

## 🐛 Bug #3: DUPLICAZIONE DELLE ISTRUZIONI

### Sintomo
```scl
// Linea 217-218
PE.PB_Minus := PosEdge(DataIn.PB.Bwd_Minus);
PE.PB_Minus := PosEdge(DataIn.PB.Bwd_Minus);  // ❌ Duplicata

// Linea 223-224
PE.B_Preset := PosEdge(HMI.B_Preset);
PE.B_Preset := PosEdge(HMI.B_Preset);        // ❌ Duplicata
```

### Causa Radice
Nel **fbfc_generator.py**, quando elabora le istruzioni LAD estratte:
- **Scorre due volte** gli stessi elementi
- Oppure **non filtra i duplicati** prima di generare

Probabilmente in una funzione tipo:
```python
def generate_assignments(self, lad_operations):
    for op in lad_operations:
        self.add_line(f"{op.dest} := {op.source};")
        # BUG: Se la lista contiene duplicati, genera duplicati!
```

**File**: `fbfc_generator.py` (funzione che genera istruzioni LAD)

---

## 🐛 Bug #4: FB CALL CON PARAMETRI INCOMPLETI

### Sintomo
```scl
// Linea 425-436 - SBAGLIATO
#Ax(
   en := ???,                   // ❌ Non estratta
   AxisCtrl := ???,             // ❌ Non estratta
   Config := ???,               // ❌ Non estratta
   HwLsMinus := DataIn.LS_Minus,
   HwLsPlus := DataIn.LS_Plus,
   ...
);
```

### Cosa Dovrebbe Essere
```scl
#Ax(
   en := CIn.Manager.Control_ON,
   AxisCtrl := Ax.AxisCtrl,
   Config := Config.Ax,
   HwLsMinus := DataIn.LS_Minus,
   HwLsPlus := DataIn.LS_Plus,
   ...
);
```

### Causa Radice
Nel **lad_parser.py**, la funzione `_extract_fb_calls()` che estrae le chiamate FB:
1. **Non mappia i parametri EN** (enabled signal)
2. **Non estrae i parametri input** da accessi collegati al blocco
3. **Lascia i parametri come `???` placeholder**

**File**: `lad_parser.py` (linea 298+)

---

## 📊 Analisi della Portata

| Bug | Linee Interessate | Gravità | % Output |
|-----|-------------------|---------|----------|
| Bug #1: Nesting | 103-434 | 🔴 CRITICO | 100% |
| Bug #2: ??? placeholders | 169+, multiple | 🔴 CRITICO | 95% |
| Bug #3: Duplicazione | 217+, multiple | 🟠 ALTA | 30% |
| Bug #4: FB params | 425, 458 | 🟠 ALTA | 5% |

**Totale di righe interessate**: ~330 righe su 600 (55%)

---

## 🔧 Passi Necessari per Risolvere

### Priorità 1 - CRITICO (Architettura)

#### 1.1 Ridisegnare la struttura della generazione REGION
```python
# fbfc_generator.py
def generate_logic(self, lad_networks):
    """
    Genera le reti LAD come REGION PARALLELE, non annidate.
    """
    for i, network in enumerate(lad_networks):
        self.add_line(f'REGION "Network {network.title}"')
        self.indent()

        # Genera le istruzioni della rete
        for instruction in network.instructions:
            self.add_line(instruction)

        self.dedent()
        self.add_line('END_REGION')
        self.add_line('')  # Linea vuota tra reti
```

#### 1.2 Implementare la ricostruzione dell'espressione booleana
```python
# lad_parser.py
def _build_expression_from_wires(self, coil_uid):
    """
    Ricostruisce l'espressione booleana seguendo i wires
    dal coil indietro fino alle variabili di ingresso.

    Algoritmo:
    1. Trova il coil con UId = coil_uid
    2. Traccia l'ingresso del coil attraverso i wires
    3. Ricostruisci l'albero dell'espressione
    4. Trasforma in notazione infissa SCL
    """
    pass
```

#### 1.3 Implementare il parsing dei gate logici
```python
# lad_parser.py
LOGIC_GATES = {
    'O': 'OR',
    'A': 'AND',
    'X': 'XOR',
    'O_N': 'NOR',
    'A_N': 'NAND',
    'X_N': 'XNOR'
}

def _get_gate_operation(self, gate_name):
    return LOGIC_GATES.get(gate_name, 'UNKNOWN')
```

### Priorità 2 - ALTA (Correctness)

#### 2.1 Implementare deduplica delle istruzioni
```python
# fbfc_generator.py
def generate_logic(self, lad_operations):
    """Genera istruzioni LAD deduplicando."""
    seen = set()
    for op in lad_operations:
        op_str = str(op)
        if op_str not in seen:
            self.add_line(op_str)
            seen.add(op_str)
```

#### 2.2 Completare l'estrazione dei parametri FB
```python
# lad_parser.py
def _extract_fb_parameters(self, call_uid, call_info):
    """
    Estrae tutti i parametri di una chiamata FB mappando
    i wires agli ingressi del blocco.
    """
    parameters = {}

    # Per ogni ingresso del blocco
    for port in call_info.input_ports:
        # Trova il wire connesso a questo ingresso
        source = self._find_source(call_uid, port)
        if source:
            parameters[port] = source.symbol
        else:
            parameters[port] = '???'  # Solo come ultimo ricorso

    return parameters
```

---

## 📝 Conclusione

Il **LAD Parser è fondamentalmente incompleto**. Non è un semplice bug di implementazione, ma manca l'**intero algoritmo** di:
1. Ricostruzione di espressioni booleane da topologia ladder
2. Generazione corretta della struttura REGION
3. Mapping completo dei parametri FB

**Raccomandazione**: Prima di fare conversioni su blocchi LAD/FBD complessi, questi bug vanno risolti. Altrimenti è meglio usare SCL nativo (che funziona perfettamente come visto nei network con StructuredText).

---

## 📎 File Coinvolti

- **lad_parser.py** - Incompleto (Bug #2, #4)
- **fbfc_generator.py** - Logica di generazione errata (Bug #1, #3)
- **fbfc_parser.py** - Delega al LAD parser (Bug indiretto)
- **main.py** - Instrada ai parser corretti (no bug diretto)

---

## 🎯 Test Case

**File test**: `Positioning_MOL_Machine_FB.xml`
**Network test**: Network 6 (linea 624-743) - Semplice OR di contatti
**Output attuale**: 169-170 (doppi `???`)
**Output atteso**: `Ctrl.StopDueDoorOpeningRequest := (TON_NoPendingCmd.Q OR Sts.Standstill OR Ctrl.StopDueDoorOpeningRequest) AND CIn.Manager.EnableStopDoorOpeningReq AND ZSI.Door_NormalStop AND NOT ZSI.Door_Opened;`

