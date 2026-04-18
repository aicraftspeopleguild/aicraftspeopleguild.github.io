---
title: The Konomi Standard
slug: konomi-standard
authors: [Open Standard, Living Document]
publication_date: March 2026
summary: Self-Defining Industrial Standards Compression v1.0
status: published
site_href: konomi-standard.html
---

**A white paper that is also its own specification.**

This document is recursive by design. Each section defines the very structure used to write the section itself, so the paper serves both as explanation and as executable compression grammar for industrial standards.

## 0. How To Read This Paper

Section 1 defines what a standard is using the standard format. Section 2 defines what a UDT is as a UDT. Section 3 compresses major industrial standards using the meta-structures from the first two sections. Section 4 maps them to one another using the same crosswalk format the paper defines for itself.

If you understand Section 0, you understand the entire document. If you understand the entire document, you can generate any industrial standard, in any target format, from this single source.

- **Human mode:** read top to bottom. Each layer builds on the previous one.
- **LLM/Agent mode:** parse the STD, UDT, LEVEL, STATE\_MACHINE, ENTITY, RELATION, RULE, and CROSSWALK blocks as structured data and generate implementations from them.
- **Validator mode:** every structure in the paper can be checked against its own definition. A Konomi document that violates Layer 0 is malformed.

## 1. The Meta-Standard (Layer 0)

Layer 0 is the grammar of the grammar. It defines the minimal structure required for a standard to be self-describing, enforceable, and crosswalkable.

### 1.1 What Is A Standard?

```
STD = {
  id        : str               - unique key (e.g. "ISA-95", "ISA-88")
  scope     : str               - what domain this standard covers
  udt       : [UDT]             - user-defined types, listed FIRST
  hierarchy : [LEVEL]           - levels or layers, if the standard has them
  states    : [STATE_MACHINE]   - state models, if the standard has them
  entities  : [ENTITY]          - core objects the standard defines
  relations : [RELATION]        - how those objects connect
  rules     : [RULE]            - constraints, validations, invariants
  crosswalk : {std_id -> MAP}   - mappings to other standards
}
```

The paper argues that exactly these eight components are enough: identity, scope, vocabulary, hierarchy, behavior, objects, connections, constraints, plus a network layer that links one standard to another. UDTs come first because types are the dependency base for every entity and rule that follows.

### 1.2 Component Definitions

```
UDT = {
  name        : str
  base        : str | null
  fields      : [{name, type, unit, range, desc}]
  methods     : [{name, params, returns, desc}]
  constraints : [RULE]
}

LEVEL = {
  id        : int | str
  name      : str
  scope     : str
  timescale : str
  systems   : [str]
  data_down : [str]
  data_up   : [str]
}

STATE_MACHINE = {
  name        : str
  states      : [str]
  initial     : str
  transitions : [{from, to, trigger, guard, action}]
}

ENTITY = {
  name     : str
  udt      : str
  parent   : str | null
  children : [str]
  tags     : {category -> [TAG_DEF]}
}

RELATION = {
  type        : contains | references | triggers | produces | consumes
  from        : str
  to          : str
  cardinality : 1:1 | 1:N | N:M
}

RULE = {
  id        : str
  condition : expr
  action    : str
  severity  : info | warn | error | fatal
}

CROSSWALK = {
  from_std    : str
  from_entity : str
  to_std      : str
  to_entity   : str
  mapping     : exact | partial | semantic
  transform   : expr | null
}
```

Each component is itself a reusable structure. That recursion is the point: the meta-standard is not just describing standards in prose, it is compressing them into a formal schema that can be parsed, generated, and validated.

## 2. Base UDTs (Layer 1)

Layer 1 defines the atomic reusable types from which every later standard is built. The paper's design claim is that a shared base vocabulary makes compression and interoperability tractable.

### 2.1 Identification

```
UDT:Identifier
  UUID  : str : global scope
          format: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          use:    database keys, batch IDs, unique records

  PATH  : str : hierarchical scope
          format: "A/B/C/D"
          use:    ISA-95 asset paths (Site/Area/Line/Unit)

  TAG   : str : equipment scope
          format: "Area_Unit_Module_Point"
          use:    ISA-5.1 instrument tags (FIC-101, TT-305)

  URN   : str : global scope
          format: "urn:domain:type:id"
          use:    cross-system references
```

The paper reduces industrial identification to four patterns only: UUID, PATH, TAG, and URN. Anything outside those is treated as either an alias or an identification defect.

### 2.2 Time

```
UDT:Timestamp
  ISO8601      : str   : "YYYY-MM-DDTHH:mm:ss.sssZ" : ms resolution : UTC
  EPOCH_MS     : int64 : unix milliseconds          : ms resolution : UTC
  OPC_FILETIME : int64 : 100ns since 1601-01-01     : 100ns resolution : UTC
```

All timestamps are UTC. Local time is treated as a display concern, not a data concern.

### 2.3 Quality, Value, Range

```
UDT:Quality
  GOOD:192 | BAD:0 | UNCERTAIN:64
  Modifiers: SUBSTITUTED:+16 | LIMITED:+4

UDT:Value
  {v:any, q:Quality, t:Timestamp, unit:str|null}

UDT:Range
  {lo:num, hi:num, lo_inc:bool, hi_inc:bool, unit:str}
```

The core insight here is that industrial data is never just a number. A value without quality, timestamp, and unit is not reliable process data. It is raw assertion.

### 2.4 Quantity, Duration, Status

```
UDT:Quantity
  {value:num, unit:str, uncertainty:num|null}

UDT:Duration
  {value:num, unit: ms|s|min|hr|day|week|month|year}

UDT:Status
  {code:int, name:str, desc:str, severity: info|warn|error|fatal}
```

## 3. Industrial Standards (Layers 2-8)

With the meta-standard and base types defined, the paper compresses several industrial standards into the Konomi shape: UDT-first, hierarchy-aware, and explicitly crosswalkable.

### 3.1 ISA-95: Enterprise-to-Control Integration

```
STD = {
  id:    "ISA-95"
  scope: "Integration between enterprise business systems and
          manufacturing control systems"
}
```

The problem ISA-95 solves is not transport but boundary definition: what information moves between enterprise and manufacturing layers and in what shape.

```
L4 : Business             | ERP, BI            | days-months | "What to make and when"
L3 : Manufacturing Ops    | MES, LIMS          | shifts-days | "How it was made"
L2 : Control              | SCADA, HMI, Batch  | sec-hours   | "Make it now"
L1 : Sensing              | PLC, DCS, RTU      | ms-sec      | "Measure and actuate"
L0 : Process              | Sensors, Actuators | continuous  | "The physical world"
```

```
L4 -> L3: [ProductionSchedule, MaterialDefinition, ProductDefinition, WorkOrder]
L3 -> L4: [ProductionPerformance, Inventory, QualityResults, OperationalStatus]
L3 -> L2: [Recipe, Setpoints, Commands, DetailedSchedule]
L2 -> L3: [ProcessData, Events, Alarms, BatchRecords]
L2 -> L1: [Setpoints, Commands]
L1 -> L2: [Measurements, DeviceStatus, Alarms]
```

```
Equipment              : extends PhysicalAsset {capability, state, mode}
Material               : {id, name, properties, lot, sublots}
Personnel              : {id, name, role, qualifications, schedule}
ProcessSegment         : {equipment, personnel, materials_in, materials_out, params, duration}
ProductionSchedule     : {start, end, segments, priority, state}
ProductionPerformance  : {schedule_ref, actual_start, actual_end, actual_params, KPIs}
```

The paper also maps ISA-95 into the A.S.S.-OS ring model, claiming that both frameworks converge on the same hierarchical organization because they solve the same signal-processing problem.

### 3.2 ISA-88: Batch Process Control

```
STD = {
  id:    "ISA-88"
  scope: "Recipe management and batch execution for process manufacturing"
}
```

The core insight is recipe/equipment separation: the same recipe should run on multiple pieces of equipment, and the same equipment should run multiple recipes.

```
Equipment hierarchy:
Enterprise -> Site -> Area -> ProcessCell -> Unit -> EquipmentModule -> ControlModule

Recipe hierarchy:
Procedure -> UnitProcedure -> Operation -> Phase
```

```
IDLE -> RUNNING -> COMPLETE
        v HOLD
     HOLDING -> HELD -> RESTARTING -> RUNNING
        v STOP
     STOPPING -> STOPPED
        v ABORT
     ABORTING -> ABORTED
```

### 3.3 ISA-18.2: Alarm Management

```
STD = {
  id:    "ISA-18.2"
  scope: "Alarm management lifecycle from design through monitoring"
}
```

ISA-18.2 is presented as gate calibration for human operators: every alarm must be actionable, prioritized, and bounded so the operator is not flooded by noise.

```
P1 Emergency : response < 1 min  : Red    : continuous sound
P2 High      : response < 10 min : Orange : fast pulse sound
P3 Medium    : response < 1 hr   : Yellow : slow pulse sound
P4 Low       : response = shift  : Cyan   : no sound
```

```
NORMAL -> [condition] -> UNACK_ALARM -> [ack] -> ACKED_ALARM -> [clear] -> NORMAL
                            v                      v
                        [clear]              [ack timeout]
                            v                      v
                       RTN_UNACK ---- [ack] --> NORMAL
```

```
R1: Every alarm MUST be documented
R2: Every alarm MUST have a unique response
R3: Every alarm MUST be actionable
R4: Priority MUST be based on consequence + response time
R5: No duplicate alarms for the same condition
R6: Review frequency: annual minimum
R7: Target metrics: <6 alarms/hr average, <12 peak, no floods
```

### 3.4 ISA-101: HMI Design

```
STD = {
  id:    "ISA-101"
  scope: "Design and implementation of human-machine interfaces"
}
```

```
Core principles:
SITUATIONAL_AWARENESS > aesthetics
CONSISTENCY > novelty
GRAY_BACKGROUND
COLOR = meaning, not decoration
LAYERS = progressive detail
```

```
L1 Overview : Plant/Site KPIs, status, alarms      -> navigate to L2
L2 Area     : Process flows, states, trends        -> navigate to L1 or L3
L3 Unit     : Equipment faceplates, direct control -> navigate to L2 or L4
L4 Detail   : Diagnostics, configuration, tuning   -> navigate to L3 or L5
L5 Support  : Maintenance, calibration, history    -> navigate to L4
```

```
Gray   #808080 : Normal, no action required
Green  #00AA00 : Running, operating normally
DkGray #404040 : Stopped, standby
Yellow #FFCC00 : Warning, attention needed
Red    #CC0000 : Alarm, action required
Blue   #0066CC : Maintenance, out of service
Orange #FF6600 : Manual mode
Cyan   #00CCCC : Transitioning between states
```

### 3.5 OPC-UA, 3.6 MQTT/Sparkplug, 3.7 Modbus, 3.8 KPIs

The paper then compresses four additional standards and patterns:

- **OPC-UA** as the industrial R7 network protocol: hierarchical address space, typed nodes, and values carrying quality plus timestamps.
- **MQTT/Sparkplug** as lightweight publish/subscribe semantics for edge-to-cloud with industrial birth/death and metric conventions.
- **Modbus** as minimal R1 field communication: flat registers, low semantics, and enduring utility through simplicity.
- **KPIs** through OEE as multiplicative composition.

```
OEE = Availability x Performance x Quality

Availability = run_time / (run_time + downtime)      target: >90%
Performance  = actual_rate / ideal_rate              target: >95%
Quality      = good_units / total_units              target: >99%
OEE          = A x P x Q                             target: >85%
```

The same multiplicative logic is explicitly linked to the paper's broader thesis: one missing dimension cannot be compensated for by overperformance elsewhere.

## 4. Crosswalks (Layer delta)

Crosswalks are the network layer between standards. They make interoperability explicit rather than implicit.

```
ISA95.WorkCenter      = ISA88.ProcessCell       [EXACT]
ISA95.WorkUnit        = ISA88.Unit              [EXACT]
ISA95.ProcessSegment  = ISA88.Operation         [EXACT]
ISA95.ProductionSchedule -> ISA88.Batch         [SEMANTIC: schedule instantiates batch]

ISA95.Equipment       -> OPCUA.Object(ns=isa95) [EXACT]
ISA95.Property        -> OPCUA.Variable         [EXACT]
ISA95.Capability      -> OPCUA.Method           [EXACT]

ISA88.Phase.RUNNING   = PackML.EXECUTE          [EXACT]
ISA88.Phase.HELD      = PackML.HELD             [EXACT]
ISA88.Phase.ABORTED   = PackML.ABORTED          [EXACT]
ISA88.UnitState       ~= PackML.StateMachine    [PARTIAL: PackML is a subset]

ISA101.AlarmIndicator -> ISA18.AlarmState       [SEMANTIC]
ISA101.ColorMeaning   -> ISA18.Priority(color)  [EXACT]
ISA101.L1-L5.Summary  -> ISA18.AlarmList        [SEMANTIC]

OPCUA.Variable        -> Sparkplug.Metric       [EXACT]
OPCUA.Subscription    -> Sparkplug.NDATA/DDATA  [SEMANTIC]
OPCUA.Method          -> Sparkplug.NCMD/DCMD    [SEMANTIC]
OPCUA.AddressSpace    <-> Sparkplug.NBIRTH      [SEMANTIC]

ISA95.L0  = ASSOS.R0 (Ground)     [EXACT]
ISA95.L1  = ASSOS.R1 (Sensors)    [EXACT]
ISA95.L2  = ASSOS.R2 (Gate)       [EXACT]
ISA95.L3  = ASSOS.R3 (Affect)     [EXACT]
ISA95.L3.5= ASSOS.R4 (Executive)  [EXACT]
ISA95.L4  = ASSOS.R5 (Identity)   [EXACT]
ISA95.L4+ = ASSOS.R6 (Observer)   [EXACT]
Fieldbus  = ASSOS.R7 (Network)    [SEMANTIC]
```

The paper's claim is that this is what makes standards interoperable without forcing every system to collapse into one vendor language: exact, partial, and semantic mappings plus explicit transforms.

## 5. Using The Konomi Standard

### 5.1 Parsing

To compress a conventional industrial standard into Konomi form:

1. Identify all defined types and populate UDTs.
2. Identify all hierarchies and populate LEVELs.
3. Identify all state models and populate STATE\_MACHINEs.
4. Identify all named objects and populate ENTITYs.
5. Identify all connections and populate RELATIONs.
6. Identify all constraints and populate RULEs.
7. Identify all mappings to other standards and populate CROSSWALKs.

### 5.2 Expanding

```
UDT        -> class/struct/type definition
LEVEL      -> namespace/module/package hierarchy
STATE      -> state machine implementation (enum + transition table)
ENTITY     -> instantiated object with tag bindings
RELATION   -> foreign keys, references, event wiring
RULE       -> validation functions, alarm configurations
CROSSWALK  -> adapter/translator modules between systems
```

### 5.3 Validating

Compliance means checking that required types exist, layer contracts are satisfied, transitions implement guards, entities instantiate correct types, rules fire at the declared severity, and crosswalk transforms match the mapping type.

### 5.4 Crosswalking

```
from konomi import KS

result = KS.crosswalk(
    entity="WorkCenter",
    from_std="ISA-95",
    to_std="ISA-88"
)

# Returns:
# {to_entity: "ProcessCell", mapping: "exact", transform: null}
```

## 6. Why This Matters

Industrial standards are necessary and painful. Engineers rarely read every relevant part of ISA-95, ISA-88, ISA-18.2, ISA-101, OPC-UA, Sparkplug, and the rest in full. Integration is often partial, inconsistent, and bespoke.

The Konomi Standard proposes a compression layer rather than a replacement standard. Its value is in making the essential shape of multiple standards parseable by humans, LLMs, validators, and code generators at the same time.

- **Parseable:** structured data instead of prose alone.
- **Expandable:** code can be generated into any implementation language.
- **Validatable:** documents can be checked against the structures that define them.
- **Crosswalkable:** mappings between standards become first-class artifacts.
- **Self-describing:** the meta-standard defines how to extend the framework itself.

The Konomi Standard is a living document.

Layer 0 defines the structure. Layer 1 defines the base types. Crosswalks connect everything else.

The standard defines how to extend itself. That recursion is the point.

STD -> UDT -> ENTITY -> RELATION -> RULE -> CROSSWALK -> STD

The circle closes. The standard is the standard for standards.

510,510
