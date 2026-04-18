#!/usr/bin/env python3
# @tag-event
# {
#   "id": "gen-docs-db:on-docs-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "docs.content.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "docs.db.rebuilt_at"
#   ]
# }
# @end-tag-event
# @script
# id: gen-docs-db
# label: Generate docs.db
# category: generate
# description: Index md/txt/csv/yaml/html/json with format-aware parsers.
# outputs:
#   - docs.db
#   - "**/docs.db"
"""
Document index generator.

Produces `docs.db` (JSON) in every non-excluded directory + a global root
`docs.db`. Sibling to `tag.db`, but focused on human-readable text formats
with format-aware parsers. One entry per file.

Supported formats (dispatched by extension):
  .md / .markdown : frontmatter, headings, links, images, code blocks, wc
  .txt / .log     : line/word count, first line
  .csv / .tsv     : header row, column/row count, delimiter
  .yaml / .yml    : top-level keys, doc count
  .html / .htm    : <title>, h1, link count
  .json           : short shape summary (top-level keys, size)
  (anything else small-ish is tagged as "other" with size only)

Each file entry has:
  { "path", "ext", "size", "lines", "sha1", "parser", "fields": {...} }

Root docs.db additionally carries `indexes`:
  - by_ext            ext → [path, ...]
  - by_heading_level  "h1"/"h2"/... → [{path, text, line}, ...]  (md only)
  - by_link_target    target_url → [{path, line}, ...]           (md/html)
  - by_tag            frontmatter_tag → [path, ...]              (md only)
  - external_links    [ {path, url} ]
  - broken_local_refs [ {path, ref, line} ]  (md local links that don't resolve)
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
from docsdb_sqlite import write_consolidated  # noqa: E402

EXCLUDE_DIRS = {
    ".git", ".github", ".vscode", ".idea",
    "node_modules", "__pycache__", ".pytest_cache",
    "dist", "build", "out", ".next", ".cache",
    "coverage", ".venv", "venv", "env",
}
DB_FILE = "docs.db"
SCHEMA_VERSION = "1.0.0"
MAX_INLINE_BYTES = 256 * 1024   # skip parsing files bigger than 256 KB (still record size)

DOC_EXTS = {
    "md", "markdown",
    "txt", "log",
    "csv", "tsv",
    "yaml", "yml",
    "html", "htm",
    "css", "js",
    "json",
    "rst", "adoc",
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


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()[:12]


# -----------------------------------------------------------------------
# Parsers
# -----------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE     = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE       = re.compile(r"^```(\S*)\s*$")
LINK_RE        = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)")
IMAGE_RE       = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_TITLE_RE  = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
HTML_H1_RE     = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
HTML_LINK_RE   = re.compile(r'<a\s+[^>]*href="([^"]+)"', re.IGNORECASE)


def parse_frontmatter(src: str) -> tuple[dict, int]:
    """Very lightweight YAML-ish frontmatter parser (key: value, lists)."""
    m = FRONTMATTER_RE.match(src)
    if not m:
        return {}, 0
    body = m.group(1)
    out: dict = {}
    cur_key: str | None = None
    for line in body.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and cur_key:
            out.setdefault(cur_key, [])
            if isinstance(out[cur_key], list):
                out[cur_key].append(line[4:].strip().strip("\"'"))
            continue
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            k = k.strip(); v = v.strip()
            cur_key = k
            if not v:
                out[k] = []
            else:
                out[k] = v.strip("\"'")
    # Split comma-separated tag-ish scalars
    for key in ("tags", "keywords", "categories"):
        v = out.get(key)
        if isinstance(v, str):
            out[key] = [t.strip() for t in v.strip("[]").split(",") if t.strip()]
    return out, len(m.group(0).splitlines())


def parse_markdown(text: str) -> dict:
    fm, fm_lines = parse_frontmatter(text)
    headings: list[dict] = []
    links:    list[dict] = []
    images:   list[dict] = []
    code_langs = Counter()

    in_fence = False
    fence_lang = ""
    for i, raw in enumerate(text.splitlines(), start=1):
        if i <= fm_lines:
            continue
        m = FENCE_RE.match(raw)
        if m:
            if in_fence:
                in_fence = False
            else:
                in_fence = True
                fence_lang = m.group(1).lower() or "(none)"
                code_langs[fence_lang] += 1
            continue
        if in_fence:
            continue
        hm = HEADING_RE.match(raw)
        if hm:
            level = len(hm.group(1))
            headings.append({"level": level, "text": hm.group(2), "line": i})
        for lm in LINK_RE.finditer(raw):
            links.append({"text": lm.group(1), "target": lm.group(2), "line": i})
        for im in IMAGE_RE.finditer(raw):
            images.append({"alt": im.group(1), "target": im.group(2), "line": i})

    words = len(re.findall(r"\w+", text))
    return {
        "frontmatter": fm,
        "headings":    headings,
        "links":       links,
        "images":      images,
        "code_langs":  dict(code_langs),
        "word_count":  words,
        "h1":          next((h["text"] for h in headings if h["level"] == 1), None),
    }


def parse_txt(text: str) -> dict:
    lines = text.splitlines()
    return {
        "word_count": len(re.findall(r"\w+", text)),
        "first_line": lines[0][:200] if lines else "",
    }


def parse_csv(text: str, delim: str) -> dict:
    try:
        reader = csv.reader(io.StringIO(text), delimiter=delim)
        rows = list(reader)
    except Exception:
        return {"error": "csv parse failed"}
    if not rows:
        return {"row_count": 0, "columns": []}
    header = rows[0]
    return {
        "delimiter":  delim,
        "row_count":  max(len(rows) - 1, 0),
        "column_count": len(header),
        "columns":    header,
    }


def parse_yaml(text: str) -> dict:
    keys: list[str] = []
    doc_count = 1
    for raw in text.splitlines():
        if raw.strip() == "---":
            doc_count += 1
            continue
        m = re.match(r"^([A-Za-z_][\w\-]*)\s*:", raw)
        if m:
            keys.append(m.group(1))
    return {"doc_count": doc_count, "top_level_keys": sorted(set(keys))}


def parse_html(text: str) -> dict:
    title = HTML_TITLE_RE.search(text)
    h1    = HTML_H1_RE.search(text)
    links = [{"target": m.group(1)} for m in HTML_LINK_RE.finditer(text)]
    return {
        "title":      (title.group(1).strip() if title else None),
        "h1":         (h1.group(1).strip() if h1 else None),
        "link_count": len(links),
        "links":      links[:200],
    }


def parse_json(text: str) -> dict:
    try:
        data = json.loads(text)
    except Exception as e:
        return {"error": f"json parse failed: {e.__class__.__name__}"}
    shape = type(data).__name__
    out: dict = {"shape": shape}
    if isinstance(data, dict):
        out["top_level_keys"] = sorted(data.keys())[:50]
        out["key_count"]      = len(data)
    elif isinstance(data, list):
        out["length"] = len(data)
    return out


def parse_file(p: Path, ext: str) -> tuple[str, dict]:
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return "binary", {}
    if ext in {"md", "markdown"}:
        return "markdown", parse_markdown(text)
    if ext in {"txt", "log", "rst", "adoc"}:
        return "text", parse_txt(text)
    if ext == "csv":
        return "csv", parse_csv(text, ",")
    if ext == "tsv":
        return "csv", parse_csv(text, "\t")
    if ext in {"yaml", "yml"}:
        return "yaml", parse_yaml(text)
    if ext in {"html", "htm"}:
        return "html", parse_html(text)
    if ext == "json":
        return "json", parse_json(text)
    return "other", {}


# -----------------------------------------------------------------------
# Scan
# -----------------------------------------------------------------------

def scan_dir(d: Path) -> list[dict]:
    entries: list[dict] = []
    for entry in sorted(d.iterdir()):
        if not entry.is_file():
            continue
        if entry.name.startswith(".") or entry.name in {DB_FILE, "tag.db", "path.json"}:
            continue
        ext = entry.suffix.lstrip(".").lower()
        if ext not in DOC_EXTS:
            continue
        try:
            size = entry.stat().st_size
        except OSError:
            continue
        rec: dict = {
            "path":   entry.name,
            "ext":    ext,
            "size":   size,
            "parser": "skipped",
            "fields": {},
        }
        if size <= MAX_INLINE_BYTES:
            try:
                text = entry.read_text(encoding="utf-8", errors="replace")
                rec["lines"] = len(text.splitlines())
                rec["sha1"]  = sha1(text)
                rec["body"]  = text
            except Exception:
                text = ""
            parser, fields = parse_file(entry, ext)
            rec["parser"] = parser
            rec["fields"] = fields
        entries.append(rec)
    return entries


def build_local(d: Path, rel: str) -> dict:
    docs = scan_dir(d)
    ext_hist = Counter(e["ext"] for e in docs)
    return {
        "dir":            rel,
        "scope":          "local",
        "generated_at":   _now(),
        "schema_version": SCHEMA_VERSION,
        "doc_count":      len(docs),
        "total_bytes":    sum(e["size"] for e in docs),
        "by_ext":         dict(sorted(ext_hist.items())),
        "docs":           docs,
    }


# -----------------------------------------------------------------------
# Global rollup
# -----------------------------------------------------------------------

def resolve_local_ref(from_dir: str, ref: str) -> str | None:
    """Resolve a relative markdown link against the repo. Returns posix path or None if external/unresolvable."""
    if re.match(r"^[a-z]+://", ref, re.IGNORECASE): return None
    if ref.startswith("#") or ref.startswith("mailto:"): return None
    target = ref.split("#", 1)[0].split("?", 1)[0]
    if not target: return None
    if target.startswith("/"):
        candidate = REPO / target.lstrip("/")
    else:
        base = REPO if from_dir == "." else (REPO / from_dir)
        candidate = (base / target).resolve()
    try:
        return str(candidate.relative_to(REPO).as_posix())
    except ValueError:
        return None


def build_global(local_dbs: dict[str, dict]) -> dict:
    by_ext            = defaultdict(list)
    by_heading_level  = defaultdict(list)
    by_link_target    = defaultdict(list)
    by_tag            = defaultdict(list)
    external_links    = []
    broken_local_refs = []
    total_docs = total_bytes = 0

    for rel, db in local_dbs.items():
        for doc in db["docs"]:
            full = doc["path"] if rel == "." else f"{rel}/{doc['path']}"
            total_docs  += 1
            total_bytes += doc["size"]
            by_ext[doc["ext"]].append(full)
            if doc["parser"] != "markdown":
                continue
            f = doc["fields"]
            for h in f.get("headings", []):
                by_heading_level[f"h{h['level']}"].append({
                    "path": full, "text": h["text"], "line": h["line"],
                })
            for tag in (f.get("frontmatter") or {}).get("tags", []) or []:
                if isinstance(tag, str):
                    by_tag[tag].append(full)
            for link in f.get("links", []):
                tgt = link["target"]
                if re.match(r"^[a-z]+://", tgt, re.IGNORECASE):
                    external_links.append({"path": full, "url": tgt, "line": link["line"]})
                    by_link_target[tgt].append({"path": full, "line": link["line"]})
                    continue
                resolved = resolve_local_ref(rel, tgt)
                by_link_target[tgt].append({"path": full, "line": link["line"]})
                if resolved is None:
                    continue
                if not (REPO / resolved).exists():
                    broken_local_refs.append({"path": full, "ref": tgt, "resolved": resolved, "line": link["line"]})

    return {
        "dir":            ".",
        "scope":          "global",
        "generated_at":   _now(),
        "schema_version": SCHEMA_VERSION,
        "dir_count":      len(local_dbs),
        "doc_count":      total_docs,
        "total_bytes":    total_bytes,
        "by_ext":         {k: sorted(v) for k, v in sorted(by_ext.items())},
        "indexes": {
            "by_heading_level":  {k: sorted(v, key=lambda x: (x["path"], x["line"])) for k, v in sorted(by_heading_level.items())},
            "by_link_target":    {k: v for k, v in sorted(by_link_target.items())},
            "by_tag":             {k: sorted(set(v)) for k, v in sorted(by_tag.items())},
            "external_links":     external_links,
            "broken_local_refs":  broken_local_refs,
        },
    }


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main() -> int:
    dirs = walk_dirs()
    local_dbs: dict[str, dict] = {}
    for d in dirs:
        rel = rel_posix(d)
        db  = build_local(d, rel)
        local_dbs[rel] = db

    # Retire every per-directory docs.db — root docs.db becomes the
    # single source of truth with every dir's rows stamped via `dir`.
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

    global_db = build_global(local_dbs)
    write_consolidated(REPO / DB_FILE, global_db, local_dbs)
    print(f"[docs.db] removed {removed_local} per-directory docs.db files")
    written = 0

    print(f"[docs.db] wrote {written} local + 1 global docs.db "
          f"({global_db['doc_count']} docs, "
          f"{global_db['total_bytes']:,} bytes, "
          f"{len(global_db['by_ext'])} extensions)")
    idx = global_db["indexes"]
    print(f"[docs.db] headings: {sum(len(v) for v in idx['by_heading_level'].values())} "
          f"| tags: {len(idx['by_tag'])} "
          f"| external links: {len(idx['external_links'])} "
          f"| broken local refs: {len(idx['broken_local_refs'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
