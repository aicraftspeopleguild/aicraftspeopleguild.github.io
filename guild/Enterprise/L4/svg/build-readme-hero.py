#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-readme-hero-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L4/svg/readme-hero.svg"]
# }
# @end-tag-event
"""
README hero banner: title, emblem, tagline, live health chips. Single SVG
card that replaces the top-of-readme title + badge cluster with one neat
composition.
"""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "readme-hero.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return {}


def render() -> str:
    health = _get(f"{BASE}/guild/Enterprise/L4/api/health.json")
    hb     = gh_tag.read("demo.heartbeat")
    w, h = 1040, 240
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="ACG hero">',
        S.shared_defs(),
        S.window_chrome(w, h, "⚒ AI Craftspeople Guild · ISA-95 live control-plane"),
    ]

    # Emblem + title
    parts.append(f'<text x="40" y="100" class="t" font-size="48" fill="{S.P["green"]}">⚒</text>')
    parts.append(f'<text x="108" y="92" class="t" font-size="30" font-weight="700" fill="{S.P["text"]}">ACG · Guild HMI</text>')
    parts.append(f'<text x="108" y="116" class="t sub">ISA-95 live control-plane · static JSON API · browser P2P mesh</text>')

    # Divider
    parts.append(S.divider(40, 140, w - 80))

    # Status chips at bottom
    chip_y = 180
    parts.append(S.chip(40,  chip_y, f'papers {health.get("paperCount","—")}',  "g"))
    parts.append(S.chip(160, chip_y, f'members {health.get("memberCount","—")}', "o"))
    parts.append(S.chip(280, chip_y, f'api v{health.get("apiVersion","—")}',    "p"))
    if hb.get("ok"):
        parts.append(S.chip(400, chip_y, f'💓 {S.pretty_ts(hb.get("value"))}', "g"))

    # Right-side quick links
    parts.append(f'<text x="{w-20}" y="92" text-anchor="end" class="t lo">teslasolar.github.io/aicraftspeopleguild.github.io</text>')
    parts.append(f'<text x="{w-20}" y="116" text-anchor="end" class="t sub">pages static · CORS open · rebuilt on push</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[readme-hero] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
