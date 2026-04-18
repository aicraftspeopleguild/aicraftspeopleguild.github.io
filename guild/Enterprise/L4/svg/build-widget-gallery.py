#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-widget-gallery-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/widget-gallery.svg"]
# }
# @end-tag-event
"""Gallery of every SvgOrganism: name, size, sources, composes list."""
import json, sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT    = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "widget-gallery.svg"
TAG_DB = REPO / "tag.db"
BASE   = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _widgets():
    if not TAG_DB.exists(): return []
    c = sqlite3.connect(str(TAG_DB))
    c.row_factory = sqlite3.Row
    rows = [dict(r) for r in c.execute(
        "SELECT id, body FROM udts WHERE udt_type='SvgOrganism' ORDER BY id"
    )]
    c.close()
    out = []
    for r in rows:
        try:
            b = json.loads(r["body"])
            if "$schema" in b: continue
            p = b.get("parameters", {})
            if not isinstance(p.get("entry"), str): continue
            out.append({
                "id": r["id"],
                "output": p.get("output", ""),
                "sources": p.get("sources") or [],
                "composes": p.get("composes") or [],
                "size": p.get("size") or {},
            })
        except Exception:
            pass
    return out


def render() -> str:
    items = _widgets()
    cols = 2
    cw, ch, gap = 504, 100, 12
    rows = (len(items) + cols - 1) // cols
    W = cols * cw + (cols + 1) * gap
    H = 56 + rows * (ch + gap) + gap
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG widget gallery">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"⚒ widget gallery · {len(items)} SvgOrganisms · click to open"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = 56 + r * (ch + gap)
        url = f"{BASE}/{it['output']}" if it["output"] else ""
        bg, _ = S.panel(x, y, cw, ch)
        parts.append(f'<a href="{S.esc(url)}" target="_blank">')
        parts.append(bg)
        parts.append(S.pulse_dot(x + 22, y + 28, "g", r=5, ring_r=8))
        parts.append(f'<text x="{x + 40}" y="{y + 32}" class="t vs">{S.esc(it["id"])}</text>')
        composes = ", ".join(it["composes"])[:72]
        if composes:
            parts.append(f'<text x="{x + 14}" y="{y + 58}" class="t sub">composes: {S.esc(composes)}</text>')
        sources = ", ".join(it["sources"])[:72] if it["sources"] else "(no sources)"
        parts.append(f'<text x="{x + 14}" y="{y + 76}" class="t sub">sources: {S.esc(sources)}</text>')
        size = it["size"]
        if isinstance(size, dict) and "w" in size:
            parts.append(f'<text x="{x + cw - 14}" y="{y + ch - 10}" text-anchor="end" class="t sub">{S.esc(size.get("w"))} × {S.esc(size.get("h"))}</text>')
        parts.append('</a>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[widget-gallery] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
