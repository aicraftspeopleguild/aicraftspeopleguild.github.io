"""Pre-built guards for PackML Process checks."""
from pathlib import Path

class CheckFailed(Exception):
    """Raised by a check callable to signal failure; message is the reason."""

def path_exists(path):
    """Return a check that asserts the given path exists on disk."""
    p = Path(path)
    def _check():
        if not p.exists():
            raise CheckFailed(f"missing: {path}")
        return True
    _check.__name__ = f"path_exists({p.name})"
    return _check

def has_files(pattern, min_count: int = 1):
    """Return a check that asserts glob(pattern) produces >= min_count files."""
    pat = Path(pattern)
    def _check():
        found = list(pat.parent.glob(pat.name)) if pat.parent.exists() else []
        if len(found) < min_count:
            raise CheckFailed(
                f"{pattern}: found {len(found)}, need >= {min_count}")
        return True
    _check.__name__ = f"has_files({pattern})"
    return _check
