# GitPLC Template — `controls/plc/git/`

Universal PLC Namespace UDT transfer-layer templates. Every file in this tree
is a **template**: copy it and fill in project-specific fields to produce a
concrete GitPLC repository instance.

## Layout

```
controls/plc/git/
├── config/
│   ├── config.json           project config (vendor, ISA level, paths)
│   └── vendor-map.json       primitive + FB mapping across vendors
├── meta/                     Layer 0 — meta-UDTs describing UDTs
│   ├── GitPLC_Type.udt.json
│   ├── Field.udt.json
│   ├── TypeRef.udt.json
│   └── Method.udt.json
├── equipment/                Layer 2 — ISA-88 equipment + PackML
│   ├── Equipment.udt.json
│   ├── PackML_State.udt.json
│   ├── PackML_Mode.udt.json
│   ├── Equipment_Cmd.udt.json
│   ├── Equipment_Sts.udt.json
│   ├── Equipment_Cfg.udt.json
│   └── Equipment_HMI.udt.json
├── cm/                       Layer 3 — control-module library
│   ├── CM_Base.udt.json
│   ├── CM_State.udt.json
│   ├── CM_Mode.udt.json
│   ├── Fault_Data.udt.json
│   ├── Sim_Data.udt.json
│   ├── CM_DiscreteIn.udt.json
│   ├── CM_DiscreteOut.udt.json
│   ├── CM_AnalogIn.udt.json
│   ├── CM_AnalogOut.udt.json
│   ├── CM_Motor.udt.json
│   ├── CM_Valve.udt.json
│   ├── CM_VFD.udt.json
│   └── CM_PID.udt.json
├── alarms/                   Layer 4 — ISA-18.2 alarm model
│   ├── Alarm_SP.udt.json
│   ├── Alarm_Instance.udt.json
│   ├── Alarm_State.udt.json
│   └── Alarm_Summary.udt.json
├── recipe/                   Layer 5 — S88 phase + batch
│   ├── Phase_Base.udt.json
│   ├── Phase_State.udt.json
│   ├── Phase_Params.udt.json
│   ├── Phase_Report.udt.json
│   ├── Batch.udt.json
│   ├── Batch_State.udt.json
│   ├── Batch_Params.udt.json
│   └── Batch_Report.udt.json
├── io/                       Layer 6 — physical IO
│   ├── IO_Card.udt.json
│   ├── IO_Status.udt.json
│   ├── IO_Config.udt.json
│   ├── IO_Point.udt.json
│   └── IO_Map.udt.json
└── hooks/                    pre-commit validators (reserved)
```

## File format

Every UDT is JSON, `$schema: "gitplc/udt/v1"`:

```json
{
  "$schema": "gitplc/udt/v1",
  "name": "CM_Motor",
  "base": "CM_Base",
  "version": "1.0.0",
  "fields": [ { "name": "...", "type": "..." } ],
  "meta": { "desc": "..." }
}
```

Field names use **dot-paths** (`cmd.start`, `io.run_fbk`) to keep each file
small while preserving structure — expanders can re-materialize the tree at
validation / export time.

## Token budget

Each `.udt.json` is kept **under 250 tokens** so templates can be fed whole
to LLM agents (α..κ) as single-message context without truncation.

## Next step

To instantiate a working repo, copy `controls/plc/git/` → `<site>/gitplc/`,
set `config/config.json → project`, and begin importing vendor projects via
the α (parse) agent.
