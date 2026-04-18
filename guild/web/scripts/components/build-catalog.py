#!/usr/bin/env python3
"""
Build nested UDT/tag catalog for components.

From components/udts/instances/*.json, produce:
  - components/tags/index.json  (Tag UDT instances: category → component IDs)
  - components/index.json       (manifest: counts, schema version, component list)

This mirrors the white-papers pipeline (ingest.py) pattern of inverted-
indexing authored instances into derived catalogs.
"""
import json, glob, sys
from pathlib import Path
from datetime import datetime, timezone

# Import the PackML wrapper (scripts/lib/packml.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from packml import Process, path_exists, has_files

HERE = Path(__file__).resolve().parent
COMPONENTS_DIR = HERE.parent.parent / "components"
INSTANCES_DIR = COMPONENTS_DIR / "udts" / "instances"
TAGS_DIR = COMPONENTS_DIR / "tags"
TEMPLATE_FILE = COMPONENTS_DIR / "udts" / "templates" / "component.udt.json"

def load_template_version():
    if TEMPLATE_FILE.exists():
        return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8")).get("version", "1.0.0")
    return "1.0.0"

def main():
    TAGS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    schema = load_template_version()

    categories = {}
    deps_by_component = {}
    used_by_views = {}
    components = []

    for f in sorted(INSTANCES_DIR.glob("*.json")):
        inst = json.loads(f.read_text(encoding="utf-8"))
        params = inst.get("parameters", {})
        tags = inst.get("tags", {})
        cid = tags.get("id") or f.stem
        cat = params.get("category") or "misc"

        categories.setdefault(cat, []).append(cid)
        deps_by_component[cid] = tags.get("dependencies", []) or []
        used_by_views[cid] = tags.get("used_by_views", []) or []
        components.append({
            "id": cid,
            "name": params.get("name"),
            "category": cat,
            "instance_path": f"udts/instances/{f.name}"
        })

    # Build Tag UDT instances — one per category
    tag_catalog = {
        "generated_at": now,
        "tags": {}
    }
    for cat, ids in sorted(categories.items()):
        tag_catalog["tags"][cat] = {
            "udtType": "Tag",
            "parameters": {
                "name": cat,
                "label": cat.replace("-", " ").title(),
                "description": f"{cat.title()} components"
            },
            "tags": {
                "component_ids": sorted(ids),
                "count": len(ids),
                "last_updated": now
            }
        }
    (TAGS_DIR / "index.json").write_text(
        json.dumps(tag_catalog, indent=2), encoding="utf-8"
    )

    # Manifest
    manifest = {
        "version": "1.0.0",
        "generated_at": now,
        "schema_version": schema,
        "counts": {
            "components": len(components),
            "categories": len(categories)
        },
        "components": components
    }
    (COMPONENTS_DIR / "index.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"[catalog] {len(components)} components, {len(categories)} categories")
    print(f"  tags/index.json     ({len(categories)} Tag instances)")
    print(f"  index.json          (manifest)")

if __name__ == "__main__":
    with Process(
        "components--build-catalog_py",
        pre_checks=[
            path_exists(INSTANCES_DIR),
            has_files(INSTANCES_DIR / "*.json", min_count=10),
        ],
        post_checks=[
            path_exists(TAGS_DIR / "index.json"),
            path_exists(COMPONENTS_DIR / "index.json"),
        ],
    ):
        main()
