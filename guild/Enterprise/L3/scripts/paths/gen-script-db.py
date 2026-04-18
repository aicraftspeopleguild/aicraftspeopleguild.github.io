#!/usr/bin/env python3
# @tag-event
# {
#   "id": "gen-script-db:on-scripts-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "scripts.source.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "script.db.rebuilt_at"
#   ]
# }
# @end-tag-event
# @script
# id: gen-script-db
# label: Generate script.db
# category: generate
# description: Discover and register every executable script as a Script UDT.
# outputs:
#   - script.db
"""
Script registry generator.

Walks the repo, finds executable scripts (.py, .js, .sh, .ps1, .mjs, .cjs),
and builds a Script UDT entry for each. Writes a single consolidated
`script.db` at the repo root. The individual UDT instance files are NOT
emitted - every field lives inside `script.db.scripts[<id>]`.

Each script may declare metadata in a leading `@script` block within its
header comment (YAML-ish). Example (Python):

    # @script
    # id: gen-tag-db
    # label: Generate tag.db
    # category: generate
    # description: Consolidated tag / UDT index generator.
    # outputs:
    #   - tag.db
    #   - "**/tag.db"
    # depends_on:
    #   - gen-fs-paths

If no `@script` block is present, the tool infers:
  - id       = filename stem (kebab-cased)
  - label    = Title Case of id
  - language = from extension
  - category = inferred from filename prefix (gen-* -> generate, build-* -> build,
               test-* -> test, fix-* -> fix, validate-* -> validate, *-query -> query,
               *-server -> dev-server)
"""
from __future__ import annotations
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]

EXCLUDE_DIRS = {
    ".git", ".github", ".vscode", ".idea",
    "node_modules", "__pycache__", ".pytest_cache",
    "dist", "build", "out", ".next", ".cache",
    "coverage", ".venv", "venv", "env",
}
SCRIPT_EXTS = {
    "py":  "python",
    "mjs": "node",
    "cjs": "node",
    "js":  "node",
    "sh":  "shell",
    "bash":"shell",
    "ps1": "powershell",
}
DEFAULT_ENTRYPOINTS = {
    "python":     "python",
    "node":       "node",
    "shell":      "bash",
    "powershell": "pwsh",
}
COMMENT_PREFIXES = {
    "python":     "#",
    "node":       "//",
    "shell":      "#",
    "powershell": "#",
}
SCHEMA_VERSION = "1.0.0"
ROOT_DB        = REPO / "script.db"
LEGACY_INSTANCES_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "scripts"
BLOCK_START_RE = re.compile(r"^\s*(#|//)\s*@script\b", re.IGNORECASE)
KV_RE          = re.compile(r"^\s*(?:#|//)\s*([A-Za-z_][\w\-]*)\s*:\s*(.*?)\s*$")
LIST_ITEM_RE   = re.compile(r"^\s*(?:#|//)\s*-\s*(.+?)\s*$")
BLOCK_END_RE   = re.compile(r"^\s*(?:#|//)?\s*$")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_excluded(name: str) -> bool:
    return name in EXCLUDE_DIRS


def rel_posix(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def infer_category(stem: str) -> str:
    s = stem.lower()
    if s.startswith("gen-") or s.startswith("generate-"): return "generate"
    if s.startswith("build-") or s == "build":           return "build"
    if s.startswith("test-") or s.endswith("-test"):     return "test"
    if s.startswith("fix-"):                             return "fix"
    if s.startswith("validate-") or s.endswith("-validate"): return "validate"
    if s.endswith("-query") or s.startswith("query-"):   return "query"
    if s.endswith("-server") or s == "serve":            return "dev-server"
    return "misc"


def kebab(s: str) -> str:
    s = re.sub(r"[_\s]+", "-", s)
    s = re.sub(r"[^A-Za-z0-9\-]", "", s)
    return s.lower().strip("-")


def parse_header_block(text: str) -> dict:
    """Scan the leading comment block for an `@script` metadata section."""
    out: dict = {}
    cur_key: str | None = None
    lines = text.splitlines()
    # Skip shebang
    i = 0
    if lines and lines[0].startswith("#!"):
        i = 1
    in_block = False
    for line in lines[i : i + 200]:
        if not in_block:
            if BLOCK_START_RE.match(line):
                in_block = True
                continue
            # Keep scanning the first comment stack; blank line ends the chase.
            if line.strip() == "":
                continue
            if not (line.lstrip().startswith("#") or line.lstrip().startswith("//")):
                # Hit real code before finding the block — bail.
                return out
            continue
        # inside block
        m = LIST_ITEM_RE.match(line)
        if m and cur_key is not None:
            out.setdefault(cur_key, [])
            if isinstance(out[cur_key], list):
                out[cur_key].append(m.group(1).strip().strip('"').strip("'"))
            continue
        m = KV_RE.match(line)
        if m:
            k = m.group(1)
            v = m.group(2)
            cur_key = k
            if not v:
                out[k] = []
            else:
                out[k] = v.strip('"').strip("'")
            continue
        # End on first non-comment or blank comment
        if not (line.lstrip().startswith("#") or line.lstrip().startswith("//")):
            break
    return out


def build_instance(script_path: Path) -> dict:
    rel    = rel_posix(script_path)
    ext    = script_path.suffix.lstrip(".").lower()
    lang   = SCRIPT_EXTS.get(ext, "other")
    stem   = kebab(script_path.stem)
    try:
        text = script_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        text = ""
    meta = parse_header_block(text)

    sid = kebab(meta.get("id") or stem)
    return {
        "udtType": "Script",
        "parameters": {
            "name":        sid,
            "label":       meta.get("label") or sid.replace("-", " ").title(),
            "path":        rel,
            "language":    lang,
            "entrypoint":  meta.get("entrypoint") or DEFAULT_ENTRYPOINTS.get(lang),
            "category":    meta.get("category") or infer_category(script_path.stem),
            "description": meta.get("description") or "",
            "inputs":      meta.get("inputs")     or [],
            "outputs":     meta.get("outputs")    or [],
            "depends_on":  meta.get("depends_on") or [],
            "args":        meta.get("args")       or [],
        },
        "tags": {
            "id":           sid,
            "categories":   [meta.get("category") or infer_category(script_path.stem)],
            "ext":          ext,
            "path_dir":     str(Path(rel).parent.as_posix()),
            "last_updated": _now(),
        },
    }


def walk_scripts() -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(n for n in dirnames if not is_excluded(n))
        d = Path(dirpath)
        rel = d.relative_to(REPO)
        if any(is_excluded(part) for part in rel.parts):
            continue
        for fn in filenames:
            ext = fn.rsplit(".", 1)[-1].lower() if "." in fn else ""
            if ext in SCRIPT_EXTS:
                found.append(d / fn)
    return found


def main() -> int:
    scripts = walk_scripts()

    # Retire the legacy per-script instance folder — everything now lives
    # in script.db. (Safe: no runtime consumer; confirmed via grep.)
    removed = 0
    if LEGACY_INSTANCES_DIR.exists():
        for old in LEGACY_INSTANCES_DIR.glob("*.json"):
            try: old.unlink(); removed += 1
            except Exception: pass
        # Kill stale tag.db / path.json sidecars in that retired dir
        for sidecar in ("tag.db", "path.json"):
            p = LEGACY_INSTANCES_DIR / sidecar
            if p.exists():
                try: p.unlink()
                except Exception: pass
        try: LEGACY_INSTANCES_DIR.rmdir()
        except OSError: pass

    by_id: dict[str, dict] = {}
    collisions: list[str] = []
    for p in scripts:
        inst = build_instance(p)
        sid  = inst["tags"]["id"]
        if sid in by_id:
            dir_slug = kebab(str(Path(rel_posix(p)).parent.as_posix()).replace("/", "-")) or "root"
            sid = f"{dir_slug}--{sid}"
            inst["tags"]["id"]         = sid
            inst["parameters"]["name"] = sid
            collisions.append(sid)
        by_id[sid] = inst

    by_category: dict[str, list[str]] = {}
    by_language: dict[str, list[str]] = {}
    by_dir:      dict[str, list[str]] = {}
    for sid, inst in by_id.items():
        p = inst["parameters"]
        by_category.setdefault(p["category"], []).append(sid)
        by_language.setdefault(p["language"], []).append(sid)
        by_dir.setdefault(inst["tags"]["path_dir"], []).append(sid)
    for v in by_category.values(): v.sort()
    for v in by_language.values(): v.sort()
    for v in by_dir.values():      v.sort()

    registry = {
        "scope":          "global",
        "generated_at":   _now(),
        "schema_version": SCHEMA_VERSION,
        "script_count":   len(by_id),
        "scripts": {
            sid: {
                "path":        inst["parameters"]["path"],
                "label":       inst["parameters"]["label"],
                "language":    inst["parameters"]["language"],
                "entrypoint":  inst["parameters"]["entrypoint"],
                "category":    inst["parameters"]["category"],
                "description": inst["parameters"]["description"],
                "inputs":      inst["parameters"]["inputs"],
                "outputs":     inst["parameters"]["outputs"],
                "depends_on":  inst["parameters"]["depends_on"],
                "args":        inst["parameters"]["args"],
            }
            for sid, inst in sorted(by_id.items())
        },
        "indexes": {
            "by_category": {k: by_category[k] for k in sorted(by_category)},
            "by_language": {k: by_language[k] for k in sorted(by_language)},
            "by_dir":      {k: by_dir[k]      for k in sorted(by_dir)},
        },
    }
    ROOT_DB.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    hist = Counter(inst["parameters"]["category"] for inst in by_id.values())
    print(f"[script.db] wrote {len(by_id)} entries to script.db")
    for cat, n in sorted(hist.items(), key=lambda kv: -kv[1]):
        print(f"  {cat:<10} {n}")
    if removed:
        print(f"[script.db] retired {removed} legacy per-script instance files")
    if collisions:
        print(f"[script.db] resolved {len(collisions)} id collision(s) by dir-prefixing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
