"""
docs_query — read docs out of the consolidated docs.db.

Lets other tooling (and the user) pull content directly from the DB when
the on-disk source has been archived away.
"""
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DB   = REPO / "docs.db"


def _conn() -> sqlite3.Connection:
    if not DB.exists():
        raise FileNotFoundError(f"docs.db not found at {DB}")
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    return con


def read(path: str = "") -> dict:
    """Return the archived body for a path.
    path accepts either `dir/name` or `dir` + separate `name` via `|`:
        path=docs/engineering/architecture/isa-95/level-2-scada.md
    """
    if not path:
        return {"ok": False, "error": "path required"}
    parts = path.split("/")
    dir_rel = "/".join(parts[:-1])
    name    = parts[-1]
    con = _conn()
    try:
        row = con.execute(
            "SELECT dir, path, ext, size, lines, sha1, h1, word_count, body "
            "FROM docs WHERE dir=? AND path=?", (dir_rel, name)
        ).fetchone()
    finally:
        con.close()
    if not row:
        return {"ok": False, "error": f"not found: {path}"}
    d = dict(row)
    d["ok"] = True
    return d


def list_docs(prefix: str = "", ext: str = "") -> dict:
    """Enumerate docs. Optional: dir prefix (LIKE 'prefix%'), ext filter."""
    con = _conn()
    try:
        q = "SELECT dir, path, ext, size, lines, h1 FROM docs"
        clauses = []
        params: list = []
        if prefix:
            clauses.append("dir LIKE ?")
            params.append(prefix + "%")
        if ext:
            clauses.append("ext = ?")
            params.append(ext)
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY dir, path"
        rows = [dict(r) for r in con.execute(q, params)]
    finally:
        con.close()
    return {"ok": True, "count": len(rows), "docs": rows}


def search(q: str = "", limit: str = "20") -> dict:
    """Full-text-ish search over body (naive LIKE). For real FTS add a virtual table later."""
    if not q:
        return {"ok": False, "error": "q required"}
    try: lim = max(1, int(limit))
    except: lim = 20
    con = _conn()
    try:
        rows = [dict(r) for r in con.execute(
            "SELECT dir, path, h1, substr(body, 1, 200) AS preview "
            "FROM docs WHERE body LIKE ? ORDER BY LENGTH(body) LIMIT ?",
            (f"%{q}%", lim)
        )]
    finally:
        con.close()
    return {"ok": True, "matches": len(rows), "results": rows}
