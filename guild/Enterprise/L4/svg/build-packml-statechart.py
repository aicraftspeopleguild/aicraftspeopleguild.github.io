#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-packml-statechart-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/packml-statechart.svg"]
# }
# @end-tag-event
"""PackML state chart — the 16 ISA-88/PackML states laid out as nodes
with major mode edges. The current-state halo reflects
`packml.current` if present, otherwise stays on `EXECUTE`."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag
import site_base

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "packml-statechart.svg"
BASE = site_base.site_base()

# state → (col, row, family, human label)
STATES = {
    "STOPPED":    (0, 2, "idle",    "STOPPED"),
    "IDLE":       (1, 2, "idle",    "IDLE"),
    "STARTING":   (2, 2, "run",     "STARTING"),
    "EXECUTE":    (3, 2, "run",     "EXECUTE"),
    "COMPLETING": (4, 2, "run",     "COMPLETING"),
    "COMPLETE":   (5, 2, "run",     "COMPLETE"),
    "RESETTING":  (6, 2, "idle",    "RESETTING"),

    "HOLDING":    (2, 1, "hold",    "HOLDING"),
    "HELD":       (3, 1, "hold",    "HELD"),
    "UNHOLDING":  (4, 1, "hold",    "UNHOLDING"),

    "SUSPENDING": (2, 3, "suspend", "SUSPENDING"),
    "SUSPENDED":  (3, 3, "suspend", "SUSPENDED"),
    "UNSUSPENDING": (4, 3, "suspend", "UNSUSPENDING"),

    "ABORTING":   (5, 0, "abort",   "ABORTING"),
    "ABORTED":    (6, 0, "abort",   "ABORTED"),
    "CLEARING":   (6, 1, "abort",   "CLEARING"),
    "STOPPING":   (1, 0, "idle",    "STOPPING"),
}

EDGES = [
    ("STOPPED", "IDLE"), ("IDLE", "STARTING"), ("STARTING", "EXECUTE"),
    ("EXECUTE", "COMPLETING"), ("COMPLETING", "COMPLETE"),
    ("COMPLETE", "RESETTING"), ("RESETTING", "IDLE"),
    ("EXECUTE", "HOLDING"), ("HOLDING", "HELD"),
    ("HELD", "UNHOLDING"), ("UNHOLDING", "EXECUTE"),
    ("EXECUTE", "SUSPENDING"), ("SUSPENDING", "SUSPENDED"),
    ("SUSPENDED", "UNSUSPENDING"), ("UNSUSPENDING", "EXECUTE"),
    ("EXECUTE", "ABORTING"), ("ABORTING", "ABORTED"),
    ("ABORTED", "CLEARING"), ("CLEARING", "STOPPED"),
    ("IDLE", "STOPPING"), ("STOPPING", "STOPPED"),
]

COLORS = {
    "idle":    "#8b949e",
    "run":     "#3fb950",
    "hold":    "#e3b341",
    "suspend": "#79c0ff",
    "abort":   "#f85149",
}


def _current():
    v = gh_tag.read("packml.current")
    if v.get("ok") and v.get("value"):
        return str(v["value"]).upper()
    return "EXECUTE"


def _node_xy(col, row):
    return 100 + col * 130, 90 + row * 110


def render() -> str:
    cur = _current()
    W, H = 1040, 520

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="PackML state chart">',
        S.shared_defs(),
        '<defs>'
        '  <marker id="arr" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="6" markerHeight="6" orient="auto">'
        '    <path d="M0,0 L8,4 L0,8 z" fill="#8b949e"/>'
        '  </marker>'
        '</defs>',
        S.window_chrome(W, 36, f"⚙ PackML state chart · ISA-88 · current = {cur}"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    # Edges first
    for a, b in EDGES:
        if a not in STATES or b not in STATES: continue
        ax, ay = _node_xy(*STATES[a][:2])
        bx, by = _node_xy(*STATES[b][:2])
        parts.append(
            f'<line x1="{ax + 36}" y1="{ay}" x2="{bx - 36}" y2="{by}" '
            f'stroke="#30363d" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="3 3"/>'
        )

    # Nodes
    for name, (col, row, fam, label) in STATES.items():
        x, y = _node_xy(col, row)
        color = COLORS[fam]
        is_cur = name == cur
        if is_cur:
            parts.append(f'<circle cx="{x}" cy="{y}" r="36" fill="{color}" opacity="0.22" class="pulse"/>')
        parts.append(f'<rect x="{x-36}" y="{y-18}" width="72" height="36" rx="8" '
                     f'fill="#161b22" stroke="{color}" stroke-width="{3 if is_cur else 1.5}"/>')
        parts.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" class="t" font-size="10" '
                     f'font-weight="{700 if is_cur else 600}" fill="{S.P["text"]}">{S.esc(label)}</text>')

    # Legend
    lx, ly = 24, H - 34
    parts.append(f'<text x="{lx}" y="{ly}" class="t sub">families:</text>')
    for i, (k, c) in enumerate(COLORS.items()):
        parts.append(f'<rect x="{lx + 84 + i*110}" y="{ly-10}" width="12" height="12" rx="3" fill="{c}"/>')
        parts.append(f'<text x="{lx + 100 + i*110}" y="{ly}" class="t" font-size="11" fill="{S.P["dim"]}">{k}</text>')
    parts.append(f'<text x="{W-24}" y="{ly}" text-anchor="end" class="t sub">writes packml.current to re-halo</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[packml-statechart] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
