# Document UDT

Engineering document metadata — the structured header carried by every `docs/` markdown file.

## YAML

```yaml:udt:Document
name: Document
version: 1.0.0
fields:
  doc_id:    { type: string, required: true,  pattern: "^ACG-[A-Z]+-\\d{3}-\\d{4}$", description: "e.g. ACG-TS-003-2026" }
  title:     { type: string, required: true }
  version:   { type: string, required: true,  description: "semver string" }
  category:  { type: enum,   required: true,  values: [tech-spec, standard, urs, architecture, component-catalog, template] }
  status:    { type: enum,   required: false, values: [draft, review, published, archived], default: draft }
  author:    { type: string, required: false }
  date:      { type: string, required: false, format: iso8601-date }
  tags:      { type: string-array, required: false }
  path:      { type: string, required: false, description: "Repo-relative path to this file" }
```

## Python

```python:udt:Document
from dataclasses import dataclass, field
from typing import Literal
Category = Literal["tech-spec","standard","urs","architecture","component-catalog","template"]
Status   = Literal["draft","review","published","archived"]

@dataclass
class Document:
    doc_id: str
    title: str
    version: str
    category: Category
    status: Status = "draft"
    author: str | None = None
    date: str | None = None
    tags: list[str] = field(default_factory=list)
    path: str | None = None
```

## SQL

```sql:udt:Document
CREATE TABLE IF NOT EXISTS documents (
    doc_id   TEXT PRIMARY KEY,
    title    TEXT NOT NULL,
    version  TEXT NOT NULL,
    category TEXT NOT NULL,
    status   TEXT NOT NULL DEFAULT 'draft',
    author   TEXT,
    date     TEXT,
    path     TEXT
);
```
