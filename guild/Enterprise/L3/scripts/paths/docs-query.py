#!/usr/bin/env python3
# @script
# id: docs-query
# label: Query docs.db
# category: query
# description: CLI to query the docs.db registry (stats/headings/links/grep).
# inputs:
#   - docs.db
"""
Query tool for docs.db (and its local shards).

Usage:
  docs-query.py <command> [args...]

Commands:
  stats                          Show global summary.
  ext <ext>                      List all docs with extension.
  headings [level] [substr]      List markdown headings, optional level (1-6) + substring filter.
  tag <tag>                      List docs with a given frontmatter tag.
  search <regex>                 Regex search headings text + doc first lines.
  links [--broken|--external]    List links of the chosen kind.
  doc <path>                     Dump a single doc's parsed fields.
  toc <path>                     Print a TOC for a markdown file.
  grep <regex> [--ext md]        Grep across doc contents (live file read).

Reads the root docs.db by default. Pass --db <path> to use another.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
DEFAULT_DB = REPO / "docs.db"


def load(db_path: Path) -> dict:
    if not db_path.exists():
        print(f"docs.db not found at {db_path}. Run gen-docs-db.py first.", file=sys.stderr)
        sys.exit(2)
    return json.loads(db_path.read_text(encoding="utf-8"))


def cmd_stats(db: dict, _) -> int:
    print(f"dir_count    {db['dir_count']}")
    print(f"doc_count    {db['doc_count']}")
    print(f"total_bytes  {db['total_bytes']:,}")
    print("by_ext:")
    for ext, files in sorted(db["by_ext"].items(), key=lambda kv: -len(kv[1])):
        print(f"  .{ext:<10} {len(files):>5}")
    idx = db["indexes"]
    print(f"headings     {sum(len(v) for v in idx['by_heading_level'].values())}")
    print(f"tags         {len(idx['by_tag'])}")
    print(f"ext links    {len(idx['external_links'])}")
    print(f"broken refs  {len(idx['broken_local_refs'])}")
    return 0


def cmd_ext(db: dict, args) -> int:
    ext = args.arg.lstrip(".")
    for p in db["by_ext"].get(ext, []):
        print(p)
    return 0


def cmd_headings(db: dict, args) -> int:
    level  = args.level
    needle = args.substr
    pat    = re.compile(needle, re.IGNORECASE) if needle else None
    levels = [f"h{level}"] if level else sorted(db["indexes"]["by_heading_level"].keys())
    for lv in levels:
        for h in db["indexes"]["by_heading_level"].get(lv, []):
            if pat and not pat.search(h["text"]):
                continue
            print(f"{lv}  {h['path']}:{h['line']}  {h['text']}")
    return 0


def cmd_tag(db: dict, args) -> int:
    for p in db["indexes"]["by_tag"].get(args.arg, []):
        print(p)
    return 0


def cmd_search(db: dict, args) -> int:
    pat = re.compile(args.arg, re.IGNORECASE)
    hits = 0
    for lv, items in db["indexes"]["by_heading_level"].items():
        for h in items:
            if pat.search(h["text"]):
                print(f"[{lv}] {h['path']}:{h['line']}  {h['text']}")
                hits += 1
    print(f"-- {hits} heading match(es)", file=sys.stderr)
    return 0


def cmd_links(db: dict, args) -> int:
    idx = db["indexes"]
    if args.broken:
        for r in idx["broken_local_refs"]:
            print(f"{r['path']}:{r['line']}  -> {r['ref']}  (resolved: {r['resolved']})")
    elif args.external:
        for r in idx["external_links"]:
            print(f"{r['path']}:{r['line']}  {r['url']}")
    else:
        for tgt, refs in idx["by_link_target"].items():
            for r in refs:
                print(f"{r['path']}:{r['line']}  {tgt}")
    return 0


def cmd_doc(_db: dict, args) -> int:
    target = args.arg
    # Find in local shard for precision
    d = REPO / Path(target).parent if "/" in target else REPO
    shard = d / "docs.db"
    if not shard.exists():
        shard = DEFAULT_DB
    data = json.loads(shard.read_text(encoding="utf-8"))
    name = Path(target).name
    for doc in data.get("docs", []):
        if doc["path"] == name or (data.get("dir", ".") + "/" + doc["path"]).lstrip("./") == target:
            print(json.dumps(doc, indent=2, ensure_ascii=False))
            return 0
    # Fallback: scan global by_ext
    print("not found in local shard; use ext/headings to find it", file=sys.stderr)
    return 1


def cmd_toc(_db: dict, args) -> int:
    target = Path(args.arg)
    if not target.is_absolute():
        target = REPO / target
    shard = target.parent / "docs.db"
    if not shard.exists():
        print(f"no docs.db in {target.parent}", file=sys.stderr)
        return 2
    data = json.loads(shard.read_text(encoding="utf-8"))
    for doc in data["docs"]:
        if doc["path"] == target.name and doc["parser"] == "markdown":
            for h in doc["fields"]["headings"]:
                indent = "  " * (h["level"] - 1)
                print(f"{indent}- {h['text']}  (L{h['line']})")
            return 0
    print("not a markdown doc in that shard", file=sys.stderr)
    return 1


def cmd_grep(db: dict, args) -> int:
    pat = re.compile(args.arg)
    ext_filter = set(e.lstrip(".") for e in (args.ext or []))
    hits = 0
    for ext, files in db["by_ext"].items():
        if ext_filter and ext not in ext_filter:
            continue
        for rel in files:
            p = REPO / rel
            if not p.exists(): continue
            try:
                for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                    if pat.search(line):
                        print(f"{rel}:{i}: {line.rstrip()}")
                        hits += 1
            except Exception:
                continue
    print(f"-- {hits} match(es)", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="docs-query")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("stats")

    p = sub.add_parser("ext");      p.add_argument("arg")
    p = sub.add_parser("headings")
    p.add_argument("--level", type=int, choices=range(1, 7))
    p.add_argument("substr", nargs="?")
    p = sub.add_parser("tag");      p.add_argument("arg")
    p = sub.add_parser("search");   p.add_argument("arg")
    p = sub.add_parser("links")
    p.add_argument("--broken",   action="store_true")
    p.add_argument("--external", action="store_true")
    p = sub.add_parser("doc");      p.add_argument("arg")
    p = sub.add_parser("toc");      p.add_argument("arg")
    p = sub.add_parser("grep")
    p.add_argument("arg")
    p.add_argument("--ext", nargs="*")

    args = ap.parse_args()
    db = load(args.db)
    handler = {
        "stats":    cmd_stats,
        "ext":      cmd_ext,
        "headings": cmd_headings,
        "tag":      cmd_tag,
        "search":   cmd_search,
        "links":    cmd_links,
        "doc":      cmd_doc,
        "toc":      cmd_toc,
        "grep":     cmd_grep,
    }[args.cmd]
    return handler(db, args)


if __name__ == "__main__":
    sys.exit(main())
