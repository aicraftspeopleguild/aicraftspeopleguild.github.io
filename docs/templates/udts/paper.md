# Paper UDT

A Guild publication — white paper, position paper, experimental, research note, knowledge-about-knowledge, or standard.

## Source of truth — YAML

```yaml:udt:Paper
name: Paper
version: 1.0.0
fields:
  id:               { type: string, required: true,  pattern: "^ACG-[A-Z]+-\\d+-\\d{4}$" }
  type:             { type: enum,   required: true,  values: [white-paper, position-paper, experimental, research-note, knowledge, standard] }
  title:            { type: string, required: true,  max: 120 }
  author:           { type: string, required: true }
  date:             { type: string, required: true,  format: iso8601-date }
  status:           { type: enum,   required: false, values: [draft, review, published, archived], default: draft }
  tags:             { type: string-array, required: false }
  abstract:         { type: string, required: true,  min_words: 60, max_words: 400 }
  slug:             { type: string, required: true }
  doc_number:       { type: string, required: false }
  publication_date: { type: string, required: false }
```

## Python

```python:udt:Paper
from dataclasses import dataclass, field
from typing import Literal
PaperType   = Literal["white-paper","position-paper","experimental","research-note","knowledge","standard"]
PaperStatus = Literal["draft","review","published","archived"]

@dataclass
class Paper:
    id: str
    type: PaperType
    title: str
    author: str
    date: str
    abstract: str
    slug: str
    status: PaperStatus = "draft"
    tags: list[str] = field(default_factory=list)
    doc_number: str | None = None
    publication_date: str | None = None
```

## SQL

```sql:udt:Paper
CREATE TABLE IF NOT EXISTS papers (
    id         TEXT PRIMARY KEY,
    type       TEXT NOT NULL CHECK(type IN ('white-paper','position-paper','experimental','research-note','knowledge','standard')),
    title      TEXT NOT NULL,
    author     TEXT NOT NULL,
    date       TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','review','published','archived')),
    abstract   TEXT NOT NULL,
    slug       TEXT NOT NULL UNIQUE,
    doc_number TEXT,
    publication_date TEXT
);
```

## TypeScript

```typescript:udt:Paper
export type PaperType   = "white-paper"|"position-paper"|"experimental"|"research-note"|"knowledge"|"standard";
export type PaperStatus = "draft"|"review"|"published"|"archived";
export interface Paper {
  id: string;
  type: PaperType;
  title: string;
  author: string;
  date: string;
  abstract: string;
  slug: string;
  status?: PaperStatus;
  tags?: string[];
  doc_number?: string;
  publication_date?: string;
}
```

## JSON Schema

```json-schema:udt:Paper
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "$id": "acg.udt.Paper",
  "type": "object",
  "required": ["id","type","title","author","date","abstract","slug"],
  "properties": {
    "id":     {"type":"string","pattern":"^ACG-[A-Z]+-\\d+-\\d{4}$"},
    "type":   {"enum":["white-paper","position-paper","experimental","research-note","knowledge","standard"]},
    "title":  {"type":"string","maxLength":120},
    "author": {"type":"string"},
    "date":   {"type":"string","format":"date"},
    "status": {"enum":["draft","review","published","archived"],"default":"draft"},
    "tags":   {"type":"array","items":{"type":"string"}},
    "abstract":{"type":"string"},
    "slug":   {"type":"string"}
  }
}
```

## Example instance

```json:udt:Paper
{
  "id": "ACG-WP-002-2026",
  "type": "white-paper",
  "title": "The Harm Equation",
  "author": "Thomas Frumkin",
  "date": "2026-02-22",
  "status": "published",
  "tags": ["ethics","risk","harm"],
  "abstract": "A structural white paper on why large-scale AI harms recur...",
  "slug": "the-harm-equation",
  "doc_number": "ACG-WP-002-2026"
}
```
