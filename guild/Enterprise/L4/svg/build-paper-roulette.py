#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-paper-roulette-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/paper-roulette.svg"]
# }
# @end-tag-event
"""Random-paper teaser. Picks a slug by (heartbeat timestamp mod N) so
every workflow run features a different paper — deterministic but
looks random to a reader."""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "paper-roulette.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return []


def render() -> str:
    papers = _get(f"{BASE}/guild/Enterprise/L4/api/papers.json") or []
    hb     = gh_tag.read("demo.heartbeat")
    seed   = int(str(hb.get("value") or 0)) if hb.get("ok") else 0
    p      = papers[seed % len(papers)] if papers else {}

    W, H = 1040, 180
    slug  = p.get("slug") or (p.get("id","") or "").lower()
    url   = f"{BASE}/#/whitepapers/{slug}" if slug else BASE

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="random paper roulette">',
        S.shared_defs(),
        f'<a href="{S.esc(url)}" target="_blank">',
        S.window_chrome(W, H, "⚒ paper roulette · 🎲 click for the current pick"),
    ]

    parts.append(f'<text x="40" y="96" class="t" font-size="40">🎲</text>')
    title = (p.get("title") or "no papers yet")[:72]
    parts.append(f'<text x="104" y="86" class="t" font-size="20" font-weight="700" fill="{S.P["text"]}">{S.esc(title)}</text>')
    sub = f'{p.get("author","")}  ·  {p.get("date","")}  ·  {p.get("doc_number","")}'
    parts.append(f'<text x="104" y="110" class="t sub">{S.esc(sub)}</text>')
    if p.get("abstract"):
        parts.append(f'<text x="104" y="134" class="t" font-size="11" fill="{S.P["dim"]}" font-style="italic">{S.esc(p.get("abstract","")[:120])}…</text>')

    parts.append(f'<text x="{W-20}" y="88" text-anchor="end" class="t" font-size="12" fill="{S.P["blue"]}">open paper ↗</text>')
    parts.append(f'<text x="{W-20}" y="106" text-anchor="end" class="t sub">pick rerolls on every heartbeat</text>')

    parts.append('</a>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[paper-roulette] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
