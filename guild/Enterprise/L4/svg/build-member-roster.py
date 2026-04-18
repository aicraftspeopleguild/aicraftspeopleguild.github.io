#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-member-roster-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/member-roster.svg"]
# }
# @end-tag-event
"""Full member roster — 8 cards, 4-per-row. Each card has an <image>
avatar, name, role, top 3 expertise tags, paper count, and a clickable
<a href> to the member page. Rendered avatars reference the same
relative path as the HTML members page."""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import site_base

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "member-roster.svg"
BASE = site_base.site_base()


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return []


def _paper_count(papers, name):
    if not name: return 0
    key = name.lower()
    return sum(1 for p in papers if key in (p.get("author", "") or "").lower())


def render() -> str:
    members = _get(f"{BASE}/guild/Enterprise/L4/api/members.json") or []
    papers  = _get(f"{BASE}/guild/Enterprise/L4/api/papers.json")  or []

    cols, cw, ch, gap = 4, 244, 156, 14
    rows = (len(members) + cols - 1) // cols or 1
    W = cols * cw + (cols + 1) * gap
    H = 56 + rows * (ch + gap) + 40

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Guild member roster">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"👥 member roster · {len(members)} craftspeople · click any card"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    for i, m in enumerate(members):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = 52 + r * (ch + gap)
        handle  = m.get("handle") or ""
        name    = m.get("name") or handle
        role    = m.get("role") or ""
        tags    = (m.get("expertise_tags") or [])[:3]
        avatar  = m.get("avatar_href") or ""
        papers_n = _paper_count(papers, name)
        href = f"{BASE}/guild/Enterprise/members/#{handle}"
        parts.append(f'<a href="{S.esc(href)}" target="_blank">')
        bg, _ = S.panel(x, y, cw, ch)
        parts.append(bg)
        # Avatar
        if avatar:
            ahref = f"{BASE}/guild/Enterprise/L4/members/{handle}/{avatar}"
            parts.append(
                f'<clipPath id="clip-{i}"><circle cx="{x+36}" cy="{y+40}" r="22"/></clipPath>'
                f'<image x="{x+14}" y="{y+18}" width="44" height="44" href="{S.esc(ahref)}" clip-path="url(#clip-{i})" preserveAspectRatio="xMidYMid slice"/>'
                f'<circle cx="{x+36}" cy="{y+40}" r="22" fill="none" stroke="{S.P["border"]}" stroke-width="2"/>'
            )
        else:
            parts.append(f'<circle cx="{x+36}" cy="{y+40}" r="22" fill="{S.P["bg_b"]}" stroke="{S.P["border"]}" stroke-width="2"/>')
            parts.append(f'<text x="{x+36}" y="{y+46}" text-anchor="middle" class="t" font-size="14" font-weight="700" fill="{S.P["green"]}">{S.esc("".join(w[0] for w in name.split()[:2]).upper())}</text>')
        # Name + role
        short = name if len(name) <= 20 else name[:19] + "…"
        parts.append(f'<text x="{x+70}" y="{y+36}" class="t" font-size="13" font-weight="700" fill="{S.P["text"]}">{S.esc(short)}</text>')
        parts.append(f'<text x="{x+70}" y="{y+52}" class="t sub">{S.esc(role)}</text>')
        # Paper count chip
        if papers_n:
            parts.append(S.chip(x + 70, y + 60, f"{papers_n} paper{'s' if papers_n != 1 else ''}", "g"))
        # Expertise tag chips (max 3), wrapped in 2 rows
        ty = y + 94
        tx = x + 14
        for t in tags:
            t_short = t if len(t) <= 14 else t[:13] + "…"
            chip_w = max(54, len(t_short) * 7 + 14)
            if tx + chip_w > x + cw - 14:
                tx = x + 14
                ty += 22
            parts.append(f'<rect x="{tx}" y="{ty-12}" width="{chip_w}" height="18" rx="9" fill="{S.P["bg_b"]}" stroke="{S.P["border"]}"/>')
            parts.append(f'<text x="{tx + chip_w//2}" y="{ty+1}" text-anchor="middle" class="t" font-size="10" fill="{S.P["dim"]}">{S.esc(t_short)}</text>')
            tx += chip_w + 6
        # Signed checkmark
        if m.get("signed"):
            parts.append(f'<text x="{x + cw - 16}" y="{y + 24}" text-anchor="end" class="t" font-size="12" fill="{S.P["green"]}">✓ signed</text>')
        parts.append('</a>')

    # Footer
    fy = H - 18
    parts.append(f'<text x="24" y="{fy}" class="t sub">every card → deep-link to the member page</text>')
    parts.append(f'<text x="{W-24}" y="{fy}" text-anchor="end" class="t sub">rebuilt on every heartbeat</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[member-roster] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
