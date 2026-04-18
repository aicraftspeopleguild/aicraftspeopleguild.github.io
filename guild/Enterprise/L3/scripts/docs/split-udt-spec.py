#!/usr/bin/env python3
# @tag-event
# {
#   "id": "split-udt-spec:on-docs-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "docs.engineering.tech-spec.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "docs.udt-spec.split_at"
#   ]
# }
# @end-tag-event
"""Split tech-spec/udt-system.md into per-type files."""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "udt-system.md"
DEST = HERE / "udt-types"

SECTION_RE = re.compile(
    r"^###\s+3\.\d+\s+(\w+)\n\n```json:udt:Template\s*\n(.+?)\n```",
    re.DOTALL | re.MULTILINE
)

def main():
    text = SRC.read_text(encoding="utf-8")
    DEST.mkdir(exist_ok=True)
    matches = list(SECTION_RE.finditer(text))
    print(f"Found {len(matches)} UDT types")
    names = []
    for m in matches:
        name = m.group(1)
        block = m.group(2).strip()
        slug = name.lower().replace(" ", "-")
        content = f"# {name} UDT\n\n```json:udt:Template\n{block}\n```\n"
        (DEST / f"{slug}.md").write_text(content, encoding="utf-8")
        names.append((name, slug))
        print(f"  [write] udt-types/{slug}.md")

    # Rewrite the main spec to reference the split files
    toc_lines = ["# UDT System Specification",
                 "",
                 "**Document:** ACG-TS-002-2026  **Version:** 1.0.0",
                 "",
                 "## Core Pattern",
                 "",
                 "Every entity in the ACG system is a UDT instance — a JSON object with three keys:",
                 "",
                 "```json",
                 "{",
                 '  "udtType": "TypeName",',
                 '  "parameters": { },',
                 '  "tags": { }',
                 "}",
                 "```",
                 "",
                 "- **udtType**: References the template defining this instance's schema.",
                 "- **parameters**: Authored fields — written by humans or pipelines.",
                 "- **tags**: Derived fields — computed by the system (IDs, hashes, timestamps).",
                 "",
                 "## Type Catalog",
                 ""]
    for name, slug in names:
        toc_lines.append(f"- [{name}](udt-types/{slug}.md)")
    toc_lines += ["",
                  "## Validation Rules",
                  "",
                  "1. `udtType` MUST match a template file name.",
                  "2. All `required: true` parameters MUST be present and non-empty.",
                  "3. `dataType` MUST match the JSON type.",
                  "4. Tags are system-managed — do not author manually.",
                  "5. `schema_version` MUST match the template's `version` at ingest time.",
                  ""]
    SRC.write_text("\n".join(toc_lines), encoding="utf-8")
    print(f"[split] {SRC.name} is now a TOC ({sum(len(l) for l in toc_lines)} chars)")

if __name__ == "__main__":
    main()
