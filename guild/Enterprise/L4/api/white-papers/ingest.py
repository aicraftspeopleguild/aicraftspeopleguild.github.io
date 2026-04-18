#!/usr/bin/env python3
"""
white-papers/ingest.py

Scan white-papers/originals/ for new or changed files and emit UDT instances
under white-papers/udts/instances/. Supports .md (with YAML front-matter), .csv
(one paper per row), and .html (metadata extracted from the document).

Run from repo root or from this directory — paths are resolved relative to
this file, not the current working directory.

    python3 white-papers/ingest.py

State is kept in white-papers/index.json. Files already ingested with the same
sha256 are skipped. Tag counts are recomputed into white-papers/tags/index.json.

No third-party dependencies. Python 3.8+.
"""
from __future__ import annotations

import csv
import datetime as _dt
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
ORIGINALS = ROOT / "originals"
INSTANCES = ROOT / "udts" / "instances"
TEMPLATES = ROOT / "udts" / "templates"
TAGS_DIR = ROOT / "tags"
INDEX_PATH = ROOT / "index.json"
TAGS_INDEX_PATH = TAGS_DIR / "index.json"
UDT_TEMPLATE_PATH = TEMPLATES / "white-paper.udt.json"

SUPPORTED_EXTS = {".md", ".markdown", ".csv", ".html", ".htm", ".txt"}


# --- small utilities ---------------------------------------------------------

def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "paper"


def _read_template_version() -> str:
    try:
        return json.loads(UDT_TEMPLATE_PATH.read_text(encoding="utf-8")).get("version", "0.0.0")
    except FileNotFoundError:
        return "0.0.0"


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _split_list(value: Any) -> List[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    # allow "a; b; c" or "a, b, c" or a single string
    parts = re.split(r"[;,]", str(value))
    return [p.strip() for p in parts if p.strip()]


# --- parsers -----------------------------------------------------------------

_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def _parse_front_matter(text: str) -> Tuple[Dict[str, Any], str]:
    """Minimal YAML-ish front-matter parser. Supports key: value and key: [a, b]."""
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    meta: Dict[str, Any] = {}
    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
        else:
            meta[key] = val.strip("\"'")
    return meta, body


def _extract_html_meta(text: str) -> Dict[str, Any]:
    """Pull a minimal set of fields out of an HTML white paper."""
    meta: Dict[str, Any] = {}
    title_m = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if title_m:
        meta["title"] = html.unescape(title_m.group(1).strip())
    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)
    if h1_m and "title" not in meta:
        meta["title"] = re.sub(r"<[^>]+>", "", h1_m.group(1)).strip()
    # strip tags for body
    stripped = re.sub(r"<script.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    stripped = re.sub(r"<style.*?</style>", "", stripped, flags=re.IGNORECASE | re.DOTALL)
    stripped = re.sub(r"<[^>]+>", " ", stripped)
    meta["_body"] = re.sub(r"\s+", " ", html.unescape(stripped)).strip()
    return meta


def _records_from_file(path: Path) -> List[Dict[str, Any]]:
    """Return a list of record dicts (one per paper) from a single source file."""
    ext = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")

    if ext in {".md", ".markdown", ".txt"}:
        meta, body = _parse_front_matter(text)
        rec = dict(meta)
        rec.setdefault("title", path.stem.replace("-", " ").title())
        rec["body"] = body.strip()
        rec["_format"] = "md"
        return [rec]

    if ext in {".html", ".htm"}:
        meta = _extract_html_meta(text)
        rec = {
            "title": meta.get("title", path.stem.replace("-", " ").title()),
            "body": meta.get("_body", ""),
            "site_href": path.name if path.parent == ORIGINALS else None,
            "_format": "html",
        }
        return [rec]

    if ext == ".csv":
        rows: List[Dict[str, Any]] = []
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            rec = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
            rec["_format"] = "csv"
            rows.append(rec)
        return rows

    raise ValueError(f"Unsupported extension: {ext}")


# --- instance construction ---------------------------------------------------

def _build_instance(rec: Dict[str, Any], source: Path, file_hash: str, schema_version: str) -> Dict[str, Any]:
    title = str(rec.get("title") or "Untitled").strip()
    explicit_id = str(rec.get("id") or "").strip()
    slug = _slugify(explicit_id or title)
    instance_rel = f"udts/instances/{slug}.json"
    original_rel = str(source.relative_to(ROOT)).replace(os.sep, "/")

    parameters = {
        "title": title,
        "authors": _split_list(rec.get("authors") or rec.get("author")),
        "publication_date": rec.get("publication_date") or rec.get("date") or "",
        "doc_number": rec.get("doc_number") or "",
        "source_medium": rec.get("source_medium") or rec.get("medium") or "",
        "summary": rec.get("summary") or rec.get("abstract") or "",
        "tags": [t.lower() for t in _split_list(rec.get("tags"))],
        "status": rec.get("status") or "published",
        "site_href": rec.get("site_href") or "",
    }

    tag_block = {
        "id": slug,
        "original_path": original_rel,
        "original_format": rec.get("_format") or source.suffix.lower().lstrip("."),
        "original_hash_sha256": file_hash,
        "body": rec.get("body") or "",
        "instance_path": instance_rel,
        "ingested_at": _now_iso(),
        "schema_version": schema_version,
    }

    return {
        "udtType": "WhitePaper",
        "parameters": parameters,
        "tags": tag_block,
    }


# --- tag catalog -------------------------------------------------------------

def _rebuild_tag_catalog(instances: List[Dict[str, Any]]) -> Dict[str, Any]:
    catalog: Dict[str, Dict[str, Any]] = {}
    for inst in instances:
        paper_id = inst["tags"]["id"]
        for tag in inst["parameters"].get("tags", []) or []:
            slug = _slugify(tag)
            entry = catalog.setdefault(slug, {
                "udtType": "Tag",
                "parameters": {"name": slug, "label": tag, "description": ""},
                "tags": {"paper_ids": [], "count": 0, "last_updated": ""},
            })
            if paper_id not in entry["tags"]["paper_ids"]:
                entry["tags"]["paper_ids"].append(paper_id)
    now = _now_iso()
    for entry in catalog.values():
        entry["tags"]["paper_ids"].sort()
        entry["tags"]["count"] = len(entry["tags"]["paper_ids"])
        entry["tags"]["last_updated"] = now
    return {"generated_at": now, "tags": catalog}


# --- main pipeline -----------------------------------------------------------

def ingest(verbose: bool = True) -> Dict[str, Any]:
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    INSTANCES.mkdir(parents=True, exist_ok=True)
    TAGS_DIR.mkdir(parents=True, exist_ok=True)

    schema_version = _read_template_version()
    index = _load_json(INDEX_PATH, {"generated_at": "", "files": {}, "instances": {}})
    files_state = dict(index.get("files", {}))
    instances_state = dict(index.get("instances", {}))

    source_files = [p for p in sorted(ORIGINALS.rglob("*")) if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]

    events = {"added": [], "updated": [], "skipped": [], "errored": []}

    for src in source_files:
        rel = str(src.relative_to(ROOT)).replace(os.sep, "/")
        try:
            file_hash = _sha256(src)
        except OSError as e:
            events["errored"].append({"path": rel, "error": str(e)})
            continue

        prev = files_state.get(rel)
        if prev and prev.get("sha256") == file_hash:
            events["skipped"].append(rel)
            continue

        try:
            records = _records_from_file(src)
        except Exception as e:
            events["errored"].append({"path": rel, "error": str(e)})
            continue

        produced: List[str] = []
        for rec in records:
            try:
                inst = _build_instance(rec, src, file_hash, schema_version)
            except Exception as e:
                events["errored"].append({"path": rel, "error": f"build: {e}"})
                continue
            slug = inst["tags"]["id"]
            out_path = INSTANCES / f"{slug}.json"
            _write_json(out_path, inst)
            produced.append(slug)
            instances_state[slug] = {
                "path": f"udts/instances/{slug}.json",
                "source": rel,
                "sha256": file_hash,
                "ingested_at": inst["tags"]["ingested_at"],
                "title": inst["parameters"]["title"],
            }

        bucket = "updated" if prev else "added"
        events[bucket].append({"path": rel, "produced": produced})
        files_state[rel] = {"sha256": file_hash, "produced": produced, "last_seen": _now_iso()}

    # Drop instances whose source disappeared
    live_sources = {str(p.relative_to(ROOT)).replace(os.sep, "/") for p in source_files}
    orphaned = [k for k, v in list(instances_state.items()) if v.get("source") not in live_sources]
    for slug in orphaned:
        instances_state.pop(slug, None)
        out_path = INSTANCES / f"{slug}.json"
        if out_path.exists():
            out_path.unlink()
    # Same for files_state
    for rel in list(files_state.keys()):
        if rel not in live_sources:
            files_state.pop(rel, None)

    # Rebuild tag catalog from current instances on disk
    loaded_instances: List[Dict[str, Any]] = []
    for slug in sorted(instances_state.keys()):
        path = INSTANCES / f"{slug}.json"
        if path.exists():
            loaded_instances.append(json.loads(path.read_text(encoding="utf-8")))
    tag_catalog = _rebuild_tag_catalog(loaded_instances)
    _write_json(TAGS_INDEX_PATH, tag_catalog)

    new_index = {
        "generated_at": _now_iso(),
        "schema_version": schema_version,
        "counts": {
            "sources": len(files_state),
            "instances": len(instances_state),
            "tags": len(tag_catalog["tags"]),
        },
        "files": files_state,
        "instances": instances_state,
    }
    _write_json(INDEX_PATH, new_index)

    if verbose:
        print(f"[white-papers] sources={new_index['counts']['sources']} "
              f"instances={new_index['counts']['instances']} "
              f"tags={new_index['counts']['tags']}")
        for evt, items in events.items():
            if items:
                print(f"  {evt}: {items}")

    return {"index": new_index, "events": events}


if __name__ == "__main__":
    result = ingest(verbose=True)
    if result["events"]["errored"]:
        sys.exit(1)
