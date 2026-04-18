"""
query_runner — load Query UDT instances, ingest them into tag.db.queries,
and execute them on demand. If a query declares output_tag, the result is
written through state_db.tag_write so widgets/other tags pick it up.

DB routing:
  db: 'state' -> guild/Enterprise/L2/state/state.db
  db: 'tag'   -> tag.db  (root)
  db: 'acg'   -> guild/Enterprise/L4/database/acg.db
"""
import json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

LIB  = Path(__file__).resolve().parent
REPO = LIB.parents[3]
sys.path.insert(0, str(LIB))
import state_db  # noqa: E402

QUERIES_DIR = REPO / "guild" / "Enterprise" / "L3" / "automation" / "instances" / "queries"
TAG_DB      = REPO / "tag.db"

DB_MAP = {
    "state": REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db",
    "tag":   TAG_DB,
    "acg":   REPO / "guild" / "Enterprise" / "L4" / "database" / "acg.db",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS queries (
    id            TEXT PRIMARY KEY,
    name          TEXT,
    description   TEXT,
    db            TEXT NOT NULL,
    sql           TEXT NOT NULL,
    output_tag    TEXT,
    trigger_json  TEXT,
    enabled       INTEGER DEFAULT 1,
    file_path     TEXT,
    parsed_at     TEXT
);
CREATE INDEX IF NOT EXISTS idx_queries_enabled ON queries(enabled);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_file(f: Path) -> dict | None:
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None
    if doc.get("udtType") != "Query":
        return None
    return doc


def ingest() -> dict:
    """Scan query UDT files + upsert into tag.db.queries."""
    if not TAG_DB.exists():
        return {"ok": False, "error": f"tag.db missing; run build:tag-dbs first"}
    con = sqlite3.connect(str(TAG_DB))
    con.executescript(SCHEMA)
    con.execute("DELETE FROM queries")
    count = 0
    for f in sorted(QUERIES_DIR.glob("*.json")):
        doc = _load_file(f)
        if not doc: continue
        p = doc["parameters"]
        con.execute(
            "INSERT OR REPLACE INTO queries(id,name,description,db,sql,output_tag,trigger_json,enabled,file_path,parsed_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (p["id"], p.get("name"), p.get("description"),
             p["db"], p["sql"], p.get("output_tag"),
             json.dumps(p.get("trigger") or None) if p.get("trigger") else None,
             1 if p.get("enabled", True) else 0,
             str(f.relative_to(REPO).as_posix()), _now()),
        )
        count += 1
    con.commit()
    con.close()
    return {"ok": True, "ingested": count}


def list_queries() -> dict:
    if not TAG_DB.exists(): return {"ok": False, "error": "tag.db missing"}
    con = sqlite3.connect(str(TAG_DB))
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    out = [dict(row) for row in con.execute(
        "SELECT id, name, db, output_tag, enabled FROM queries ORDER BY id"
    )]
    con.close()
    return {"ok": True, "count": len(out), "queries": out}


def run(id: str = "") -> dict:
    """Execute a stored query. Writes result to its output_tag if set."""
    if not id: return {"ok": False, "error": "query id required"}
    if not TAG_DB.exists(): return {"ok": False, "error": "tag.db missing"}
    tcon = sqlite3.connect(str(TAG_DB))
    tcon.row_factory = sqlite3.Row
    row = tcon.execute(
        "SELECT id, db, sql, output_tag FROM queries WHERE id=? AND enabled=1", (id,)
    ).fetchone()
    tcon.close()
    if not row:
        return {"ok": False, "error": f"no enabled query '{id}'"}

    db_file = DB_MAP.get(row["db"])
    if not db_file or not db_file.exists():
        return {"ok": False, "error": f"db not found: {row['db']} -> {db_file}"}

    try:
        con = sqlite3.connect(str(db_file))
        cur = con.execute(row["sql"])
        rows = cur.fetchall()
        cols = [c[0] for c in (cur.description or [])]
        con.close()
    except sqlite3.Error as e:
        return {"ok": False, "error": f"sql error: {e}"}

    # Coerce result: single cell -> scalar; single col -> list; else list of dicts
    if len(rows) == 1 and len(rows[0]) == 1:
        result = rows[0][0]
    elif len(cols) == 1:
        result = [r[0] for r in rows]
    else:
        result = [dict(zip(cols, r)) for r in rows]

    wrote = None
    if row["output_tag"]:
        wrote = state_db.tag_write(row["output_tag"], result)

    return {
        "ok":         True,
        "id":         id,
        "db":         row["db"],
        "row_count":  len(rows),
        "result":     result,
        "output_tag": row["output_tag"],
        "wrote":      wrote,
    }


def run_all() -> dict:
    """Run every enabled query; return combined report."""
    enumerated = list_queries().get("queries") or []
    results = []
    for q in enumerated:
        if not q["enabled"]: continue
        results.append(run(q["id"]))
    return {"ok": all(r.get("ok") for r in results), "ran": len(results), "results": results}
