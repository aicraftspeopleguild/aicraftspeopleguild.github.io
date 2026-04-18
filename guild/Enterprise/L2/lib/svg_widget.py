"""
svg_widget — reusable SVG primitives for dashboard/tag cards in the
README. Each function returns a snippet that can be composed into a
larger <svg>. Pure string templating, no deps.

Shared palette matches the repo's charter (github dark chrome):
  bg a/b          gradient background
  green/amber/red state colors
  dim/text        foreground
"""
from datetime import datetime, timezone


# ── palette (mirrors terminal.svg / heartbeat.svg) ──────────────────────
P = {
    "bg_a":    "#0d1117",
    "bg_b":    "#161b22",
    "chrome":  "#161b22",
    "border":  "#30363d",
    "text":    "#e6edf3",
    "dim":     "#8b949e",
    "green":   "#3fb950",
    "blue":    "#79c0ff",
    "purple":  "#a371f7",
    "amber":   "#e3b341",
    "red":     "#f85149",
    "orange":  "#f0883e",
}


def esc(s) -> str:
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pretty_ts(value) -> str:
    """Format an epoch-seconds counter as UTC datetime. Falls back to str()."""
    try:
        return datetime.fromtimestamp(int(str(value)), tz=timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    except Exception:
        return str(value) if value is not None else "—"


# ── building blocks ─────────────────────────────────────────────────────

def shared_defs() -> str:
    """Gradient + font + pulse animation. Emit once per SVG."""
    return f"""<defs>
    <linearGradient id="gBg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="{P['bg_a']}"/>
      <stop offset="1" stop-color="{P['bg_b']}"/>
    </linearGradient>
    <style>
      .t{{font-family:'SFMono-Regular',Consolas,monospace}}
      .lb{{fill:{P['dim']};font-size:10px;text-transform:uppercase;letter-spacing:1.6px}}
      .va{{fill:{P['text']};font-size:20px;font-weight:700}}
      .vs{{fill:{P['text']};font-size:14px;font-weight:600}}
      .lo{{fill:{P['blue']};font-size:11px}}
      .sub{{fill:{P['dim']};font-size:11px}}
      .g{{fill:{P['green']}}} .a{{fill:{P['amber']}}} .r{{fill:{P['red']}}}
      .p{{fill:{P['purple']}}} .o{{fill:{P['orange']}}}
      .pulse{{animation:plz 1.8s ease-out infinite}}
      @keyframes plz{{
        0%{{transform:scale(1);opacity:.85}}
        45%{{transform:scale(1.35);opacity:.3}}
        100%{{transform:scale(1.8);opacity:0}}
      }}
      .spin{{animation:sp 4s linear infinite;transform-origin:center}}
      @keyframes sp{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
    </style>
  </defs>"""


def window_chrome(w: int, h: int, title: str = "") -> str:
    """macOS-style window title bar, top 36px of the SVG."""
    return f"""<rect width="{w}" height="{h}" rx="10" fill="url(#gBg)"/>
  <rect x="0" y="0" width="{w}" height="36" rx="10" fill="{P['chrome']}"/>
  <rect x="0" y="26" width="{w}" height="10" fill="{P['chrome']}"/>
  <circle cx="22" cy="18" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="18" r="6" fill="#ffbd2e"/>
  <circle cx="66" cy="18" r="6" fill="#27c93f"/>
  <text x="{w//2}" y="22" text-anchor="middle" class="t" font-size="12" fill="{P['dim']}">{esc(title)}</text>"""


def pulse_dot(cx: int, cy: int, color_class: str = "g", r: int = 8,
              ring_r: int = 12) -> str:
    """Dot with two animated pulse rings. color_class: g | a | r | p | o."""
    stroke = {"g": P['green'], "a": P['amber'], "r": P['red'],
              "p": P['purple'], "o": P['orange']}.get(color_class, P['green'])
    return f"""<g style="transform-origin:{cx}px {cy}px">
    <circle cx="{cx}" cy="{cy}" r="{ring_r}" fill="none" stroke="{stroke}" stroke-width="2" opacity=".5" class="pulse"/>
    <circle cx="{cx}" cy="{cy}" r="{ring_r}" fill="none" stroke="{stroke}" stroke-width="2" opacity=".5" class="pulse" style="animation-delay:.6s"/>
  </g>
  <circle cx="{cx}" cy="{cy}" r="{r}" class="{color_class}"/>"""


def panel(x: int, y: int, w: int, h: int) -> tuple:
    """Rounded panel background. Returns (open_tag, close_tag) to wrap child content."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{P["bg_b"]}" stroke="{P["border"]}" stroke-width="1"/>',
        ''  # no close needed since <rect/> is self-closing
    )


def kv(x: int, y: int, label: str, value, value_class: str = "va") -> str:
    """Stacked label / value block at (x, y). y is the baseline of the VALUE text."""
    return (
        f'<text x="{x}" y="{y-18}" class="t lb">{esc(label)}</text>'
        f'<text x="{x}" y="{y}" class="t {value_class}">{esc(value)}</text>'
    )


def tag_card(x: int, y: int, w: int, h: int, label: str, value,
             color_class: str = "g", subtitle: str = "") -> str:
    """Self-contained tag card panel with pulse dot."""
    bg, _ = panel(x, y, w, h)
    return (
        bg +
        pulse_dot(x + 22, y + 24, color_class, r=6, ring_r=9) +
        f'<text x="{x + 40}" y="{y + 28}" class="t lb">{esc(label)}</text>'
        f'<text x="{x + 14}" y="{y + 60}" class="t va">{esc(value)}</text>' +
        (f'<text x="{x + 14}" y="{y + h - 10}" class="t sub">{esc(subtitle)}</text>' if subtitle else '')
    )


def sparkline(x: int, y: int, w: int, h: int, values: list,
              color_class: str = "g") -> str:
    """Min-max-normalized polyline across the given values list."""
    stroke = {"g": P['green'], "a": P['amber'], "r": P['red'],
              "p": P['purple'], "o": P['orange']}.get(color_class, P['green'])
    if not values:
        return f'<text x="{x}" y="{y+h//2}" class="t sub">no data</text>'
    nums = [float(v or 0) for v in values]
    lo, hi = min(nums), max(nums)
    span = (hi - lo) or 1
    pts = []
    n = len(nums)
    for i, v in enumerate(nums):
        px = x + (i / (n - 1 if n > 1 else 1)) * w
        py = y + h - ((v - lo) / span) * h
        pts.append(f"{px:.1f},{py:.1f}")
    poly = " ".join(pts)
    return (
        f'<polyline fill="none" stroke="{stroke}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" points="{poly}"/>'
    )


# ── atomic additions ────────────────────────────────────────────────────

def chip(x: int, y: int, text: str, color_class: str = "g",
         min_w: int = 60, pad: int = 10) -> str:
    fg = {"g": P['green'], "a": P['amber'], "r": P['red'],
          "p": P['purple'], "o": P['orange']}.get(color_class, P['text'])
    w = max(min_w, len(text) * 8 + pad * 2)
    return (
        f'<g><rect x="{x}" y="{y-16}" rx="11" width="{w}" height="22" '
        f'fill="none" stroke="{fg}" stroke-width="1" opacity=".6"/>'
        f'<text x="{x + w//2}" y="{y-1}" text-anchor="middle" class="t" '
        f'font-size="11" fill="{fg}">{esc(text)}</text></g>'
    )


def bar(x: int, y: int, w: int, h: int, pct: float,
        color_class: str = "g") -> str:
    fill_w = max(0, min(w, int(w * pct)))
    fg = {"g": P['green'], "a": P['amber'], "r": P['red'],
          "p": P['purple'], "o": P['orange']}.get(color_class, P['green'])
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h//2}" '
        f'fill="{P["bg_a"]}" stroke="{P["border"]}" stroke-width="1"/>'
        f'<rect x="{x}" y="{y}" width="{fill_w}" height="{h}" rx="{h//2}" fill="{fg}"/>'
    )


def divider(x: int, y: int, w: int) -> str:
    return f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y}" stroke="{P["border"]}" stroke-width="1"/>'


def section_heading(x: int, y: int, text: str, color_class: str = "g") -> str:
    fg = {"g": P['green'], "a": P['amber'], "r": P['red'],
          "p": P['purple'], "o": P['orange']}.get(color_class, P['green'])
    return (
        f'<text x="{x}" y="{y}" class="t lb" fill="{fg}">{esc(text)}</text>'
        f'<line x1="{x}" y1="{y+6}" x2="{x+80}" y2="{y+6}" stroke="{fg}" stroke-width="2"/>'
    )


def emoji_badge(x: int, y: int, emoji: str, label: str,
                color_class: str = "g") -> str:
    fg = {"g": P['green'], "a": P['amber'], "r": P['red'],
          "p": P['purple'], "o": P['orange']}.get(color_class, P['text'])
    return (
        f'<text x="{x}" y="{y}" class="t" font-size="20">{esc(emoji)}</text>'
        f'<text x="{x+28}" y="{y}" class="t va" fill="{fg}">{esc(label)}</text>'
    )


# ── molecule additions ─────────────────────────────────────────────────

def stat_block(x: int, y: int, w: int, h: int,
               label: str, value, sub: str = "",
               color_class: str = "g") -> str:
    """Card: section heading + big value + optional subtitle."""
    bg, _ = panel(x, y, w, h)
    return (
        bg +
        section_heading(x + 14, y + 22, label, color_class) +
        f'<text x="{x + 14}" y="{y + 54}" class="t va">{esc(value)}</text>' +
        (f'<text x="{x + 14}" y="{y + h - 10}" class="t sub">{esc(sub)}</text>' if sub else '')
    )


def link_card(x: int, y: int, w: int, h: int,
              title: str, url: str, emoji: str = "→") -> str:
    """Clickable nav card with emoji + title + url preview."""
    bg, _ = panel(x, y, w, h)
    u = url.replace("https://", "").replace("http://", "")
    return (
        f'<a href="{esc(url)}" target="_blank">' +
        bg +
        f'<text x="{x + 14}" y="{y + h//2 + 4}" class="t" font-size="18">{esc(emoji)}</text>'
        f'<text x="{x + 44}" y="{y + h//2 - 3}" class="t vs">{esc(title)}</text>'
        f'<text x="{x + 44}" y="{y + h//2 + 13}" class="t sub">{esc(u[:44])}</text>'
        + '</a>'
    )


def row_kv(x: int, y: int, w: int,
           label: str, value, value_class: str = "vs") -> str:
    return (
        f'<text x="{x}" y="{y}" class="t sub">{esc(label)}</text>'
        f'<text x="{x + w}" y="{y}" text-anchor="end" class="t {value_class}">{esc(value)}</text>'
    )
