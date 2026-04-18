#!/usr/bin/env python3
# @tag-event
# {
#   "id": "components-extract:on-build-start",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "pipeline.build.status",
#     "from": "IDLE",
#     "to":   "RUNNING"
#   },
#   "reads":  ["docs.engineering.component-catalog"],
#   "writes": ["components.extracted.count", "components.extracted.at"]
# }
# @end-tag-event
"""
Extract Component UDT instances from engineering docs.

Scans docs/engineering/**/*.md for fenced code blocks tagged
`json:udt:Component` and writes each as a standalone JSON file in
guild/Enterprise/L2/hmi/web/components/.
"""
import json, re, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DOCS = REPO / "docs" / "engineering"
OUT_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances"

# Pattern: ```json:udt:Component ... ```
BLOCK_RE = re.compile(
    r"```json:udt:Component\s*\n(.*?)\n```",
    re.DOTALL
)

def main():
    if not DOCS.exists():
        print(f"docs dir not found: {DOCS}")
        return

    written = 0
    for md_file in DOCS.rglob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        for match in BLOCK_RE.finditer(text):
            block = match.group(1).strip()
            try:
                data = json.loads(block)
            except json.JSONDecodeError as e:
                print(f"  [skip] {md_file}: malformed JSON ({e})")
                continue

            if data.get("udtType") != "Component":
                continue

            # Derive output filename from tags.id or parameters.name
            comp_id = data.get("tags", {}).get("id") or _slugify(data.get("parameters", {}).get("name", ""))
            if not comp_id:
                print(f"  [skip] {md_file}: no id")
                continue

            out_file = OUT_DIR / f"{comp_id}.json"
            out_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  [write] {out_file.relative_to(REPO)}")
            written += 1

    print(f"\nWrote {written} component files to {OUT_DIR.relative_to(REPO)}/")

def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

if __name__ == "__main__":
    main()
