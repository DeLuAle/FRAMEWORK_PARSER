# HMI Buttons e ButtonsSafe - Pattern Framework

**Estratto da:** MBK_2/DOCUMENTAZIONE/01_Area01
**Versione:** 1.0
**Data:** 2025-12-29

---

## 1. Architettura Due Sistemi

Il framework implementa **due sistemi paralleli** per comandi manuali:

| Sistema | Posizione Operatore | Requisiti Safety | VelocitÃ  |
|---------|---------------------|------------------|----------|
| **HMI** | Fuori barriere | Barriere CHIUSE | Normale |
| **ButtonsSafe** | Dentro zone | Bimanuale + chiave manutenzione | SLS_VEL (6 m/min) |

---

## 2. Sistema HMI - ButtonsHMIDecoder

### 2.1 Architettura

```
HMI Screen â†’ CodeReq (Int) â†’ ButtonsHMIDecoder_FB â†’ Device
                                    â†“
                            JOG+/JOG- (pulpito)
```

### 2.2 Interface ButtonsHMIDecoder

```scl
VAR_INPUT
    ButtonMinus : Bool;      // Pulsante JOG -
    ButtonPlus : Bool;       // Pulsante JOG +
    OpEnabled : Bool;        // Device pronto (CheckNext OK)
    OpRunning : Bool;        // Device in esecuzione
    OpDone : Bool;           // Operazione completata
    CodeReq : Int;           // Codice richiesto da HMI
END_VAR

VAR_OUTPUT
    Code : Int;              // Codice attivo (dopo stabilitÃ  50ms)
    OperationMinus : Bool;   // Comando MINUS attivo
    OperationPlus : Bool;    // Comando PLUS attivo
    Lamp : Bool;             // Lampada selezione
END_VAR

VAR_STATIC
    SavedCode : Int;         // Codice salvato (latch)
    tonStable : TON_TIME;    // Timer stabilitÃ  50ms
    PE_Aux_ButtonMinus : Bool;
    PE_Aux_ButtonPlus : Bool;
END_VAR
```

### 2.3 Logica Principale

```scl
// 1. StabilitÃ  codice (anti-glitch HMI)
IF CodeReq = SavedCode THEN
    tonStable(IN := TRUE, PT := T#50MS);
    IF tonStable.Q THEN
        Code := CodeReq;
    END_IF;
ELSE
    tonStable(IN := FALSE);
    SavedCode := CodeReq;
END_IF;

// 2. Edge detection JOG (impulso su fronte)
OperationMinus := ButtonMinus AND NOT PE_Aux_ButtonMinus;
OperationPlus := ButtonPlus AND NOT PE_Aux_ButtonPlus;
PE_Aux_ButtonMinus := ButtonMinus;
PE_Aux_ButtonPlus := ButtonPlus;

// 3. Lampada
Lamp := OpEnabled OR OpRunning OR OpDone;
```

### 2.4 Codici HMI Standard (Area01)

| Range | Gruppo | Esempi |
|-------|--------|--------|
| 1001-1009 | Hydraulic Units | HU_AREA01, HU_DECOILER |
| 1011-1017 | Decoiler InLine | FEED, JAWS, COUPLING, SNUBBER |
| 1021-1027 | Decoiler OutLine | (stessi comandi aspo standby) |
| 1031-1035 | Decoiler Rotation | ROTATION, PIVOT, TRASLATION |
| 1041-1042 | Peeler | LIFT, EXTENSION |
| 1051-1054 | Straightener | MOVE, LIFT_ENTRY/EXIT, COUPLING |
| 1061-1066 | JointBox | CUT, TORCH, CLAMPS, WELDER, WELD_CYCLE |
| 1071-1073 | JB PinchRoll | MOVE, LIFT, COUPLING |
| 1081 | Loop | LOOP1 |

---

## 3. Sistema Safe - Buttons2Hands

### 3.1 Architettura

```
Safety PLC â†’ TwoHandsPushed (Bool) â†’ Buttons2Hands_FB
                                           â†“
                    Pulsanti selezione â†’ Operations[] â†’ Device
                    Lampade â† Lamps[]
```

### 3.2 UDT Buttons2Hands

```scl
TYPE "Buttons2Hands"
   STRUCT
      // Input
      Items : Int;                          // Numero operazioni (1-32)
      Activation : Bool;                    // Abilitazione pannello
      TwoHandsPushed : Bool;                // Entrambe mani premute
      Buttons : Array[1..32] of Bool;       // Pulsanti selezione
      Enables : Array[1..32, 1..32] of Bool;// Matrice interlock
      OpEnabled : Array[1..32] of Bool;     // Operazione pronta (CheckNext)
      OpRunning : Array[1..32] of Bool;     // Operazione in esecuzione
      OpDone : Array[1..32] of Bool;        // Operazione completata
      
      // Output
      ResetAlarms : Bool;                   // Comando reset allarmi
      Operations : Array[1..32] of Bool;    // Comandi operazioni attivi
      Lamps : Array[1..32] of Bool;         // Lampade selezione
      
      // Static
      ButtonsSelected : Array[1..32] of Bool; // Selezioni latched
      ButtonsOneShot : Array[1..32] of Bool;  // Edge detection
   END_STRUCT;
END_TYPE
```

### 3.3 Macchina a Stati

```scl
// CASO 1: NOT Activation â†’ RESET tutto
IF NOT Activation THEN
    FOR i := 1 TO Items DO
        Operations[i] := FALSE;
        ButtonsSelected[i] := FALSE;
    END_FOR;

// CASO 2: NOT TwoHandsPushed â†’ SELEZIONE (toggle pulsanti)
ELSIF NOT TwoHandsPushed THEN
    FOR i := 1 TO Items DO
        Operations[i] := FALSE;  // Nessuna esecuzione
        // Edge detection pulsante
        IF Buttons[i] AND NOT ButtonsOneShot[i] THEN
            ButtonsSelected[i] := NOT ButtonsSelected[i];  // Toggle
        END_IF;
        ButtonsOneShot[i] := Buttons[i];
    END_FOR;

// CASO 3: TwoHandsPushed AND Activation â†’ ESECUZIONE
ELSIF TwoHandsPushed AND Activation THEN
    FOR i := 1 TO Items DO
        Operations[i] := ButtonsSelected[i] AND OpEnabled[i];
        // Verifica conflitti
        FOR j := 1 TO Items DO
            IF i <> j AND ButtonsSelected[j] THEN
                IF NOT Enables[i, j] THEN
                    Operations[i] := FALSE;  // CONFLITTO
                END_IF;
            END_IF;
        END_FOR;
    END_FOR;
END_IF;
```

### 3.4 Matrice Enables (Interlock)

La matrice `Enables[i,j]` definisce quali operazioni possono eseguire **contemporaneamente**:

```scl
// Esempio: LB111 - Decoiler + Snubber possono muoversi insieme
Enables[DECOILER_FWD, SNUBBER_ROLL_FWD] := TRUE;
Enables[DECOILER_BWD, SNUBBER_ROLL_BWD] := TRUE;
Enables[SNUBBER_LIFT_DOWN, DECOILER_FWD] := TRUE;
Enables[SNUBBER_LIFT_DOWN, DECOILER_BWD] := TRUE;

// Operazioni mutuamente esclusive (stesso attuatore)
// Enables[DECOILER_FWD, DECOILER_BWD] := FALSE; // default
```

### 3.5 Lampade Safe (PB_Lamp)

```scl
// Stati lampada
Lamp := 
    (Selected AND NOT Request)                    // ON: Selezionato
    OR (Selected AND Request AND Running)         // ON: In esecuzione
    OR (Selected AND Request AND NOT Done AND Sys.Clock_1S)   // BLINK 1Hz: In attesa
    OR (Selected AND Request AND Done AND Sys.Clock_250MS);   // BLINK 4Hz: Completato
```

---

## 4. Pattern ButtonsSafe_LBxxx_FB

### 4.1 Struttura Standard

```scl
FUNCTION_BLOCK "ButtonsSafe_LBxxx_FB"
VAR_INPUT
    Reset_OthersPBs_Activation_IN : Bool;
END_VAR

VAR_OUTPUT
    Reset_OthersPBs_Activation_OUT : Bool;
END_VAR

VAR_STATIC
    PbPanel : "Buttons2Hands";
    PB : Struct
        // Operazioni specifiche pannello
        Op1 : Bool;
        Op2 : Bool;
        // ...
    END_STRUCT;
END_VAR

VAR_CONSTANT
    ITEMS : Int := N;        // Numero operazioni
    OP1 : Int := 1;          // Indice operazione 1
    OP2 : Int := 2;          // Indice operazione 2
    // ...
END_VAR
```

### 4.2 Network Standard (8+)

| Network | Funzione | Contenuto |
|---------|----------|-----------|
| 0 | **Interlocks** | Inizializza matrice Enables[i,j] |
| 1 | **Buttons** | PbPanel.Buttons[i] := Tag_Pb_xxx |
| 2 | **OpEnabled** | PbPanel.OpEnabled[i] := Device.CheckNext |
| 3 | **OpRunning** | PbPanel.OpRunning[i] := Device.Running |
| 4 | **OpDone** | PbPanel.OpDone[i] := Device.AtPosition |
| 5 | **Main** | Chiamata Buttons2Hands FB |
| 6 | **Safe Buttons** | PB.Op := PbPanel.Operations[i] |
| 7 | **Lamps** | Tag_Lp_xxx := PbPanel.Lamps[i] |
| 8 | **Reset Others** | Logica reset pannelli concorrenti |

### 4.3 Esempio Completo: LB111 (12 operazioni)

```scl
VAR_CONSTANT
    ITEMS : Int := 12;
    COILCAR_UP : Int := 1;
    COILCAR_DOWN : Int := 2;
    COILCAR_FWD : Int := 3;
    COILCAR_BWD : Int := 4;
    JAWS_OPEN : Int := 5;
    JAWS_CLOSE : Int := 6;
    DECOILER_FWD : Int := 7;
    DECOILER_BWD : Int := 8;
    SNUBBER_LIFT_UP : Int := 9;
    SNUBBER_LIFT_DOWN : Int := 10;
    SNUBBER_ROLL_FWD : Int := 11;
    SNUBBER_ROLL_BWD : Int := 12;
END_VAR

// Network 0: Matrice interlock
Enables[DECOILER_BWD, SNUBBER_ROLL_BWD] := TRUE;
Enables[DECOILER_FWD, SNUBBER_ROLL_FWD] := TRUE;
Enables[SNUBBER_LIFT_DOWN, DECOILER_FWD] := TRUE;
Enables[SNUBBER_LIFT_DOWN, DECOILER_BWD] := TRUE;
// ... (simmetria)

// Network 2: OpEnabled (dinamico in base a Decoiler InLine)
IF DecoilersHRot.COut.Decoiler1_InLine THEN
    PbPanel.OpEnabled[JAWS_OPEN] := Decoiler2.COut.Jaws.Work_CheckNext;
    // ... Decoiler2 ops
ELSIF DecoilersHRot.COut.Decoiler2_InLine THEN
    PbPanel.OpEnabled[JAWS_OPEN] := Decoiler1.COut.Jaws.Work_CheckNext;
    // ... Decoiler1 ops
END_IF;
```

---

## 5. Safety Interface

### 5.1 F_DB (Safety Database)

```scl
// Ogni pannello bimanuale ha un record in F_DB
F_DB.LB111.SafeMotion : Bool;   // TwoHandsPushed validato da Safety PLC
F_DB.LB112.SafeMotion : Bool;
// ...

// Porte zone
F_DB.D02.OK : Bool;   // Porta Decoiler1 OK
F_DB.D03.OK : Bool;   // Porta Decoiler2 OK
```

### 5.2 Condizioni Abilitazione Safety (F-LAD)

```f-lad
A01_Sel_SetUp = 1           // Chiave manutenzione
    AND F_DB.D03.OK = TRUE  // Porta zona OK
    AND LB112_Button_L      // Pulsante sinistro
    AND LB112_Button_R      // Pulsante destro
    AND F_DB.A01_Estop = TRUE
        â†’ TwoHand_FB(LB112).Enable := TRUE
```

### 5.3 Mutua Esclusione Pannelli

```scl
// Network 8: Reset altri pannelli quando uno Ã¨ attivo
Reset_OthersPBs_Activation_OUT := FALSE;
FOR i := 1 TO ITEMS DO
    IF PbPanel.Buttons[i] OR PbPanel.Operations[i] THEN
        Reset_OthersPBs_Activation_OUT := TRUE;
        EXIT;
    END_IF;
END_FOR;

// Ogni pannello riceve Reset_OthersPBs_Activation_IN
IF Reset_OthersPBs_Activation_IN THEN
    Activation := FALSE;  // Disabilita questo pannello
END_IF;
```

---

## 6. Pattern Device Side (Ricezione Comandi)

### 6.1 Integrazione in Machine FB

```scl
// L2 Machine riceve comandi da HMI e Safe
REGION "Manual Commands"
    // HMI decoder output
    IF A01_HMI.MB1.Code = HMI_CODE_DECOILER_FEED THEN
        Ctrl.Man.Fwd := A01_HMI.MB1.OperationPlus;
        Ctrl.Man.Bwd := A01_HMI.MB1.OperationMinus;
    END_IF;
    
    // Safe button output
    Ctrl.Man.Fwd := Ctrl.Man.Fwd OR LB111.PB.Decoiler_Fwd;
    Ctrl.Man.Bwd := Ctrl.Man.Bwd OR LB111.PB.Decoiler_Bwd;
    
    // OR con altri pannelli safe che controllano stesso device
    Ctrl.Man.Fwd := Ctrl.Man.Fwd OR LB112.PB.Decoiler_Fwd;
    Ctrl.Man.Bwd := Ctrl.Man.Bwd OR LB131.PB.Decoiler_Fwd;
END_REGION
```

### 6.2 CheckNext per OpEnabled

```scl
// Machine COut espone CheckNext per ButtonsSafe
COut.Feed.Fwd_CheckNext := Gen_Cnd 
    AND NOT Alarm.Any
    AND (Control_ON OR AreaInterface.Man);

COut.Feed.Bwd_CheckNext := Gen_Cnd 
    AND NOT Alarm.Any
    AND (Control_ON OR AreaInterface.Man);
```

---

## 7. VelocitÃ  con Safe Buttons

### 7.1 SLS_VEL Automatica

```scl
// In SpeedMachine_FB / PositioningMachine_FB
IF ZSI.Door_Opened OR DSI.SafeStop THEN
    Ctrl.Vel := MIN(Ctrl.Vel, Config.SLS_VEL);  // Es: 6 m/min
END_IF;
```

### 7.2 ExtraLowSpeed (20%)

```scl
IF CoilHandling.COut.Gen.ExtraLowSpeedSelection THEN
    Ctrl.Vel := Ctrl.Vel * (Par.ExtraLowSpeed_Percentage / 100.0);
END_IF;
```

---

## 8. Checklist Implementazione

### ButtonsSafe_LBxxx_FB

- [ ] Definire costanti ITEMS e indici operazioni
- [ ] Configurare matrice Enables[i,j] per operazioni compatibili
- [ ] Mappare Buttons[] a tag I/O fisici
- [ ] Collegare OpEnabled[] a CheckNext dei device
- [ ] Collegare OpRunning[] a stati Running dei device
- [ ] Collegare OpDone[] a stati AtPosition dei device
- [ ] Chiamare Buttons2Hands con TwoHandsPushed da F_DB
- [ ] Estrarre Operations[] verso struct PB
- [ ] Mappare Lamps[] a tag I/O fisici
- [ ] Implementare Reset_OthersPBs per mutua esclusione

### Integrazione Device

- [ ] Esporre CheckNext nel COut
- [ ] OR comandi Man da tutti i pannelli Safe abilitati
- [ ] Applicare SLS_VEL quando porte aperte / SafeStop

---

## Fonti

- `ButtonsSafe_LB101_FB.scl` - Pattern base 2 operazioni
- `ButtonsSafe_LB111_FB.scl` - Pattern completo 12 operazioni
- `Area01_Comandi_Manuali_HMI_Safe.md` - Documentazione operatore
- `Buttons2Hands.xml` (parsing) - FB generico gestione bimanuale
- `ButtonsHMIDecoder.xml` (parsing) - FB decoder HMI
