# Member UDT

A Guild member — either a signatory of the manifesto or an active contributor with a profile page.

## YAML

```yaml:udt:Member
name: Member
version: 1.0.0
fields:
  handle:         { type: string, required: true, description: "URL slug" }
  name:           { type: string, required: true }
  role:           { type: string, required: false, description: "founder|core|contributor|advisor" }
  org:            { type: string, required: false }
  joined:         { type: string, required: false, format: iso8601-date }
  signed:         { type: bool,   required: false, default: false }
  bio:            { type: string, required: false }
  avatar_href:    { type: string, required: false }
  expertise_tags: { type: string-array, required: false }
```

## Python

```python:udt:Member
from dataclasses import dataclass, field

@dataclass
class Member:
    handle: str
    name: str
    role: str | None = None
    org: str | None = None
    joined: str | None = None
    signed: bool = False
    bio: str | None = None
    avatar_href: str | None = None
    expertise_tags: list[str] = field(default_factory=list)
```

## SQL

```sql:udt:Member
CREATE TABLE IF NOT EXISTS members (
    handle       TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    role         TEXT,
    org          TEXT,
    joined       TEXT,
    signed       INTEGER NOT NULL DEFAULT 0,
    bio          TEXT,
    avatar_href  TEXT
);
```

## TypeScript

```typescript:udt:Member
export interface Member {
  handle: string;
  name: string;
  role?: string;
  org?: string;
  joined?: string;
  signed?: boolean;
  bio?: string;
  avatar_href?: string;
  expertise_tags?: string[];
}
```

## JSON Schema

```json-schema:udt:Member
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "$id": "acg.udt.Member",
  "type": "object",
  "required": ["handle","name"],
  "properties": {
    "handle": {"type":"string"},
    "name":   {"type":"string"},
    "role":   {"type":"string"},
    "org":    {"type":"string"},
    "joined": {"type":"string","format":"date"},
    "signed": {"type":"boolean","default":false},
    "bio":    {"type":"string"},
    "avatar_href":   {"type":"string"},
    "expertise_tags":{"type":"array","items":{"type":"string"}}
  }
}
```

## Instance

```json:udt:Member
{
  "handle": "alex-bunardzic",
  "name": "Alex Bunardzic",
  "role": "founder",
  "joined": "2026-01-15",
  "signed": true,
  "expertise_tags": ["tdd","mutation-testing","calibration"]
}
```
