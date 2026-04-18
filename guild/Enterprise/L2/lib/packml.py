"""Back-compat facade for the old packml module.

Existing scripts do:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
    from packml import Process, path_exists, has_files

That import path adds `lib/` to sys.path, so this file is loaded as the
top-level `packml` module — not as `lib.packml`. Use absolute imports of
sibling files (also loaded via sys.path) to re-export cleanly.
"""
from packml_process import Process
from packml_checks import CheckFailed, path_exists, has_files

__all__ = ["Process", "CheckFailed", "path_exists", "has_files"]
