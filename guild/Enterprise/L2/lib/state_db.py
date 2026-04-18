"""
state_db — the single pass-through for all runtime state.

One SQLite at guild/Enterprise/L2/state/state.db holds:

    tag_values       current Value/Quality/Timestamp per tag
    tag_history      append-only audit of every write
    events           every state-machine event that was dispatched
    tool_runs        every Tool UDT invocation (replaces JSONL-per-tool)
    pipeline_runs    every Pipeline UDT execution
    faults           active + historical fault records (tool fail, pipeline
                     abort, constraint, custom)
    repo_state       per-repo snapshot (branch, commit, packml, dirty, ahead)

Every other lib in L2/lib (tag_state, pipeline_runner, tool_runner,
state_machine) proxies its writes through here so this file is the ONE
source of truth for "what happened + what's wrong right now".
"""
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DB   = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tag_values (
    tag        TEXT PRIMARY KEY,
    value      TEXT,
    quality    TEXT DEFAULT 'good',
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS tag_history (
    tag        TEXT NOT NULL,
    value      TEXT,
    quality    TEXT,
    at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tag_history_tag ON tag_history(tag, at);

CREATE TABLE IF NOT EXISTS events (
    at              TEXT NOT NULL,
    kind            TEXT NOT NULL,
    tag             TEXT,
    from_state      TEXT,
    to_state        TEXT,
    source          TEXT,
    matched_scripts INTEGER DEFAULT 0,
    detail          TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_tag ON events(tag, at);

CREATE TABLE IF NOT EXISTS tool_runs (
    run_id       TEXT PRIMARY KEY,
    tool_id      TEXT NOT NULL,
    inputs       TEXT,
    ok           INTEGER,
    rc           INTEGER,
    started_at   TEXT NOT NULL,
    ended_at     TEXT,
    duration_s   REAL,
    stderr_tail  TEXT
);
CREATE INDEX IF NOT EXISTS idx_tool_runs_tool ON tool_runs(tool_id, started_at);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id        TEXT PRIMARY KEY,
    pipeline_id   TEXT NOT NULL,
    ok            INTEGER,
    steps_total   INTEGER,
    steps_run     INTEGER,
    started_at    TEXT NOT NULL,
    ended_at      TEXT,
    duration_s    REAL,
    detail        TEXT
);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_id ON pipeline_runs(pipeline_id, started_at);

CREATE TABLE IF NOT EXISTS faults (
    fault_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    tag         TEXT,
    kind        TEXT NOT NULL,
    severity    TEXT DEFAULT 'error',
    message     TEXT,
    raised_at   TEXT NOT NULL,
    cleared_at  TEXT,
    ack_at      TEXT,
    ack_by      TEXT,
    active      INTEGER DEFAULT 1,
    detail      TEXT
);
CREATE INDEX IF NOT EXISTS idx_faults_active ON faults(active, raised_at);
CREATE INDEX IF NOT EXISTS idx_faults_tag    ON faults(tag);

CREATE TABLE IF NOT EXISTS repo_state (
    repo        TEXT PRIMARY KEY,
    branch      TEXT,
    commit_sha  TEXT,
    packml      TEXT,
    ahead       INTEGER,
    behind      INTEGER,
    dirty       INTEGER,
    updated_at  TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _conn() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB))
    con.executescript(SCHEMA)
    con.row_factory = sqlite3.Row
    return con


def _s(v):
    if v is None: return None
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, sort_keys=True)


# ── tag_values + tag_history ────────────────────────────────────────────

def tag_read(tag: str) -> dict:
    con = _conn()
    try:
        r = con.execute(
            "SELECT value, quality, updated_at FROM tag_values WHERE tag=?", (tag,)
        ).fetchone()
        if not r:
            return {"ok": True, "tag": tag, "value": None, "quality": "uncertain", "updated_at": None}
        return {"ok": True, "tag": tag, "value": r["value"], "quality": r["quality"], "updated_at": r["updated_at"]}
    finally:
        con.close()


def tag_write(tag: str, value=None, quality: str = "good") -> dict:
    now = _now()
    v   = _s(value)
    con = _conn()
    try:
        prev = con.execute(
            "SELECT value, quality FROM tag_values WHERE tag=?", (tag,)
        ).fetchone()
        con.execute(
            "INSERT INTO tag_values(tag, value, quality, updated_at) VALUES (?,?,?,?) "
            "ON CONFLICT(tag) DO UPDATE SET value=excluded.value, quality=excluded.quality, updated_at=excluded.updated_at",
            (tag, v, quality, now),
        )
        con.execute(
            "INSERT INTO tag_history(tag, value, quality, at) VALUES (?,?,?,?)",
            (tag, v, quality, now),
        )
        con.commit()
        return {
            "ok": True, "tag": tag, "value": v, "quality": quality, "updated_at": now,
            "prev_value": prev["value"] if prev else None,
            "prev_quality": prev["quality"] if prev else None,
            "changed": (prev["value"] if prev else None) != v,
        }
    finally:
        con.close()


def tag_list(prefix: str = "") -> dict:
    con = _conn()
    try:
        q = "SELECT tag, value, quality, updated_at FROM tag_values"
        p: tuple = ()
        if prefix:
            q += " WHERE tag LIKE ?"
            p = (prefix + "%",)
        out = {row["tag"]: {"value": row["value"], "quality": row["quality"], "updated_at": row["updated_at"]}
               for row in con.execute(q, p)}
        return {"ok": True, "count": len(out), "tags": out}
    finally:
        con.close()


# ── events ──────────────────────────────────────────────────────────────

def log_event(kind: str, tag: str = "", from_state: str = "", to_state: str = "",
              source: str = "", matched: int = 0, detail=None) -> None:
    con = _conn()
    try:
        con.execute(
            "INSERT INTO events(at, kind, tag, from_state, to_state, source, matched_scripts, detail) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (_now(), kind, tag, from_state, to_state, source, int(matched), _s(detail)),
        )
        con.commit()
    finally:
        con.close()


# ── tool_runs ───────────────────────────────────────────────────────────

def log_tool_run(run_id: str, tool_id: str, inputs: dict, ok: bool, rc,
                 started_at: str, ended_at: str, duration_s: float,
                 stderr_tail: str = "") -> None:
    con = _conn()
    try:
        con.execute(
            "INSERT OR REPLACE INTO tool_runs(run_id, tool_id, inputs, ok, rc, started_at, ended_at, duration_s, stderr_tail) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (run_id, tool_id, _s(inputs), 1 if ok else 0, rc, started_at, ended_at, float(duration_s), stderr_tail or ""),
        )
        con.commit()
    finally:
        con.close()


# ── pipeline_runs ───────────────────────────────────────────────────────

def log_pipeline_run(run_id: str, pipeline_id: str, ok: bool, steps_total: int,
                     steps_run: int, started_at: str, ended_at: str,
                     duration_s: float, detail=None) -> None:
    con = _conn()
    try:
        con.execute(
            "INSERT OR REPLACE INTO pipeline_runs(run_id, pipeline_id, ok, steps_total, steps_run, started_at, ended_at, duration_s, detail) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (run_id, pipeline_id, 1 if ok else 0, int(steps_total), int(steps_run), started_at, ended_at, float(duration_s), _s(detail)),
        )
        con.commit()
    finally:
        con.close()


# ── faults ──────────────────────────────────────────────────────────────

def raise_fault(kind: str = "custom", message: str = "", tag: str = "",
                severity: str = "error", detail=None) -> dict:
    con = _conn()
    try:
        cur = con.execute(
            "INSERT INTO faults(tag, kind, severity, message, raised_at, active, detail) "
            "VALUES (?,?,?,?,?,1,?)",
            (tag or None, kind, severity, message, _now(), _s(detail)),
        )
        con.commit()
        return {"ok": True, "fault_id": cur.lastrowid, "kind": kind, "severity": severity, "message": message, "tag": tag}
    finally:
        con.close()


def clear_fault(fault_id: str = "", tag: str = "") -> dict:
    con = _conn()
    try:
        if fault_id:
            con.execute(
                "UPDATE faults SET active=0, cleared_at=? WHERE fault_id=? AND active=1",
                (_now(), int(fault_id)),
            )
        elif tag:
            con.execute(
                "UPDATE faults SET active=0, cleared_at=? WHERE tag=? AND active=1",
                (_now(), tag),
            )
        else:
            return {"ok": False, "error": "supply fault_id or tag"}
        con.commit()
        return {"ok": True, "cleared_fault_id": fault_id, "cleared_tag": tag}
    finally:
        con.close()


def ack_fault(fault_id: str, ack_by: str = "") -> dict:
    con = _conn()
    try:
        con.execute(
            "UPDATE faults SET ack_at=?, ack_by=? WHERE fault_id=?",
            (_now(), ack_by or "anon", int(fault_id)),
        )
        con.commit()
        return {"ok": True, "ack_fault_id": fault_id}
    finally:
        con.close()


def list_faults(active_only: str = "1") -> dict:
    con = _conn()
    try:
        q = ("SELECT fault_id, tag, kind, severity, message, raised_at, cleared_at, active, ack_at "
             "FROM faults")
        p: tuple = ()
        if str(active_only) in ("1", "true", "True"):
            q += " WHERE active=1"
        q += " ORDER BY raised_at DESC LIMIT 200"
        out = [dict(row) for row in con.execute(q, p)]
        return {"ok": True, "count": len(out), "faults": out}
    finally:
        con.close()


# ── repo_state ──────────────────────────────────────────────────────────

def set_repo_state(repo: str, **kwargs) -> dict:
    con = _conn()
    try:
        con.execute(
            "INSERT INTO repo_state(repo, branch, commit_sha, packml, ahead, behind, dirty, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(repo) DO UPDATE SET "
            "branch=excluded.branch, commit_sha=excluded.commit_sha, packml=excluded.packml, "
            "ahead=excluded.ahead, behind=excluded.behind, dirty=excluded.dirty, updated_at=excluded.updated_at",
            (repo, kwargs.get("branch"), kwargs.get("commit_sha"), kwargs.get("packml"),
             kwargs.get("ahead"), kwargs.get("behind"),
             1 if kwargs.get("dirty") else 0, _now()),
        )
        con.commit()
        return {"ok": True, "repo": repo}
    finally:
        con.close()


# ── summary ─────────────────────────────────────────────────────────────

def summary() -> dict:
    con = _conn()
    try:
        def one(q, *args): return con.execute(q, args).fetchone()
        row = {
            "ok": True,
            "db":              str(DB.relative_to(REPO).as_posix()),
            "tag_values":      one("SELECT count(*) c FROM tag_values")["c"],
            "tag_history":     one("SELECT count(*) c FROM tag_history")["c"],
            "events":          one("SELECT count(*) c FROM events")["c"],
            "tool_runs":       one("SELECT count(*) c FROM tool_runs")["c"],
            "tool_failures":   one("SELECT count(*) c FROM tool_runs WHERE ok=0")["c"],
            "pipeline_runs":   one("SELECT count(*) c FROM pipeline_runs")["c"],
            "pipeline_failures":one("SELECT count(*) c FROM pipeline_runs WHERE ok=0")["c"],
            "faults_active":   one("SELECT count(*) c FROM faults WHERE active=1")["c"],
            "faults_total":    one("SELECT count(*) c FROM faults")["c"],
            "repo_state":      one("SELECT count(*) c FROM repo_state")["c"],
        }
        # Last event + last pipeline run as sentinels
        le = one("SELECT at, kind, tag, from_state, to_state FROM events ORDER BY at DESC LIMIT 1")
        lp = one("SELECT started_at, pipeline_id, ok FROM pipeline_runs ORDER BY started_at DESC LIMIT 1")
        row["last_event"]        = dict(le) if le else None
        row["last_pipeline_run"] = dict(lp) if lp else None
        return row
    finally:
        con.close()
