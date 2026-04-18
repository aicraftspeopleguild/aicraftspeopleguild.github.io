"""udt_query — read UDT instance bodies out of tag.db.udts. Mirrors docs_query."""
import json, sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DB   = REPO / "tag.db"


def _conn() -> sqlite3.Connection:
    if not DB.exists():
        raise FileNotFoundError(f"tag.db not found at {DB}")
    con = sqlite3.connect(str(DB))
    con.row_factory = sqlite3.Row
    return con


def read(id: str = "", udt_type: str = "") -> dict:
    """Return a UDT body by id (+ optional udt_type disambiguator)."""
    if not id:
        return {"ok": False, "error": "id required"}
    con = _conn()
    try:
        q = "SELECT dir, file, udt_type, body FROM udts WHERE id=?"
        params: list = [id]
        if udt_type:
            q += " AND udt_type=?"; params.append(udt_type)
        q += " LIMIT 1"
        row = con.execute(q, params).fetchone()
    finally:
        con.close()
    if not row:
        return {"ok": False, "error": f"not found: id={id}"}
    body_raw = row["body"]
    try:
        body = json.loads(body_raw) if body_raw else None
    except Exception:
        body = body_raw
    return {
        "ok": True, "id": id, "dir": row["dir"], "file": row["file"],
        "udt_type": row["udt_type"], "body": body,
    }


def list_udts(udt_type: str = "", dir_prefix: str = "") -> dict:
    con = _conn()
    try:
        q = "SELECT id, dir, file, udt_type FROM udts"
        cs: list = []
        ps: list = []
        if udt_type:
            cs.append("udt_type=?"); ps.append(udt_type)
        if dir_prefix:
            cs.append("dir LIKE ?"); ps.append(dir_prefix + "%")
        if cs: q += " WHERE " + " AND ".join(cs)
        q += " ORDER BY udt_type, id"
        rows = [dict(r) for r in con.execute(q, ps)]
    finally:
        con.close()
    return {"ok": True, "count": len(rows), "udts": rows}
