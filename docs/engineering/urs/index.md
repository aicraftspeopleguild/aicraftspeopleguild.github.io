# User Requirements Specification — ACG Guild Site

**Document:** ACG-URS-001-2026
**Version:** 1.0.0
**Status:** Draft
**Authors:** Thomas Frumkin, ACG Technical Committee

---

## 1. Purpose

The AI Craftspeople Guild website serves as the public face, knowledge base, and governance record of the Guild. This URS defines what the site must do, who it serves, and what constraints apply — independent of implementation.

## 2. Stakeholders

| Role | Needs |
|------|-------|
| Guild Members | Publish white papers, maintain profiles, participate in rituals |
| Visitors | Read manifesto, browse papers, understand the Guild's position |
| Contributors | Submit papers, sign manifesto, join mob sessions |
| Maintainers | Add pages, update content, deploy without breaking links |

## 3. Functional Requirements

### FR-01: Content Publishing

- **FR-01.1**: The site SHALL display white papers, position papers, experimental papers, research notes, and knowledge-about-knowledge publications.
- **FR-01.2**: Each paper SHALL have: title, author(s), date, optional document number, summary, topic tags, and status.
- **FR-01.3**: Papers SHALL be browseable from a central index with card-based layout.
- **FR-01.4**: Papers SHALL be cross-referenceable (paper A links to paper B).

### FR-02: Member Directory

- **FR-02.1**: The site SHALL maintain a directory of Guild members.
- **FR-02.2**: Each member SHALL have: name, role, bio, portrait photo, expertise tags, and optional links.
- **FR-02.3**: Member profiles SHALL be accessible from the directory and from authored papers.

### FR-03: Governance Documents

- **FR-03.1**: The site SHALL publish the Guild Charter, Code of Conduct, Manifesto, and Mission Statement.
- **FR-03.2**: Governance documents SHALL be versioned and linkable.

### FR-04: Manifesto Signatures

- **FR-04.1**: Visitors SHALL be able to sign the manifesto via a web form.
- **FR-04.2**: Signatures SHALL be stored in Google Sheets and displayed on the home page.

### FR-05: Navigation

- **FR-05.1**: Every page SHALL have a path back to the home page.
- **FR-05.2**: Every sub-page SHALL have a path back to its parent index.
- **FR-05.3**: The home page SHALL link to all major site sections.

### FR-06: Component Reuse

- **FR-06.1**: Common UI patterns (header, footer, cards, navigation) SHALL be defined as reusable components.
- **FR-06.2**: Components SHALL be described by UDT instances with typed props.
- **FR-06.3**: Pages SHALL be composable from component instances via a view renderer.

### FR-07: Ingestion Pipeline

- **FR-07.1**: New content SHALL be ingestible from Markdown, CSV, HTML, or plain text sources.
- **FR-07.2**: Ingestion SHALL be idempotent — re-running with unchanged sources produces no changes.
- **FR-07.3**: Ingestion SHALL generate UDT instances and rebuild tag indexes automatically.

## 4. Non-Functional Requirements

### NFR-01: Static Hosting

- The site SHALL deploy as static files on GitHub Pages with no server-side runtime.

### NFR-02: Performance

- Pages SHALL load without JavaScript for core content (progressive enhancement).
- The renderer SHALL hydrate from JSON manifests without blocking first paint.

### NFR-03: Accessibility

- All images SHALL have alt text.
- Navigation SHALL be keyboard-accessible.
- Color contrast SHALL meet WCAG AA.

### NFR-04: Maintainability

- Adding a new page type SHALL require only: a UDT template, a view template, and a registry entry.
- No HTML duplication across pages — shared structure lives in component templates.

## 5. UDT Instance

```json:udt:Document
{
  "udtType": "Document",
  "parameters": {
    "title": "User Requirements Specification — ACG Guild Site",
    "doc_number": "ACG-URS-001-2026",
    "doc_type": "urs",
    "version": "1.0.0",
    "authors": ["Thomas Frumkin", "ACG Technical Committee"],
    "status": "draft",
    "summary": "Defines functional and non-functional requirements for the ACG Guild website including content publishing, member directory, governance, component reuse, and ingestion pipeline.",
    "tags": ["requirements", "site-architecture", "urs"]
  },
  "tags": {
    "id": "acg-urs-001-2026",
    "source_path": "docs/engineering/urs/index.md",
    "schema_version": "1.0.0"
  }
}
```
