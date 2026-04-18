#!/usr/bin/env python3
"""
sm-test — drive state_machine.load_scripts + _match in dry-run mode so
we can see, without actually spawning tool processes, which scripts
would fire for a given synthetic event.

Usage
-----
  python bin/sm-test.py
      Default: fire tag=demo.heartbeat from=* to=CHANGED. Equivalent to
      one heartbeat bump — should match every @tag-event header that
      regenerates SVGs on heartbeat.

  python bin/sm-test.py --tag git:state --to CHANGED
      Alternate transition.

  python bin/sm-test.py --table
      Matrix printout — every script, one line per row, showing its
      source / kind / tag / transition / whether it matched.

  python bin/sm-test.py --fire
      NOT dry-run — actually invoke each matching tool through
      state_machine.fire_event. Use this only in CI or locally.
"""
import argparse, json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIB  = REPO / "guild" / "Enterprise" / "L2" / "lib"
sys.path.insert(0, str(LIB))

import state_machine  # noqa: E402


def _row(script: dict, matched: bool) -> str:
    t = script.get("trigger", {})
    src = script.get("_source") or "?"
    sid = (script.get("id") or "?")[:48]
    tag = (t.get("tag") or "")[:24]
    frm = (t.get("from") or "*") if t.get("kind") == "on_transition" else ""
    to  = (t.get("to")   or "*") if t.get("kind") == "on_transition" else ""
    mark = "HIT" if matched else " . "
    return f"{mark}  {src:<26}  {sid:<48}  {t.get('kind',''):<14}  {tag:<24}  {frm:>6} -> {to:<6}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag",  default="demo.heartbeat")
    ap.add_argument("--from", dest="from_state", default="*")
    ap.add_argument("--to",   default="CHANGED")
    ap.add_argument("--kind", default="on_transition")
    ap.add_argument("--table", action="store_true", help="print every script, matched or not")
    ap.add_argument("--fire",  action="store_true", help="actually execute matching tools")
    ap.add_argument("--json",  action="store_true", help="JSON summary only")
    args = ap.parse_args()

    scripts = state_machine.load_scripts()

    # dedupe counts by source
    by_src = {}
    for s in scripts:
        by_src[s.get("_source", "?")] = by_src.get(s.get("_source", "?"), 0) + 1

    event = {"kind": args.kind, "tag": args.tag, "from": args.from_state, "to": args.to}
    matched = [s for s in scripts if state_machine._match(s, event)]

    summary = {
        "event": event,
        "scripts_total": len(scripts),
        "scripts_by_source": by_src,
        "matched": len(matched),
        "matched_ids": [s.get("id") for s in matched],
    }

    if args.fire:
        out = state_machine.fire_event(
            tag=args.tag, from_state=args.from_state, to_state=args.to, kind=args.kind,
        )
        summary["executed"] = out.get("executed", [])
        summary["fire_ok"]  = out.get("ok")

    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    print(f"== sm-test == event: kind={args.kind}  tag={args.tag}  from={args.from_state}  to={args.to}")
    print(f"  scripts loaded: {len(scripts)}  ({', '.join(f'{k}={v}' for k,v in by_src.items())})")
    print(f"  matched:        {len(matched)}")
    print()

    if args.table:
        print("     source                      id                                                kind            tag                         from -> to")
        print("     " + "-" * 140)
        for s in scripts:
            print("     " + _row(s, s in matched))
    else:
        for s in matched:
            print("     " + _row(s, True))

    if args.fire:
        print()
        print(f"  fire_event result: ok={summary['fire_ok']}  executed={len(summary.get('executed', []))}")

    return 0 if matched or args.table else 1


if __name__ == "__main__":
    sys.exit(main())
