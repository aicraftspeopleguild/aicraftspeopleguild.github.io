#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-path-graph:on-paths-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "paths.source.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "paths.graph.rebuilt_at"
#   ]
# }
# @end-tag-event
# @script
# id: build-path-graph
# label: Build URL-path graph (deprecated shim)
# category: generate
# description: Deprecated — delegates to gen-tag-db.py.
# depends_on:
#   - gen-tag-db
"""
DEPRECATED — superseded by guild/web/scripts/paths/gen-tag-db.py.
"""
import subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
NEW  = REPO / "guild" / "web" / "scripts" / "paths" / "gen-tag-db.py"

if __name__ == "__main__":
    print("[build-path-graph] DEPRECATED — delegating to gen-tag-db.py")
    sys.exit(subprocess.call([sys.executable, str(NEW)]))
#!/usr/bin/env python3
"""
DEPRECATED — superseded by guild/web/scripts/paths/gen-tag-db.py.

The URL-path graph and tag index now live inside the root `tag.db`
(under `graphs.url_paths` and `indexes.*`). This script is kept as a
thin shim so existing call sites don't break; it just delegates to the
new consolidator.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
NEW  = REPO / "guild" / "web" / "scripts" / "paths" / "gen-tag-db.py"

if __name__ == "__main__":
    print("[build-path-graph] DEPRECATED — delegating to gen-tag-db.py")
    sys.exit(subprocess.call([sys.executable, str(NEW)]))
#!/usr/bin/env python3
"""
DEPRECATED — superseded by guild/web/scripts/paths/gen-tag-db.py.

The URL-path graph and tag index now live inside the root `tag.db`
(under `graphs.url_paths` and `indexes.*`). This script is kept as a
thin shim so existing call sites don't break; it just delegates to the
new consolidator.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
NEW  = REPO / "guild" / "web" / "scripts" / "paths" / "gen-tag-db.py"

if __name__ == "__main__":
    print("[build-path-graph] DEPRECATED — delegating to gen-tag-db.py")
    sys.exit(subprocess.call([sys.executable, str(NEW)]))

import json, sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
PATHS_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "paths"
TAGS_DIR  = PATHS_DIR / "tags"

sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
from packml import Process, path_exists, has_files  # type: ignore

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_paths():
    out = {}
    for f in sorted(PATHS_DIR.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        pid = d.get("tags", {}).get("id") or f.stem
        out[pid] = d
    return out

def compute_breadcrumb(pid, paths, seen=None):
    seen = seen or set()
    if pid in seen: return [pid]  # cycle guard
    seen.add(pid)
    p = paths.get(pid)
    if not p: return [pid]
    parent = p.get("parameters", {}).get("parent")
    if not parent or parent == pid:
        return [pid]
    return compute_breadcrumb(parent, paths, seen) + [pid]

def build_catalog(paths):
    now = _now()

    by_section  = {}
    by_parent   = {}
    by_depth    = {}
    by_kind     = {"static": [], "dynamic": []}
    dependents  = {pid: [] for pid in paths}
    errors      = []

    for pid, p in paths.items():
        params = p.get("parameters", {})
        tags   = p.get("tags", {})
        section = params.get("section") or "meta"
        parent  = params.get("parent")
        kind    = "dynamic" if params.get("dynamic") else "static"
        depth   = tags.get("depth", 0)

        by_section.setdefault(section, []).append(pid)
        by_kind[kind].append(pid)
        by_depth.setdefault(str(depth), []).append(pid)
        if parent:
            by_parent.setdefault(parent, []).append(pid)
            if parent not in paths and parent != "home":
                errors.append(f"{pid}: parent '{parent}' not found")

        # Dependency edges
        for dep in params.get("dependencies") or []:
            if dep in dependents:
                dependents[dep].append(pid)

    # Tag UDT per index
    def tag_index(name, map_):
        return {
            "udtType": "Tag",
            "parameters": {"name": name, "label": name.replace("_"," ").title(),
                           "description": f"Path index by {name}"},
            "tags": {
                "path_ids":     sorted(set(sum(map_.values(), []))) if isinstance(list(map_.values())[0], list) else [],
                "groups":       {k: sorted(v) for k, v in map_.items()},
                "count":        sum(len(v) for v in map_.values()),
                "last_updated": now,
            }
        }

    catalog = {
        "generated_at": now,
        "count": len(paths),
        "tags": {
            "by_section": tag_index("by_section", by_section),
            "by_parent":  tag_index("by_parent",  by_parent),
            "by_depth":   tag_index("by_depth",   by_depth),
            "by_kind":    tag_index("by_kind",    by_kind),
            "dependents": {
                "udtType": "Tag",
                "parameters": {"name": "dependents",
                               "label": "Reverse dependencies",
                               "description": "path_id → paths that depend on it"},
                "tags": {
                    "map": {k: sorted(v) for k, v in dependents.items() if v},
                    "last_updated": now
                }
            }
        },
        "errors": errors
    }
    return catalog

def build_graph(paths):
    """Produce a node/edge graph for visualization / validation."""
    nodes, edges = [], []
    for pid, p in paths.items():
        params = p.get("parameters", {})
        tags   = p.get("tags", {})
        nodes.append({
            "id":      pid,
            "label":   params.get("label") or pid,
            "section": params.get("section") or "meta",
            "depth":   tags.get("depth", 0),
            "dynamic": bool(params.get("dynamic")),
            "path":    params.get("path"),
            "page":    params.get("page"),
        })
        parent = params.get("parameters", {}).get("parent") or params.get("parent")
        if parent:
            edges.append({"from": parent, "to": pid, "kind": "parent"})
        for dep in params.get("dependencies") or []:
            edges.append({"from": dep, "to": pid, "kind": "dependency"})

    return {
        "generated_at": _now(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges
    }

def main():
    TAGS_DIR.mkdir(parents=True, exist_ok=True)
    paths = load_paths()
    print(f"[path-graph] loaded {len(paths)} Path UDT instances")

    catalog = build_catalog(paths)
    (TAGS_DIR / "index.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")

    graph = build_graph(paths)
    (PATHS_DIR / "_graph.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary
    sects = catalog["tags"]["by_section"]["tags"]["groups"]
    for sec in sorted(sects):
        print(f"  {sec:<12} {len(sects[sec])} paths")
    if catalog["errors"]:
        print(f"[path-graph] {len(catalog['errors'])} validation errors:")
        for e in catalog["errors"]:
            print("  -", e)
    print(f"[path-graph] wrote tags/index.json and _graph.json "
          f"({graph['edge_count']} edges)")

if __name__ == "__main__":
    with Process(
        "pages--build-path-graph_py",
        pre_checks=[has_files(PATHS_DIR / "*.json", min_count=10)],
        post_checks=[
            path_exists(TAGS_DIR / "index.json"),
            path_exists(PATHS_DIR / "_graph.json"),
        ],
    ):
        main()
