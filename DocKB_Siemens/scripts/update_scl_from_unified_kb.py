#!/usr/bin/env python3
"""
Aggiorna SINAMICS_AlarmHandler.scl con dati della Unified Knowledge Base
Converte i dati JSON in array SCL con tutti gli allarmi/fault consolidati
"""

import json
from pathlib import Path


def escape_scl_string(s: str) -> str:
    """Escapa una stringa per SCL (max 256 caratteri)"""
    if not s:
        return ""
    # Rimuovi newline e limita a 256 caratteri
    s = s.replace('\n', ' ').replace('\r', ' ')
    s = ' '.join(s.split())  # Normalizza spazi
    return s[:256]


def generate_scl_alarm_handler(unified_kb_dir: str = None) -> str:
    """Genera il file SINAMICS_AlarmHandler.scl dalla Unified KB"""

    # Se non specificato, usa il path predefinito
    if unified_kb_dir is None:
        unified_kb_dir = str(Path(__file__).parent.parent / "kb" / "unified_knowledge_base")

    kb_path = Path(unified_kb_dir)
    alarms_file = kb_path / "alarms_faults.json"

    if not alarms_file.exists():
        raise FileNotFoundError(f"File non trovato: {alarms_file}")

    # Carica dati
    with open(alarms_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    alarms = data.get('alarms', {})
    faults = data.get('faults', {})

    total_alarms = len(alarms)
    total_faults = len(faults)

    print(f"📊 Allarmi trovati: {total_alarms}")
    print(f"📊 Fault trovati: {total_faults}")

    # Genera array SCL per allarmi
    alarm_records = []
    for key, alarm in alarms.items():
        code = escape_scl_string(alarm.get('code', ''))
        description = escape_scl_string(alarm.get('description', ''))
        section_id = escape_scl_string(alarm.get('section_id', ''))
        source_kb = escape_scl_string(alarm.get('source_kb', ''))

        # Formato SCL per record
        record = (
            f'        (Code := "{code}", Type := "ALARM", '
            f'Description := "{description}", '
            f'Solution := "Consultare manuale {source_kb}", '
            f'SectionID := "{section_id}")'
        )
        alarm_records.append(record)

    # Genera array SCL per fault
    fault_records = []
    for key, fault in faults.items():
        code = escape_scl_string(fault.get('code', ''))
        description = escape_scl_string(fault.get('description', ''))
        section_id = escape_scl_string(fault.get('section_id', ''))
        source_kb = escape_scl_string(fault.get('source_kb', ''))

        # Formato SCL per record
        record = (
            f'        (Code := "{code}", Type := "FAULT", '
            f'Description := "{description}", '
            f'Solution := "Consultare manuale {source_kb}", '
            f'SectionID := "{section_id}")'
        )
        fault_records.append(record)

    # Costruisci SCL
    scl_content = f'''(*
  ============================================================================
  SINAMICS S120/S150 Alarm and Fault Handler
  UNIFIED KNOWLEDGE BASE VERSION

  Funzione SCL per TIA Portal (S7-1200, S7-1500)
  Gestione allarmi e fault del drive SINAMICS

  Genera descrizioni e soluzioni partendo dal numero di allarme/fault
  Dati estratti dalla Unified Knowledge Base SINAMICS S120/S150

  Contiene: {total_alarms} allarmi + {total_faults} fault
  Fonti:
  - sinamics_s120_communication
  - sinamics_s120_drive_functions
  - sinamics_s120_s150_list_manual
  ============================================================================
*)

TYPE AlarmFaultRecord
STRUCT
    Code : STRING[10];           (* Codice alarm/fault: "0230", "F3000", etc. *)
    Type : STRING[10];           (* "ALARM" o "FAULT" *)
    Description : STRING[256];   (* Descrizione del messaggio *)
    Solution : STRING[256];      (* Soluzione consigliata *)
    SectionID : STRING[20];      (* ID sezione manuale *)
END_STRUCT
END_TYPE

(* Tipo per il risultato della ricerca *)
TYPE SearchResult
STRUCT
    Found : BOOL;                (* TRUE se alarm/fault trovato *)
    Record : AlarmFaultRecord;   (* Dati dell'alarm/fault *)
    ErrorMessage : STRING[256];  (* Messaggio di errore se non trovato *)
END_STRUCT
END_TYPE

(*
  ============================================================================
  DATABASE ALLARMI E FAULT - UNIFIED KNOWLEDGE BASE
  Estratto automaticamente da Unified KB ({total_alarms} allarmi + {total_faults} fault)
  ============================================================================
*)

VAR CONSTANT
    (* Tabella allarmi SINAMICS - UNIFIED *)
    ALARM_DATABASE : ARRAY [1..{total_alarms}] OF AlarmFaultRecord := (
{','.join(alarm_records)}
    );

    (* Tabella fault SINAMICS - UNIFIED *)
    FAULT_DATABASE : ARRAY [1..{total_faults}] OF AlarmFaultRecord := (
{','.join(fault_records)}
    );
END_VAR

(*
  ============================================================================
  FUNCTION: SearchAlarmByCode

  Ricerca un allarme nel database per codice

  Parametri di ingresso:
    AlarmCode : STRING - Codice allarme da cercare (es. "0230", "A0681")

  Ritorna:
    SearchResult - Struttura con risultati della ricerca
  ============================================================================
*)
FUNCTION SearchAlarmByCode : SearchResult
    VAR_INPUT
        AlarmCode : STRING;
    END_VAR
    VAR
        i : INT;
        Result : SearchResult;
        UpperCode : STRING;
    END_VAR
BEGIN
    Result.Found := FALSE;
    Result.ErrorMessage := '';

    (* Converte il codice a maiuscole per ricerca case-insensitive *)
    UpperCode := UPPER(AlarmCode);

    (* Ricerca nel database allarmi *)
    FOR i := 1 TO ARRAY_SIZE(ALARM_DATABASE, 1) DO
        IF UPPER(ALARM_DATABASE[i].Code) = UpperCode THEN
            Result.Found := TRUE;
            Result.Record := ALARM_DATABASE[i];
            RETURN Result;
        END_IF;
    END_FOR;

    (* Se non trovato nei database allarmi, restituisce errore *)
    Result.ErrorMessage := CONCAT('Allarme non trovato: ', AlarmCode);
    RETURN Result;
END_FUNCTION

(*
  ============================================================================
  FUNCTION: SearchFaultByCode

  Ricerca un fault nel database per codice

  Parametri di ingresso:
    FaultCode : STRING - Codice fault da cercare (es. "F0300", "3000")

  Ritorna:
    SearchResult - Struttura con risultati della ricerca
  ============================================================================
*)
FUNCTION SearchFaultByCode : SearchResult
    VAR_INPUT
        FaultCode : STRING;
    END_VAR
    VAR
        i : INT;
        Result : SearchResult;
        UpperCode : STRING;
    END_VAR
BEGIN
    Result.Found := FALSE;
    Result.ErrorMessage := '';

    (* Converte il codice a maiuscole per ricerca case-insensitive *)
    UpperCode := UPPER(FaultCode);

    (* Ricerca nel database fault *)
    FOR i := 1 TO ARRAY_SIZE(FAULT_DATABASE, 1) DO
        IF UPPER(FAULT_DATABASE[i].Code) = UpperCode THEN
            Result.Found := TRUE;
            Result.Record := FAULT_DATABASE[i];
            RETURN Result;
        END_IF;
    END_FOR;

    (* Se non trovato nei database fault, restituisce errore *)
    Result.ErrorMessage := CONCAT('Fault non trovato: ', FaultCode);
    RETURN Result;
END_FUNCTION

(*
  ============================================================================
  FUNCTION: SearchAlarmOrFault

  Ricerca sia allarmi che fault per codice (procedura unificata)

  Parametri di ingresso:
    Code : STRING - Codice da cercare (funziona per allarmi e fault)

  Ritorna:
    SearchResult - Struttura con risultati della ricerca
  ============================================================================
*)
FUNCTION SearchAlarmOrFault : SearchResult
    VAR_INPUT
        Code : STRING;
    END_VAR
    VAR
        Result : SearchResult;
    END_VAR
BEGIN
    (* Prova a cercare prima negli allarmi *)
    Result := SearchAlarmByCode(Code);

    IF NOT Result.Found THEN
        (* Se non trovato negli allarmi, cerca nei fault *)
        Result := SearchFaultByCode(Code);
    END_IF;

    RETURN Result;
END_FUNCTION

(*
  ============================================================================
  FUNCTION: GetAlarmDescription

  Ritorna solo la descrizione di un allarme (senza struttura completa)

  Parametri di ingresso:
    AlarmCode : STRING - Codice allarme

  Ritorna:
    STRING - Descrizione dell'allarme o messaggio di errore
  ============================================================================
*)
FUNCTION GetAlarmDescription : STRING
    VAR_INPUT
        AlarmCode : STRING;
    END_VAR
    VAR
        Result : SearchResult;
    END_VAR
BEGIN
    Result := SearchAlarmByCode(AlarmCode);

    IF Result.Found THEN
        RETURN Result.Record.Description;
    ELSE
        RETURN Result.ErrorMessage;
    END_IF;
END_FUNCTION

(*
  ============================================================================
  FUNCTION: GetFaultDescription

  Ritorna solo la descrizione di un fault

  Parametri di ingresso:
    FaultCode : STRING - Codice fault

  Ritorna:
    STRING - Descrizione del fault o messaggio di errore
  ============================================================================
*)
FUNCTION GetFaultDescription : STRING
    VAR_INPUT
        FaultCode : STRING;
    END_VAR
    VAR
        Result : SearchResult;
    END_VAR
BEGIN
    Result := SearchFaultByCode(FaultCode);

    IF Result.Found THEN
        RETURN Result.Record.Description;
    ELSE
        RETURN Result.ErrorMessage;
    END_IF;
END_FUNCTION

(*
  ============================================================================
  FUNCTION: GetSolution

  Ritorna la soluzione consigliata per un allarme/fault

  Parametri di ingresso:
    Code : STRING - Codice allarme/fault

  Ritorna:
    STRING - Soluzione consigliata o messaggio di errore
  ============================================================================
*)
FUNCTION GetSolution : STRING
    VAR_INPUT
        Code : STRING;
    END_VAR
    VAR
        Result : SearchResult;
    END_VAR
BEGIN
    Result := SearchAlarmOrFault(Code);

    IF Result.Found THEN
        RETURN Result.Record.Solution;
    ELSE
        RETURN Result.ErrorMessage;
    END_IF;
END_FUNCTION
'''

    return scl_content


def main():
    """Funzione principale"""
    print("=" * 80)
    print("AGGIORNAMENTO SINAMICS_AlarmHandler.scl DALLA UNIFIED KB")
    print("=" * 80)
    print()

    try:
        # Genera nuovo SCL
        scl_content = generate_scl_alarm_handler()

        # Salva file
        output_file = Path("SINAMICS_AlarmHandler_Unified.scl")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(scl_content)

        print(f"\n✅ SCL generato con successo!")
        print(f"   File: {output_file}")
        print(f"   Dimensione: {len(scl_content):,} bytes")
        print()
        print("📋 RIEPILOGO:")
        print(f"   - Database unificato da 3 Knowledge Base")
        print(f"   - Funzioni disponibili: SearchAlarmByCode, SearchFaultByCode, SearchAlarmOrFault")
        print(f"   - Shortcut: GetAlarmDescription, GetFaultDescription, GetSolution")
        print()
        print("🔄 PROSSIMI PASSI:")
        print(f"   1. Sostituisci SINAMICS_AlarmHandler.scl con SINAMICS_AlarmHandler_Unified.scl")
        print(f"   2. Importa il file in TIA Portal")
        print(f"   3. Usa le funzioni nel tuo codice PLC")

    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
