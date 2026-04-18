"""
api_tick — poll every Api UDT instance, compare to the last snapshot
stored in state.db.api_watches, and on change write output_tag + fire an
on_transition event so any Script can react.

Exposed via Tool UDTs:
  api:tick   (poll + fire matching events)
  api:list   (show watches + last_value)
  api:force  (ignore interval_s cooldown, force-fetch one id)

Uses urllib.request (stdlib only); no third-party deps.
"""
import hashlib, json, sqlite3, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

LIB   = Path(__file__).resolve().parent
REPO  = LIB.parents[3]
sys.path.insert(0, str(LIB))
import state_db
import state_machine

APIS_DIR = REPO / "guild" / "Enterprise" / "L3" / "automation" / "instances" / "apis"
STATE_DB = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS api_watches (
    id            TEXT PRIMARY KEY,
    url           TEXT NOT NULL,
    output_tag    TEXT NOT NULL,
    watch_field   TEXT,
    interval_s    INTEGER DEFAULT 60,
    enabled       INTEGER DEFAULT 1,
    last_value    TEXT,
    last_hash     TEXT,
    last_checked  TEXT,
    last_changed  TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _conn() -> sqlite3.Connection:
    STATE_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(STATE_DB))
    con.executescript(_SCHEMA)
    con.row_factory = sqlite3.Row
    return con


def _load_watches_from_fs() -> list[dict]:
    out = []
    if not APIS_DIR.exists():
        return out
    for f in sorted(APIS_DIR.glob("*.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if doc.get("udtType") != "Api":
            continue
        p = doc["parameters"]
        out.append({
            "id":          p["id"],
            "url":         p["url"],
            "output_tag":  p["output_tag"],
            "watch_field": p.get("watch_field"),
            "interval_s":  int(p.get("interval_s", 60)),
            "enabled":     1 if p.get("enabled", True) else 0,
        })
    return out


def _sync_watches_into_db(con: sqlite3.Connection) -> int:
    watches = _load_watches_from_fs()
    for w in watches:
        con.execute(
            "INSERT INTO api_watches(id,url,output_tag,watch_field,interval_s,enabled) "
            "VALUES (?,?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET url=excluded.url, output_tag=excluded.output_tag, "
            "watch_field=excluded.watch_field, interval_s=excluded.interval_s, enabled=excluded.enabled",
            (w["id"], w["url"], w["output_tag"], w["watch_field"], w["interval_s"], w["enabled"]),
        )
    con.commit()
    return len(watches)


def _dig(obj, dotted: str):
    if not dotted:
        return obj
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def _fetch(url: str, timeout: float = 10.0) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "acg-api-tick/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return body, hashlib.sha256(body).hexdigest()


def _check_one(con: sqlite3.Connection, row: sqlite3.Row, force: bool = False) -> dict:
    now_ts = time.time()
    if not force and row["last_checked"]:
        try:
            last = datetime.fromisoformat(row["last_checked"].replace("Z", "+00:00")).timestamp()
            if (now_ts - last) < int(row["interval_s"] or 60):
                return {"id": row["id"], "skipped": "cooldown"}
        except Exception:
            pass

    try:
        body, h = _fetch(row["url"])
    except Exception as e:
        return {"id": row["id"], "ok": False, "error": str(e)}

    text = body.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = None

    value = _dig(parsed, row["watch_field"]) if (parsed is not None and row["watch_field"]) else parsed
    value_str = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True) if value is not None else ""

    changed = (h != (row["last_hash"] or ""))
    prev_value = row["last_value"]
    con.execute(
        "UPDATE api_watches SET last_hash=?, last_value=?, last_checked=?, last_changed=COALESCE(?, last_changed) WHERE id=?",
        (h, value_str, _now(), _now() if changed else None, row["id"]),
    )
    con.commit()

    if changed:
        state_db.tag_write(row["output_tag"], value)
        state_machine.fire_event(
            tag=row["output_tag"],
            from_state=prev_value or "",
            to_state=value_str,
        )

    return {
        "id":         row["id"],
        "url":        row["url"],
        "output_tag": row["output_tag"],
        "changed":    changed,
        "value":      value,
        "prev_value": prev_value,
    }


def tick() -> dict:
    """Poll every enabled Api watch whose cooldown has elapsed."""
    con = _conn()
    synced = _sync_watches_into_db(con)
    rows = list(con.execute("SELECT * FROM api_watches WHERE enabled=1 ORDER BY id"))
    out  = [_check_one(con, r) for r in rows]
    con.close()
    changed = sum(1 for r in out if r.get("changed"))
    return {"ok": True, "synced": synced, "checked": len(out), "changed": changed, "results": out}


def force(id: str = "") -> dict:
    """Force-fetch a watch, ignoring cooldown."""
    if not id:
        return {"ok": False, "error": "id required"}
    con = _conn()
    _sync_watches_into_db(con)
    row = con.execute("SELECT * FROM api_watches WHERE id=?", (id,)).fetchone()
    if not row:
        con.close()
        return {"ok": False, "error": f"no api watch '{id}'"}
    out = _check_one(con, row, force=True)
    con.close()
    return {"ok": True, **out}


def list_watches() -> dict:
    con = _conn()
    _sync_watches_into_db(con)
    rows = [dict(r) for r in con.execute(
        "SELECT id,url,output_tag,watch_field,interval_s,enabled,last_value,last_checked,last_changed FROM api_watches ORDER BY id"
    )]
    con.close()
    return {"ok": True, "count": len(rows), "watches": rows}
