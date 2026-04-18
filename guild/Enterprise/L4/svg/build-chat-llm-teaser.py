#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-chat-llm-teaser-svg:on-heartbeat",
#   "listens": {"kind":"on_transition","tag":"demo.heartbeat","from":"*","to":"CHANGED"},
#   "writes": ["guild/Enterprise/L2/hmi/web/assets/svg/chat-llm-teaser.svg"]
# }
# @end-tag-event
"""Headline teaser card for the WebLLM sandbox. Click → launches MLC
web-llm engine in the browser (WebGPU, model cached in IndexedDB after
first load). Design mirrors the hero card's gradient chrome."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import svg_widget as S

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "chat-llm-teaser.svg"
URL = "https://teslasolar.github.io/aicraftspeopleguild.github.io/guild/Enterprise/L4/sandbox/web-llm/"


def render() -> str:
    W, H = 1040, 260
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="chat with the guild · WebLLM">',
        S.shared_defs(),
        f'<a href="{S.esc(URL)}" target="_blank">',
        S.window_chrome(W, H, "⚒ chat with the guild · WebLLM · click to launch"),
    ]

    # Purple pulse bank
    for i, cx in enumerate((60, 100, 140)):
        parts.append(f'<g style="transform-origin:{cx}px 120px">'
                     f'<circle cx="{cx}" cy="120" r="14" fill="none" stroke="{S.P["purple"]}" stroke-width="2" opacity=".5" class="pulse" style="animation-delay:{i*.3}s"/>'
                     f'</g>')
    parts.append(f'<circle cx="100" cy="120" r="11" fill="{S.P["purple"]}"/>')
    parts.append(f'<text x="100" y="125" text-anchor="middle" class="t" font-size="13" fill="#fff">🧠</text>')

    parts.append(f'<text x="190" y="102" class="t" font-size="30" font-weight="700" fill="{S.P["text"]}">Chat with the guild</text>')
    parts.append(f'<text x="190" y="132" class="t" font-size="14" fill="{S.P["dim"]}">WebLLM engine · Phi-3 / Llama-3.2 · WebGPU · no server · no account · peer-shared via the mesh</text>')

    # Feature chips
    chips_y = 182
    chips = [
        ("🖥 runs in your browser",        "p"),
        ("💾 cached after 1st load",       "g"),
        ("🛰 shares context via p2p mesh", "o"),
        ("🔧 calls the acg tool catalog",  "g"),
    ]
    cx = 40
    for text, color in chips:
        parts.append(S.chip(cx, chips_y, text, color))
        cx += max(60, len(text) * 8 + 20) + 10

    # right-side launch affordance
    parts.append(f'<text x="{W-30}" y="108" text-anchor="end" class="t" font-size="13" fill="{S.P["blue"]}">launch ↗</text>')
    parts.append(f'<text x="{W-30}" y="130" text-anchor="end" class="t sub">{S.esc(URL.replace("https://",""))[:58]}</text>')

    # Footer hint
    parts.append(f'<text x="{W//2}" y="{H-14}" text-anchor="middle" class="t sub">First load downloads the model (~1-2 GB) into IndexedDB. Subsequent chats are instant.</text>')

    parts.append('</a>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"[chat-llm-teaser] wrote {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
