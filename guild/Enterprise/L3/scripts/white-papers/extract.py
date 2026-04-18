#!/usr/bin/env python3
# @tag-event
# {
#   "id": "white-papers-extract:on-originals-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "white-papers.originals.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "white-papers.extracted.at",
#     "papers.count"
#   ]
# }
# @end-tag-event
"""
Extract rendered HTML white papers into markdown originals.

For each guild/Enterprise/L4/api/white-papers/*.html, parse title/authors/date/body and
emit guild/Enterprise/L4/api/white-papers/originals/<slug>.md with YAML front-matter.

Preserves: headings, paragraphs, lists, figures, callouts, code blocks,
blockquotes, tables. Strips: nav, header chrome, footer, CTA sections.
"""
import re, os, sys
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md

REPO = Path(__file__).resolve().parents[4]
HTML_DIR = REPO / "guild" / "Enterprise" / "L4" / "api" / "white-papers"
OUT_DIR = HTML_DIR / "originals"

# Known type labels → status mapping
TYPE_TO_STATUS = {
    "position paper": "position",
    "white paper": "published",
    "experimental paper": "experimental",
    "research note": "research-note",
    "knowledge about knowledge": "knowledge-about-knowledge",
    "knowledge-about-knowledge": "knowledge-about-knowledge",
}

def extract_metadata(soup):
    """Pull title, subtitle, eyebrow, meta badges from the page header."""
    data = {
        "title": None,
        "subtitle": None,
        "eyebrow": None,
        "meta": [],
    }

    h1 = soup.find("h1")
    if h1:
        data["title"] = h1.get_text(strip=True)

    subtitle_el = soup.select_one("p.subtitle, .subtitle")
    if subtitle_el:
        data["subtitle"] = subtitle_el.get_text(strip=True)

    eyebrow_el = soup.select_one(".eyebrow")
    if eyebrow_el:
        data["eyebrow"] = eyebrow_el.get_text(strip=True)

    for span in soup.select(".article-meta span"):
        txt = span.get_text(strip=True)
        if txt:
            data["meta"].append(txt)

    return data

def parse_meta_list(meta_list):
    """Meta spans typically contain type, author, date, doc-number in varying order."""
    result = {
        "authors": [],
        "publication_date": None,
        "doc_number": None,
        "source_medium": None,
        "type": None,
    }
    # Heuristics:
    #   "Position Paper" → type
    #   "ACG-WP-001-2026" → doc_number
    #   month name present → publication_date
    #   "Medium, ..." or similar → source_medium
    for m in meta_list:
        low = m.lower()
        if re.match(r"^acg-[a-z-]*\d{3,}-\d{4}$", low, re.IGNORECASE):
            result["doc_number"] = m
        elif re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d", low) or re.match(r"^\d{4}", low):
            result["publication_date"] = m
        elif any(t in low for t in TYPE_TO_STATUS):
            result["type"] = m
        elif "medium" in low or "arxiv" in low or "ssrn" in low:
            result["source_medium"] = m
        elif re.match(r"^[A-Z][a-zA-Z.\s'\-]+$", m) and len(m.split()) <= 6:
            # Looks like an author name
            result["authors"].append(m)
    return result

def extract_body(soup):
    """Isolate the article body — drop header, nav, footer, CTA sections."""
    # Find the article-shell (the paper body container)
    article = soup.select_one("article.article-shell, main.container, main")
    if not article:
        article = soup.body

    # Remove navigation and CTA noise
    for sel in [
        "nav.article-nav",
        ".back-link",
        ".cta-section",
        "footer",
        ".paper-mark",
        "header",
        "script",
        "style",
    ]:
        for el in article.select(sel):
            el.decompose()

    return article

def html_to_md(article):
    """Convert the body element to markdown. Preserve figure alt text and links."""
    raw = str(article)
    text = md(
        raw,
        heading_style="ATX",
        strip=["script", "style"],
        bullets="-",
    )
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace on each line's right side
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip() + "\n"

def yaml_str(v):
    """Serialize a value for YAML front-matter, quoting when needed."""
    if v is None:
        return '""'
    s = str(v)
    if re.search(r"[:'\"\n]", s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s

def to_frontmatter(d):
    lines = ["---"]
    for k, v in d.items():
        if v is None or (isinstance(v, list) and not v):
            continue
        if isinstance(v, list):
            if all(isinstance(x, str) for x in v):
                lines.append(f"{k}: [{', '.join(yaml_str(x) for x in v)}]")
            else:
                lines.append(f"{k}:")
                for x in v:
                    lines.append(f"  - {yaml_str(x)}")
        else:
            lines.append(f"{k}: {yaml_str(v)}")
    lines.append("---\n")
    return "\n".join(lines)

def slug_from_filename(fname):
    return fname.replace(".html", "")

def process_file(html_path):
    slug = slug_from_filename(html_path.name)
    try:
        html_text = html_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [error] read {html_path.name}: {e}")
        return False

    soup = BeautifulSoup(html_text, "html.parser")

    header_data = extract_metadata(soup)
    meta_data = parse_meta_list(header_data["meta"])
    article = extract_body(soup)
    body_md = html_to_md(article)

    # Determine status from type
    status = "published"
    if meta_data["type"]:
        for key, val in TYPE_TO_STATUS.items():
            if key in meta_data["type"].lower():
                status = val
                break

    # Summary from subtitle
    summary = header_data.get("subtitle") or ""

    frontmatter_dict = {
        "title": header_data["title"] or slug.replace("-", " ").title(),
        "slug": slug,
        "authors": meta_data["authors"] if meta_data["authors"] else [],
        "publication_date": meta_data["publication_date"],
        "doc_number": meta_data["doc_number"],
        "source_medium": meta_data["source_medium"],
        "summary": summary,
        "tags": [],
        "status": status,
        "site_href": f"{slug}.html",
    }

    content = to_frontmatter(frontmatter_dict) + "\n" + body_md

    out_path = OUT_DIR / f"{slug}.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"  [write] originals/{slug}.md  ({len(body_md):,} chars body)")
    return True

def main():
    if not HTML_DIR.exists():
        print(f"[error] not found: {HTML_DIR}")
        sys.exit(1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    html_files = sorted(HTML_DIR.glob("*.html"))
    print(f"[extract] {len(html_files)} papers found")
    ok = 0
    for f in html_files:
        # Skip if ai-harness.md already exists (hand-authored original)
        if f.stem == "ai-harness":
            print(f"  [skip] {f.name} — originals/ai-harness.md is hand-authored")
            continue
        if process_file(f):
            ok += 1
    print(f"[extract] wrote {ok}/{len(html_files)} markdown files")

if __name__ == "__main__":
    main()
