# UDT standard per gestione macchine (Framework PLC)

Questo documento raccoglie **tutti gli UDT obbligatori** utilizzati dalle macchine a singolo attuatore del framework, con la descrizione dettagliata dei bit e la logica di sequenza dove rilevante.

---

## 1  `AreaInterface`

| Segnale          | Descrizione operativa                                                 |
| ---------------- | --------------------------------------------------------------------- |
| `EStop`          | **Emergenza area attiva**. Impedisce l'avvio di nuovi comandi.        |
| `Man`            | Area in **modo MANUALE** (abilita i comandi manuali).                 |
| `Aut`            | Area in **modo AUTOMATICO** (disabilita e annulla i comandi manuali). |
| `Cycle`          | **Ciclo automatico in corso** per tutte le macchine.                  |
| `StopInPhase`    | Richiesta **Stop in fase** (arresto a fine movimento).                |
| `StopProgrammed` | Richiesta **Stop programmato** (fine ordine / svuotamento zona).      |
| `RstAlarms`      | Fronte di salita per **reset allarmi**.                               |
| `ManOneShot`     | Fronte passaggio in MANUALE: usato per inizializzazioni oneâ€‘shot.     |
| `AutOneShot`     | Fronte passaggio in AUTOMATICO.                                       |
| `CycleOneShot`   | Fronte all'avvio del ciclo automatico.                                |
| `CheckAutReady`  | Handshake: l'Area chiede alle macchine se sono pronte (`AutReady`).   |

---

## 2  `MachineInterface`

| Segnale             | Descrizione operativa                                                     |
| ------------------- | ------------------------------------------------------------------------- |
| `AutReady`          | **Macchina pronta** a partire in AUTO (no allarmi, homing ok, safety ok). |
| `Aborting`          | Allarme critico â†’ richiede Stop in fase immediato.                        |
| `AckStopInPhase`    | Conferma che lo **Stop in fase** Ã¨ completato.                            |
| `AckStopProgrammed` | Conferma che lo **Stop programmato** Ã¨ completato.                        |
| `MotionsStandStill` | Attuatori fermi **e nessun comando pendente**.                            |
| `AlarmsPresence`    | Almeno un **allarme bloccante** presente.                                 |
| `WarningPresence`   | Presenza di **warning** non bloccanti.                                    |

---

## 3  `udt_ZoneSafetyInterface` (ZSI)

| Segnale            | Descrizione                                                                            |
| ------------------ | -------------------------------------------------------------------------------------- |
| `Door_NormalStop`  | **Fase 1 â€“ Richiesta accesso**: stop normale delle macchine di zona.                   |
| `Door_SafeStop`    | **Fase 2 â€“ Safeâ€‘Stop**: la Safety avvia SS1/SS2 togliendo energia.                     |
| `Door_EntryEnable` | **Fase 3 â€“ Porta sbloccabile**: energia a zero, serratura sbloccabile.                 |
| `Door_Opened`      | **Fase 4 â€“ Porta aperta/non riarmata**: resta TRUE finchÃ© la porta non viene richiusa. |

**Sequenza tipica**

1. `Door_NormalStop` â†’ fermata controllata.
2. Standâ€‘still macchine, quindi `Door_SafeStop` â†’ decadimento energia.
3. `Door_EntryEnable` â†’ elettroserratura sbloccata.
4. Apertura porta â†’ `Door_Opened = TRUE`.

---

## 4  `udt_DeviceSafetyInterface` (DSI)

| Segnale              | Descrizione                                                    |
| -------------------- | -------------------------------------------------------------- |
| `SafeStop`           | **Fase 1 â€“ Arresto sicuro in corso** (SS1/SS2).                |
| `PowerEnable`        | **Fase 2 â€“ Preâ€‘STO** (â‰ˆ â€‘300 ms): consenso potenza rimosso.    |
| `DevicesInSafeState` | **Fase 3 â€“ Sicuro raggiunto**: drive/contattori disalimentati. |

**Sequenza arresto sicuro**
*SafeStop* â†’ *PowerEnable* (va FALSE) â†’ *DevicesInSafeState* (energia rimossa).

---

## 5  `TAx_DriveInterface`

| Segnale       | Descrizione                                                                              |
| ------------- | ---------------------------------------------------------------------------------------- |
| `Infeed_ON`   | **Alimentatore S120 attivo** (P864). Se FALSE, il drive genera fault se riceve servoâ€‘on. |
| `AccessPoint` | **Nome CU320â€‘2 PN** (configurazione TIA) usato da **SinaParaS**.                         |
| `AxisID`      | **Item ID** asse nella *Telegram Configuration* della CU.                                |
| `TokenChain`  | **Indice tokenâ€‘chain** (una per CU) per arbitraggio richieste acicliche.                |

**Sequenza servoâ€‘on**

1. Verificare `Infeed_ON = TRUE`.
2. Comandare servoâ€‘on (nel FB device) â†’ drive abilita potenza.
3. Drive conferma (`DrivePower`) â†’ comandi RUN/Setâ€‘point permessi.

---

**Versione 1.0 â€“ UDT standard (estratto da "Descrizione Fb Framework" paragrafi 7Â·8Â·10Â·11Â·12)
