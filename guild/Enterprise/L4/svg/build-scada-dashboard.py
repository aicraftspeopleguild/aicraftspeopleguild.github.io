#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-scada-dashboard-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/scada-dashboard.svg"]
# }
# @end-tag-event
"""
Full SCADA dashboard — one SVG, seven live panels, every value read from
the current public endpoints + GitHub Issues. Composed from the atomic
svg_widget primitives (chip · pulse_dot · section_heading · stat_block
· bar · sparkline · tag_card).

Layout (1040 × 900):
  1. Hero bar              window chrome + title + heartbeat timestamp
  2. CATALOG row           4 stat_blocks from /api/health.json
  3. ENTERPRISE row        6 stat_blocks from /runtime/tags.json
  4. PIPELINE panel        complete / aborted / states + sparkline + bar
  5. IDENTITY chips        host · deployMode · apiVersion · latestPaper
  6. TAGS grid             up to 8 live GitHub-Issue tag cards
  7. FAULTS strip          active faults from /api/state.json
"""
import json, sys, sqlite3, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "scada-dashboard.svg"
BASE = "https://teslasolar.github.io/aicraftspeopleguild.github.io"


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception:
        return {}


def _durations():
    f = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"
    if not f.exists(): return []
    try:
        con = sqlite3.connect(str(f))
        rows = con.execute(
            "SELECT duration_s FROM pipeline_runs ORDER BY started_at DESC LIMIT 20"
        ).fetchall()
        con.close()
        return [float(r[0] or 0) for r in reversed(rows)]
    except Exception:
        return []


def render() -> str:
    health   = _get(f"{BASE}/guild/Enterprise/L4/api/health.json")
    tags     = _get(f"{BASE}/guild/Enterprise/L4/runtime/tags.json")
    state    = _get(f"{BASE}/guild/Enterprise/L4/api/state.json")
    hb       = gh_tag.read("demo.heartbeat")
    gh_tags  = gh_tag.list_tags().get("tags", []) or []
    durations = _durations()

    def tv(obj, key, default=0):
        v = obj.get(key, {})
        return v.get("value", default) if isinstance(v, dict) else default

    enterprise = tags.get("enterprise", {}) if isinstance(tags, dict) else {}
    pipeline   = tags.get("pipeline",   {}) if isinstance(tags, dict) else {}
    identity   = tags.get("identity",   {}) if isinstance(tags, dict) else {}
    catalog    = tags.get("catalog",    {}) if isinstance(tags, dict) else {}

    W, H = 1040, 900
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG SCADA dashboard">',
        S.shared_defs(),
        S.window_chrome(W, H, "⚒ ACG · SCADA dashboard · live"),
    ]

    # Heartbeat indicator in the top-right
    parts.append(S.pulse_dot(W - 40, 18, "g", r=5, ring_r=8))
    hb_label = S.pretty_ts(hb.get("value")) if hb.get("ok") else "offline"
    parts.append(f'<text x="{W-52}" y="22" text-anchor="end" class="t" font-size="11" fill="{S.P["blue"]}">💓 {S.esc(hb_label)}</text>')

    y = 56
    # ────── CATALOG row ─────────────────────────────────────────────
    parts.append(S.section_heading(24, y + 14, "CATALOG · /api/health.json", "g"))
    row_y = y + 30
    sw, sh, gap = 244, 96, 12
    cat_rows = [
        ("papers",     health.get("paperCount", "—"), "g"),
        ("members",    health.get("memberCount", "—"), "o"),
        ("api",        f"v{health.get('apiVersion', '—')}", "p"),
        ("lastBuild",  (health.get("lastUpdated") or "—")[-20:-1] if health.get("lastUpdated") else "—", "g"),
    ]
    for i, (lbl, val, color) in enumerate(cat_rows):
        x = 24 + i * (sw + gap)
        parts.append(S.stat_block(x, row_y, sw, sh, lbl, val, "", color))

    # ────── ENTERPRISE row ──────────────────────────────────────────
    y = row_y + sh + 24
    parts.append(S.section_heading(24, y + 14, "ENTERPRISE · runtime/tags.json", "o"))
    row_y = y + 30
    sw, sh, gap = 160, 80, 8
    ent_rows = [
        ("paperCount",    tv(enterprise, "paperCount"),    "g"),
        ("memberCount",   tv(enterprise, "memberCount"),   "o"),
        ("programCount",  tv(enterprise, "programCount"),  "p"),
        ("runCount",      tv(enterprise, "runCount"),      "g"),
        ("tagEdges",      tv(enterprise, "tagEdges"),      "p"),
        ("authoredLinks", tv(enterprise, "authoredLinks"), "o"),
    ]
    for i, (lbl, val, color) in enumerate(ent_rows):
        x = 24 + i * (sw + gap)
        parts.append(S.stat_block(x, row_y, sw, sh, lbl, val, "", color))

    # ────── PIPELINE panel ──────────────────────────────────────────
    y = row_y + sh + 24
    parts.append(S.section_heading(24, y + 14, "PIPELINE · L3 runs", "p"))
    row_y = y + 30
    panel_w, panel_h = W - 48, 120
    bg, _ = S.panel(24, row_y, panel_w, panel_h)
    parts.append(bg)

    complete = tv(pipeline, "complete", 0)
    aborted  = tv(pipeline, "aborted", 0)
    states   = tv(pipeline, "states", 0)
    total    = (complete or 0) + (aborted or 0)
    rate     = int(100 * (complete or 0) / total) if total else 100

    # counters on the left
    parts.append(S.pulse_dot(54, row_y + 32, "r" if aborted else "g", r=7, ring_r=11))
    parts.append(f'<text x="78" y="{row_y + 28}" class="t lb">complete</text>')
    parts.append(f'<text x="78" y="{row_y + 54}" class="t va g">{complete}</text>')
    parts.append(f'<text x="200" y="{row_y + 28}" class="t lb">aborted</text>')
    parts.append(f'<text x="200" y="{row_y + 54}" class="t va {"r" if aborted else "g"}">{aborted}</text>')
    parts.append(f'<text x="300" y="{row_y + 28}" class="t lb">events</text>')
    parts.append(f'<text x="300" y="{row_y + 54}" class="t va">{states}</text>')
    parts.append(f'<text x="400" y="{row_y + 28}" class="t lb">success</text>')
    parts.append(f'<text x="400" y="{row_y + 54}" class="t va g">{rate}%</text>')

    # sparkline on the right
    if durations:
        parts.append(f'<text x="{W - 284}" y="{row_y + 28}" class="t lb">last {len(durations)} runs</text>')
        parts.append(S.sparkline(W - 284, row_y + 36, 240, 32, durations, "g"))

    # full-width success bar at the bottom of the panel
    parts.append(S.bar(40, row_y + panel_h - 22, panel_w - 32, 8, rate / 100, "g" if rate >= 80 else "a"))

    # ────── IDENTITY chips ──────────────────────────────────────────
    y = row_y + panel_h + 20
    parts.append(S.section_heading(24, y + 14, "IDENTITY · deploy", "p"))
    row_y = y + 40
    chips = [
        (f'host {tv(identity, "host", "—")}',            "g"),
        (f'deploy {tv(identity, "deployMode", "—")}',    "o"),
        (f'api v{tv(identity, "apiVersion", "1.0")}',    "p"),
        (f'latest {str(tv(catalog, "latestPaperTitle", "—"))[:32]}', "g"),
    ]
    cx = 24
    for text, color in chips:
        parts.append(S.chip(cx, row_y, text, color))
        cx += max(60, len(text) * 8 + 20) + 10

    # ────── TAGS grid ───────────────────────────────────────────────
    y = row_y + 30
    parts.append(S.section_heading(24, y + 14, f"TAGS · GitHub Issues ({len(gh_tags)})", "g"))
    row_y = y + 30
    cw, ch, gap = 244, 72, 12
    cols = 4
    for i, t in enumerate(gh_tags[:8]):
        r, c = divmod(i, cols)
        x = 24 + c * (cw + gap)
        ty = row_y + r * (ch + gap)
        val = str(t.get("value") or "—")[:20]
        parts.append(S.tag_card(x, ty, cw, ch, t["path"], val,
                                "g" if t.get("quality") == "good" else "a",
                                subtitle=f'#{t.get("issue","?")} · {t.get("comments",0)} edits'))

    # fixed row height regardless of tag count
    row_y += 2 * (ch + gap) + 8

    # ────── FAULTS strip ────────────────────────────────────────────
    parts.append(S.section_heading(24, row_y + 14, "FAULTS · active", "r"))
    strip_y = row_y + 26
    fault_list = (state.get("faults_active") if isinstance(state, dict) else []) or []
    summary = state.get("summary") if isinstance(state, dict) else {}
    active_n = summary.get("faults_active", len(fault_list)) if isinstance(summary, dict) else len(fault_list)
    if fault_list:
        parts.append(S.pulse_dot(48, strip_y + 18, "r", r=7, ring_r=11))
        parts.append(f'<text x="72" y="{strip_y + 22}" class="t va r">{active_n} active fault{"s" if active_n != 1 else ""}</text>')
        cx = 240
        for f in fault_list[:5]:
            msg = f'{f.get("kind","?")} · {(f.get("message") or "")[:40]}'
            parts.append(S.chip(cx, strip_y + 22, msg, "r"))
            cx += max(60, len(msg) * 8 + 20) + 10
    else:
        parts.append(S.pulse_dot(48, strip_y + 18, "g", r=7, ring_r=11))
        parts.append(f'<text x="72" y="{strip_y + 22}" class="t va g">0 active · all quiet</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[scada-dashboard] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
