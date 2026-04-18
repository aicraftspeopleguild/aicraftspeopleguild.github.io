#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-readme-api-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L4/svg/readme-api.svg"]
# }
# @end-tag-event
"""API table as SVG — endpoint path + live indicator chip."""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "readme-api.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"

ENDPOINTS = [
    ("/guild/Enterprise/L4/api/health.json",   "health.json",   "api"),
    ("/guild/Enterprise/L4/api/papers.json",   "papers.json",   "api"),
    ("/guild/Enterprise/L4/api/members.json",  "members.json",  "api"),
    ("/guild/Enterprise/L4/api/state.json",    "state.json",    "api"),
    ("/guild/Enterprise/L4/runtime/tags.json", "runtime tags",  "runtime"),
]


def _probe(url: str) -> tuple:
    try:
        req = urllib.request.Request(BASE + url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, int(r.headers.get("Content-Length") or 0)
    except Exception:
        return 0, 0


def render() -> str:
    w = 1040
    row_h = 44
    rows = len(ENDPOINTS)
    h = 56 + rows * row_h + 20

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="ACG live API endpoints">',
        S.shared_defs(),
        S.window_chrome(w, 36, "📡 live API endpoints · static JSON · CORS open"),
        f'<rect y="36" width="{w}" height="{h-36}" fill="url(#gBg)"/>',
    ]

    for i, (path, label, kind) in enumerate(ENDPOINTS):
        y = 56 + i * row_h
        color = "g" if kind == "api" else "p"
        parts.append(S.pulse_dot(28, y + 16, color, r=5, ring_r=8))
        parts.append(f'<a href="{S.esc(BASE + path)}" target="_blank">'
                     f'<text x="50" y="{y + 20}" class="t vs">{S.esc(label)}</text>'
                     f'<text x="50" y="{y + 36}" class="t sub">{S.esc(path)}</text></a>')
        status, size = _probe(path)
        chip_color = "g" if status == 200 else "r"
        chip_txt = f"{status} · {size//1024}KB" if status == 200 else f"HTTP {status or '—'}"
        parts.append(S.chip(w - 160, y + 22, chip_txt, chip_color))

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[readme-api] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
