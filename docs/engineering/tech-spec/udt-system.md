# UDT System Specification

**Document:** ACG-TS-002-2026  **Version:** 1.0.0

## Core Pattern

Every entity in the ACG system is a UDT instance — a JSON object with three keys:

```json
{
  "udtType": "TypeName",
  "parameters": { },
  "tags": { }
}
```

- **udtType**: References the template defining this instance's schema.
- **parameters**: Authored fields — written by humans or pipelines.
- **tags**: Derived fields — computed by the system (IDs, hashes, timestamps).

## Type Catalog

- [WhitePaper](udt-types/whitepaper.md)
- [Tag](udt-types/tag.md)
- [Component](udt-types/component.md)
- [View](udt-types/view.md)
- [Page](udt-types/page.md)
- [Member](udt-types/member.md)
- [Document](udt-types/document.md)

## Validation Rules

1. `udtType` MUST match a template file name.
2. All `required: true` parameters MUST be present and non-empty.
3. `dataType` MUST match the JSON type.
4. Tags are system-managed — do not author manually.
5. `schema_version` MUST match the template's `version` at ingest time.
