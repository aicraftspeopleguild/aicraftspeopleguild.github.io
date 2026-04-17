# UDT System Specification

**Document:** ACG-TS-002-2026
**Version:** 1.0.0

---

## 1. Core Pattern

Every entity in the ACG system is a UDT instance — a JSON object with three top-level keys:

```json
{
  "udtType": "TypeName",
  "parameters": { },
  "tags": { }
}
```

- **udtType**: References the template that defines this instance's schema.
- **parameters**: Authored fields — written by humans or ingestion pipelines.
- **tags**: Derived fields — computed by the system (IDs, hashes, timestamps, indexes).

## 2. Template Schema

A UDT template defines the shape of its instances:

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "TypeName",
  "version": "1.0.0",
  "description": "What this type represents",
  "parameters": {
    "fieldName": {
      "dataType": "String | StringArray | Int | Boolean | JSON",
      "required": true | false,
      "default": "optional default",
      "description": "What this field means"
    }
  },
  "tags": {
    "fieldName": {
      "dataType": "String | StringArray | Int",
      "description": "What the system derives"
    }
  }
}
```

## 3. Type Catalog

### 3.1 WhitePaper

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "WhitePaper",
  "version": "1.0.0",
  "description": "A Guild white paper, position paper, or research publication.",
  "parameters": {
    "title":            { "dataType": "String",      "required": true },
    "authors":          { "dataType": "StringArray",  "required": true },
    "publication_date": { "dataType": "String",      "required": false },
    "doc_number":       { "dataType": "String",      "required": false },
    "source_medium":    { "dataType": "String",      "required": false },
    "summary":          { "dataType": "String",      "required": false },
    "tags":             { "dataType": "StringArray",  "required": false },
    "status":           { "dataType": "String",      "required": false, "default": "published" },
    "site_href":        { "dataType": "String",      "required": false }
  },
  "tags": {
    "id":                    { "dataType": "String" },
    "original_path":         { "dataType": "String" },
    "original_format":       { "dataType": "String" },
    "original_hash_sha256":  { "dataType": "String" },
    "body":                  { "dataType": "String" },
    "instance_path":         { "dataType": "String" },
    "ingested_at":           { "dataType": "String" },
    "schema_version":        { "dataType": "String" }
  }
}
```

### 3.2 Tag

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Tag",
  "version": "1.0.0",
  "description": "A topic tag that indexes entities.",
  "parameters": {
    "name":        { "dataType": "String", "required": true },
    "label":       { "dataType": "String", "required": false },
    "description": { "dataType": "String", "required": false }
  },
  "tags": {
    "paper_ids":    { "dataType": "StringArray" },
    "count":        { "dataType": "Int" },
    "last_updated": { "dataType": "String" }
  }
}
```

### 3.3 Component

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Component",
  "version": "1.0.0",
  "description": "A reusable UI component with typed props and slot definitions.",
  "parameters": {
    "name":        { "dataType": "String",      "required": true,  "description": "PascalCase component name" },
    "tag":         { "dataType": "String",      "required": false, "default": "div", "description": "HTML element tag" },
    "cssClass":    { "dataType": "String",      "required": false, "description": "Root CSS class(es)" },
    "description": { "dataType": "String",      "required": false },
    "category":    { "dataType": "String",      "required": false, "description": "atomic | composite | layout | page-level" },
    "props":       { "dataType": "JSON",        "required": false, "description": "Prop name → { type, required, default }" },
    "slots":       { "dataType": "StringArray", "required": false, "description": "Named insertion points for children" },
    "template":    { "dataType": "String",      "required": false, "description": "HTML template string with {{ prop }} bindings" }
  },
  "tags": {
    "id":             { "dataType": "String" },
    "file_path":      { "dataType": "String" },
    "dependencies":   { "dataType": "StringArray", "description": "Component IDs this depends on" },
    "used_by_views":  { "dataType": "StringArray", "description": "View IDs that use this component" },
    "schema_version": { "dataType": "String" }
  }
}
```

### 3.4 View

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "View",
  "version": "1.0.0",
  "description": "A page-level component tree with data bindings.",
  "parameters": {
    "name":        { "dataType": "String",  "required": true },
    "description": { "dataType": "String",  "required": false },
    "root":        { "dataType": "JSON",    "required": true, "description": "Component tree root node" }
  },
  "tags": {
    "id":               { "dataType": "String" },
    "component_ids":    { "dataType": "StringArray", "description": "All components used in this view" },
    "data_sources":     { "dataType": "StringArray", "description": "JSON paths referenced by bindings" },
    "schema_version":   { "dataType": "String" }
  }
}
```

### 3.5 Page

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Page",
  "version": "1.0.0",
  "description": "A route entry binding a URL path to a view and data sources.",
  "parameters": {
    "title":       { "dataType": "String",      "required": true },
    "slug":        { "dataType": "String",      "required": true },
    "route":       { "dataType": "String",      "required": true, "description": "URL path pattern" },
    "view":        { "dataType": "String",      "required": true, "description": "Path to view.json" },
    "data":        { "dataType": "JSON",        "required": false, "description": "Named data source paths" },
    "stylesheets": { "dataType": "StringArray", "required": false },
    "section":     { "dataType": "String",      "required": false },
    "parent_slug": { "dataType": "String",      "required": false },
    "status":      { "dataType": "String",      "required": false, "default": "published" }
  },
  "tags": {
    "id":             { "dataType": "String" },
    "view_id":        { "dataType": "String" },
    "schema_version": { "dataType": "String" }
  }
}
```

### 3.6 Member

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Member",
  "version": "1.0.0",
  "description": "A Guild member profile.",
  "parameters": {
    "name":           { "dataType": "String",      "required": true },
    "role":           { "dataType": "String",      "required": false, "description": "founder | core | contributor | advisor" },
    "title":          { "dataType": "String",      "required": false, "description": "Professional title" },
    "bio":            { "dataType": "String",      "required": false },
    "avatar_href":    { "dataType": "String",      "required": false },
    "expertise_tags": { "dataType": "StringArray", "required": false },
    "links":          { "dataType": "JSON",        "required": false, "description": "{ github, linkedin, website }" },
    "joined_date":    { "dataType": "String",      "required": false }
  },
  "tags": {
    "id":              { "dataType": "String" },
    "slug":            { "dataType": "String" },
    "paper_ids":       { "dataType": "StringArray", "description": "Papers this member authored" },
    "instance_path":   { "dataType": "String" },
    "schema_version":  { "dataType": "String" }
  }
}
```

### 3.7 Document

```json:udt:Template
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "udtType": "Document",
  "version": "1.0.0",
  "description": "An engineering document (URS, tech spec, architecture record).",
  "parameters": {
    "title":      { "dataType": "String",      "required": true },
    "doc_number": { "dataType": "String",      "required": false },
    "doc_type":   { "dataType": "String",      "required": true, "description": "urs | tech-spec | architecture | adr" },
    "version":    { "dataType": "String",      "required": false },
    "authors":    { "dataType": "StringArray", "required": false },
    "status":     { "dataType": "String",      "required": false, "default": "draft" },
    "summary":    { "dataType": "String",      "required": false },
    "tags":       { "dataType": "StringArray", "required": false }
  },
  "tags": {
    "id":             { "dataType": "String" },
    "source_path":    { "dataType": "String" },
    "schema_version": { "dataType": "String" }
  }
}
```

## 4. Instance Validation Rules

1. `udtType` MUST match a template file name (case-sensitive).
2. All `required: true` parameters MUST be present and non-empty.
3. `dataType` MUST match the JSON type (`String` → string, `StringArray` → array of strings, `Int` → number, `Boolean` → boolean, `JSON` → object or array).
4. Tags are system-managed — instances SHOULD NOT author tag values manually.
5. `schema_version` in tags MUST match the template's `version` field at ingestion time.

## 5. UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "UDT System Specification",
    "doc_number": "ACG-TS-002-2026",
    "doc_type": "tech-spec",
    "version": "1.0.0",
    "authors": ["Thomas Frumkin"],
    "status": "draft",
    "summary": "Defines the UDT type system pattern, all entity type templates (WhitePaper, Tag, Component, View, Page, Member, Document), and instance validation rules.",
    "tags": ["udt", "type-system", "schema", "templates"]
  },
  "tags": {
    "id": "acg-ts-002-2026",
    "source_path": "docs/engineering/tech-spec/udt-system.md",
    "schema_version": "1.0.0"
  }
}
```
