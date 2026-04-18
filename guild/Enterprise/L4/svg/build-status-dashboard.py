#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-status-dashboard-svg:on-heartbeat",
#   "listens": {
#     "kind": "on_transition", "tag": "demo.heartbeat",
#     "from": "*", "to": "CHANGED"
#   },
#   "writes": ["guild/Enterprise/L4/svg/status-dashboard.svg"]
# }
# @end-tag-event
"""
4-panel status dashboard. Pulls live values from:
  · https://.../guild/Enterprise/L4/api/health.json       (papers, members)
  · https://.../guild/Enterprise/L4/runtime/tags.json      (enterprise, pipeline)
  · GitHub Issues demo.heartbeat via gh_tag.py
"""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag

OUT      = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "status-dashboard.svg"
BASE_URL = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return {}


def render() -> str:
    health = _get(f"{BASE_URL}/guild/Enterprise/L4/api/health.json")
    tags   = _get(f"{BASE_URL}/guild/Enterprise/L4/runtime/tags.json")
    hb     = gh_tag.read("demo.heartbeat")

    enterprise = tags.get("enterprise", {})
    pipeline   = tags.get("pipeline", {})

    def tv(obj, key):
        v = obj.get(key, {})
        return v.get("value", "—") if isinstance(v, dict) else "—"

    w, h = 960, 300
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="ACG status dashboard">',
        S.shared_defs(),
        S.window_chrome(w, h, "⚒ ACG status dashboard · live"),
    ]

    # Four panels in one row
    pw, ph, gap = 220, 220, 20
    y = 56
    x0 = 20
    panels = [
        ("CATALOG",    "g", [
            ("papers",  health.get("paperCount", "—")),
            ("members", health.get("memberCount", "—")),
            ("api",     f"v{health.get('apiVersion', '—')}"),
        ]),
        ("ENTERPRISE", "o", [
            ("programCount",  tv(enterprise, "programCount")),
            ("runCount",      tv(enterprise, "runCount")),
            ("tagEdges",      tv(enterprise, "tagEdges")),
        ]),
        ("PIPELINE",   "p", [
            ("complete", tv(pipeline, "complete")),
            ("aborted",  tv(pipeline, "aborted")),
            ("states",   tv(pipeline, "states")),
        ]),
        ("HEARTBEAT",  "g", [
            ("last",    S.pretty_ts(hb.get("value")) if hb.get("ok") else "—"),
            ("issue",   f"#{hb.get('issue','—')}"     if hb.get("ok") else "—"),
            ("quality", hb.get("quality", "—")        if hb.get("ok") else "—"),
        ]),
    ]
    for i, (title, color, rows) in enumerate(panels):
        x = x0 + i * (pw + gap)
        bg, _ = S.panel(x, y, pw, ph)
        parts.append(bg)
        parts.append(S.pulse_dot(x + 22, y + 30, color, r=7, ring_r=11))
        parts.append(f'<text x="{x + 42}" y="{y + 34}" class="t lb">{S.esc(title)}</text>')
        for j, (lbl, val) in enumerate(rows):
            ry = y + 72 + j * 52
            parts.append(f'<text x="{x + 16}" y="{ry - 14}" class="t sub">{S.esc(lbl)}</text>')
            parts.append(f'<text x="{x + 16}" y="{ry + 8}" class="t vs">{S.esc(val)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[status-dashboard] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
