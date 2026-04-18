"""Markdown -> HTML with paper-link rewriting for app pages."""
import markdown
try:
    from .link_rewrite import for_paper_app
except ImportError:
    from link_rewrite import for_paper_app

_EXTENSIONS = ["fenced_code", "tables", "attr_list", "toc"]

def render(md_text: str) -> str:
    """Render markdown body to HTML. Empty input yields empty string."""
    if not md_text:
        return ""
    html = markdown.markdown(md_text, extensions=_EXTENSIONS)
    return for_paper_app(html)
