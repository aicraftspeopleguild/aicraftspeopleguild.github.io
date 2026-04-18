#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-udt-tree-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/udt-tree.svg"]
# }
# @end-tag-event
"""UDT type hierarchy — renders the atomic→page SVG ladder and the
Tool→Script→Pipeline stack as a tree with live instance counts from
tag.db. Each node links to the UDT editor filtered by its type."""
import sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import site_base

OUT    = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "udt-tree.svg"
TAG_DB = REPO / "tag.db"
BASE   = site_base.site_base()

GROUPS = [
    {
        "title": "SVG composition ladder",
        "color": "g",
        "nodes": [
            ("SvgAtom",     "primitive — chip, dot, bar, divider"),
            ("SvgMolecule", "atoms bound together — tag card, stat block, kv row"),
            ("SvgOrganism", "live dashboards — scada, heatmap, network"),
            ("Page",        "full pages composed of organisms"),
        ],
    },
    {
        "title": "Automation stack",
        "color": "p",
        "nodes": [
            ("Tool",     "one shell/py call the runner can invoke"),
            ("Script",   "tool + @tag-event trigger"),
            ("Pipeline", "ordered script graph with gating"),
            ("Api",      "http watcher that writes to a tag"),
        ],
    },
    {
        "title": "Catalog entities",
        "color": "o",
        "nodes": [
            ("WhitePaper", "authored published artefact"),
            ("Member",     "charter signatory"),
            ("Program",    "governance body or working group"),
            ("PackMLState","a single node in the PackML state chart"),
        ],
    },
    {
        "title": "Fabric",
        "color": "a",
        "nodes": [
            ("Component",  "reusable UI fragment"),
            ("View",       "named route into the site"),
            ("Path",       "filesystem anchor for a UDT"),
            ("Query",      "named SQL view into a db"),
        ],
    },
]


def _counts():
    if not TAG_DB.exists(): return {}
    c = sqlite3.connect(str(TAG_DB))
    rows = dict(c.execute("SELECT udt_type, COUNT(*) FROM udts WHERE udt_type IS NOT NULL AND udt_type!='' GROUP BY udt_type"))
    c.close()
    return rows


def render() -> str:
    counts = _counts()
    cols = 2
    W = 1040
    col_w = (W - 48) // cols
    group_rows = [GROUPS[i:i+cols] for i in range(0, len(GROUPS), cols)]

    row_h = 170
    H = 56 + len(group_rows) * row_h + 40

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="UDT type hierarchy">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"🌲 UDT tree · {sum(counts.values())} instances across {len(counts)} types"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    for r, gs in enumerate(group_rows):
        for ci, grp in enumerate(gs):
            x = 24 + ci * (col_w + 16)
            y = 52 + r * row_h
            bg, _ = S.panel(x, y, col_w - 16, row_h - 16)
            parts.append(bg)
            col = {"g":"green", "p":"purple", "o":"orange", "a":"amber"}[grp["color"]]
            parts.append(f'<text x="{x+14}" y="{y+22}" class="t" font-size="11" font-weight="700" fill="{S.P[col]}">{S.esc(grp["title"])}</text>')
            # Tree trunk
            trunk_x = x + 24
            first_y = y + 52
            last_y  = first_y + (len(grp["nodes"]) - 1) * 28
            parts.append(f'<line x1="{trunk_x}" y1="{first_y}" x2="{trunk_x}" y2="{last_y}" stroke="{S.P["border"]}" stroke-width="1"/>')
            for i, (name, blurb) in enumerate(grp["nodes"]):
                ny = first_y + i * 28
                n  = counts.get(name, 0)
                # branch
                parts.append(f'<line x1="{trunk_x}" y1="{ny}" x2="{trunk_x + 20}" y2="{ny}" stroke="{S.P["border"]}" stroke-width="1"/>')
                parts.append(f'<circle cx="{trunk_x}" cy="{ny}" r="4" fill="{S.P[col]}"/>')
                href = f"{BASE}/guild/apps/udt-editor/#udt={name.lower()}"
                parts.append(f'<a href="{S.esc(href)}" target="_blank">')
                parts.append(f'<text x="{trunk_x + 28}" y="{ny + 4}" class="t" font-size="13" font-weight="600" fill="{S.P["text"]}">{S.esc(name)}</text>')
                parts.append(f'<text x="{trunk_x + 28 + 9 * len(name)}" y="{ny + 4}" class="t sub"> · {S.esc(blurb)}</text>')
                # count chip
                parts.append(S.chip(x + col_w - 76, ny - 8, f"{n:>3}", grp["color"]))
                parts.append('</a>')

    fy = H - 18
    parts.append(f'<text x="24" y="{fy}" class="t sub">counts pulled from tag.db.udts</text>')
    parts.append(f'<text x="{W-24}" y="{fy}" text-anchor="end" class="t sub">click any type → UDT editor filter</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[udt-tree] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
