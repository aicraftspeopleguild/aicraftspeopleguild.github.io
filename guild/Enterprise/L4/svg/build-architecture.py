#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-architecture-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/architecture.svg"]
# }
# @end-tag-event
"""ISA-95 pyramid, every tier clickable to its dir."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "architecture.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"

TIERS = [
    ("L4", "ERP · business",       "#c47a20", "g", "/api/*.json · runtime/tags.json · acg.db · members · papers"),
    ("L3", "MES · ops",            "#a371f7", "p", "build pipeline · L3/scripts · L3/tools · state.db"),
    ("L2", "SCADA · HMI",          "#4a8868", "o", "tag plant · gateway · hmi · PackML · renderer"),
    ("L1", "sensing · PLC",        "#79c0ff", "g", "GitPLC UDTs · submit form"),
    ("L0", "physical · people",    "#8b949e", "g", "authors · mobbers · reviewers"),
]

PATHS = {
    "L0": f"{BASE}/guild/Enterprise/L0/",
    "L1": f"{BASE}/guild/Enterprise/L1/",
    "L2": f"{BASE}/guild/Enterprise/L2/",
    "L3": f"{BASE}/guild/Enterprise/L3/",
    "L4": f"{BASE}/guild/Enterprise/L4/",
}


def render() -> str:
    W, H = 1040, 400
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG ISA-95 architecture">',
        S.shared_defs(),
        S.window_chrome(W, H, "⚒ architecture · ISA-95 levels · click a tier"),
    ]

    cx = W // 2
    top_y  = 60
    row_h  = 52
    gap    = 4
    base_w = 820     # bottom row width
    top_w  = 240     # top row width

    for i, (lvl, title, color_hex, color_class, desc) in enumerate(TIERS):
        # i=0 is L4 (top), i=4 is L0 (bottom). Interpolate width linearly.
        t = i / (len(TIERS) - 1)
        w = int(top_w + (base_w - top_w) * t)
        x = cx - w // 2
        y = top_y + i * (row_h + gap)
        parts.append(
            f'<a href="{S.esc(PATHS[lvl])}" target="_blank">'
            f'<rect x="{x}" y="{y}" width="{w}" height="{row_h}" rx="6" '
            f'fill="{S.P["bg_b"]}" stroke="{color_hex}" stroke-width="2"/>'
            f'<text x="{x + 14}" y="{y + row_h//2 + 4}" class="t" font-size="14" font-weight="700" fill="{color_hex}">{lvl}</text>'
            f'<text x="{x + 56}" y="{y + row_h//2 - 2}" class="t vs">{S.esc(title)}</text>'
            f'<text x="{x + 56}" y="{y + row_h//2 + 14}" class="t sub">{S.esc(desc)}</text>'
            f'</a>'
        )

    parts.append(f'<text x="{W//2}" y="{H-14}" text-anchor="middle" class="t sub">Each row is a clickable deep-link to its Enterprise directory.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[architecture] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
