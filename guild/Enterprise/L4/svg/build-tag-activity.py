#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-tag-activity-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/tag-activity.svg"]
# }
# @end-tag-event
"""Rolling activity feed: last 12 tag_history rows from state.db."""
import sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "tag-activity.svg"
STATE_DB = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"


def _rows():
    if not STATE_DB.exists(): return []
    try:
        c = sqlite3.connect(str(STATE_DB))
        r = c.execute(
            "SELECT tag, value, quality, at FROM tag_history ORDER BY at DESC LIMIT 12"
        ).fetchall()
        c.close()
        return r
    except Exception:
        return []


def render() -> str:
    rows = _rows()
    W, row_h = 1040, 30
    H = 56 + max(1, len(rows)) * row_h + 16
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG tag activity">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"⚒ tag activity · last {len(rows)} writes · state.db/tag_history"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]
    if not rows:
        parts.append(f'<text x="{W//2}" y="{H//2}" text-anchor="middle" class="t sub">no activity recorded — state.db is empty</text>')
    else:
        for i, (tag, value, quality, at) in enumerate(rows):
            y = 56 + i * row_h
            color = "g" if (quality or "good") == "good" else ("a" if quality == "uncertain" else "r")
            parts.append(S.pulse_dot(24, y + 10, color, r=4, ring_r=7))
            # dim timestamp, blue tag path, white value
            ts = (at or "")[-9:-1]  # HH:MM:SS slice
            parts.append(f'<text x="42" y="{y + 14}" class="t sub">{S.esc(ts)}</text>')
            parts.append(f'<text x="110" y="{y + 14}" class="t" font-size="12" fill="{S.P["blue"]}">{S.esc(tag)}</text>')
            v = str(value)[:60]
            parts.append(f'<text x="{W-20}" y="{y + 14}" text-anchor="end" class="t" font-size="12" fill="{S.P["text"]}">{S.esc(v)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[tag-activity] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
