#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-cmd-panel-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/cmd-panel.svg"]
# }
# @end-tag-event
"""
Clickable README control panel. Each button is an <a href> inside the
SVG pointing at a pre-filled `issues/new` URL on the fork repo. User
clicks → GitHub opens with the title/body/labels pre-populated → user
clicks Submit → .github/workflows/cmd.yml fires and runs the matching
action, auto-closing the issue with a receipt comment.
"""
import sys, urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "cmd-panel.svg"
REPO_SLUG = "teslasolar/aicraftspeopleguild.github.io"


def issue_url(title: str, body: str = "", labels: list = None) -> str:
    q = {"title": title, "labels": ",".join((labels or ["cmd"]))}
    if body:
        q["body"] = body
    return f"https://github.com/{REPO_SLUG}/issues/new?" + urllib.parse.urlencode(q)


BUTTONS = [
    ("🔄", "bump heartbeat",     "Click Submit to fire cmd:bump-heartbeat. The dashboard SVG will refresh with the new timestamp within 60s.",
     "cmd:bump-heartbeat",    "g"),
    ("🔁", "rebuild SVGs",       "Regenerate every SvgOrganism (heartbeat, scada-dashboard, tag-grid, …) without bumping the heartbeat.",
     "cmd:rebuild-svgs",      "p"),
    ("📡", "rebuild API",        "Rerun init-db.py + build-api.py + build-runtime-tags.py + build-state.py.",
     "cmd:rebuild-api",       "o"),
    ("✅", "clear faults",       "Clear every currently active fault in state.db.",
     "cmd:clear-faults",      "g"),
    ("⚒",  "write a tag",        "Update the title to `cmd:tag-write path=<path> value=<value>` before submitting.",
     "cmd:tag-write path=demo.example value=1",  "p"),
    ("🖍", "open whiteboard",    "Jump to the p2p whiteboard — no issue, opens the app directly.",
     "open-whiteboard",       "o"),
]


def render() -> str:
    cols, cw, ch, gap = 3, 320, 84, 14
    rows = (len(BUTTONS) + cols - 1) // cols
    W = cols * cw + (cols + 1) * gap
    H = 36 + rows * (ch + gap) + gap + 28   # extra for footnote

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG cmd panel">',
        S.shared_defs(),
        S.window_chrome(W, 36, "⚒ cmd panel · click a button to file a pre-filled issue"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="url(#gBg)"/>',
    ]

    for i, (emoji, title, body, cmd, color) in enumerate(BUTTONS):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = 56 + r * (ch + gap)
        if cmd == "open-whiteboard":
            url = f"https://teslasolar.github.io/aicraftspeopleguild.github.io/guild/apps/whiteboard/"
        else:
            url = issue_url(cmd, body)
        bg, _ = S.panel(x, y, cw, ch)
        parts.append(
            f'<a href="{S.esc(url)}" target="_blank">' +
            bg +
            S.pulse_dot(x + 28, y + 30, color, r=6, ring_r=9) +
            f'<text x="{x + cw - 18}" y="{y + 32}" text-anchor="end" class="t" font-size="24">{S.esc(emoji)}</text>'
            f'<text x="{x + 48}" y="{y + 34}" class="t vs">{S.esc(title)}</text>'
            f'<text x="{x + 14}" y="{y + 62}" class="t sub">{S.esc(cmd)}</text>'
            f'<text x="{x + 14}" y="{y + ch - 8}" class="t" font-size="10" fill="{S.P["dim"]}">click → opens a pre-filled GitHub issue</text>'
            + '</a>'
        )

    foot_y = H - 10
    parts.append(f'<text x="{W//2}" y="{foot_y}" text-anchor="middle" class="t sub">Submit the issue on GitHub. The cmd workflow runs it, comments the receipt, and closes it automatically.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[cmd-panel] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
