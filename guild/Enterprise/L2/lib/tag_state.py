"""
tag_state — thin alias module that routes every tag read/write through
state_db. Kept as its own module so the existing Tool UDT entries
(`tag_state.py:read`, `tag_state.py:write`, `tag_state.py:list_prefix`)
continue to resolve unchanged.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import state_db  # noqa: E402


def read(tag: str) -> dict:
    return state_db.tag_read(tag)


def write(tag: str, value=None, quality: str = "good") -> dict:
    return state_db.tag_write(tag, value, quality)


def list_prefix(prefix: str = "") -> dict:
    return state_db.tag_list(prefix)
