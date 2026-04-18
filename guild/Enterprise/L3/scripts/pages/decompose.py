#!/usr/bin/env python3
# @tag-event
# {
#   "id": "decompose:on-html-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "pages.source.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "pages.decomposed_at"
#   ]
# }
# @end-tag-event
"""
Decompose static HTML pages into view.json + data.json.

For each guild/web/static/<slug>.html:
  - Extract header metadata (title, subtitle, eyebrow, meta, back-link)
  - Capture <main> inner HTML as the body content
  - Write guild/Enterprise/L2/hmi/web/views/<slug>.view.json — tree of PageShell + RawHTML
  - Write guild/Enterprise/L2/hmi/web/views/data/<slug>.data.json — {title, subtitle, body}
  - Update guild/Enterprise/L2/hmi/web/pages/<slug>.page.json — switch from static-page to <slug> view

After running, build.js will produce dist/<slug>.html from the view trees,
and static/*.html becomes a build artifact that can be regenerated.
"""
import json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[4]
STATIC_DIR = REPO / "guild" / "web" / "static"
VIEWS_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "views"
DATA_DIR = VIEWS_DIR / "data"
PAGES_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "pages"

def parse(html_path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    data = {
        "title": None,
        "subtitle": None,
        "eyebrow": None,
        "meta": [],
        "backHref": None,
        "backLabel": None,
        "bodyClass": None,
        "body": "",
    }

    # Body class
    body = soup.find("body")
    if body and body.get("class"):
        data["bodyClass"] = " ".join(body.get("class"))

    h1 = soup.find("h1")
    if h1:
        data["title"] = h1.get_text(strip=True)

    sub = soup.select_one("p.subtitle, .subtitle")
    if sub:
        data["subtitle"] = sub.get_text(strip=True)

    eyeb = soup.select_one(".eyebrow")
    if eyeb:
        data["eyebrow"] = eyeb.get_text(strip=True)

    for span in soup.select(".article-meta span"):
        t = span.get_text(strip=True)
        if t:
            data["meta"].append(t)

    back = soup.select_one(".back-link a")
    if back:
        back_href = back.get("href", "")
        data["backHref"] = LINK_REWRITES.get(back_href, back_href)
        txt = back.get_text(strip=True)
        data["backLabel"] = re.sub(r"^←\s*", "", txt)

    # Main body — everything inside <main class="container">
    main = soup.select_one("main.container") or soup.find("main") or body
    if main:
        # Drop the footer + header if they got included
        for sel in ["header", "footer"]:
            for el in main.select(sel):
                el.decompose()
        # Serialize inner HTML of main
        inner = "".join(str(c) for c in main.children)
        # Normalize whitespace
        inner = re.sub(r"\n\s*\n\s*\n+", "\n\n", inner).strip()
        # Rewrite stale internal links to match current dist/ slugs
        inner = rewrite_internal_links(inner)
        data["body"] = inner

    return data

# Map old-style filenames (from when pages were at static/foo.html) to
# the current dist/ output slugs (from Path UDT IDs).
LINK_REWRITES = {
    # SPA hash routes (kept in sync with guild/Enterprise/L2/hmi/web/site-map.json)
    "aicraftspeopleguild-manifesto.html": "#/manifesto",
    "manifesto.html":                     "#/manifesto",
    "chief-ai-skeptic-officer.html":      "#/chief-ai-skeptic",
    "chief-ai-skeptic.html":              "#/chief-ai-skeptic",
    "charter.html":                       "#/charter",
    "code-of-conduct.html":               "#/code-of-conduct",
    "mission-statement.html":             "#/mission",
    "members.html":                       "#/members",
    "../web/dist/members.html":           "#/members",
    "white-papers.html":                  "#/white-papers",
    "../web/dist/white-papers.html":      "#/white-papers",
    "showcases.html":                     "#/showcases",
    "flywheel.html":                      "#/flywheel",
    "guild-radar.html":                   "#/guild-radar",
    "hall-of-fame.html":                  "#/hall-of-fame",
    "hall-of-shame.html":                 "#/hall-of-shame",
    "ai-rituals.html":                    "#/rituals",
    "mob-programming.html":               "#/mob-programming",
    "hushbell.html":                      "#/hushbell",
    "hushbell-full-spec.html":            "#/hushbell/spec",
    # Back-to-home + sign anchor
    "../../../index.html#sign":           "#sign",
    "../../../index.html#manifesto":      "#manifesto-cards",
    "../../../index.html":                "#/",
}

def rewrite_internal_links(html):
    """Rewrite known stale internal links to current dist/ slugs."""
    for old, new in LINK_REWRITES.items():
        # href="old"  ->  href="new"   (also handles src="" via greedy attribute match)
        html = re.sub(
            rf'((?:href|src)\s*=\s*["\']){re.escape(old)}(["\'])',
            lambda m: m.group(1) + new + m.group(2),
            html
        )
    return html

def build_view(slug, meta):
    return {
        "udtType": "View",
        "parameters": {
            "name": slug,
            "description": f"Decomposed view for {slug}",
            "root": {
                "type": "PageShell",
                "props": {
                    "title":    "{{ page.title }}",
                    "subtitle": "{{ page.subtitle }}",
                    "eyebrow":  "{{ page.eyebrow }}",
                    "bodyClass":"{{ page.bodyClass }}",
                    "backHref": "{{ page.backHref }}",
                    "backLabel":"{{ page.backLabel }}"
                },
                "children": [
                    {
                        "type": "RawHTML",
                        "props": { "html": "{{ page.body }}" }
                    }
                ]
            }
        },
        "tags": {
            "id": slug,
            "component_ids": ["page-shell", "raw-html"],
            "data_sources": [f"views/data/{slug}.data.json"],
            "schema_version": "1.0.0"
        }
    }

def build_page(slug, title, section):
    # Reuse the existing page.json if present to keep section/parent
    existing = PAGES_DIR / f"{slug}.page.json"
    existing_data = {}
    if existing.exists():
        try:
            existing_data = json.loads(existing.read_text(encoding="utf-8"))
        except:
            pass
    params = existing_data.get("parameters", {}) if existing_data else {}
    params.update({
        "title": title,
        "slug": slug,
        "route": f"/{slug}",
        "view": f"views/{slug}.view.json",
        "data": {"page": f"views/data/{slug}.data.json"},
        "stylesheets": ["style/main.css"],
        "section": params.get("section", section),
        "parent_slug": params.get("parent_slug", "home"),
        "status": "published"
    })
    # staticSrc no longer needed — view renders directly
    params.pop("staticSrc", None)
    return {
        "udtType": "Page",
        "parameters": params,
        "tags": {
            "id": slug,
            "view_id": slug,
            "schema_version": "1.0.0"
        }
    }

# Heuristic section mapping
SECTIONS = {
    "aicraftspeopleguild-manifesto": "about",
    "charter": "about",
    "code-of-conduct": "about",
    "mission-statement": "about",
    "chief-ai-skeptic-officer": "about",
    "ai-rituals": "resources",
    "mob-programming": "resources",
    "hushbell": "resources",
    "hushbell-full-spec": "resources",
    "flywheel": "community",
    "guild-radar": "community",
    "showcases": "community",
    "hall-of-fame": "recognition",
    "hall-of-shame": "recognition",
    # members.html and white-papers.html are handled separately (regen from UDT)
}

def main():
    VIEWS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    html_files = sorted(STATIC_DIR.glob("*.html"))
    # Exclude members.html + white-papers.html (they're regenerated from UDT instances)
    skip = {"members.html", "white-papers.html"}

    for f in html_files:
        if f.name in skip:
            continue
        slug = f.stem
        data = parse(f)

        # Write data file
        data_file = DATA_DIR / f"{slug}.data.json"
        data_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # Write view
        view_file = VIEWS_DIR / f"{slug}.view.json"
        view_file.write_text(
            json.dumps(build_view(slug, data), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # Write page
        section = SECTIONS.get(slug, "meta")
        page_file = PAGES_DIR / f"{slug}.page.json"
        page_file.write_text(
            json.dumps(build_page(slug, data.get("title") or slug, section), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print(f"  [decompose] {slug}: view + data + page (body={len(data['body']):,} chars)")

    print(f"[decompose] done")

if __name__ == "__main__":
    main()
