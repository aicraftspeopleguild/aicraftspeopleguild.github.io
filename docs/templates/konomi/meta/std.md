# Konomi Standard Manifest

The root meta-document for the Konomi compression schema. Defines layers, agents, and scope.

## Source — `meta/_std.json`

```json:konomi:manifest
{"$schema":"konomi/std/v1","id":"Konomi","version":"1.0.0",
"scope":"self-defining industrial standards compression",
"layers":{
  "0":"meta/ — STD,UDT,LEVEL,SM,ENTITY,RELATION,RULE,CROSSWALK",
  "1":"base/ — Identifier,Timestamp,Quality,Value,Range,Quantity,Duration,Status",
  "2":"isa95/","3":"isa88/","4":"isa101/","5":"isa18/",
  "6":"opcua/","7":"mqtt/","8":"modbus/","9":"kpi/",
  "x":"crosswalks/"
},
"agents":{
  "parse":"doc→UDT","expand":"UDT→impl","validate":"impl→compliant",
  "crosswalk":"std_A↔std_B","generate":"template→code"
},
"motto":"max info, min tokens"}
```

## Layer meanings

| Layer | Path   | Contents |
|-------|--------|----------|
| 0     | meta/  | The standard itself — schema objects: STD, UDT, LEVEL, SM, ENTITY, RELATION, RULE, CROSSWALK |
| 1     | base/  | Primitive UDTs shared across all layers: Identifier, Timestamp, Quality, Value, Range, Quantity, Duration, Status |
| 2–9   | std/   | One folder per industrial standard (ISA-95, ISA-88, OPC-UA, MQTT, Modbus, KPI, …) |
| x     | crosswalks/ | Bidirectional mappings between standards |

## Agents

| Agent     | Contract            |
|-----------|---------------------|
| parse     | document → UDT      |
| expand    | UDT → implementation |
| validate  | impl → compliant    |
| crosswalk | std_A ↔ std_B       |
| generate  | template → code     |
