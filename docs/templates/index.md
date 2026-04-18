# ACG Templates — UDT Source of Truth

Every ACG domain type is defined **once**, in code blocks across six languages. A generator script can extract each block and emit native type code per language.

## UDTs

- [Tag](udts/tag.md) — topic/expertise/routing tag
- [Paper](udts/paper.md) — Guild publication
- [Member](udts/member.md) — Guild member profile
- [Experiment](udts/experiment.md) — ritual experiment card
- [Component](udts/component.md) — reusable UI component
- [View](udts/view.md) — Perspective-style view
- [Page](udts/page.md) — route binding
- [Path](udts/path.md) — URL path entry
- [Program](udts/program.md) — build pipeline program
- [PackMLState](udts/packml-state.md) — state machine run record
- [App](udts/app.md) — addressable render unit
- [Document](udts/document.md) — engineering doc metadata

## Block format

Each UDT file embeds the same type in parseable code blocks:

| Lang         | Fence tag                  | Purpose                       |
|--------------|----------------------------|-------------------------------|
| YAML         | `yaml:udt:<Name>`          | Source-of-truth schema        |
| Python       | `python:udt:<Name>`        | dataclass / TypedDict         |
| SQL          | `sql:udt:<Name>`           | CREATE TABLE                  |
| TypeScript   | `typescript:udt:<Name>`    | `interface` / `type`          |
| JSON Schema  | `json-schema:udt:<Name>`   | Draft 07 JSON Schema          |
| JSON (instance) | `json:udt:<Name>`       | Example instance              |

The ingest pipeline (`scripts/templates/extract.py`) scans this directory and writes each block to `guild/web/generated/<lang>/<Name>.{yml,py,sql,ts,json}`.

## Views

See [views/](views/) for Perspective view templates.
