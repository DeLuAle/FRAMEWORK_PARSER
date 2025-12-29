# PLC Framework Patterns - Documentazione Completa

**Versione:** 2.0  
**Data:** 2025-12-28  
**Autore:** Alessandro (PM Forming)  
**Fonte:** Codice reale verificato (Area.scl, FeedMachine_FB.scl, DecoilersHRot_FB.scl, etc.)

---

## Indice

1. [Architettura Generale](#1-architettura-generale)
2. [Software Units e Areas_ITF](#2-software-units-e-areas_itf)
3. [L5 - Area Manager](#3-l5---area-manager)
4. [L4 - Zone Manager](#4-l4---zone-manager)
5. [L3 - Aggregator (Multi-Device)](#5-l3---aggregator-multi-device)
6. [L2 - Single-Actuator Machine](#6-l2---single-actuator-machine)
7. [L1 - Device](#7-l1---device)
8. [UDT Standard](#8-udt-standard)
9. [Safety Interfaces (ZSI / DSI)](#9-safety-interfaces-zsi--dsi)
10. [Checklist Implementazione](#10-checklist-implementazione)

---

# 1. Architettura Generale

## Gerarchia Livelli

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  L5 - AREA MANAGER                                                          â”‚
â”‚  â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                                                           â”‚
â”‚  Gestisce: Modo (Man/Aut), Ciclo (Start/Stop), Broadcast AreaInterface      â”‚
â”‚  FB: Area.scl + Area_CALL.scl                                               â”‚
â”‚  Output: AreaInterface (broadcast a tutti)                                  â”‚
â”‚  Input: MachinesStatus (aggregato da zone)                                  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  L4 - ZONE MANAGER                                                          â”‚
â”‚  â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                                                           â”‚
â”‚  Gestisce: Coordinamento macchine zona, sequenze processo                   â”‚
â”‚  FB: ZoneName_FB.scl + ZoneName_CALL.scl                                    â”‚
â”‚  Input: AreaInterface                                                       â”‚
â”‚  Output: COut.Machine_Manager per ogni macchina                             â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  L3 - AGGREGATOR (Multi-Device Coordinator)                                 â”‚
â”‚  â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                                 â”‚
â”‚  Gestisce: Coordinamento piÃ¹ L2 per operazioni complesse                    â”‚
â”‚  FB: MachineName_FB.scl + MachineName_CALL.scl                              â”‚
â”‚  Contiene: Istanze statiche di L2 Machines                                  â”‚
â”‚  Pattern: ExtEnable per sequenze, ExternalAlarms per Aborting               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  L2 - SINGLE-ACTUATOR MACHINE                                               â”‚
â”‚  â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                                               â”‚
â”‚  Gestisce: Coordinamento unico device, arbitraggio Man/Aut                  â”‚
â”‚  FB: MachineName_FB.scl                                                     â”‚
â”‚  Pattern: Control_ON, CheckNext/ExtEnable, Stop Handling, CtrlSafe          â”‚
â”‚  Contiene: Istanza statica di L1 Device                                     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  L1 - DEVICE (Attuatore Base)                                               â”‚
â”‚  â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•                                                â”‚
â”‚  Gestisce: Logica attuatore singolo (valvola, asse, motore)                 â”‚
â”‚  FB: Valve_FB.scl, OnOffAxis_FB.scl, Motor_FB.scl                           â”‚
â”‚  Pattern: Ctrl/Sts UDT, Timer, Alarm detection                              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Pattern FB + CALL (Tutti i Livelli)

```
MachineName/
â”œâ”€â”€ MachineName_FB.scl      # Logica principale
â”œâ”€â”€ MachineName_CALL.scl    # FC wrapper: I/O mapping, aggregazione
â””â”€â”€ MachineName_PERS.db     # DB persistente (Par, Pers) - RETAIN
```

| Componente | ResponsabilitÃ  |
|------------|----------------|
| **FB** | Logica, coordinamento, allarmi, state machine |
| **FC CALL** | Mapping I/O fisici, aggregazione status, dispatch comandi |
| **DB PERS** | Parametri HMI (Par), stati persistenti (Pers) - RETAIN |

## Composizione Gerarchica (Static Instances)

```scl
// L3 contiene L2 come istanze statiche
FUNCTION_BLOCK "Aggregator_FB"
VAR
    Machine1 : SingleActuatorMachine_FB;  // L2 istanza
    Machine2 : SingleActuatorMachine_FB;  // L2 istanza
END_VAR

// L2 contiene L1 come istanza statica
FUNCTION_BLOCK "SingleActuatorMachine_FB"
VAR
    Device : Valve_FB;  // L1 istanza
END_VAR
```

**Vantaggi:**
- Un solo DB contiene tutta la gerarchia
- Accesso diretto: `L3.Machine1.Device.Sts`
- RETAIN propagato automaticamente
- Struttura visibile in TIA Portal

---

# 2. Software Units e Areas_ITF

## Principio Architetturale

TIA Portal **Software Units** garantiscono isolamento tra aree. Il DB `Areas_ITF` nell'Orchestrator Ã¨ l'**unico punto di scambio dati**.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              1_Orchestrator_Safety (Software Unit)              â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚
â”‚  â”‚                    Areas_ITF (DB)                        â”‚   â”‚
â”‚  â”‚  Struttura CUSTOM per progetto                           â”‚   â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚
â”‚                         â–²                                       â”‚
â”‚            R/W da tutte le Software Units                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
        â–²               â–²               â–²               â–²
        â”‚               â”‚               â”‚               â”‚
   â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”
   â”‚ 31_Area01â”‚   â”‚ 32_Area02 â”‚   â”‚ 33_Area03 â”‚   â”‚ 3x_AreaNN â”‚
   â”‚ (isolata)â”‚   â”‚ (isolata) â”‚   â”‚ (isolata) â”‚   â”‚ (isolata) â”‚
   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Regole Fisse

| Regola | Descrizione |
|--------|-------------|
| **Isolamento** | Ogni Area = Software Unit separata |
| **No accesso diretto** | Area01 NON puÃ² accedere a DB di Area02 |
| **Punto comune** | `Areas_ITF` in Orchestrator = unico scambio |
| **R/W condiviso** | Tutte le unit possono R/W su Areas_ITF |

## Struttura ITF (Custom per Progetto)

```scl
DATA_BLOCK "Areas_ITF"
    A01 : ITF_A01;           // Interfaccia Area 01
    A02 : ITF_A02;           // Interfaccia Area 02
    A03 : ITF_A03;           // Interfaccia Area 03
    AG  : ITF_AG;            // Area General (aggregato)
    Prod : ITF_ProductionMng; // Production Manager / MES
END_DATA_BLOCK
```

### Template ITF_Axx (tipico)

```scl
TYPE "ITF_Axx"
   STRUCT
      AreaInterface : AreaInterface;           // Broadcast modi/ciclo
      ZoneManager_MachineInterface : MachineInterface; // Stato zona principale
      Infeed_REQ_ON : Bool;                    // Richiesta Infeed
      PB : Struct                              // Pulsanti cross-area
         MBx_PB_Reset : Bool;
         MBx_AreaYY_PB_Start : Bool;
         MBx_AreaYY_PB_Stop : Bool;
      END_STRUCT;
      Safety_SuperUser : Struct                // Reset safety da HMI
         PbSafetyReset : Bool;
         SgnSafetyReset : Bool;
      END_STRUCT;
      Safety_EntryEnable : Struct              // Consenso ingresso zone
         Z01 : Bool;
         Z02 : Bool;
      END_STRUCT;
      Safety_CtrlSafe : Struct                 // CtrlSafe per ogni device
         HU_xxx_Motor : Bool;
         Sinamics_xxx : Bool;
      END_STRUCT;
      Doors_Closed : Bool;                     // Porte zona chiuse
      Production_Running : Bool;               // Stato produzione
      MaterialPresence : Bool;                 // Presenza materiale
      FreeBool : Array[1..16] of Bool;         // Espansione futura
      FreeLReal : Array[1..16] of LReal;
      FreeDINT : Array[1..16] of DInt;
   END_STRUCT;
END_TYPE
```

### ITF_AG - Area General

```scl
TYPE "ITF_AG"
   STRUCT
      Infeed_Running : Bool;           // Alimentatore S120 attivo
      CC1_PorteAperte : Bool;          // Cabina comando aperta
      Area01 : MachineInterface;       // Aggregato Area01
      Area02 : MachineInterface;       // Aggregato Area02
      Area03 : MachineInterface;       // Aggregato Area03
      FreeBool : Array[1..16] of Bool;
   END_STRUCT;
END_TYPE
```

### Uso nel Codice

```scl
// Area01 legge pulsanti da Area02
Area01.DataIn.PbStart := MB1_PbStart 
                         OR Areas_ITF.A02.PB.MB2_Area01_PB_Start;

// Area01 scrive il suo stato
Areas_ITF.AG.Area01.Aborting := MachinesStatus.AtLeastOneMachineIsAborting;

// Area01 legge stato globale
Infeed_OK := Areas_ITF.AG.Infeed_Running;
```

---

# 3. L5 - Area Manager

## Scopo

L'**Area Manager** Ã¨ il livello piÃ¹ alto. Gestisce:
- Modo operativo (Man/0/Aut)
- Ciclo automatico (Start/Stop)
- Broadcast `AreaInterface` a tutte le zone
- Raccolta `MachinesStatus` aggregato
- Interfaccia operatore (pulsantiera + tower lamp)

## Configurazione Standard Pulsantiera

| Elemento | Input | Sempre Presente |
|----------|-------|-----------------|
| **Sel Man/0/Aut** | SelMan, SelAut | âœ… |
| **PB Start** | PbStart | âœ… |
| **PB Stop** | PbStop | âœ… |
| **PB Ack/Rst** | PbAckRst | âœ… |
| **PB StopProgrammed** | PbStopProgrammed | âŒ Opzionale |

### DataIn Multi-Source (da CALL)

```scl
// Selettori: physical OR HMI SuperUser
Area.DataIn.SelMan := (NOT Priority AND MB1_SelMan) 
                      OR (Priority AND SuperUser.SelManAut = 1);

// PbStart: da MB1 OR HMI OR altre aree
Area.DataIn.PbStart := MB1_PbStart 
                       OR HMI.SuperUser.PbStart 
                       OR Areas_ITF.A02.PB.MB2_Area01_PB_Start;

// PbAckRst: HMI OR main panel OR local boxes
Area.DataIn.PbAckRst := SuperUser.PbReset 
                        OR MB1_Pb_ResetAlarms 
                        OR LB101.PB.ResetAlarms;
```

**SuperUser.Priority:** Per commissioning/debug da HMI - bypassa pulsantiera fisica.

## Tower Lamp

| Lampada | Segnale | Comportamento |
|---------|---------|---------------|
| Ready (Bianca) | lampReady | Fisso: pronto per start |
| Cycle (Bianca) | lampCycle | Vedi sotto |
| Warning (Arancione) | LampWarningPresence | Warning attivo |
| Alarm (Rossa) | LampAlarmPresence | Allarme attivo |
| Horn | horn | Durante countdown start |

### lampCycle (da codice verificato)

```scl
DataOut.lampCycle := 
    (CheckStartCnd AND MachinesReady AND Clock_500MS)  // Starting: 500ms
    OR CycleStarted 
    OR CycleOn                                          // Ciclo: Fisso
    OR (StopInPhase AND Clock_1S)                       // Stop fase: 1s
    OR (StopProgrammed AND Clock_2S);                   // Stop progr: 2s
```

## Trigger Stop (VERIFICATO)

### StopInPhase

```scl
IF DataIn.PbStop                                    // Trigger 1: PB Stop
   OR MachinesStatus.AtLeastOneMachineIsAborting    // Trigger 2: Aborting
   OR ForceStopInPhase                              // Trigger 3: Forzatura
   OR CycleStopImmediately THEN                     // Trigger 4: EStop
    CycleStopInPhase := TRUE;
END_IF;
```

### StopProgrammed

```scl
IF (PosEdge(PbStart) AND CycleOn)    // Trigger 1: Start durante ciclo
   OR DataIn.PbStopProgrammed        // Trigger 2: PB dedicato
   OR ForceStopProgrammed THEN       // Trigger 3: Forzatura
    CycleStopProgrammed := TRUE;
END_IF;
```

## Sequenza Start Ciclo

```
PbStart premuto (Area in Aut, macchine Ready)
        â”‚
        â–¼ Delay 2s (horn attivo, lamp 500ms)
        â”‚
        â”œâ”€ Se rilasciato prima â†’ annullato
        â”‚
        â–¼ TON_DelayPbStart.Q = TRUE
        â”‚
CycleStarted := TRUE
        â”‚
        â–¼ Rilascio PbStart
        â”‚
CycleOn := TRUE â†’ AreaInterface.Cycle broadcast
```

## MachinesStatus Aggregazione

```scl
// AND aggregation (tutte devono essere TRUE)
AllMachineAutReady := Machine1.AutReady AND Machine2.AutReady AND ...;
AllMachineAckStopInPhase := Machine1.AckStop AND Machine2.AckStop AND ...;

// OR aggregation (basta una TRUE)
AtLeastOneMachineIsAborting := Machine1.Aborting OR Machine2.Aborting OR ...;
AtLeastOneAlrPresence := Machine1.AlarmsPresence OR Machine2.AlarmsPresence OR ...;
```

## HMI Status Codes

| Codice | Stato |
|--------|-------|
| 01 | Emergency |
| 02 | Selettore in 0 |
| 11 | Manuale |
| 21 | Automatico - Non pronto |
| 22 | Automatico - Pronto |
| 31 | Ciclo in avvio |
| 32 | Ciclo attivo |
| 41 | Stop immediato |
| 42 | Stop in fase |
| 43 | Stop programmato |

## Message Handling Pattern

```scl
// Array mapping con base index per gruppo
AlrIndex := 20;  // CoilHandling group
Area_Messages.A.Msg[AlrIndex + 0] := Machine.Alarm.Error1;

AlrIndex := 110; // Decoiler1 group
Area_Messages.A.Msg[AlrIndex + 0] := Decoiler1.Alarm.Feed.BrakeTimeOut;

// FB Manager call
Area_Msg_Alarms(
    Ack := Area.DataIn.PbAckRst,
    Messages := Area_Messages.A.Msg,
    MessagesHMI := Area_Messages.A.Hmi,
    MessageCount => HMI.AlarmsNumber
);
```

---

# 4. L4 - Zone Manager

## Scopo

Il **Zone Manager** coordina piÃ¹ macchine (L2/L3) di una zona per:
- Sequenze di processo
- Distribuzione `EnableStopXxx` selettiva
- Raccolta `MachineInterface` aggregato
- Gestione `Control_ON` per ogni macchina

## Pattern Stop Sequencing

```scl
REGION "Stop In Phase Sequencing"
    // Fase 1: Ferma alimentazione subito
    IF AreaInterface.StopInPhase THEN
        Feeder.CIn.Manager.EnableStopInPhase := TRUE;
    END_IF;
    
    // Fase 2: Ferma Pinch dopo che Feeder Ã¨ fermo
    IF AreaInterface.StopInPhase 
       AND Feeder.MachineInterface.AckStopInPhase THEN
        Pinch.CIn.Manager.EnableStopInPhase := TRUE;
    END_IF;
    
    // Fase 3: Ferma Decoiler per ultimo
    IF AreaInterface.StopInPhase 
       AND Pinch.MachineInterface.AckStopInPhase THEN
        Decoiler.CIn.Manager.EnableStopInPhase := TRUE;
    END_IF;
END_REGION
```

## Varianti StopProgrammed

| Variante | Comportamento |
|----------|---------------|
| **Svuotamento linea** | Ferma ingresso, materiale esce, ogni macchina si ferma quando vuota |
| **Dopo taglio** | Completa pezzo, taglia, scarica, poi stop |
| **Fallback** | Come StopInPhase |

---

# 5. L3 - Aggregator (Multi-Device)

## Scopo

L'**L3 Aggregator** coordina piÃ¹ L2 che devono lavorare in sequenza.

**Esempi:**
- DecoilersHRot: Rotation + Pivot + Translation
- Decoiler: Feed + Jaws + Coupling + SnubberLift + SnubberRoll
- Straightener: Feed + Lift_Entry + Lift_Exit

## FC CALL Structure

```scl
FUNCTION "MachineName_CALL" : Void
BEGIN
    REGION "DataIn"           // Input fisici + pulsanti
    REGION "CIn - Manager"    // Comandi da L4
    REGION "CIn - Pressure"   // PressureRunning (HU OK)
    REGION "DSI"              // Safety per device
    REGION "Drive"            // Infeed, AccessPoint, AxisID
    REGION "HW ID"            // Hardware IDs telegram
    REGION "Machine Manager"  // Chiamata FB
    REGION "Data Out"         // Uscite fisiche
END_FUNCTION
```

## CIn.Manager Ricorsivo

```scl
// Stop passthrough (SEMPRE diretto)
Device1.Cin.Manager.EnableStopInPhase := CIn.Manager.EnableStopInPhase;

// Control_ON esteso con comandi interni
Device1.Cin.Manager.Control_ON := CIn.Manager.Control_ON 
                                  OR Device1.Cin.Manager.Rest 
                                  OR Device1.Cin.Manager.Work;
```

**Principio:** L3 puÃ² estendere Control_ON, ma Stop sempre passato direttamente.

## Sequenza via ExtEnable

```scl
// Rotation puÃ² muoversi solo se Pivot Ã¨ a Rest
Rotation.Cin.Rest_ExtEnable := CIn.Manager.ChangeDecoilerEnable 
                               AND CIn.CoilCar_OutOfLine 
                               AND Pivot.COut.Rest;

// Pivot puÃ² muoversi solo se Rotation Ã¨ fermo
Pivot.Cin.Work_ExtEnable := CIn.Manager.ChangeDecoilerEnable 
                            AND Rotation.COut.Standstill;
```

**Pattern:** L3 usa ExtEnable per dipendenze tra L2 senza state machine esplicita.

## Allarmi L3 â†’ L2 (ExternalAlarms)

```scl
// L3 genera allarme per relazione tra macchine
Alarm.Rotation_NotInPosition := TON.Q AND NOT Ls_Ok;

// L3 inietta verso L2 specifica
Rotation.CIn.ExternalAlarms := Alarm.Rotation_NotInPosition;

// L2 tratta ExternalAlarms come allarme proprio â†’ Aborting
MachineInterface.Aborting := InternalAlarms OR CIn.ExternalAlarms;
```

**Principio:** L2 non sa perchÃ© Ã¨ in allarme, sa solo che deve andare in Aborting. La diagnostica Ã¨ in L3.

## MachineInterface Aggregation

FC helper `MachineInterface_2_To_1`:

```scl
MachineInterface := MachineInterface_2_To_1(
    MachineInterface_1 := Device1.MachineInterface,
    MachineInterface_2 := Device2.MachineInterface,
    AdditionalAlarms := Alarm.L3_Alarm,
    AdditionalWarnings := Warning.L3_Warning
);
```

| Campo | Aggregazione |
|-------|--------------|
| AutReady | AND + NOT AdditionalAlarms |
| Aborting | OR + AdditionalAlarms |
| AckStopXxx | AND |
| MotionsStandStill | AND |
| AlarmsPresence | OR + AdditionalAlarms |

## Dual MachineInterface (Boundary Machine)

Per macchine al confine tra 2 aree (es. Loop/Ansa):

```scl
FUNCTION_BLOCK "Loop1_FB"
VAR_OUTPUT
    MachineInterfaceEntry : MachineInterface;  // â†’ Area01
    MachineInterfaceExit : MachineInterface;   // â†’ Area02
END_VAR
```

---

# 6. L2 - Single-Actuator Machine

## Scopo

La **Single-Actuator Machine** gestisce un unico device con:
- Arbitraggio Man/Aut (Control_ON)
- Handshake CheckNext/ExtEnable
- Stop coordinati
- Coordinamento Safety (CtrlSafe)

## Pattern 1: Control_ON Arbitration

```scl
// Condizioni
ManualEnabled := AreaInterface.Man AND NOT CIn.Manager.Control_ON;
AutoEnabled := CIn.Manager.Control_ON;

// Arbitraggio
IF AutoEnabled THEN
    Cmd.Fwd := CIn.Manager.Fwd;
    Cmd.Vel := CIn.Manager.Vel;
ELSIF ManualEnabled THEN
    Cmd.Fwd := HMI_Ctrl.JogFwd;
    Cmd.Vel := Par.ManualVelocity;  // VelocitÃ  ridotta
ELSE
    Cmd.Fwd := FALSE;
END_IF;
```

**Regola:** Control_ON ha prioritÃ  su Area.Man.

## Pattern 2: CheckNext / ExtEnable

```scl
// 1. CheckNext = richiesta movimento
COut.Bwd_CheckNext := Ctrl.Bwd_Man OR Ctrl.Bwd_Aut;

// 2. Condizioni complete
Sts.Bwd_Cnd := Sts.Gen_Cnd
               AND Ax.AxisSts.MoveMinusPermitted
               AND CIn.Bwd_ExtEnable;  // â† DA L3/L4

// 3. Comando = CheckNext AND Condizioni
Ax.AxisCtrl.MoveMinus := COut.Bwd_CheckNext AND Sts.Bwd_Cnd;

// 4. Warning se ExtEnable non arriva
TON_MissingCnd(
    IN := Standstill AND CheckNext AND NOT Cnd,
    PT := Config.DelayMissingCondition  // es. T#3s
);
Warning.MissingCnd_Bwd := TON_MissingCnd.Q;
```

## Pattern 3: Stop Handling

```scl
// LATCH Stop In Phase
IF NOT AreaInterface.StopInPhase THEN
    Ctrl.StopInPhase := FALSE;
ELSIF CIn.Manager.EnableStopInPhase THEN
    Ctrl.StopInPhase := TRUE;  // LATCH
END_IF;

// Blocco comandi
Sts.Gen_Cnd := NOT Ctrl.StopDueDoorOpeningRequest
               AND NOT Ctrl.StopInPhase
               AND NOT Ctrl.StopProgrammed
               AND NOT Ctrl.StopAborting
               AND NOT DSI.SafeStop;

// Feedback
MachineInterface.AckStopInPhase := Ctrl.StopInPhase AND MotionsStandStill;
```

**Principio:** L2 non decide quando fermarsi - il Manager (L3/L4) abilita lo stop.

## Pattern 4: CtrlSafe

```scl
// Timer no pending commands
TON_NoPendingCmd(
    IN := NOT CheckNext_Fwd AND NOT CheckNext_Bwd AND NOT Moving,
    PT := T#500MS
);

// CtrlSafe = "ho bisogno di restare attivo"
COut.CtrlSafe := NOT TON_NoPendingCmd.IN                    // Comandi pendenti
                 OR (COut.CtrlSafe AND Ax.Enabled)          // LATCH asse abilitato
                 OR (Control_ON AND NOT StopDoorReq);       // Auto senza stop porte
```

**Uso:** Safety usa CtrlSafe per decidere quando applicare SafeStop.

## Pattern 5: Alarm â†’ Aborting

```scl
// TUTTI gli allarmi diventano Aborting (quasi sempre immediato)
MachineInterface.Aborting := Alarm.TimeoutFeedback 
                              OR Alarm.PositionError
                              OR Alarm.SafetyFault
                              OR CIn.ExternalAlarms;  // Da L3

MachineInterface.AlarmsPresence := MachineInterface.Aborting;
```

---

# 7. L1 - Device

## Tipologie

| Family | Device Type | Caratteristiche |
|--------|-------------|-----------------|
| motion | linear_servo | MC_MoveAbsolute, positioning |
| motion | linear_onoff | PosFbk_ITF, no servo |
| motion | servo_drive | TAx_DriveInterface |
| actuator | motor_contactor | RunPermitted, contactor feedback |
| pneumatic | cylinder_double | Extend + Retract |
| pneumatic | valve | Open + Close |
| pneumatic | gripper | Open + Close + Grip |

## Pattern Motor

```scl
// RunPermitted (da codice Motor.scl)
RunPermitted := NOT AlarmPresence 
                AND NOT MotorCtrl.SafeStop
                AND PressureRunning;  // HU pressure OK

// Contactor control
ContactorCmd := RunPermitted AND MotorCtrl.Run;

// Alarm con timeout feedback
TON_ContactorFbk(IN := ContactorCmd AND NOT ContactorFbk, PT := T#2s);
Alarm.ContactorTimeout := TON_ContactorFbk.Q;
```

## PressureRunning

Segnale da Hydraulic Unit che indica **pressione olio OK**.

```
HU Running â†’ PressureRunning = TRUE â†’ Abilita comando solenoidi valvole
```

Senza pressione, comandare il solenoide Ã¨ inutile.

---

# 8. UDT Standard

## AreaInterface (L5 â†’ tutti)

```scl
TYPE "AreaInterface"
   STRUCT
      EStop : Bool;              // Emergenza attiva
      Man : Bool;                // Modo manuale
      Aut : Bool;                // Modo automatico
      Cycle : Bool;              // Ciclo attivo
      StopInPhase : Bool;        // Richiesta stop in fase
      StopProgrammed : Bool;     // Richiesta stop programmato
      RstAlarms : Bool;          // Comando reset allarmi
      ManOneShot : Bool;         // Fronte cambio modo Man
      AutOneShot : Bool;         // Fronte cambio modo Aut
      CycleOneShot : Bool;       // Fronte avvio ciclo
      CheckAutReady : Bool;      // Verifica AutReady
   END_STRUCT;
END_TYPE
```

## MachineInterface (L2 â†’ L3/L4/L5)

```scl
TYPE "MachineInterface"
   STRUCT
      AutReady : Bool;           // Pronta per automatico
      Aborting : Bool;           // Allarme critico
      AckStopInPhase : Bool;     // Conferma stop fase
      AckStopProgrammed : Bool;  // Conferma stop programmato
      MotionsStandStill : Bool;  // Ferma + no comandi pendenti
      AlarmsPresence : Bool;     // Allarmi presenti
      WarningPresence : Bool;    // Warning presenti
   END_STRUCT;
END_TYPE
```

## MachineStatus (aggregato in L5)

```scl
TYPE "MachineStatus"
   STRUCT
      AtLeastOneMachineIsAborting : Bool;
      AllMachineAutReady : Bool;
      AllMachineAckStopInPhase : Bool;
      AllMachineAckStopProgrammed : Bool;
      AtLeastOneWngPresence : Bool;
      AtLeastOneAlrPresence : Bool;
   END_STRUCT;
END_TYPE
```

---

# 9. Safety Interfaces (ZSI / DSI)

## Gerarchia Safety

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    ZONA DI SICUREZZA (es. Z01)                  â”‚
â”‚                                                                 â”‚
â”‚  ZSI (Zone Safety Interface)                                    â”‚
â”‚  â”œâ”€â”€ Door_NormalStop      â† Fase 1: richiesta accesso          â”‚
â”‚  â”œâ”€â”€ Door_SafeStop        â† Fase 2: SS1/SS2 attivo             â”‚
â”‚  â”œâ”€â”€ Door_EntryEnable     â† Fase 3: porta sbloccabile          â”‚
â”‚  â””â”€â”€ Door_Opened          â† Fase 4: porta aperta               â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”       â”‚
â”‚  â”‚  Machine A    â”‚  â”‚  Machine B    â”‚  â”‚  Machine C    â”‚       â”‚
â”‚  â”‚               â”‚  â”‚               â”‚  â”‚               â”‚       â”‚
â”‚  â”‚  DSI Device1  â”‚  â”‚  DSI Device1  â”‚  â”‚  DSI Device1  â”‚       â”‚
â”‚  â”‚  DSI Device2  â”‚  â”‚  DSI Device2  â”‚  â”‚               â”‚       â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

| Livello | Interface | Scope |
|---------|-----------|-------|
| **Zona** | ZSI | Tutte le macchine della zona |
| **Device** | DSI | Singolo attuatore o gruppo |

## udt_ZoneSafetyInterface (ZSI)

```scl
TYPE "udt_ZoneSafetyInterface"
   STRUCT
      Door_NormalStop : Bool;    // Fase 1: richiesta accesso
      Door_SafeStop : Bool;      // Fase 2: SS1/SS2 attivo
      Door_EntryEnable : Bool;   // Fase 3: porta sbloccabile
      Door_Opened : Bool;        // Fase 4: porta aperta
   END_STRUCT;
END_TYPE
```

## udt_DeviceSafetyInterface (DSI)

```scl
TYPE "udt_DeviceSafetyInterface"
   STRUCT
      SafeStop : Bool;           // Fase 1: arresto sicuro in corso
      PowerEnable : Bool;        // Fase 2: consenso potenza
      DevicesInSafeState : Bool; // Fase 3: sicuro raggiunto
   END_STRUCT;
END_TYPE
```

## Sequenza Apertura Porte

```
Door_NormalStop = TRUE (richiesta accesso)
        â”‚
        â–¼ L3/L4 attiva EnableStopDoorOpeningReq
        â”‚
Macchine si fermano (StopDueDoorOpeningRequest)
        â”‚
        â–¼ CtrlSafe = FALSE (tutte le macchine)
        â”‚
Safety applica SafeStop (DSI.SafeStop = TRUE)
        â”‚
        â–¼ Energia decade
        â”‚
DevicesInSafeState = TRUE
        â”‚
        â–¼ Door_EntryEnable = TRUE
        â”‚
Porta sbloccabile â†’ Door_Opened = TRUE
```

---

# 10. Checklist Implementazione

## L5 Area Manager

- [ ] DataIn multi-source (physical + HMI + cross-area)
- [ ] Gestione modi Man/0/Aut con EStop
- [ ] Sequenza start con delay 2s + horn
- [ ] Trigger StopInPhase (4 trigger)
- [ ] Trigger StopProgrammed (3 trigger)
- [ ] MachinesStatus aggregazione (AND/OR)
- [ ] Tower lamp comportamenti
- [ ] HMI Status codes
- [ ] Message handling array

## L3 Aggregator

- [ ] FC CALL con tutte le REGION
- [ ] CIn.Manager passthrough (Stop sempre diretto)
- [ ] Control_ON esteso con comandi interni
- [ ] ExtEnable per sequenze L2
- [ ] Stati parziali â†’ COut aggregato
- [ ] ExternalAlarms â†’ L2 per Aborting
- [ ] MachineInterface aggregazione

## L2 Single-Actuator Machine

- [ ] Control_ON arbitration (Auto prioritÃ )
- [ ] CheckNext / ExtEnable handshake
- [ ] Warning MissingCondition con timeout
- [ ] Stop LATCH con EnableStop da Manager
- [ ] Gen_Cnd blocca tutti i comandi
- [ ] AckStopXxx = Stop AND Standstill
- [ ] CtrlSafe formula completa
- [ ] Alarm â†’ Aborting (quasi sempre immediato)

## DB Persistente

- [ ] DB separato con RETAIN
- [ ] Par: parametri HMI
- [ ] Pers: stati persistenti (Homed, counters)
- [ ] Passato via VAR_IN_OUT

## Safety

- [ ] ZSI ricevuto dalla zona appartenenza
- [ ] DSI per ogni device
- [ ] CtrlSafe raccolto per Safety PLC
- [ ] Safety_CtrlSafe in Areas_ITF

---

# Appendice: Anti-Pattern

## âŒ ERRATO

```scl
// Manuale sovrascrive automatico
IF HMI_Ctrl.JogFwd THEN
    Cmd.Fwd := TRUE;  // Pericoloso! Ignora Control_ON
END_IF;

// Stop senza abilitazione Manager
IF AreaInterface.StopInPhase THEN
    Ctrl.StopInPhase := TRUE;  // Tutte le macchine si fermano!
END_IF;

// CtrlSafe solo da comandi
COut.CtrlSafe := NOT NoPendingCmd.IN;  // Oscillazioni tra comandi!
```

## âœ… CORRETTO

```scl
// Arbitraggio esplicito
IF ManualEnabled AND HMI_Ctrl.JogFwd THEN
    Cmd.Fwd := TRUE;
END_IF;

// Stop solo se Manager abilita
IF NOT AreaInterface.StopInPhase THEN
    Ctrl.StopInPhase := FALSE;
ELSIF CIn.Manager.EnableStopInPhase THEN
    Ctrl.StopInPhase := TRUE;
END_IF;

// CtrlSafe formula completa
COut.CtrlSafe := NOT NoPendingCmd.IN
                 OR (COut.CtrlSafe AND Ax.Enabled)
                 OR (Control_ON AND NOT StopDoorReq);
```

---

**Fine Documento**

*Generato da analisi codice reale - PM Forming Framework*
