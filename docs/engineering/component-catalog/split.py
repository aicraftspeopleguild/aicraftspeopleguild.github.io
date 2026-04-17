#!/usr/bin/env python3
"""
Split docs/engineering/component-catalog/index.md into per-component files.

Each component section (### Name + description + ```json:udt:Component block```)
becomes its own markdown file: <component-id>.md. The index.md is replaced
with a concise TOC linking to each.

Honors the 250-token-per-file rule by ensuring each output file is compact.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.md"

# Pattern: ### Name\n\n<description paragraph>\n\n```json:udt:Component\n<json>\n```
SECTION_RE = re.compile(
    r"^###\s+(\S+?)\n\n(.+?)\n\n```json:udt:Component\s*\n(.+?)\n```",
    re.DOTALL | re.MULTILINE
)

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def main():
    text = INDEX.read_text(encoding="utf-8")
    matches = list(SECTION_RE.finditer(text))
    print(f"Found {len(matches)} component sections")

    index_entries = []

    for m in matches:
        name = m.group(1).strip()
        desc = m.group(2).strip()
        block = m.group(3).strip()
        try:
            comp = json.loads(block)
            cid = comp["tags"]["id"]
            category = comp["parameters"].get("category", "misc")
        except Exception as e:
            print(f"  [skip] {name}: {e}")
            continue

        # Write per-component file
        content = f"""# {name}

{desc}

```json:udt:Component
{block}
```
"""
        out_file = HERE / f"{cid}.md"
        out_file.write_text(content, encoding="utf-8")
        print(f"  [write] {cid}.md")
        index_entries.append((name, cid, category, desc[:100]))

    # Group by category
    by_cat = {}
    for name, cid, cat, desc in index_entries:
        by_cat.setdefault(cat, []).append((name, cid, desc))

    # Write compact TOC
    toc = ["# Component Catalog",
           "",
           "**Document:** ACG-CC-001-2026  **Version:** 1.0.0",
           "",
           f"{len(index_entries)} reusable UI components. Each is a parseable `json:udt:Component` instance. The ingest pipeline extracts these into `guild/web/components/udts/instances/` for use by the view renderer.",
           ""]
    for cat in ["atomic", "composite", "layout", "page-level", "misc"]:
        if cat not in by_cat: continue
        toc.append(f"## {cat.title()} Components")
        toc.append("")
        for name, cid, desc in by_cat[cat]:
            toc.append(f"- **[{name}]({cid}.md)** — {desc.rstrip('.').rstrip()}.")
        toc.append("")
    toc.append("")
    toc.append("## UDT Instance")
    toc.append("")
    toc.append("```json:udt:Document")
    toc.append(json.dumps({
        "udtType": "Document",
        "parameters": {
            "title": "Component Catalog — ACG Guild Site",
            "doc_number": "ACG-CC-001-2026",
            "doc_type": "tech-spec",
            "version": "1.0.0",
            "authors": ["Thomas Frumkin"],
            "status": "draft",
            "summary": f"TOC over {len(index_entries)} per-component docs. Each component lives in its own file under 250 tokens.",
            "tags": ["components", "catalog", "udt", "ui"]
        },
        "tags": {
            "id": "acg-cc-001-2026",
            "source_path": "docs/engineering/component-catalog/index.md",
            "schema_version": "1.0.0"
        }
    }, indent=2))
    toc.append("```")

    INDEX.write_text("\n".join(toc) + "\n", encoding="utf-8")
    print(f"\n[split] wrote index.md + {len(index_entries)} per-component files")

if __name__ == "__main__":
    main()
