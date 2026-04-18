"""HTML -> markdown body extractor for rendered Guild papers/members."""
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as _md

def parse(html_text: str) -> BeautifulSoup:
    return BeautifulSoup(html_text, "html.parser")

def clean_body(soup: BeautifulSoup, selectors_to_drop=None):
    """Strip chrome (header, footer, nav, cta) from the page body."""
    drop = selectors_to_drop or [
        "nav.article-nav", ".back-link", ".cta-section",
        "footer", ".paper-mark", "header", "script", "style",
    ]
    for sel in drop:
        for el in soup.select(sel):
            el.decompose()
    return soup

def to_markdown(article_el) -> str:
    """Convert a BeautifulSoup element tree to markdown, normalizing whitespace."""
    text = _md(str(article_el),
               heading_style="ATX",
               strip=["script", "style"],
               bullets="-")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip() + "\n"
