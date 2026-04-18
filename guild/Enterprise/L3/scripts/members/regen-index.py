#!/usr/bin/env python3
# @tag-event
# {
#   "id": "members-regen:on-members-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "members.count",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "members.index.rebuilt_at"
#   ]
# }
# @end-tag-event
"""
Regenerate guild/web/static/members.html from Member UDT instances.
Each card links to the markdown source (originals/<slug>.md).
"""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
INSTANCES = REPO / "guild" / "Enterprise" / "L4" / "members" / "udts" / "instances"
OUT = REPO / "guild" / "web" / "dist" / "members.html"

def load_instances():
    return [json.loads(f.read_text(encoding="utf-8"))
            for f in sorted(INSTANCES.glob("*.json"))]

def render_card(m):
    p = m["parameters"]
    t = m["tags"]
    slug = t.get("slug") or t.get("id", "")
    name = p.get("name", "Unknown")
    title = p.get("title", "") or p.get("role", "")
    role = p.get("role", "") or ""
    avatar = p.get("avatar_href", "")
    tags = p.get("expertise_tags") or []
    md_href = f"../members/originals/{slug}.md"
    avatar_href = f"../members/{slug}/{avatar}" if avatar else ""

    tag_html = "\n                        ".join(
        f'<span>{t}</span>' for t in tags
    )
    img_html = (
        f'<div class="member-photo">\n                            '
        f'<img src="{avatar_href}" alt="{name} portrait">\n                        </div>'
        if avatar_href else ""
    )

    return f"""                <article class="member-card">
                    <div class="member-meta">
                        <span>{role.title() if role else ""}</span>
                        <span>{title}</span>
                    </div>
                    <h3><a href="{md_href}">{name}</a></h3>
                    <div class="profile-layout">
                        {img_html}
                        <div class="member-body">
                            <div class="member-tags">
                                {tag_html}
                            </div>
                            <div class="member-actions">
                                <a href="{md_href}" class="btn btn-primary">Read Profile (Markdown)</a>
                            </div>
                        </div>
                    </div>
                </article>"""

def render_page(members):
    cards = "\n".join(render_card(m) for m in members)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Members - AI Craftspeople Guild</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&amp;family=Work+Sans:wght@300;400;600&amp;family=Courier+Prime:wght@400;700&amp;display=swap" rel="stylesheet">
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-Z1CEF69ZSH"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-Z1CEF69ZSH');
    </script>
    <link rel="stylesheet" href="../style/main.css">
    <link rel="stylesheet" href="../style/member-profile.css">
</head>
<body class="page-members">
    <header>
        <div class="guild-mark">
            <div class="emblem">⚒ ACG ⚒</div>
        </div>
        <h1>Members</h1>
        <p class="subtitle">The craftspeople of the Guild.</p>
        <div class="back-link">
            <a href="../../../index.html">← Back to Home</a>
        </div>
    </header>

    <main class="container">
        <section class="intro-panel">
            <p>
                This page is regenerated from Member UDT instances at <code>guild/web/members/udts/instances/</code>.
                Each member's canonical source is in <code>guild/web/members/originals/*.md</code>.
            </p>
        </section>

        <section class="members-shell">
            <div class="section-heading">
                <h2>Guild Members</h2>
                <p>{len(members)} members in the Guild directory.</p>
            </div>

{cards}
        </section>
    </main>

    <footer>
        <p>© 2026 AI Craftspeople Guild. Built by practitioners, not evangelists.</p>
        <p><a href="https://github.com/aicraftspeopleguild">GitHub</a></p>
    </footer>
</body>
</html>
"""

def main():
    members = load_instances()
    OUT.write_text(render_page(members), encoding="utf-8")
    print(f"[regen] wrote {OUT.relative_to(REPO)} with {len(members)} members")

if __name__ == "__main__":
    main()
