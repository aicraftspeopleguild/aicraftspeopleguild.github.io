#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-pipeline-pulse-svg:on-heartbeat",
#   "listens": {
#     "kind": "on_transition", "tag": "demo.heartbeat",
#     "from": "*", "to": "CHANGED"
#   },
#   "writes": ["guild/Enterprise/L4/svg/pipeline-pulse.svg"]
# }
# @end-tag-event
"""
Pipeline pulse card — shows the last N pipeline_runs durations as a
sparkline + current complete/aborted counters + latest step status.
Falls back gracefully when state.db / runtime/tags.json aren't present.
"""
import json, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "pipeline-pulse.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return {}


def _durations_from_state_db():
    """Read local state.db for recent pipeline_runs durations."""
    import sqlite3
    f = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"
    if not f.exists():
        return []
    try:
        con = sqlite3.connect(str(f))
        rows = con.execute(
            "SELECT duration_s FROM pipeline_runs ORDER BY started_at DESC LIMIT 20"
        ).fetchall()
        con.close()
        return [float(r[0] or 0) for r in reversed(rows)]  # chronological
    except Exception:
        return []


def render() -> str:
    tags = _get(f"{BASE}/guild/Enterprise/L4/runtime/tags.json")
    pipeline = tags.get("pipeline", {}) if isinstance(tags, dict) else {}
    def tv(key): v = pipeline.get(key, {}); return v.get("value", 0) if isinstance(v, dict) else 0
    complete = tv("complete")
    aborted  = tv("aborted")
    states   = tv("states")
    durations = _durations_from_state_db()

    w, h = 720, 200
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="ACG pipeline pulse">',
        S.shared_defs(),
        S.window_chrome(w, h, "⚒ pipeline · run pulse"),
    ]

    # left: counters stack
    color = "r" if (aborted or 0) > 0 else "g"
    parts.append(S.pulse_dot(40, 80, color, r=8, ring_r=12))
    parts.append(f'<text x="64" y="78" class="t lb">pipeline.complete</text>')
    parts.append(f'<text x="64" y="104" class="t va g">{S.esc(complete)}</text>')
    parts.append(f'<text x="220" y="78" class="t lb">pipeline.aborted</text>')
    parts.append(f'<text x="220" y="104" class="t va {"r" if (aborted or 0) > 0 else "g"}">{S.esc(aborted)}</text>')
    parts.append(f'<text x="380" y="78" class="t lb">pipeline.states</text>')
    parts.append(f'<text x="380" y="104" class="t va">{S.esc(states)}</text>')

    # right: sparkline
    if durations:
        parts.append(f'<text x="{w-200}" y="78" class="t lb">last {len(durations)} run{"s" if len(durations)!=1 else ""}</text>')
        parts.append(S.sparkline(w - 210, 86, 180, 24, durations, color_class="g"))
        avg = sum(durations) / len(durations)
        parts.append(f'<text x="{w-20}" y="130" text-anchor="end" class="t sub">avg {avg:.1f}s</text>')
    else:
        parts.append(f'<text x="{w-20}" y="110" text-anchor="end" class="t sub">no runs yet</text>')

    # footer: bar of complete:aborted
    total = (complete or 0) + (aborted or 0)
    if total > 0:
        cw = int(680 * (complete or 0) / total)
        aw = 680 - cw
        parts.append(f'<rect x="20" y="156" width="{cw}" height="8" rx="3" fill="{S.P["green"]}"/>')
        parts.append(f'<rect x="{20+cw}" y="156" width="{aw}" height="8" rx="3" fill="{S.P["red"]}"/>')
        rate = int(100 * (complete or 0) / total)
        parts.append(f'<text x="20" y="180" class="t sub">{rate}% success</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[pipeline-pulse] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
