#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-tag-heatmap-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/tag-heatmap.svg"]
# }
# @end-tag-event
"""Tag density heatmap — rows are top-N directories, one column per
UDT type, cell brightness = log(count). Pulled directly from
tag.db.udts grouped by (dir, udt_type)."""
import math, sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT    = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "tag-heatmap.svg"
TAG_DB = REPO / "tag.db"

TYPE_ORDER = [
    "Tool", "Script", "Path", "Page", "View", "Component",
    "App", "WhitePaper", "Member", "Program",
    "SvgAtom", "SvgMolecule", "SvgOrganism", "PackMLState", "Query", "Api",
]


def _data():
    if not TAG_DB.exists(): return {}, {}
    c = sqlite3.connect(str(TAG_DB))
    by_dir = {}
    by_type = {}
    for d, t, n in c.execute(
        "SELECT dir, udt_type, count(*) FROM udts "
        "WHERE udt_type IS NOT NULL AND udt_type != '' "
        "GROUP BY dir, udt_type"
    ):
        d = d or "(root)"
        by_dir[d] = by_dir.get(d, {})
        by_dir[d][t] = n
        by_type[t] = by_type.get(t, 0) + n
    c.close()
    return by_dir, by_type


def _dir_total(by_dir, d):
    return sum(by_dir[d].values())


def render() -> str:
    by_dir, by_type = _data()
    # Top 16 dirs by total UDT count
    top_dirs = sorted(by_dir.keys(), key=lambda d: -_dir_total(by_dir, d))[:18]
    types = [t for t in TYPE_ORDER if t in by_type]
    # Add any unexpected types at the end
    types += [t for t in by_type if t not in types]

    label_w = 300
    cell_w, cell_h, gap = 34, 22, 2
    W = label_w + len(types) * (cell_w + gap) + 24
    H = 80 + len(top_dirs) * (cell_h + gap) + 80

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="tag density heatmap">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"⚒ tag heatmap · {len(top_dirs)} dirs × {len(types)} UDT types · brightness = log(count)"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    # Column headers (type names, rotated)
    for i, t in enumerate(types):
        x = label_w + i * (cell_w + gap) + cell_w // 2
        parts.append(f'<text x="{x}" y="68" text-anchor="middle" class="t" font-size="9" fill="{S.P["dim"]}" transform="rotate(-45 {x} 68)">{S.esc(t)}</text>')

    # Max count for normalization
    all_counts = [by_dir[d].get(t, 0) for d in top_dirs for t in types]
    max_c = max(all_counts) if all_counts else 1
    log_max = math.log(max_c + 1)

    # Rows
    for r, d in enumerate(top_dirs):
        y = 80 + r * (cell_h + gap)
        short = d if len(d) <= 44 else "…" + d[-42:]
        parts.append(f'<text x="{label_w - 8}" y="{y + cell_h//2 + 4}" text-anchor="end" class="t" font-size="10" fill="{S.P["text"]}">{S.esc(short)}</text>')
        total = _dir_total(by_dir, d)
        parts.append(f'<text x="{label_w - 8}" y="{y + cell_h//2 + 14}" text-anchor="end" class="t" font-size="9" fill="{S.P["dim"]}">{total}</text>')
        for i, t in enumerate(types):
            x = label_w + i * (cell_w + gap)
            count = by_dir[d].get(t, 0)
            if count:
                intensity = math.log(count + 1) / log_max
                # blend between bg and green
                alpha = 0.15 + 0.85 * intensity
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="2" fill="{S.P["green"]}" opacity="{alpha:.2f}"/>')
                if count > 1:
                    parts.append(f'<text x="{x + cell_w//2}" y="{y + cell_h//2 + 3}" text-anchor="middle" class="t" font-size="9" fill="#0d1117">{count}</text>')
            else:
                parts.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="2" fill="{S.P["bg_b"]}" opacity="0.4"/>')

    # Footer legend
    fy = H - 30
    parts.append(f'<text x="24" y="{fy}" class="t sub">legend:</text>')
    for i, alpha in enumerate([0.2, 0.4, 0.6, 0.8, 1.0]):
        parts.append(f'<rect x="{100 + i * 30}" y="{fy - 10}" width="20" height="12" fill="{S.P["green"]}" opacity="{alpha}"/>')
    parts.append(f'<text x="260" y="{fy}" class="t sub">1 → many (log-scaled)</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[tag-heatmap] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
