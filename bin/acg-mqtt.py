#!/usr/bin/env python3
"""
acg-mqtt — headless MQTT-ish tag watcher. Polls the GH-Issues tag DB
via gh_tag and fires a callback on value change. The durable side of
the browser pub/sub at guild/Enterprise/L2/mqtt/.

This is not a full broker — the browser is the live bus, this is the
bridge from the GH-Issues-backed retained store.

Usage
-----
  python bin/acg-mqtt.py sub demo.heartbeat
      Print every change to tag:demo.heartbeat (polls every 10 s).

  python bin/acg-mqtt.py sub "api.health.*"
      Poll a set of tags. * wildcards work on the client side, so we
      list-pull the matching issues and diff each one.

  python bin/acg-mqtt.py pub demo.hello "world"
      Publish a tag value (gh_tag.write).

  python bin/acg-mqtt.py pub demo.counter 5 --type Counter

Requires GITHUB_TOKEN / `gh auth token` for pub; reads are public.
"""
import argparse, fnmatch, json, re, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import gh_tag  # noqa: E402

DEFAULT_INTERVAL = 10


def _list_tag_titles() -> list:
    """Walk label:tag issues and return their path portions."""
    out = []
    for state in ("open", "closed"):
        page = 1
        while True:
            rsp = gh_tag._req("GET", f"/repos/{gh_tag.REPO}/issues?labels=tag&state={state}&per_page=100&page={page}")
            if not rsp:
                break
            for issue in rsp if isinstance(rsp, list) else []:
                title = issue.get("title") or ""
                if title.startswith("tag:"):
                    out.append(title[4:])
            if not isinstance(rsp, list) or len(rsp) < 100:
                break
            page += 1
    return sorted(set(out))


def _match(pattern: str, path: str) -> bool:
    # Convert MQTT-style wildcards to fnmatch: * -> one segment, # -> rest
    if "#" in pattern:
        prefix = pattern.split("#", 1)[0].rstrip(".")
        return path == prefix or path.startswith(prefix + ".")
    # Single-segment * → fnmatch * is multi-segment, so translate to regex
    if "*" in pattern:
        re_p = re.escape(pattern).replace("\\*", "[^.]+")
        return re.fullmatch(re_p, path) is not None
    return pattern == path


def cmd_sub(args) -> int:
    seen = {}
    interval = max(2, args.interval)
    print(f"[acg-mqtt] sub {args.pattern!r}  interval={interval}s  repo={gh_tag.REPO}")
    while True:
        if "*" in args.pattern or "#" in args.pattern:
            paths = [p for p in _list_tag_titles() if _match(args.pattern, p)]
        else:
            paths = [args.pattern]
        for p in paths:
            v = gh_tag.read(p)
            if not v.get("ok"):
                continue
            ts = v.get("updated_at") or ""
            key = f"{p}:{v.get('value')}:{ts}"
            if seen.get(p) != key:
                seen[p] = key
                out = {
                    "topic":    p,
                    "msg":      v.get("value"),
                    "quality":  v.get("quality"),
                    "ts":       ts,
                    "retained": True,
                }
                print(json.dumps(out, ensure_ascii=False))
                sys.stdout.flush()
        if args.once:
            return 0
        time.sleep(interval)


def cmd_pub(args) -> int:
    out = gh_tag.write(
        path=args.topic,
        value=args.value,
        quality=args.quality,
        type=args.type,
        description=args.description or f"acg-mqtt pub at {int(time.time())}",
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out.get("ok") else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("sub", help="subscribe to a tag pattern")
    s.add_argument("pattern")
    s.add_argument("--interval", type=int, default=DEFAULT_INTERVAL)
    s.add_argument("--once", action="store_true", help="emit current values then exit")
    s.set_defaults(fn=cmd_sub)

    p = sp.add_parser("pub", help="publish a tag value")
    p.add_argument("topic")
    p.add_argument("value")
    p.add_argument("--quality",     default="good")
    p.add_argument("--type",        default="String")
    p.add_argument("--description", default="")
    p.set_defaults(fn=cmd_pub)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
