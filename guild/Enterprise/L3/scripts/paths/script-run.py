#!/usr/bin/env python3
# @script
# id: script-run
# label: Run a registered script
# category: query
# description: Dispatch any script in script.db by id, with dep resolution.
# inputs:
#   - script.db
"""
Registry-driven script runner.

Loads `script.db` (root registry) and dispatches scripts by id. Does
dependency-first ordering when you pass --with-deps.

Usage:
  script-run.py list [--category CAT] [--language LANG]
  script-run.py info <id>
  script-run.py run <id> [--with-deps] [-- <args passed through>]
  script-run.py search <regex>
  script-run.py graph            (prints dependency graph as ASCII)
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
DB   = REPO / "script.db"


def load() -> dict:
    if not DB.exists():
        print("script.db not found — run gen-script-db.py first.", file=sys.stderr)
        sys.exit(2)
    return json.loads(DB.read_text(encoding="utf-8"))


def resolve_deps(scripts: dict, sid: str, seen: set[str] | None = None) -> list[str]:
    seen = seen if seen is not None else set()
    if sid in seen:
        return []
    seen.add(sid)
    entry = scripts.get(sid)
    if not entry:
        return []
    order: list[str] = []
    for dep in entry.get("depends_on") or []:
        if dep not in scripts:
            print(f"WARN: {sid} depends on unknown script '{dep}'", file=sys.stderr)
            continue
        order.extend(resolve_deps(scripts, dep, seen))
    order.append(sid)
    return order


def invoke(entry: dict, passthrough: list[str]) -> int:
    path = REPO / entry["path"]
    cmd  = [entry.get("entrypoint") or "python", str(path)]
    cmd += entry.get("args") or []
    cmd += passthrough
    print(f"[run] {entry['label']}  ({' '.join(cmd)})", file=sys.stderr)
    return subprocess.call(cmd, cwd=str(REPO))


def cmd_list(db: dict, args) -> int:
    scripts = db["scripts"]
    ids = sorted(scripts)
    if args.category:
        ids = [i for i in ids if scripts[i]["category"] == args.category]
    if args.language:
        ids = [i for i in ids if scripts[i]["language"] == args.language]
    width = max((len(i) for i in ids), default=0)
    for i in ids:
        s = scripts[i]
        print(f"{i:<{width}}  {s['category']:<9} {s['language']:<10} {s['description'] or s['path']}")
    print(f"-- {len(ids)}/{len(scripts)} script(s)", file=sys.stderr)
    return 0


def cmd_info(db: dict, args) -> int:
    s = db["scripts"].get(args.id)
    if not s:
        print(f"no such script: {args.id}", file=sys.stderr)
        return 1
    print(json.dumps(s, indent=2, ensure_ascii=False))
    return 0


def cmd_search(db: dict, args) -> int:
    pat = re.compile(args.pattern, re.IGNORECASE)
    for sid, s in sorted(db["scripts"].items()):
        blob = " ".join([sid, s.get("label", ""), s.get("description", ""), s["path"]])
        if pat.search(blob):
            print(f"{sid}  {s['description'] or s['path']}")
    return 0


def cmd_run(db: dict, args) -> int:
    scripts = db["scripts"]
    if args.id not in scripts:
        print(f"no such script: {args.id}", file=sys.stderr)
        return 1
    order = resolve_deps(scripts, args.id) if args.with_deps else [args.id]
    for sid in order:
        rc = invoke(scripts[sid], args.passthrough or [])
        if rc != 0:
            print(f"[run] {sid} exited with {rc}", file=sys.stderr)
            return rc
    return 0


def cmd_graph(db: dict, _args) -> int:
    scripts = db["scripts"]
    for sid in sorted(scripts):
        deps = scripts[sid].get("depends_on") or []
        if deps:
            print(f"{sid}  <-  {', '.join(deps)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="script-run")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--category")
    p.add_argument("--language")
    p = sub.add_parser("info");   p.add_argument("id")
    p = sub.add_parser("search"); p.add_argument("pattern")
    p = sub.add_parser("run")
    p.add_argument("id")
    p.add_argument("--with-deps", action="store_true")

    # Split argv on `--` so REMAINDER-style passthrough doesn't swallow flags.
    argv = sys.argv[1:]
    passthrough: list[str] = []
    if "--" in argv:
        idx = argv.index("--")
        passthrough = argv[idx + 1:]
        argv = argv[:idx]

    sub.add_parser("graph")

    args = ap.parse_args(argv)
    args.passthrough = passthrough
    db = load()
    handler = {
        "list":   cmd_list,
        "info":   cmd_info,
        "search": cmd_search,
        "run":    cmd_run,
        "graph":  cmd_graph,
    }[args.cmd]
    return handler(db, args)


if __name__ == "__main__":
    sys.exit(main())
