# ACG Engineering Documentation

Technical specifications, architecture decisions, and component catalog for the AI Craftspeople Guild site.

## Directory Structure

```
docs/engineering/
├── urs/                    # User Requirements Specifications
│   └── index.md            # Site-wide URS
├── tech-spec/              # Technical Specifications
│   ├── index.md            # Master tech spec
│   ├── udt-system.md       # UDT/Tag type system spec
│   └── renderer.md         # View renderer spec
├── architecture/           # Architecture Decision Records
│   └── index.md            # System architecture overview
└── component-catalog/      # Component library reference
    └── index.md            # Full catalog with UDT instances
```

## Convention

All UDT and Tag instances in these docs are embedded in fenced code blocks tagged with the language `json:udt` or `json:tag`. These blocks are machine-parseable — the ingest pipeline can extract them to seed the `udts/instances/` directories.

Example:

````
```json:udt:Component
{ "udtType": "Component", "parameters": { ... }, "tags": { ... } }
```
````

The format is `json:udt:<TypeName>` or `json:tag:<TypeName>` so tooling can filter by entity type.
