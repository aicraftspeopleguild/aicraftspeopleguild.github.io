#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-readme-controls-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L4/svg/readme-controls.svg"]
# }
# @end-tag-event
"""README controls grid: link cards for terminal, whiteboard, p2p mesh,
submit form. SVG composed from link_card molecules."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "readme-controls.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"

LINKS = [
    ("⌨", "live terminal",     f"{BASE}/guild/apps/terminal/"),
    ("🖍", "p2p whiteboard",    f"{BASE}/guild/apps/whiteboard/"),
    ("🛰", "p2p mesh",          f"{BASE}/guild/apps/p2p/"),
    ("📝", "submit a paper",    f"{BASE}/guild/Enterprise/L1/forms/submit/"),
    ("🎛", "controls",          f"{BASE}/guild/Enterprise/"),
    ("📜", "manifesto",         f"{BASE}/#/manifesto"),
]


def render() -> str:
    cols = 3
    cw, ch, gap = 320, 60, 14
    rows = (len(LINKS) + cols - 1) // cols
    w = cols * cw + (cols + 1) * gap
    h = 56 + rows * (ch + gap) + gap
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="ACG controls">',
        S.shared_defs(),
        S.window_chrome(w, 36, "⚒ controls · jump into an app"),
        f'<rect y="36" width="{w}" height="{h-36}" fill="url(#gBg)"/>',
    ]
    for i, (emoji, title, url) in enumerate(LINKS):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = 56 + r * (ch + gap)
        parts.append(S.link_card(x, y, cw, ch, title, url, emoji))
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[readme-controls] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
