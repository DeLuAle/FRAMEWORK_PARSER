#!/usr/bin/env python3
"""Update PositioningMachine JSON with complete Optional Features documentation"""
import json

json_path = r"c:\Projects\FRAMEWORK_PARSER\JSON_integrazione\PositioningMachine_L1_L2_L3_semantic_v3.json"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Replace Optional_Features section with complete analysis
data['L2_PositioningMachine']['Optional_Features'] = {
    "description": "Procedure opzionali gestite da Config, eseguite automaticamente da L2",
    "L3_responsibility": "L3 aspetta COut.AxisInOperation=TRUE senza intervento",
    
    "EncoderSelection": {
        "description": "Cambio encoder motore ↔ encoder misura (measuring wheel)",
        "config": "Config.Ax.OptionON_EncoderSelection",
        "trigger": {
            "when": "Manager.SelectMotorEncoder XOR ActiveEncoder",
            "condition": "Man mode AND Standstill AND NoPendingCmd"
        },
        "sequence": [
            "Status 0: IDLE - Wait Execute command",
            "Status 1: Force AxisPowerOff (timeout 10s)",
            "Status 2: Call MC_SETSENSOR with encoder number (timeout 1s)",
            "Status 3: Wait MC_SETSENSOR.Done (timeout 1s)",
            "Status 4: Verify encoder change succeeded",
            "Status 5: DONE - Release power"
        ],
        "persistence": "Pers_Data.AxisEncoderSelection_OK",
        "side_effects": "Forces Pers_Data.AxisReloadPostion_OK := FALSE (must re-home)",
        "motor_encoder": "Encoder on motor shaft (high resolution)",
        "mwheel_encoder": "Encoder on measuring wheel (load-side, material tracking)",
        "alarms": ["TOut_AxisPowerRemoving", "TOut_WaitCndEncoderChange", "TOut_WaitDoneEncoderChange", "Error_MC_SetSensor", "Error_NoEncoderChange"],
        "L3_note": "Used for multi-material systems (different wheel diameters)",
        "bypass_if_disabled": "Config.OptionON=FALSE → Pers_Data.AxisEncoderSelection_OK := TRUE"
    },
    
    "WritePar": {
        "description": "Scrittura parametri Technology Object runtime (11 parametri)",
        "config": "Config.Ax.OptionON_ParameterChange",
        "trigger": {
            "when": "CIn.TOParameters.DataPresence AND parameters differ from TO",
            "condition": "Man mode AND Standstill AND NoPendingCmd AND EncoderSelection_OK"
        },
        "parameters_list": {
            "EncoderInverseDirection": "Inverte senso encoder",
            "MotorInverseDirection": "Inverte senso motore",
            "LoadGearNumerator": "Rapporto riduzione numeratore",
            "LoadGearDenominator": "Rapporto riduzione denominatore",
            "MechanicsLeadScrew": "Passo vite mm/giro",
            "EncoderDistancePerRevolution": "Distance per revolution encoder (measuring wheel)",
            "DynamicsLimitsMaxVelocity": "Velocità massima dinamica",
            "DynamicsLimitsVelocity": "Velocità default",
            "ControlLoop_Kv": "Guadagno proporzionale anello posizione",
            "ControlLoop_Kpc": "Precontrollo posizione",
            "ControlLoop_Vtc": "Costante tempo velocità"
        },
        "sequence": [
            "Status 0: IDLE",
            "Status 1: Force AxisPowerOff (timeout 3s)",
            "Status 2-12: Write each parameter sequentially (timeout 1s each)",
            "Status 13: Verify all writes successful",
            "Status 14: MC_ResetHW (axis restart, timeout 60s)",
            "Status 15: DONE"
        ],
        "write_method": "WRIT_DBL function (runtime write to TO DB)",
        "persistence": "Pers_Data.AxisParameters_OK",
        "side_effects": "Forces Pers_Data.AxisReloadPostion_OK := FALSE (must re-home)",
        "validation": "All parameters > 0 (except bools), enforced before execution",
        "L3_responsibility": "Provide CIn.TOParameters.Data from recipe/product DB",
        "use_case": "Different products with different mechanics (different lead screw pitch, gear ratios)",
        "bypass_if_disabled": "Config.OptionON=FALSE → Pers_Data.AxisParameters_OK := TRUE"
    },
    
    "AutoReloadPosition": {
        "description": "Ricarica posizione da persistent memory @ startup (surrogate homing)",
        "config": "Config.Ax.OptionON_AutoReloadPosition",
        "trigger": {
            "when": "NOT Pers_Data.AxisReloadPostion_OK",
            "auto_triggers": ["PLC startup", "After EncoderSelection", "After WritePar"],
            "condition": "Man mode AND Standstill AND EncoderSelection_OK AND Parameters_OK"
        },
        "sequence": [
            "Status 0: IDLE",
            "Status 1: Wait HomingPermitted (Ctrl_ForcePosCtrl if in velocity mode, timeout 10s)",
            "Status 2: Execute MC_HOME with Ctrl_ReloadPosAx = Pers_Data.ActualPosition (timeout 10s)",
            "Status 3: DONE - Set Pers_Data.AxisReloadPostion_OK := TRUE"
        ],
        "modulo_axis_handling": {
            "check": "IF Pers_Data.ActualPosition within [Modulo.StartValue, Modulo.Length]",
            "valid": "Use Pers_Data.ActualPosition",
            "invalid": "Use 0.0 (safe default)"
        },
        "persistence": "Pers_Data.ActualPosition updated ogni ciclo se Homed=TRUE",
        "reset_trigger": "Se Ax.Homed=FALSE → Pers_Data.AxisReloadPostion_OK := FALSE",
        "L3_note": "Evita homing fisico su limit switch - startup rapido",
        "bypass_if_disabled": "Config.OptionON=FALSE → Pers_Data.AxisReloadPostion_OK := TRUE",
        "benefits": ["No limit switch required", "Faster startup", "No mechanical wear"]
    },
    
    "ManPreset": {
        "description": "Set posizione manuale da HMI (operator preset)",
        "config": "Config.Ax.OptionON_ManPreset",
        "trigger": {
            "when": "HMI.B_Preset positive edge",
            "condition": "Man mode AND Standstill AND EncoderSelection_OK AND Parameters_OK"
        },
        "sequence": [
            "Status 0: IDLE",
            "Status 1: Wait HomingPermitted (Ctrl_ForcePosCtrl if needed, timeout 10s)",
            "Status 2: Execute MC_HOME with Ctrl_LoadPosAx = HMI.PresetPosition (timeout 10s)",
            "Status 3: DONE"
        },
        "side_effects": "Sets Pers_Data.AxisReloadPostion_OK := TRUE (enables AutoReload next boot)",
        "persistence": "Pers_Data.ActualPosition = new preset value",
        "L3_responsibility": "None - operator action only",
        "use_case": "Operator calibrates position to known physical reference point",
        "example": "Material loaded at position 1500mm, operator sets preset to 1500.0"
    },
    
    "Execution_Priority": {
        "description": "Sequenza esecuzione opzioni @ startup",
        "priority_order": [
            "1. EncoderSelection (if needed)",
            "2. WritePar (if needed)",
            "3. AutoReloadPosition (always if enabled)",
            "4. ManPreset (manual trigger only)"
        ],
        "chaining": "Each procedure forces next in chain via Pers_Data flags",
        "L4_orchestration": "L4 Zone Manager triggers EncoderSelection/WritePar during startup phase"
    }
}

# Add Config details
data['PositioningMachine_Config'] = {
    "description": "Configuration structure for PositioningMachine",
    "SLS_VEL": {"type": "LReal", "meaning": "Safe Limited Speed (door opened)", "unit": "mm/min"},
    "DelayMissingCondition": {"type": "Time", "meaning": "Timeout warning condizioni mancanti"},
    "Ax": {
        "OptionON_EncoderSelection": {"type": "Bool", "meaning": "Enable encoder selection procedure"},
        "OptionON_ParameterChange": {"type": "Bool", "meaning": "Enable parameter change procedure"},
        "OptionON_AutoReloadPosition": {"type": "Bool", "meaning": "Enable auto reload position @ startup"},
        "OptionON_ManPreset": {"type": "Bool", "meaning": "Enable manual preset from HMI"},
        "HomeMode": {"type": "Int", "meaning": "MC_HOME mode parameter"},
        "PosAxis": {"type": "TAx_Config", "meaning": "PositioningAxis L1 configuration"}
    },
    "Fan": {
        "Presence": {"type": "Bool", "meaning": "Fan motor present"},
        "DelayOff": {"type": "Time", "meaning": "Fan delay off (cooling)"}
    },
    "Brake_Presence": {"type": "Bool", "meaning": "External brake present"}
}

# Save updated JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated {json_path} with complete Optional Features documentation")
