#!/usr/bin/env python3
# @tag-event
# {
#   "id": "gen-fs-paths:on-fs-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "fs.structure.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "fs.paths.rebuilt_at"
#   ]
# }
# @end-tag-event
# @script
# id: gen-fs-paths
# label: Generate FsPath UDT instances
# category: generate
# description: Stamps path.json (FsPath UDT) in every directory.
# outputs:
#   - "**/path.json"
"""
Generate filesystem Path UDT instances (`path.json`) in every non-excluded
directory of the repo, and compute cross-directory tags automatically.

Two-pass algorithm:
  Pass 1 (walk):     for each dir, collect kids, files, file-ext kinds.
  Pass 2 (stitch):   populate `parent`, `children`, `siblings`, `breadcrumb`,
                     `descendants`, and `route_bindings` (cross-link to URL
                     Path instances whose `page` field points inside the dir).
  Pass 3 (write):    emit `path.json` into each dir + a root graph
                     `guild/Enterprise/L2/hmi/web/components/udts/instances/fs-paths/_graph.json`.

Preserves user-authored fields on rerun:
  - parameters.purpose
  - parameters.owners

Run with no args from repo root.
"""
from __future__ import annotations
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]

# Directories we never want to stamp with `path.json`.
EXCLUDE_DIRS = {
    ".git", ".github", ".vscode", ".idea",
    "node_modules", "__pycache__", ".pytest_cache",
    "dist", "build", "out", ".next", ".cache",
    "coverage", ".venv", "venv", "env",
}
# Also skip any dir whose name starts with one of these prefixes.
EXCLUDE_PREFIXES = ("_",)  # `_graph`, `_probe`, `_fix_*`, etc. don't exist as dirs but be safe.

GRAPH_OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "fs-paths" / "_graph.json"
PATHS_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "paths"

PATH_FILE = "path.json"
SCHEMA_VERSION = "1.0.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_excluded(name: str) -> bool:
    if name in EXCLUDE_DIRS:
        return True
    if any(name.startswith(p) for p in EXCLUDE_PREFIXES):
        return True
    return False


def rel_posix(p: Path) -> str:
    rp = p.relative_to(REPO)
    s = rp.as_posix()
    return s if s else "."


def slug_id(rel: str) -> str:
    if rel == ".":
        return "root"
    return rel.replace("/", "_").replace(".", "_")


def walk_dirs() -> list[Path]:
    """Return every non-excluded directory (including REPO root) as absolute paths."""
    keep: list[Path] = []
    for dirpath, dirnames, _ in os.walk(REPO):
        d = Path(dirpath)
        # Prune in-place
        dirnames[:] = sorted(n for n in dirnames if not is_excluded(n))
        # Skip if any ancestor was excluded (walker already pruned, so this is redundant
        # for fresh walks but harmless)
        try:
            rel = d.relative_to(REPO)
        except ValueError:
            continue
        if any(is_excluded(part) for part in rel.parts):
            continue
        keep.append(d)
    return keep


def file_histogram(d: Path) -> tuple[int, dict[str, int]]:
    count = 0
    hist: Counter[str] = Counter()
    for entry in d.iterdir():
        if entry.is_file():
            if entry.name == PATH_FILE:
                continue
            if entry.name.startswith("."):
                continue  # skip hidden
            count += 1
            ext = entry.suffix.lstrip(".").lower() or "(none)"
            hist[ext] += 1
    return count, dict(hist)


def load_existing(path_file: Path) -> dict:
    if path_file.exists():
        try:
            return json.loads(path_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def load_url_paths() -> list[dict]:
    out = []
    if not PATHS_DIR.exists():
        return out
    for f in sorted(PATHS_DIR.glob("*.json")):
        if f.name.startswith("_") or f.name == "index.json":
            continue
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return out


def compute_route_bindings(dir_rel: str, url_paths: list[dict]) -> list[str]:
    """Return URL-Path ids whose `page` field lives inside this dir (not a descendant)."""
    bindings = []
    for p in url_paths:
        page = (p.get("parameters", {}) or {}).get("page") or ""
        if not page:
            continue
        # Normalize `page` relative to repo root if needed. Existing instances use
        # paths like "pages/charter.page.json" (relative to guild/web/) or
        # "guild/apps/whitepapers/pages/foo.page.json" (repo-relative).
        page_posix = PurePosixPath(page).as_posix()
        # Try both interpretations
        candidates = [page_posix, f"guild/web/{page_posix}"]
        for c in candidates:
            parent = str(PurePosixPath(c).parent)
            if parent == dir_rel or (dir_rel == "." and parent == "."):
                pid = (p.get("tags", {}) or {}).get("id")
                if pid:
                    bindings.append(pid)
                break
    return sorted(set(bindings))


def main() -> int:
    dirs = walk_dirs()
    rel_paths = [rel_posix(d) for d in dirs]
    abs_by_rel = dict(zip(rel_paths, dirs))

    # Pass 1: direct children per parent
    children_map: dict[str, list[str]] = defaultdict(list)
    for r in rel_paths:
        if r == ".":
            continue
        parent = str(PurePosixPath(r).parent)
        if parent == ".":
            parent = "."
        children_map[parent].append(r)
    for v in children_map.values():
        v.sort()

    # Pass 2: descendant counts (post-order: deepest first)
    def _depth(s: str) -> int:
        return 0 if s == "." else len(s.split("/"))
    descendants: dict[str, int] = {}
    for r in sorted(rel_paths, key=lambda s: -_depth(s)):
        total = 0
        for c in children_map.get(r, []):
            total += 1 + descendants.get(c, 0)
        descendants[r] = total

    url_paths = load_url_paths()

    # Pass 3: emit
    written = 0
    preserved_fields = 0
    now = _now()

    for rel, absd in sorted(abs_by_rel.items()):
        fcount, hist = file_histogram(absd)
        parent = None if rel == "." else str(PurePosixPath(rel).parent)
        if parent == ".":
            parent = "."
        kids = children_map.get(rel, [])
        sibs = []
        if parent is not None:
            sibs = [s for s in children_map.get(parent, []) if s != rel]
        depth = 0 if rel == "." else len(rel.split("/"))
        breadcrumb: list[str] = []
        if rel == ".":
            breadcrumb = ["root"]
        else:
            acc = []
            parts = rel.split("/")
            breadcrumb = ["root"] + [slug_id("/".join(parts[: i + 1])) for i in range(len(parts))]
            _ = acc

        path_file = absd / PATH_FILE
        existing = load_existing(path_file)
        existing_params = existing.get("parameters", {}) if isinstance(existing, dict) else {}

        doc = {
            "udtType": "FsPath",
            "parameters": {
                "path":    rel,
                "label":   absd.name if rel != "." else REPO.name,
                "parent":  parent,
                "kind":    "filesystem",
                # Preserve user-authored fields if present
                "purpose": existing_params.get("purpose"),
                "owners":  existing_params.get("owners") or [],
            },
            "tags": {
                "id":             slug_id(rel),
                "fs_path":        rel,
                "depth":          depth,
                "breadcrumb":     breadcrumb,
                "children":       kids,
                "siblings":       sibs,
                "descendants":    descendants.get(rel, 0),
                "file_count":     fcount,
                "subdir_count":   len(kids),
                "kinds":          hist,
                "route_bindings": compute_route_bindings(rel, url_paths),
                "last_generated": now,
                "schema_version": SCHEMA_VERSION,
            },
        }
        if existing_params.get("purpose") or existing_params.get("owners"):
            preserved_fields += 1
        path_file.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        written += 1

    # Note: the filesystem graph is now emitted into the consolidated
    # root `tag.db` by gen-tag-db.py under `graphs.fs_paths`. This
    # generator only writes per-directory `path.json` FsPath instances.

    print(f"[fs-paths] wrote {written} path.json files "
          f"(preserved user fields in {preserved_fields})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
