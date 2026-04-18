#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-tag-grid-svg:on-heartbeat",
#   "listens": {
#     "kind": "on_transition", "tag": "demo.heartbeat",
#     "from": "*", "to": "CHANGED"
#   },
#   "writes": ["guild/Enterprise/L4/svg/tag-grid.svg"]
# }
# @end-tag-event
"""
Grid of GitHub-Issue tags (every open issue with label=tag). Each becomes
a small card: namespace, value, quality pulse. Regenerated on each
heartbeat bump so new tags materialize automatically in the README.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "tag-grid.svg"


def render() -> str:
    tags = gh_tag.list_tags().get("tags") or []
    # card grid: 4 columns
    cols = 4
    cw, ch, gap = 220, 90, 14
    rows = (len(tags) + cols - 1) // cols or 1
    w = cols * cw + (cols + 1) * gap
    h = 56 + rows * (ch + gap) + gap

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="ACG tag grid">',
        S.shared_defs(),
        S.window_chrome(w, 36, f"⚒ dynamic tags · {len(tags)} GitHub-Issue tag{'s' if len(tags)!=1 else ''}"),
        # body background continuation
        f'<rect y="36" width="{w}" height="{h-36}" fill="url(#gBg)"/>',
    ]

    for i, t in enumerate(tags):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = 56 + r * (ch + gap)
        color = "g" if (t.get("quality") or "good") == "good" else "a"
        value = t.get("value")
        if value is None: value = "—"
        value_str = str(value)[:28]
        parts.append(S.tag_card(x, y, cw, ch, t["path"], value_str, color,
                                subtitle=f'#{t.get("issue","?")} · {t.get("comments",0)} edit{"s" if t.get("comments")!=1 else ""}'))

    if not tags:
        parts.append(f'<text x="{w//2}" y="{h//2}" text-anchor="middle" class="t sub">no tags yet — run gh-tag:init to seed one</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[tag-grid] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
