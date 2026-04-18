#!/usr/bin/env python3
# @tag-event
# {
#   "id": "white-papers-regen:on-papers-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "papers.count",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "white-papers.index.rebuilt_at"
#   ]
# }
# @end-tag-event
"""
Regenerate guild/web/static/white-papers.html from UDT instances.

Each paper-card links to the markdown source (originals/<slug>.md) as
its canonical location until the view renderer takes over.
"""
import json, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
INSTANCES = REPO / "guild" / "Enterprise" / "L4" / "api" / "white-papers" / "udts" / "instances"
OUT = REPO / "guild" / "web" / "dist" / "white-papers.html"

def load_instances():
    papers = []
    for f in sorted(INSTANCES.glob("*.json")):
        with f.open(encoding="utf-8") as fh:
            papers.append(json.load(fh))
    return papers

def render_card(p):
    params = p.get("parameters", {})
    tags = p.get("tags", {})
    title = params.get("title", "Untitled")
    authors = params.get("authors") or []
    author_str = ", ".join(authors) if authors else ""
    date = params.get("publication_date", "")
    doc = params.get("doc_number", "")
    summary = params.get("summary", "")
    slug = tags.get("id", "")
    # Link to markdown source (renderer-ready, works on GitHub with raw display)
    href = f"/guild/Enterprise/L4/api/white-papers/originals/{params.get('slug', slug)}.md" if slug else "#"
    if not params.get("slug") and slug:
        # Fallback: try slug-based filename
        md_path = INSTANCES.parent.parent / "originals" / f"{slug}.md"
        if not md_path.exists():
            # Fall back to original_path tag
            orig = tags.get("original_path", "")
            if orig:
                href = f"/guild/Enterprise/L4/api/white-papers/{orig}"

    meta_parts = []
    if author_str: meta_parts.append(f"<span>{author_str}</span>")
    if date:       meta_parts.append(f"<span>{date}</span>")
    if doc:        meta_parts.append(f"<span>{doc}</span>")
    meta_html = "\n                        ".join(meta_parts)

    return f"""                <article class="paper-card">
                    <div class="paper-meta">
                        {meta_html}
                    </div>
                    <h3>{title}</h3>
                    <p>{summary}</p>
                    <div class="paper-actions">
                        <a href="{href}" class="btn btn-primary">Read Source (Markdown)</a>
                    </div>
                </article>"""

def render_page(papers):
    cards = "\n".join(render_card(p) for p in papers)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>White Papers - AI Craftspeople Guild</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&amp;family=Work+Sans:wght@300;400;600&amp;family=Courier+Prime:wght@400;700&amp;display=swap" rel="stylesheet">

    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-Z1CEF69ZSH"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-Z1CEF69ZSH');
    </script>
    <link rel="stylesheet" href="../style/main.css">
</head>
<body class="page-white-papers">
    <header>
        <div class="guild-mark">
            <div class="emblem">⚒ ACG ⚒</div>
        </div>
        <h1>White Papers</h1>
        <p class="subtitle">A home for the Guild's white papers, position papers, experimental papers, research notes, knowledge-about-knowledge papers, and technical publications on AI-assisted software engineering.</p>
        <div class="back-link">
            <a href="../../../index.html">← Back to Home</a>
        </div>
    </header>

    <main class="container">
        <section class="intro-panel">
            <p>
                This page is regenerated from the UDT instances at <code>guild/Enterprise/L4/api/white-papers/udts/instances/</code>.
                Each paper's canonical source is in <code>guild/Enterprise/L4/api/white-papers/originals/*.md</code>.
                Rendered HTML pages will be produced by the view renderer in a future pass.
            </p>
        </section>

        <section class="papers-shell">
            <div class="section-heading">
                <h2>Available Papers</h2>
                <p>{len(papers)} papers in the Guild catalog.</p>
            </div>

            <div class="papers-grid">
{cards}
            </div>
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
    papers = load_instances()
    html = render_page(papers)
    OUT.write_text(html, encoding="utf-8")
    print(f"[regen] wrote {OUT.relative_to(REPO)} with {len(papers)} papers")

    # Emit split view data: one file for page metadata, one for papers array
    data_dir = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "views" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    page_data = {
        "title": "White Papers",
        "subtitle": "Guild publications.",
        "intro": f"<p>The Guild catalog has {len(papers)} publications. Source of truth: <code>guild/Enterprise/L4/api/white-papers/originals/*.md</code>.</p>",
        "grid_subheading": f"{len(papers)} publications in the Guild catalog."
    }
    (data_dir / "white-papers.data.json").write_text(
        json.dumps(page_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (data_dir / "white-papers-list.data.json").write_text(
        json.dumps(papers, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[regen] wrote view data: white-papers.data.json + white-papers-list.data.json")

if __name__ == "__main__":
    main()
