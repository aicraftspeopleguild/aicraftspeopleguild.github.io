#!/usr/bin/env python3
"""
ingest-script-events — scan the repo for every @tag-event header and
materialise each one as a StateMachineScript UDT instance under
  guild/Enterprise/L3/udts/script/instances/<slug>.json
Also rewrites
  guild/Enterprise/L3/udts/script/instances/_index.json
  guild/Enterprise/L3/udts/machine/instances/_index.json
so the compressed UDT editor can populate its dropdowns dynamically.

Usage
-----
  python bin/ingest-script-events.py              # local JSON only
  python bin/ingest-script-events.py --push       # also upsert GitHub
                                                  # issues `tag:script.<id>`
                                                  # via gh_tag.write

Running with --push requires GITHUB_TOKEN or `gh auth token`. Safe to
run anywhere (it dedupes by title via gh_tag.write's upsert path).
"""
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIB  = REPO / "guild" / "Enterprise" / "L2" / "lib"
sys.path.insert(0, str(LIB))
from tag_event_parser import parse_tree  # noqa: E402

UDT_DIR   = REPO / "guild" / "Enterprise" / "L3" / "udts"
SCRIPT_OUT = UDT_DIR / "script" / "instances"
MACHINE_OUT = UDT_DIR / "machine" / "instances"
SCAN_DIRS = [
    REPO / "guild" / "Enterprise" / "L3" / "scripts",
    REPO / "guild" / "Enterprise" / "L4" / "api" / "scripts",
    REPO / "guild" / "Enterprise" / "L4" / "svg",
    REPO / "guild" / "Enterprise" / "L2" / "lib",
    REPO / "bin",
]

SLUG_RE = re.compile(r"[^a-z0-9._-]+")


def _slug(s: str) -> str:
    return SLUG_RE.sub("-", (s or "anon").lower()).strip("-")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(decl: dict, script_rel: str) -> dict:
    listens = decl.get("listens") or {}
    if isinstance(listens, list):
        listens = listens[0] if listens else {}
    sid = decl.get("id") or f"{Path(script_rel).stem}:anon"
    return {
        "id":             sid,
        "enabled":        bool(decl.get("enabled", True)),
        "script_file":    script_rel,
        "schemaVersion":  "1.0.0",
        "kind":           listens.get("kind") or "on_transition",
        "listens_tag":    listens.get("tag"),
        "listens_from":   listens.get("from"),
        "listens_to":     listens.get("to"),
        "interval_s":     listens.get("interval_s"),
        "condition":      decl.get("condition"),
        "action_tool_id": decl.get("action_tool_id"),
        "reads":          decl.get("reads")  or [],
        "writes":         decl.get("writes") or [],
        "fires":          decl.get("fires")  or [],
        "lastFiredAt":    None,
        "fireCount":      0,
        "lastError":      None,
        "parsed_at":      _now(),
    }


def _write_instance(out_dir: Path, udt_type: str, slug: str, params: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = {"udtType": udt_type, "instance": slug, "parameters": params}
    p = out_dir / f"{slug}.json"
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def _write_index(out_dir: Path, udt_type: str, items: list[dict]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    idx = {
        "udtType":  udt_type,
        "count":    len(items),
        "generated": _now(),
        "instances": items,
    }
    p = out_dir / "_index.json"
    p.write_text(json.dumps(idx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def ingest(push: bool = False) -> dict:
    hits = []
    for d in SCAN_DIRS:
        if d.exists():
            hits.extend(parse_tree(d))
    hits.sort(key=lambda t: (t[0].as_posix(), (t[1].get("id") or "")))

    items = []
    kept = 0
    # Clear old instance files (keep _index.json stub) to match current scan.
    if SCRIPT_OUT.exists():
        for old in SCRIPT_OUT.glob("*.json"):
            if old.name != "_index.json":
                old.unlink()

    for path, decl in hits:
        rel = path.relative_to(REPO).as_posix()
        params = _norm(decl, rel)
        slug = _slug(params["id"])
        if not slug:
            continue
        _write_instance(SCRIPT_OUT, "StateMachineScript", slug, params)
        items.append({
            "slug":        slug,
            "id":          params["id"],
            "script_file": params["script_file"],
            "enabled":     params["enabled"],
            "kind":        params["kind"],
            "listens_tag": params["listens_tag"],
        })
        kept += 1

    _write_index(SCRIPT_OUT, "StateMachineScript", items)

    # Also refresh the machine index so the editor's dropdown is uniform.
    if MACHINE_OUT.exists():
        machines = []
        for f in sorted(MACHINE_OUT.glob("*.json")):
            if f.name == "_index.json":
                continue
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
                machines.append({
                    "slug": f.stem,
                    "id":   doc.get("parameters", {}).get("id", f.stem),
                    "name": doc.get("parameters", {}).get("name", f.stem),
                })
            except Exception:
                continue
        _write_index(MACHINE_OUT, "Machine", machines)

    summary = {"scripts_ingested": kept, "local_out": str(SCRIPT_OUT.relative_to(REPO))}

    if push and kept:
        sys.path.insert(0, str(LIB))
        import gh_tag  # noqa: E402
        pushed = 0
        errs = 0
        for path, decl in hits:
            rel = path.relative_to(REPO).as_posix()
            params = _norm(decl, rel)
            sid = params["id"]
            try:
                gh_tag.write(
                    path=f"script.{sid}",
                    value=("enabled" if params["enabled"] else "disabled"),
                    quality="good",
                    type="UDT:StateMachineScript",
                    description=json.dumps(params, ensure_ascii=False),
                )
                pushed += 1
            except Exception as e:
                errs += 1
                print(f"✗ push {sid}: {e}", file=sys.stderr)
        summary["pushed"] = pushed
        summary["push_errors"] = errs

    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true",
                    help="also upsert tag:script.<id> issues via gh_tag")
    args = ap.parse_args()
    out = ingest(push=args.push)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
