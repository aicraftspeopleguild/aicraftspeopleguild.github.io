#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-commit-activity-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/commit-activity.svg"]
# }
# @end-tag-event
"""Commit sparkline + last N commits from the GitHub API.
Uses /repos/.../stats/participation for weekly counts; falls back to
/commits if the stats endpoint hasn't been warmed yet."""
import json, os, sys, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "commit-activity.svg"
REPO_SLUG = os.environ.get("GH_TAG_REPO", "teslasolar/aicraftspeopleguild.github.io")


def _api(path):
    try:
        req = urllib.request.Request(f"https://api.github.com{path}",
                                     headers={"Accept":"application/vnd.github+json",
                                              "User-Agent":"acg-svg/1.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return None


def render() -> str:
    stats = _api(f"/repos/{REPO_SLUG}/stats/participation") or {}
    weekly = stats.get("all", [])[-12:] if isinstance(stats, dict) else []
    commits = _api(f"/repos/{REPO_SLUG}/commits?per_page=8") or []

    W, H = 1040, 240
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="commit activity">',
        S.shared_defs(),
        S.window_chrome(W, H, f"⚒ commit activity · github.com/{REPO_SLUG}"),
    ]

    # Left: big weekly sparkline
    if weekly:
        total = sum(weekly)
        parts.append(f'<text x="24" y="70" class="t lb g">last {len(weekly)} weeks</text>')
        parts.append(f'<text x="24" y="96" class="t va">{total}</text>')
        parts.append(f'<text x="24" y="114" class="t sub">commits</text>')
        parts.append(S.sparkline(24, 128, 400, 60, weekly, "g"))
    else:
        parts.append(f'<text x="24" y="90" class="t sub">stats/participation not yet warm — hit the URL once on GitHub to seed it</text>')

    # Right: last 8 commits
    parts.append(S.divider(440, 56, 1))  # vertical-ish separator (drawn as line)
    parts.append(f'<line x1="460" y1="56" x2="460" y2="{H-24}" stroke="{S.P["border"]}"/>')
    parts.append(f'<text x="480" y="70" class="t lb p">last {len(commits)} commits</text>')
    if isinstance(commits, list):
        for i, c in enumerate(commits[:8]):
            y = 96 + i * 18
            sha = (c.get("sha") or "")[:7]
            msg = (((c.get("commit") or {}).get("message") or "").split("\n")[0])[:68]
            date = (((c.get("commit") or {}).get("author") or {}).get("date") or "")[:10]
            parts.append(f'<text x="480" y="{y}" class="t" font-size="11" fill="{S.P["blue"]}">{S.esc(sha)}</text>')
            parts.append(f'<text x="540" y="{y}" class="t sub">{S.esc(date)}</text>')
            parts.append(f'<text x="620" y="{y}" class="t" font-size="11" fill="{S.P["text"]}">{S.esc(msg)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[commit-activity] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
