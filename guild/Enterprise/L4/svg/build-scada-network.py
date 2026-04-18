#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-scada-network-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/scada-network.svg"]
# }
# @end-tag-event
"""SCADA subsystem network — hand-placed nodes showing the real data
flow between the moving parts of the ACG control plane. Edges colored
by flow kind (read / write / trigger)."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "scada-network.svg"

# Hand-placed nodes — keep on a 1040×520 grid.
NODES = [
    # (id, x, y, emoji, label, color_class)
    ("gh",    140, 100, "🐙", "GitHub Issues",      "p"),
    ("gha",   140, 220, "⚙",  ".github/workflows",  "p"),
    ("state", 520, 340, "🗄",  "state.db",           "o"),
    ("tagdb", 520, 100, "🗄",  "tag.db",             "g"),
    ("docdb", 340, 220, "📚", "docs.db",            "g"),
    ("api",   720, 220, "📡", "/api/*.json",        "g"),
    ("rttag", 720, 340, "⚡", "runtime/tags.json",  "g"),
    ("svg",   900, 220, "🖼",  "assets/svg/*.svg",   "o"),
    ("term",  900, 400, "⌨",  "terminal",           "p"),
    ("llm",   520, 480, "🧠", "WebLLM sandbox",     "p"),
    ("mesh",  140, 400, "🛰",  "p2p mesh",           "o"),
]

EDGES = [
    # (from, to, kind: read/write/trigger, label)
    ("gha",   "gh",   "w", "bump heartbeat"),
    ("gha",   "svg",  "w", "regen"),
    ("gha",   "api",  "w", "build"),
    ("gha",   "rttag","w", "build"),
    ("gh",    "gha",  "t", "issues/cmd"),
    ("state", "svg",  "r", ""),
    ("tagdb", "svg",  "r", ""),
    ("docdb", "term", "r", ""),
    ("api",   "term", "r", ""),
    ("api",   "svg",  "r", ""),
    ("rttag", "svg",  "r", ""),
    ("term",  "gh",   "w", "gh-tag:write"),
    ("term",  "state","w", "tag:write"),
    ("mesh",  "term", "t", "chat"),
    ("mesh",  "llm",  "t", ""),
]

COLORS = {"r": "#79c0ff", "w": "#3fb950", "t": "#f0883e"}


def render() -> str:
    W, H = 1040, 540
    pos = {n[0]: (n[1], n[2]) for n in NODES}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG subsystem network">',
        S.shared_defs(),
        f'''<defs>
  <marker id="arrow-r" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{COLORS["r"]}"/></marker>
  <marker id="arrow-w" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{COLORS["w"]}"/></marker>
  <marker id="arrow-t" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{COLORS["t"]}"/></marker>
</defs>''',
        S.window_chrome(W, H, "⚒ ACG subsystem network · read (blue) · write (green) · trigger (orange)"),
    ]

    # Edges first (under nodes)
    for f, t, kind, label in EDGES:
        x1, y1 = pos[f]
        x2, y2 = pos[t]
        stroke = COLORS.get(kind, S.P["dim"])
        dash = 'stroke-dasharray="4 4"' if kind == "t" else ""
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="1.5" opacity="0.6" '
            f'marker-end="url(#arrow-{kind})" {dash}/>'
        )
        if label:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            parts.append(f'<text x="{mx}" y="{my-4}" text-anchor="middle" class="t" font-size="9" fill="{S.P["dim"]}">{S.esc(label)}</text>')

    # Nodes
    for nid, x, y, emoji, label, color in NODES:
        r = 32
        bg = {"g": "#1a5c4c22", "p": "#a371f722", "o": "#f0883e22", "r": "#f8514922"}.get(color, "#33333322")
        stroke = {"g": S.P["green"], "p": S.P["purple"], "o": S.P["orange"], "r": S.P["red"]}.get(color, S.P["dim"])
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{bg}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" class="t" font-size="22">{S.esc(emoji)}</text>')
        parts.append(f'<text x="{x}" y="{y+r+14}" text-anchor="middle" class="t" font-size="11" fill="{S.P["text"]}">{S.esc(label)}</text>')

    # Legend
    ly = H - 24
    parts.append(f'<circle cx="24" cy="{ly}" r="4" fill="{COLORS["r"]}"/><text x="36" y="{ly+4}" class="t sub">read</text>')
    parts.append(f'<circle cx="110" cy="{ly}" r="4" fill="{COLORS["w"]}"/><text x="122" y="{ly+4}" class="t sub">write</text>')
    parts.append(f'<circle cx="200" cy="{ly}" r="4" fill="{COLORS["t"]}"/><text x="212" y="{ly+4}" class="t sub">trigger (event-driven)</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[scada-network] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
