#!/usr/bin/env python3
# @tag-event
# {
#   "id": "gen-tag-db:on-commit",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "git:state",
#     "from": "HOLD",
#     "to":   "COMPLETE"
#   },
#   "reads":  ["git.head", "guild.**.udt.json"],
#   "writes": ["tag.db.rebuilt_at"]
# }
# @end-tag-event
# @script
# id: gen-tag-db
# label: Generate tag.db
# category: generate
# description: Consolidated tag / UDT index + URL-path / FS-path graphs.
# outputs:
#   - tag.db
#   - "**/tag.db"
# depends_on:
#   - gen-fs-paths
"""
Consolidated tag / UDT index generator.

Produces `tag.db` (JSON) in every non-excluded directory + a global root
`tag.db`. Replaces and supersedes:

  - guild/Enterprise/L2/hmi/web/components/udts/instances/paths/tags/index.json
  - guild/Enterprise/L2/hmi/web/components/udts/instances/paths/_graph.json
  - guild/Enterprise/L2/hmi/web/components/udts/instances/fs-paths/_graph.json

The root tag.db carries everything those files used to carry, plus:
  * every tag observed across the repo (namespaced: `udt:*`, `id:*`,
    `section:*`, `components:*`, `papers:*`, `paths:*`, `members:*`,
    `data_sources:*`, `meta_tags:*`, `dependencies:*`, `provides:*`,
    `ext:*`)
  * a `graphs` block with `url_paths` (URL route graph) + `fs_paths`
    (filesystem graph)
  * an `indexes` block with by_section / by_parent / by_depth / by_kind /
    dependents rollups

Each local tag.db carries only its own files' observations plus the full
UDT instance bodies under `udts` so the dir is fully introspectable from
a single file.
"""
from __future__ import annotations
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
from tagdb_sqlite import write_consolidated  # noqa: E402

EXCLUDE_DIRS = {
    ".git", ".github", ".vscode", ".idea",
    "node_modules", "__pycache__", ".pytest_cache",
    "dist", "build", "out", ".next", ".cache",
    "coverage", ".venv", "venv", "env",
}
DB_FILE = "tag.db"
SCHEMA_VERSION = "2.0.0"

URL_PATHS_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "paths"
FS_PATHS_DIR  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "fs-paths"

LEGACY_FILES = [
    URL_PATHS_DIR / "tags" / "index.json",
    URL_PATHS_DIR / "_graph.json",
    FS_PATHS_DIR  / "_graph.json",
]

REF_FIELDS = {
    ("tags", "component_ids"):      "components",
    ("tags", "paper_ids"):          "papers",
    ("tags", "path_ids"):           "paths",
    ("tags", "member_ids"):         "members",
    ("tags", "data_sources"):       "data_sources",
    ("parameters", "meta_tags"):    "meta_tags",
    ("parameters", "dependencies"): "dependencies",
    ("parameters", "provides"):     "provides",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_excluded(name: str) -> bool:
    return name in EXCLUDE_DIRS


def rel_posix(p: Path) -> str:
    rp = p.relative_to(REPO)
    s = rp.as_posix()
    return s if s else "."


def walk_dirs() -> list[Path]:
    keep: list[Path] = []
    for dirpath, dirnames, _ in os.walk(REPO):
        dirnames[:] = sorted(n for n in dirnames if not is_excluded(n))
        d = Path(dirpath)
        rel = d.relative_to(REPO)
        if any(is_excluded(part) for part in rel.parts):
            continue
        keep.append(d)
    return keep


def scan_json(file: Path) -> tuple[dict, dict | None]:
    obs: dict = {
        "udt_types": [],
        "ids":       [],
        "sections":  [],
        "refs":      defaultdict(list),
        "file_tags": [],
    }
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except Exception:
        return obs, None
    if not isinstance(data, dict):
        return obs, None

    is_udt = "udtType" in data
    ut = data.get("udtType")
    if isinstance(ut, str):
        obs["udt_types"].append(ut)
        obs["file_tags"].append(f"udt:{ut}")

    params = data.get("parameters") if isinstance(data.get("parameters"), dict) else {}
    tags   = data.get("tags")       if isinstance(data.get("tags"), dict)       else {}

    tid = tags.get("id") if isinstance(tags, dict) else None
    if isinstance(tid, str):
        obs["ids"].append(tid)
        obs["file_tags"].append(f"id:{tid}")

    sec = (tags.get("section") if isinstance(tags, dict) else None) or params.get("section")
    if isinstance(sec, str):
        obs["sections"].append(sec)
        obs["file_tags"].append(f"section:{sec}")

    for (scope, key), bucket in REF_FIELDS.items():
        src = data.get(scope)
        if not isinstance(src, dict):
            continue
        vals = src.get(key)
        if isinstance(vals, list):
            for v in vals:
                if isinstance(v, str) and v:
                    obs["refs"][bucket].append(v)
                    obs["file_tags"].append(f"{bucket}:{v}")
    return obs, (data if is_udt else None)


def scan_dir_files(d: Path) -> tuple[dict, list[str], list[dict]]:
    agg = {
        "udt_types": Counter(),
        "ids":       Counter(),
        "sections":  Counter(),
        "refs":      defaultdict(Counter),
        "kinds":     Counter(),
        "tags":      defaultdict(list),
    }
    files: list[str] = []
    udts:  list[dict] = []
    for entry in sorted(d.iterdir()):
        if not entry.is_file():
            continue
        if entry.name.startswith(".") or entry.name in {DB_FILE, "path.json"}:
            continue
        files.append(entry.name)
        ext = entry.suffix.lstrip(".").lower() or "(none)"
        agg["kinds"][ext] += 1
        agg["tags"][f"ext:{ext}"].append(entry.name)
        if ext == "json":
            obs, raw = scan_json(entry)
            for ut in obs["udt_types"]: agg["udt_types"][ut] += 1
            for i  in obs["ids"]:       agg["ids"][i]        += 1
            for s  in obs["sections"]:  agg["sections"][s]   += 1
            for bucket, vals in obs["refs"].items():
                for v in vals: agg["refs"][bucket][v] += 1
            for t in obs["file_tags"]:  agg["tags"][t].append(entry.name)
            if raw is not None:
                rtags = raw.get("tags") if isinstance(raw.get("tags"), dict) else {}
                udts.append({
                    "file":    entry.name,
                    "udtType": raw.get("udtType"),
                    "id":      rtags.get("id"),
                    "body":    raw,
                })
    return agg, files, udts


def build_local(d: Path, rel: str) -> dict:
    agg, files, udts = scan_dir_files(d)
    tags_out: dict = {}
    for tag, flist in sorted(agg["tags"].items()):
        tags_out[tag] = {"count": len(flist), "files": sorted(set(flist))}
    return {
        "dir":            rel,
        "scope":          "local",
        "generated_at":   _now(),
        "schema_version": SCHEMA_VERSION,
        "file_count":     len(files),
        "udt_count":      len(udts),
        "tags":           tags_out,
        "udt_types":      dict(sorted(agg["udt_types"].items())),
        "sections":       dict(sorted(agg["sections"].items())),
        "kinds":          dict(sorted(agg["kinds"].items())),
        "refs":           {k: dict(sorted(v.items())) for k, v in sorted(agg["refs"].items())},
        "ids":            dict(sorted(agg["ids"].items())),
        "udts":           udts,
    }


# -----------------------------------------------------------------------
# Graph builders
# -----------------------------------------------------------------------

def load_url_paths() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not URL_PATHS_DIR.exists():
        return out
    for f in sorted(URL_PATHS_DIR.glob("*.json")):
        if f.name.startswith("_") or f.name == "index.json":
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        pid = (d.get("tags") if isinstance(d.get("tags"), dict) else {}).get("id") or f.stem
        out[pid] = d
    return out


def build_url_path_graph(paths: dict[str, dict]) -> dict:
    nodes, edges = [], []
    by_section, by_parent, by_depth, by_kind = (
        defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    )
    dependents: dict[str, list[str]] = {pid: [] for pid in paths}

    for pid, p in paths.items():
        params = p.get("parameters") if isinstance(p.get("parameters"), dict) else {}
        tags   = p.get("tags")       if isinstance(p.get("tags"), dict)       else {}
        section = params.get("section") or "meta"
        parent  = params.get("parent")
        depth   = tags.get("depth", 0)
        kind    = "dynamic" if params.get("dynamic") else "static"

        nodes.append({
            "id":      pid,
            "label":   params.get("label") or pid,
            "section": section,
            "depth":   depth,
            "dynamic": bool(params.get("dynamic")),
            "path":    params.get("path"),
            "page":    params.get("page"),
        })
        if parent:
            edges.append({"from": parent, "to": pid, "kind": "parent"})
        for dep in params.get("dependencies") or []:
            edges.append({"from": dep, "to": pid, "kind": "dependency"})
            if dep in dependents:
                dependents[dep].append(pid)

        by_section[section].append(pid)
        by_parent[parent or "(root)"].append(pid)
        by_depth[str(depth)].append(pid)
        by_kind[kind].append(pid)

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes":      nodes,
        "edges":      edges,
        "indexes": {
            "by_section": {k: sorted(v) for k, v in sorted(by_section.items())},
            "by_parent":  {k: sorted(v) for k, v in sorted(by_parent.items())},
            "by_depth":   {k: sorted(v) for k, v in sorted(by_depth.items())},
            "by_kind":    {k: sorted(v) for k, v in sorted(by_kind.items())},
            "dependents": {k: sorted(v) for k, v in sorted(dependents.items()) if v},
        },
    }


def build_fs_path_graph(rel_paths: list[str],
                        children_map: dict[str, list[str]],
                        descendants: dict[str, int]) -> dict:
    def _slug(rel: str) -> str:
        return "root" if rel == "." else rel.replace("/", "_").replace(".", "_")
    nodes, edges = [], []
    for rel in sorted(rel_paths):
        nodes.append({
            "id":          _slug(rel),
            "path":        rel,
            "depth":       0 if rel == "." else len(rel.split("/")),
            "children":    len(children_map.get(rel, [])),
            "descendants": descendants.get(rel, 0),
        })
        if rel != ".":
            parent = str(PurePosixPath(rel).parent)
            if parent == ".":
                parent = "."
            edges.append({"from": _slug(parent), "to": _slug(rel), "kind": "contains"})
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes":      nodes,
        "edges":      edges,
    }


# -----------------------------------------------------------------------
# Global rollup
# -----------------------------------------------------------------------

def build_global(local_dbs: dict[str, dict],
                 url_graph: dict,
                 fs_graph:  dict) -> dict:
    global_tags: dict[str, dict] = {}
    udt_types = Counter()
    sections  = Counter()
    kinds     = Counter()
    refs: dict[str, Counter] = defaultdict(Counter)
    ids       = Counter()
    total_files = 0
    total_udts  = 0

    for rel, db in local_dbs.items():
        total_files += db.get("file_count", 0)
        total_udts  += db.get("udt_count", 0)
        for t, info in db.get("tags", {}).items():
            g = global_tags.setdefault(t, {"count": 0, "dirs": [], "sample_files": []})
            g["count"] += info["count"]
            g["dirs"].append(rel)
            if len(g["sample_files"]) < 10:
                for f in info["files"][: 10 - len(g["sample_files"])]:
                    g["sample_files"].append(f"{rel}/{f}" if rel != "." else f)
        for k, v in db.get("udt_types", {}).items(): udt_types[k] += v
        for k, v in db.get("sections", {}).items():  sections[k]  += v
        for k, v in db.get("kinds", {}).items():     kinds[k]     += v
        for bucket, inner in db.get("refs", {}).items():
            for k, v in inner.items(): refs[bucket][k] += v
        for k, v in db.get("ids", {}).items():       ids[k]       += v

    out_tags = {}
    for t, info in sorted(global_tags.items()):
        out_tags[t] = {
            "count":        info["count"],
            "dirs":         sorted(set(info["dirs"])),
            "sample_files": info["sample_files"],
        }

    return {
        "dir":            ".",
        "scope":          "global",
        "generated_at":   _now(),
        "schema_version": SCHEMA_VERSION,
        "dir_count":      len(local_dbs),
        "file_count":     total_files,
        "udt_count":      total_udts,
        "unique_tags":    len(out_tags),
        "tags":           out_tags,
        "udt_types":      dict(sorted(udt_types.items())),
        "sections":       dict(sorted(sections.items())),
        "kinds":          dict(sorted(kinds.items())),
        "refs":           {k: dict(sorted(v.items())) for k, v in sorted(refs.items())},
        "ids":            dict(sorted(ids.items())),
        "graphs": {
            "url_paths": url_graph,
            "fs_paths":  fs_graph,
        },
        "indexes":        url_graph.get("indexes", {}),
    }


def retire_legacy() -> int:
    removed = 0
    for f in LEGACY_FILES:
        if f.exists():
            try:
                f.unlink()
                removed += 1
            except Exception:
                pass
    legacy_tags_dir = URL_PATHS_DIR / "tags"
    if legacy_tags_dir.exists():
        remaining = [p for p in legacy_tags_dir.iterdir()]
        if not remaining:
            try: legacy_tags_dir.rmdir()
            except Exception: pass
    return removed


def main() -> int:
    dirs = walk_dirs()
    rel_paths = [rel_posix(d) for d in dirs]
    abs_by_rel = dict(zip(rel_paths, dirs))

    children_map: dict[str, list[str]] = defaultdict(list)
    for r in rel_paths:
        if r == ".":
            continue
        parent = str(PurePosixPath(r).parent)
        if parent == ".": parent = "."
        children_map[parent].append(r)
    for v in children_map.values(): v.sort()

    def _depth(s: str) -> int:
        return 0 if s == "." else len(s.split("/"))
    descendants: dict[str, int] = {}
    for r in sorted(rel_paths, key=lambda s: -_depth(s)):
        total = 0
        for c in children_map.get(r, []):
            total += 1 + descendants.get(c, 0)
        descendants[r] = total

    local_dbs: dict[str, dict] = {}
    for d in dirs:
        rel = rel_posix(d)
        local_dbs[rel] = build_local(d, rel)

    # Retire any per-directory tag.db files — root tag.db is the single
    # source of truth now, with every local dir's slice stamped by `dir`.
    removed_local = 0
    for d in dirs:
        rel = rel_posix(d)
        if rel == ".":
            continue
        f = d / DB_FILE
        if f.exists():
            try:
                f.unlink()
                removed_local += 1
            except Exception:
                pass

    url_paths = load_url_paths()
    url_graph = build_url_path_graph(url_paths)
    fs_graph  = build_fs_path_graph(rel_paths, children_map, descendants)

    global_db = build_global(local_dbs, url_graph, fs_graph)
    write_consolidated(REPO / DB_FILE, global_db, local_dbs)
    print(f"[tag.db] removed {removed_local} per-directory tag.db files")
    written = 0

    retired = retire_legacy()

    print(f"[tag.db] wrote {written} local + 1 global tag.db "
          f"({global_db['unique_tags']} unique tags, "
          f"{global_db['file_count']} files, "
          f"{global_db['udt_count']} UDT instances)")
    print(f"[tag.db] url-path graph: {url_graph['node_count']} nodes / {url_graph['edge_count']} edges")
    print(f"[tag.db] fs-path  graph: {fs_graph['node_count']} nodes / {fs_graph['edge_count']} edges")
    print(f"[tag.db] retired {retired} legacy files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
