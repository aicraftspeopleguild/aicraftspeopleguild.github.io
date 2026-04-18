"""Slug helpers: make URL-safe identifiers and cap length for Windows MAX_PATH."""
import re

def slugify(text: str, fallback: str = "untitled") -> str:
    """Lowercase, collapse non-alphanumerics to hyphens, strip edges."""
    if not text:
        return fallback
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or fallback

def safe_slug(slug: str, max_len: int = 60) -> str:
    """Truncate overly-long slugs at the last hyphen within max_len.
    Keeps filenames under Windows MAX_PATH (260) when joined with dirs."""
    if len(slug) <= max_len:
        return slug
    truncated = slug[:max_len]
    last_hyphen = truncated.rfind("-")
    if last_hyphen > max_len // 2:
        truncated = truncated[:last_hyphen]
    return truncated
