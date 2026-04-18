# ACG · controls/hmi

🖼 **HMI** subsystem — ISA-101-aligned operator interfaces.

Owns `hmi.*`.  Five screen layers (L1 Overview → L5 Support), a semantic
color palette, and a registry of active faceplates bound to tags from
other subsystems (SCADA tag plant, PLC equipment tree).

```
hmi/
  provider.py    Jython 2.7 tag provider · owns hmi.*
  udts.json      HMI UDT catalog (Faceplate, ScreenLayer, ColorMeaning, ...)
  tags.json      hmi.* tag catalog
  index.html     subsystem landing (via /index/renderer.js)
  templates/     copy-and-fill faceplate / badge / layer library

  chat/          💬  P2P chat HMI screen
                  · owns chat.*, room.*, tracker.*, peers.*, signal.*
                  · provider.py + udts.json + tags.json + templates/{wire,ui}
                  · runtime in /controls/scada/gateway/scripts/{p2p,peers,chat}.js
```

## Hosted screens

Chat lives here as the first concrete HMI screen.  Future operator
screens (alarm summary, batch monitor, recipe editor, trend grid) belong
under `controls/hmi/<screen>/` and follow the same provider contract.

## ISA-101 layer model

```
L1 Overview   Plant/Site        KPIs, status, alarm summary
L2 Area       Process Area      flows, states, trends
L3 Unit       Equipment         faceplates, control
L4 Detail     Diagnostic        config, tuning
L5 Support    Maintenance       calibration, history
```

Design principles + color palette + faceplate shape come from
`/controls/docs/standards/konomi/isa101/`.

## Namespaces

- `hmi.layer.current` — which L1-L5 screen is active
- `hmi.nav.path` — current page path
- `hmi.alarms.summary.*` — active-alarm counts by priority (mirrors ISA-18.2)
- `hmi.palette.<state>` — hex color for a semantic state
- `hmi.faceplates.<tag>.*` — registered faceplate per equipment
