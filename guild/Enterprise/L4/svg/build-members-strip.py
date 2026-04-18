#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-members-strip-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/members-strip.svg"]
# }
# @end-tag-event
"""Horizontal member strip: emoji + name + paper count."""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "members-strip.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return []


def render() -> str:
    members = _get(f"{BASE}/guild/Enterprise/L4/api/members.json") or []
    papers  = _get(f"{BASE}/guild/Enterprise/L4/api/papers.json") or []

    # Count papers per member by author-name substring match
    paper_count = {}
    for p in papers:
        for m in members:
            if (p.get("author") or "").lower().find(m.get("name", "").lower()) >= 0:
                paper_count[m.get("slug") or m.get("name")] = paper_count.get(m.get("slug") or m.get("name"), 0) + 1

    cw, ch, gap = 240, 80, 10
    cols = 4
    rows = max(1, (len(members) + cols - 1) // cols)
    W = cols * cw + (cols + 1) * gap
    H = 56 + rows * (ch + gap) + gap

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG members">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"⚒ members · {len(members)} founding · click to open profile"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]
    for i, m in enumerate(members):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = 56 + r * (ch + gap)
        slug = m.get("slug") or m.get("name", "")
        count = paper_count.get(slug, 0)
        url = f"{BASE}/#/members/{slug}"
        bg, _ = S.panel(x, y, cw, ch)
        parts.append(f'<a href="{S.esc(url)}" target="_blank">')
        parts.append(bg)
        parts.append(S.pulse_dot(x + 22, y + ch // 2, "g", r=6, ring_r=9))
        parts.append(f'<text x="{x + 42}" y="{y + ch//2 - 4}" class="t vs">{S.esc(m.get("name", "—"))}</text>')
        parts.append(f'<text x="{x + 42}" y="{y + ch//2 + 14}" class="t sub">{count} paper{"s" if count != 1 else ""} · {S.esc(m.get("role", "") or m.get("title", "")[:22])}</text>')
        parts.append('</a>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[members-strip] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
