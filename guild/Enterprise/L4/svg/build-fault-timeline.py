#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-fault-timeline-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/fault-timeline.svg"]
# }
# @end-tag-event
"""Fault timeline · every active + cleared fault in state.db plotted as
horizontal bars from raised_at → cleared_at. Colored by severity."""
import sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "fault-timeline.svg"
DB  = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"


def _parse(ts):
    if not ts: return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def render() -> str:
    rows = []
    if DB.exists():
        try:
            c = sqlite3.connect(str(DB))
            rows = list(c.execute(
                "SELECT fault_id,kind,severity,tag,raised_at,cleared_at,active "
                "FROM faults ORDER BY raised_at DESC LIMIT 20"
            ))
            c.close()
        except Exception:
            pass

    W, row_h = 1040, 28
    H = 56 + max(1, len(rows)) * row_h + 24

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="fault timeline">',
        S.shared_defs(),
        S.window_chrome(W, 36, f"⚒ fault timeline · {len(rows)} faults in state.db · active + cleared"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    if not rows:
        parts.append(f'<text x="{W//2}" y="{H//2}" text-anchor="middle" class="t sub">no faults recorded — state.db is clean</text>')
    else:
        ts_now = datetime.now(timezone.utc).timestamp()
        earliest = min([(_parse(r[4]) or ts_now) for r in rows])
        span = max(ts_now - earliest, 1)
        bar_x0, bar_w = 220, W - 240
        for i, (fid, kind, severity, tag, raised_at, cleared_at, active) in enumerate(rows):
            y = 56 + i * row_h
            color = {"error":"r","warn":"a","critical":"r","info":"g"}.get(severity or "error", "r")
            r_ts = _parse(raised_at)   or earliest
            c_ts = _parse(cleared_at)  or ts_now
            rx = bar_x0 + int((r_ts - earliest) / span * bar_w)
            cx = bar_x0 + int((c_ts - earliest) / span * bar_w)
            bar_len = max(4, cx - rx)
            parts.append(f'<text x="14" y="{y + 18}" class="t sub">#{fid}</text>')
            parts.append(f'<text x="50" y="{y + 18}" class="t" font-size="11" fill="{S.P["text"]}">{S.esc((kind or "")[:12])}</text>')
            parts.append(f'<text x="150" y="{y + 18}" class="t sub">{S.esc((tag or "")[:10])}</text>')
            fill = S.P["red"] if active else S.P["dim"]
            parts.append(f'<rect x="{rx}" y="{y + 8}" width="{bar_len}" height="14" rx="3" fill="{fill}" opacity="{"1" if active else "0.4"}"/>')
            # status chip at the right
            mark = "ACTIVE" if active else "cleared"
            parts.append(f'<text x="{W-14}" y="{y + 18}" text-anchor="end" class="t sub" fill="{S.P["red"] if active else S.P["dim"]}">{mark}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[fault-timeline] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
