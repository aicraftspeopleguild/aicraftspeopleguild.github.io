#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-paper-feed-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/paper-feed.svg"]
# }
# @end-tag-event
"""Vertical paper feed — the latest N papers from /api/papers.json as
stacked cards with title · author · date · abstract snippet. Each card
is a clickable <a href> to the paper slug."""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import site_base

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "paper-feed.svg"
BASE = site_base.site_base()

MAX_PAPERS = 6


def _papers():
    try:
        with urllib.request.urlopen(f"{BASE}/guild/Enterprise/L4/api/papers.json", timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return []


def _wrap(text: str, n: int, max_lines: int = 2) -> list:
    words, line, lines = (text or "").split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > n:
            lines.append(line); line = w
            if len(lines) >= max_lines:
                return lines[:max_lines-1] + [line[: n - 1] + "…"]
        else:
            line = (line + " " + w).strip()
    if line: lines.append(line)
    return lines[:max_lines]


def render() -> str:
    papers = _papers()[:MAX_PAPERS]

    W = 1040
    cw = W - 48
    ch = 92
    gap = 10
    H = 56 + len(papers) * (ch + gap) + 40

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Latest guild papers">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"📄 paper feed · latest {len(papers)} · click any card to open"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    for i, p in enumerate(papers):
        y = 52 + i * (ch + gap)
        x = 24
        slug   = p.get("slug") or (p.get("id") or "").lower()
        url    = f"{BASE}/#/whitepapers/{slug}" if slug else BASE
        title  = (p.get("title") or "untitled")[:82]
        author = (p.get("author") or "—")[:44]
        date   = (p.get("date") or p.get("publication_date") or "")[:28]
        doc    = p.get("doc_number") or ""
        abs_   = (p.get("abstract") or "")[:220]
        parts.append(f'<a href="{S.esc(url)}" target="_blank">')
        bg, _ = S.panel(x, y, cw, ch)
        parts.append(bg)
        # left rail — paper ordinal
        parts.append(f'<text x="{x+18}" y="{y+38}" class="t" font-size="22" font-weight="700" fill="{S.P["purple"]}">{i+1:02d}</text>')
        parts.append(f'<text x="{x+18}" y="{y+58}" class="t sub">#</text>')
        # body
        parts.append(f'<text x="{x+62}" y="{y+26}" class="t" font-size="14" font-weight="700" fill="{S.P["text"]}">{S.esc(title)}</text>')
        meta = f'{author}  ·  {date}' + (f'  ·  {doc}' if doc else '')
        parts.append(f'<text x="{x+62}" y="{y+44}" class="t sub">{S.esc(meta)}</text>')
        for li, txt in enumerate(_wrap(abs_, 126, 2)):
            parts.append(f'<text x="{x+62}" y="{y+62 + li*14}" class="t" font-size="11" fill="{S.P["dim"]}" font-style="italic">{S.esc(txt)}</text>')
        # right arrow chip
        parts.append(f'<text x="{x + cw - 18}" y="{y+26}" text-anchor="end" class="t" font-size="11" fill="{S.P["blue"]}">open ↗</text>')
        parts.append('</a>')

    fy = H - 18
    parts.append(f'<text x="24" y="{fy}" class="t sub">reads /api/papers.json · CORS open</text>')
    parts.append(f'<text x="{W-24}" y="{fy}" text-anchor="end" class="t sub">click any card → opens the paper reader</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[paper-feed] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
