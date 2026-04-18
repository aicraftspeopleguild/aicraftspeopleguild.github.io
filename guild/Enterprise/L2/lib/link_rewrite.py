"""
Link rewriting rules for rendered bodies.

Two flavors:
  - `for_spa(html)`  — rewrite relative refs to site-absolute for SPA injection
  - `for_paper_app(html)` — rewrite bodies from extracted papers to live at dist/app-*.html
"""
import re

_SPA_RULES = [
    (re.compile(r'((?:href|src)\s*=\s*["\'])\.\./mob_prog_101\.jpg'),
     r'\1/guild/Enterprise/L2/hmi/web/assets/mob_prog_101.jpg'),
    (re.compile(r'((?:href|src)\s*=\s*["\'])\.\./assets/'),
     r'\1/guild/Enterprise/L2/hmi/web/assets/'),
    (re.compile(r'((?:href|src)\s*=\s*["\'])\.\./white-papers/originals/'),
     r'\1/guild/Enterprise/L4/api/white-papers/originals/'),
    (re.compile(r'((?:href|src)\s*=\s*["\'])\.\./members/originals/'),
     r'\1/guild/Enterprise/L4/members/originals/'),
]

_PAPER_IMAGE_RE = re.compile(
    r'((?:href|src)\s*=\s*["\'])(?!https?://|#|/|\.\./|data:|mailto:)'
    r'([\w\-]+\.(?:png|jpe?g|gif|svg|webp|mp4|pdf))(["\'])',
    re.IGNORECASE
)

def for_spa(html: str) -> str:
    for pat, repl in _SPA_RULES:
        html = pat.sub(repl, html)
    return html

def for_paper_app(html: str) -> str:
    """Rewrite a paper body for rendering at guild/web/dist/app-X.html."""
    # Bare image refs -> /guild/Enterprise/L4/api/white-papers/<file>
    html = _PAPER_IMAGE_RE.sub(
        lambda m: m.group(1) + '/guild/Enterprise/L4/api/white-papers/' + m.group(2) + m.group(3), html)
    # Absolute prod URLs -> hash routes
    html = re.sub(
        r'(href\s*=\s*["\'])https?://aicraftspeopleguild\.github\.io/guild/(?:web|Enterprise/L4/api)/white-papers/'
        r'([a-z][\w-]*?)\.html(["\'])',
        r'\1#/whitepapers/\2\3', html)
    # ../white-papers/foo.html -> #/whitepapers/foo
    html = re.sub(
        r'(href\s*=\s*["\'])(?:\.\./)?white-papers/([a-z][\w-]*?)\.html(["\'])',
        r'\1#/whitepapers/\2\3', html)
    # Sibling .html refs from markdown inter-paper links
    html = re.sub(
        r'(href\s*=\s*["\'])(?!https?://|#|/|\.\.?/|mailto:)([a-z][\w-]*?)\.html(["\'])',
        r'\1#/whitepapers/\2\3', html)
    return html
