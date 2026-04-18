"""
build_tag_events — scan every script under guild/Enterprise/L3/scripts
for @tag-event JSON headers and store the declarations in tag.db so the
state-machine runner can query them directly without generated Script
UDT JSON files.

Table (in root tag.db):
  script_events (
    id TEXT PRIMARY KEY,
    script_file TEXT NOT NULL,
    kind TEXT,
    listens_tag TEXT,
    listens_from TEXT,
    listens_to TEXT,
    action_tool_id TEXT,
    reads TEXT,          -- JSON array
    writes TEXT,         -- JSON array
    fires TEXT,          -- JSON array
    enabled INTEGER DEFAULT 1,
    parsed_at TEXT
  )
"""
import json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

LIB  = Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
from tag_event_parser import parse_tree  # noqa: E402

REPO        = Path(__file__).resolve().parents[4]
SCAN_DIRS   = [
    REPO / "guild" / "Enterprise" / "L3" / "scripts",
    REPO / "guild" / "Enterprise" / "L4" / "api" / "scripts",
    REPO / "guild" / "Enterprise" / "L2" / "lib",
]
TAG_DB      = REPO / "tag.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS script_events (
    id              TEXT PRIMARY KEY,
    script_file     TEXT NOT NULL,
    kind            TEXT,
    listens_tag     TEXT,
    listens_from    TEXT,
    listens_to      TEXT,
    action_tool_id  TEXT,
    reads           TEXT,
    writes          TEXT,
    fires           TEXT,
    enabled         INTEGER DEFAULT 1,
    parsed_at       TEXT
);
CREATE INDEX IF NOT EXISTS idx_sev_tag ON script_events(listens_tag);
CREATE INDEX IF NOT EXISTS idx_sev_file ON script_events(script_file);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(decl: dict, script_rel: str) -> dict:
    listens = decl.get("listens") or {}
    if isinstance(listens, list):
        listens = listens[0] if listens else {}
    return {
        "id":             decl.get("id") or f"{Path(script_rel).stem}:anon",
        "script_file":    script_rel,
        "kind":           listens.get("kind") or "on_transition",
        "listens_tag":    listens.get("tag"),
        "listens_from":   listens.get("from"),
        "listens_to":     listens.get("to"),
        "action_tool_id": decl.get("action_tool_id"),   # optional override; defaults to script wrapper
        "reads":          json.dumps(decl.get("reads")  or [], ensure_ascii=False),
        "writes":         json.dumps(decl.get("writes") or [], ensure_ascii=False),
        "fires":          json.dumps(decl.get("fires")  or [], ensure_ascii=False),
        "enabled":        1 if decl.get("enabled", True) else 0,
        "parsed_at":      _now(),
    }


def build() -> dict:
    if not TAG_DB.exists():
        return {"ok": False, "error": f"tag.db not found at {TAG_DB} — run build:tag-dbs first"}

    con = sqlite3.connect(str(TAG_DB))
    con.executescript(SCHEMA)
    con.execute("DELETE FROM script_events")

    scripts_with = 0
    events = 0
    all_hits = []
    for d in SCAN_DIRS:
        if d.exists():
            all_hits.extend(parse_tree(d))
    for path, decl in all_hits:
        rel  = path.relative_to(REPO).as_posix()
        row  = _norm(decl, rel)
        cols = ",".join(row.keys())
        qs   = ",".join(["?"] * len(row))
        try:
            con.execute(f"INSERT OR REPLACE INTO script_events({cols}) VALUES ({qs})", tuple(row.values()))
            events += 1
        except sqlite3.Error:
            continue
    scripts_with = con.execute(
        "SELECT COUNT(DISTINCT script_file) FROM script_events"
    ).fetchone()[0]
    con.commit()
    con.close()
    return {
        "ok":             True,
        "scripts_with":   scripts_with,
        "events_stored":  events,
    }
