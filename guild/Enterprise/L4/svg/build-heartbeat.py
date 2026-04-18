#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-heartbeat-svg:on-heartbeat",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "demo.heartbeat",
#     "from": "*",
#     "to":   "CHANGED"
#   },
#   "writes": ["guild/Enterprise/L4/svg/heartbeat.svg"]
# }
# @end-tag-event
"""
Read the live demo.heartbeat tag from GitHub Issues and regenerate
guild/Enterprise/L4/svg/heartbeat.svg — a small animated card. README
embeds it via the raw.githubusercontent URL so GitHub's proxied image
cache shows the latest on every push.
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
import gh_tag

OUT = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "assets" / "svg" / "heartbeat.svg"


def render(value, updated_at: str, description: str) -> str:
    pretty_when = updated_at or "—"
    # Try to format the epoch-seconds value as a UTC datetime
    try:
        ts = int(str(value))
        pretty_value = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    except Exception:
        pretty_value = str(value if value is not None else "—")

    # Escape < > & in dynamic strings
    def e(s):
        return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 140" width="720" height="140" role="img" aria-label="ACG heartbeat · {e(pretty_value)}">
  <defs>
    <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0d1117"/>
      <stop offset="1" stop-color="#161b22"/>
    </linearGradient>
    <style>
      .t{{font-family:'SFMono-Regular',Consolas,monospace}}
      .em{{fill:#3fb950;font-size:28px;font-weight:700}}
      .lb{{fill:#8b949e;font-size:11px;text-transform:uppercase;letter-spacing:2px}}
      .va{{fill:#e6edf3;font-size:22px;font-weight:700}}
      .lo{{fill:#79c0ff;font-size:12px}}
      .pulse{{animation:p 1.6s ease-out infinite;transform-origin:60px 70px}}
      @keyframes p{{
        0%{{transform:scale(1);opacity:.9}}
        40%{{transform:scale(1.35);opacity:.3}}
        100%{{transform:scale(1.8);opacity:0}}
      }}
      .ring{{fill:none;stroke:#3fb950;stroke-width:2;opacity:.5}}
      .dot{{fill:#3fb950}}
    </style>
  </defs>
  <rect width="720" height="140" rx="10" fill="url(#g)"/>
  <rect x="0" y="0" width="720" height="36" rx="10" fill="#161b22"/>
  <rect x="0" y="26" width="720" height="10" fill="#161b22"/>
  <circle cx="22" cy="18" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="18" r="6" fill="#ffbd2e"/>
  <circle cx="66" cy="18" r="6" fill="#27c93f"/>
  <text x="360" y="22" text-anchor="middle" class="t" font-size="12" fill="#8b949e">&#x2692;  ACG heartbeat  &#xb7;  regenerated on every push</text>

  <!-- pulse ring -->
  <g>
    <circle class="ring pulse" cx="60" cy="70" r="14"/>
    <circle class="ring pulse" style="animation-delay:.5s" cx="60" cy="70" r="14"/>
    <circle class="dot" cx="60" cy="70" r="10"/>
  </g>

  <text x="100" y="68" class="t em">💓</text>
  <text x="146" y="68" class="t va">{e(pretty_value)}</text>

  <text x="100" y="92" class="t lb">demo.heartbeat</text>
  <text x="100" y="108" class="t lo">updated {e(pretty_when)}</text>

  <text x="700" y="108" text-anchor="end" class="t lo">{e((description or '')[:60])}</text>
</svg>
"""


def main() -> None:
    result = gh_tag.read("demo.heartbeat")
    if not result.get("ok"):
        print(f"[heartbeat-svg] read failed: {result.get('error')}", file=sys.stderr)
        # still emit a fallback so the SVG exists
        svg = render("—", "", "heartbeat not available")
    else:
        svg = render(result.get("value"), result.get("updated_at") or "", result.get("description") or "")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"[heartbeat-svg] wrote {OUT.relative_to(REPO)}  value={result.get('value') if result.get('ok') else 'N/A'}")


if __name__ == "__main__":
    main()
