#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-guild-values-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/guild-values.svg"]
# }
# @end-tag-event
"""Charter banner — the three pillars of the Guild rendered as a
three-up panel. Static content, dynamic signed-members count pulled
from the live API."""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import site_base

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "guild-values.svg"
BASE = site_base.site_base()

PILLARS = [
    ("🤝", "Kindness",      "How we show up for each other when the work is hard.",            "g"),
    ("🧭", "Consideration", "Craft reflects care — for users, teammates, and future readers.", "o"),
    ("🎯", "Respect",       "For the problem, the prior art, and every craftsperson's time.",  "p"),
]


def _members():
    try:
        req = urllib.request.Request(f"{BASE}/guild/Enterprise/L4/api/members.json")
        with urllib.request.urlopen(req, timeout=6) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return []


def render() -> str:
    members = _members()
    signed  = sum(1 for m in members if m.get("signed"))
    W, H = 1040, 260
    cw, cgap = 320, 20
    start_x = (W - 3 * cw - 2 * cgap) // 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Guild charter · three pillars">',
        S.shared_defs(),
        S.window_chrome(W, 36, "⚒ Guild charter · three pillars"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    for i, (emoji, name, blurb, color) in enumerate(PILLARS):
        x = start_x + i * (cw + cgap)
        y = 70
        bg, _ = S.panel(x, y, cw, 140)
        parts.append(bg)
        parts.append(f'<text x="{x + 24}" y="{y + 54}" class="t" font-size="40">{emoji}</text>')
        parts.append(f'<text x="{x + 84}" y="{y + 44}" class="t" font-size="22" font-weight="700" fill="{S.P[{"g":"green","o":"orange","p":"purple"}[color]]}">{S.esc(name)}</text>')
        parts.append(f'<text x="{x + 84}" y="{y + 68}" class="t sub">pillar {i+1}</text>')
        # word-wrap manual: split into ~36-char chunks
        words, line, lines = blurb.split(), "", []
        for w in words:
            if len(line) + len(w) + 1 > 36:
                lines.append(line); line = w
            else:
                line = (line + " " + w).strip()
        if line: lines.append(line)
        for li, txt in enumerate(lines[:3]):
            parts.append(f'<text x="{x + 24}" y="{y + 94 + li * 16}" class="t" font-size="12" fill="{S.P["text"]}">{S.esc(txt)}</text>')

    # Footer chips
    fy = H - 30
    parts.append(S.chip(24,  fy - 12, f"{signed} charter signatures", "g"))
    parts.append(S.chip(200, fy - 12, f"{len(members)} members",      "o"))
    parts.append(f'<text x="{W-24}" y="{fy}" text-anchor="end" class="t sub">kindness · consideration · respect</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[guild-values] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
