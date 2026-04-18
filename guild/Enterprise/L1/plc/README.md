# ACG · controls/plc

🔧 **PLC** subsystem — GitPLC template library + runtime tag plant.

Owns `plc.*`.  Holds the universal UDT namespace templates (vendor-
agnostic) and exposes the live state of a GitPLC project (current vendor,
equipment tree size, IO card count, sync status, HEAD commit).

```
plc/
  provider.py    Jython 2.7 tag provider
  udts.json      PLC UDT catalog (mirrors the GitPLC standard)
  tags.json      plc.* tag catalog
  index.html     subsystem landing (via /index/renderer.js)
  git/           GitPLC UDT templates (Equipment, CM_*, Alarm_*, Phase_*, IO_*, ...)
    meta/        Layer 0 · meta-UDT
    equipment/   Layer 2 · ISA-88 equipment + PackML
    cm/          Layer 3 · control modules
    alarms/      Layer 4 · ISA-18.2 alarms
    recipe/      Layer 5 · S88 phase / batch
    io/          Layer 6 · IO cards + points + map
    config/      project config + vendor primitive map
```

## Standards

The GitPLC **standard descriptor** lives under
`/controls/docs/standards/gitplc/` (Konomi-format).  The **templates**
here under `plc/git/` are the concrete UDT instances the standard
describes.

## Namespaces

- `plc.project.*` — current project name/vendor/version
- `plc.types.count` — number of UDT templates loaded
- `plc.types.<name>` — per-UDT version + field count
- `plc.equipment.count` — equipment-tree size
- `plc.io.cards` — IO card count
- `plc.sync.status` — upload/download state per vendor
- `plc.git.head` — HEAD commit hash
- `plc.git.dirty` — working-tree dirty flag
