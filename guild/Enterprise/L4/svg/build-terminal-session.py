#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-terminal-session-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/terminal-session.svg"]
# }
# @end-tag-event
"""Stylized terminal transcript — shows the live guild@acg terminal
running the canonical onboarding sequence. Reads the current
demo.heartbeat value from the GH-Issues tag DB so the transcript's
`tag:read` response line actually reflects reality."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S
import gh_tag
import site_base

OUT  = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "terminal-session.svg"
BASE = site_base.site_base()


def _script_lines():
    hb = gh_tag.read("demo.heartbeat")
    hb_val = hb.get("value") if hb.get("ok") else "—"
    hb_pretty = S.pretty_ts(hb_val)
    return [
        ("prompt", "guild@acg:~$ ", "acg health"),
        ("out",    "",               '{ "paperCount": 24, "memberCount": 8, "apiVersion": "1.0", "lastUpdated": "live" }'),
        ("prompt", "guild@acg:~$ ", "acg tag:read demo.heartbeat"),
        ("out",    "",               f'tag:demo.heartbeat → {hb_val} · good · {hb_pretty}'),
        ("prompt", "guild@acg:~$ ", "chat hello"),
        ("ok",     "",               "[→ 2 peers]  hello"),
        ("in",     "",               "[mferguson]  hi! catch me in the whiteboard?"),
        ("prompt", "guild@acg:~$ ", "join paper-review"),
        ("sub",    "",               "→ joining room paper-review"),
        ("prompt", "guild@acg:~$ ", "watch demo.heartbeat"),
        ("sub",    "",               "(press ^C to stop)"),
        ("heart",  "",               f"💓  {hb_pretty}"),
        ("prompt", "guild@acg:~$ ", "█"),
    ]


def render() -> str:
    lines = _script_lines()
    W, H = 1040, 40 + len(lines) * 22 + 24

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ACG terminal session · example onboarding flow">',
        S.shared_defs(),
        S.window_chrome(W, 36, "⌨ guild@acg:~  ·  live terminal transcript · click to launch"),
        f'<rect y="36" width="{W}" height="{H-36}" fill="#0b1018"/>',
    ]

    x_prompt = 20
    y = 58
    url = f"{BASE}/guild/apps/terminal/"
    parts.append(f'<a href="{S.esc(url)}" target="_blank">')
    for kind, pre, text in lines:
        if kind == "prompt":
            parts.append(f'<text x="{x_prompt}" y="{y}" class="t" font-size="12" fill="{S.P["green"]}">{S.esc(pre)}</text>')
            parts.append(f'<text x="{x_prompt + 110}" y="{y}" class="t" font-size="12" fill="{S.P["text"]}">{S.esc(text)}</text>')
        elif kind == "out":
            parts.append(f'<text x="{x_prompt + 24}" y="{y}" class="t" font-size="12" fill="{S.P["blue"]}">{S.esc(text)}</text>')
        elif kind == "ok":
            parts.append(f'<text x="{x_prompt + 24}" y="{y}" class="t" font-size="12" fill="{S.P["green"]}">{S.esc(text)}</text>')
        elif kind == "in":
            parts.append(f'<text x="{x_prompt + 24}" y="{y}" class="t" font-size="12" fill="{S.P["orange"]}">{S.esc(text)}</text>')
        elif kind == "sub":
            parts.append(f'<text x="{x_prompt + 24}" y="{y}" class="t" font-size="11" fill="{S.P["dim"]}" font-style="italic">{S.esc(text)}</text>')
        elif kind == "heart":
            parts.append(f'<text x="{x_prompt + 24}" y="{y}" class="t" font-size="13" fill="{S.P["red"]}" font-weight="700">{S.esc(text)}</text>')
        y += 22
    parts.append('</a>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[terminal-session] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
