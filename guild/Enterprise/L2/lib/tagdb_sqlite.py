"""
tagdb_sqlite — write the in-memory tag.db dicts (produced by gen-tag-db.py)
into SQLite files. Replaces the earlier JSON-in-.db representation.

Two entry points:
  write_local(db_path, d)   — per-directory tag.db (scope='local')
  write_global(db_path, d)  — root tag.db (scope='global', carries graphs)

Schema is identical for both, with extra tables only populated when
scope='global' (tag_dirs, tag_samples, graphs).
"""
import json, sqlite3
from pathlib import Path


LOCAL_SCHEMA = """
DROP TABLE IF EXISTS manifest;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS udt_types;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS kinds;
DROP TABLE IF EXISTS refs;
DROP TABLE IF EXISTS ids;
DROP TABLE IF EXISTS udts;

CREATE TABLE manifest (
    key   TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE tags (
    name  TEXT NOT NULL,
    file  TEXT NOT NULL,
    dir   TEXT,
    PRIMARY KEY (name, file, dir)
);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_dir  ON tags(dir);
CREATE TABLE udt_types (
    name  TEXT NOT NULL,
    dir   TEXT,
    count INTEGER NOT NULL,
    PRIMARY KEY (name, dir)
);
CREATE INDEX idx_udt_types_dir ON udt_types(dir);
CREATE TABLE sections (
    name  TEXT NOT NULL,
    dir   TEXT,
    count INTEGER NOT NULL,
    PRIMARY KEY (name, dir)
);
CREATE TABLE kinds (
    ext   TEXT NOT NULL,
    dir   TEXT,
    count INTEGER NOT NULL,
    PRIMARY KEY (ext, dir)
);
CREATE TABLE refs (
    bucket TEXT NOT NULL,
    name   TEXT NOT NULL,
    dir    TEXT,
    count  INTEGER NOT NULL,
    PRIMARY KEY (bucket, name, dir)
);
CREATE INDEX idx_refs_bucket ON refs(bucket);
CREATE TABLE ids (
    id    TEXT NOT NULL,
    dir   TEXT,
    count INTEGER NOT NULL,
    PRIMARY KEY (id, dir)
);
CREATE TABLE udts (
    id       TEXT NOT NULL,
    dir      TEXT,
    file     TEXT,
    udt_type TEXT,
    body     TEXT,
    PRIMARY KEY (id, dir)
);
CREATE INDEX idx_udts_type ON udts(udt_type);
CREATE INDEX idx_udts_dir  ON udts(dir);
"""

GLOBAL_EXTRA = """
DROP TABLE IF EXISTS tag_dirs;
DROP TABLE IF EXISTS tag_samples;
DROP TABLE IF EXISTS graph_url_nodes;
DROP TABLE IF EXISTS graph_url_edges;
DROP TABLE IF EXISTS graph_fs_nodes;
DROP TABLE IF EXISTS graph_fs_edges;
DROP TABLE IF EXISTS graph_indexes;

CREATE TABLE tag_dirs (
    tag_name TEXT NOT NULL,
    dir      TEXT NOT NULL,
    PRIMARY KEY (tag_name, dir)
);
CREATE INDEX idx_tag_dirs_tag ON tag_dirs(tag_name);
CREATE TABLE tag_samples (
    tag_name TEXT NOT NULL,
    file     TEXT NOT NULL,
    PRIMARY KEY (tag_name, file)
);
CREATE TABLE graph_url_nodes (
    id   TEXT PRIMARY KEY,
    body TEXT
);
CREATE TABLE graph_url_edges (
    from_id TEXT NOT NULL,
    to_id   TEXT NOT NULL,
    kind    TEXT NOT NULL
);
CREATE INDEX idx_url_edges_from ON graph_url_edges(from_id);
CREATE INDEX idx_url_edges_to   ON graph_url_edges(to_id);
CREATE TABLE graph_fs_nodes (
    id   TEXT PRIMARY KEY,
    body TEXT
);
CREATE TABLE graph_fs_edges (
    from_id TEXT NOT NULL,
    to_id   TEXT NOT NULL,
    kind    TEXT NOT NULL
);
CREATE TABLE graph_indexes (
    kind   TEXT NOT NULL,
    bucket TEXT NOT NULL,
    member TEXT NOT NULL,
    PRIMARY KEY (kind, bucket, member)
);
"""


def _manifest_rows(d: dict) -> list[tuple[str, str]]:
    keys = ("dir", "scope", "generated_at", "schema_version",
            "dir_count", "file_count", "udt_count", "unique_tags")
    return [(k, str(d[k])) for k in keys if k in d]


def _s(v):
    if v is None: return None
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, sort_keys=True)


def _ingest_one(con: sqlite3.Connection, d: dict, dir_rel: str) -> None:
    """Insert one dir's slice (tags/udt_types/sections/kinds/refs/ids/udts)
    into the DB, stamped with dir_rel. Used by write_local (dir='.') and
    write_global (dir=each local dir)."""
    for tag_name, info in (d.get("tags") or {}).items():
        files = info.get("files") if isinstance(info, dict) else []
        for f in files or []:
            con.execute("INSERT OR IGNORE INTO tags(name,file,dir) VALUES (?,?,?)",
                        (tag_name, f, dir_rel))
    for name, cnt in (d.get("udt_types") or {}).items():
        con.execute("INSERT OR REPLACE INTO udt_types(name,dir,count) VALUES (?,?,?)",
                    (name, dir_rel, int(cnt)))
    for name, cnt in (d.get("sections") or {}).items():
        con.execute("INSERT OR REPLACE INTO sections(name,dir,count) VALUES (?,?,?)",
                    (name, dir_rel, int(cnt)))
    for ext, cnt in (d.get("kinds") or {}).items():
        con.execute("INSERT OR REPLACE INTO kinds(ext,dir,count) VALUES (?,?,?)",
                    (ext, dir_rel, int(cnt)))
    for bucket, inner in (d.get("refs") or {}).items():
        for name, cnt in (inner or {}).items():
            con.execute("INSERT OR REPLACE INTO refs(bucket,name,dir,count) VALUES (?,?,?,?)",
                        (bucket, name, dir_rel, int(cnt)))
    for uid, cnt in (d.get("ids") or {}).items():
        con.execute("INSERT OR REPLACE INTO ids(id,dir,count) VALUES (?,?,?)",
                    (uid, dir_rel, int(cnt)))
    for u in d.get("udts") or []:
        if not isinstance(u, dict): continue
        body = u.get("body") or u
        con.execute(
            "INSERT OR REPLACE INTO udts(id,dir,file,udt_type,body) VALUES (?,?,?,?,?)",
            (_s(u.get("id") or u.get("file")),
             dir_rel,
             _s(u.get("file")),
             _s(u.get("udtType")),
             json.dumps(body, ensure_ascii=False, sort_keys=True)),
        )


def _write_common(con: sqlite3.Connection, d: dict) -> None:
    con.executemany("INSERT INTO manifest(key,value) VALUES (?,?)", _manifest_rows(d))
    _ingest_one(con, d, d.get("dir") or ".")


def _write_global_extra(con: sqlite3.Connection, d: dict) -> None:
    for tag_name, info in (d.get("tags") or {}).items():
        for dir_rel in (info.get("dirs") or []) if isinstance(info, dict) else []:
            con.execute("INSERT OR IGNORE INTO tag_dirs(tag_name,dir) VALUES (?,?)",
                        (tag_name, dir_rel))
        for sample in (info.get("sample_files") or []) if isinstance(info, dict) else []:
            con.execute("INSERT OR IGNORE INTO tag_samples(tag_name,file) VALUES (?,?)",
                        (tag_name, sample))

    graphs = d.get("graphs") or {}
    url_g = graphs.get("url_paths") or {}
    fs_g  = graphs.get("fs_paths")  or {}

    for n in url_g.get("nodes") or []:
        con.execute("INSERT OR REPLACE INTO graph_url_nodes(id,body) VALUES (?,?)",
                    (n.get("id"), json.dumps(n, ensure_ascii=False, sort_keys=True)))
    for e in url_g.get("edges") or []:
        con.execute("INSERT INTO graph_url_edges(from_id,to_id,kind) VALUES (?,?,?)",
                    (e.get("from"), e.get("to"), e.get("kind")))
    for n in fs_g.get("nodes") or []:
        con.execute("INSERT OR REPLACE INTO graph_fs_nodes(id,body) VALUES (?,?)",
                    (n.get("id"), json.dumps(n, ensure_ascii=False, sort_keys=True)))
    for e in fs_g.get("edges") or []:
        con.execute("INSERT INTO graph_fs_edges(from_id,to_id,kind) VALUES (?,?,?)",
                    (e.get("from"), e.get("to"), e.get("kind")))

    idx = d.get("indexes") or {}
    for bucket_kind, buckets in idx.items():
        for bucket, members in (buckets or {}).items():
            for m in (members or []):
                con.execute(
                    "INSERT OR IGNORE INTO graph_indexes(kind,bucket,member) VALUES (?,?,?)",
                    (bucket_kind, str(bucket), m))


def _fresh(db_path: Path, extra_schema: str = "") -> sqlite3.Connection:
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.executescript(LOCAL_SCHEMA + extra_schema)
    return con


def write_local(db_path: str | Path, d: dict) -> None:
    con = _fresh(Path(db_path))
    _write_common(con, d)
    con.commit()
    con.close()


def write_global(db_path: str | Path, d: dict) -> None:
    con = _fresh(Path(db_path), GLOBAL_EXTRA)
    _write_common(con, d)
    _write_global_extra(con, d)
    con.commit()
    con.close()


def _snapshot_udts(db_path: Path) -> dict:
    """Read existing (id,dir) -> full-row dict from tag.db.udts so archived
    bodies survive source-file deletion."""
    if not db_path.exists():
        return {}
    out = {}
    try:
        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "udts" in tables:
            for row in con.execute("SELECT id, dir, file, udt_type, body FROM udts"):
                out[(row["id"], row["dir"])] = dict(row)
        con.close()
    except sqlite3.Error:
        pass
    return out


def write_consolidated(db_path: str | Path, global_d: dict, local_dbs: dict) -> None:
    """Root tag.db containing EVERY local dir's full content stamped with dir.
    Replaces per-directory tag.db files. Archived UDT rows whose source file
    is no longer on disk are preserved from the prior tag.db."""
    db_path = Path(db_path)
    snapshot = _snapshot_udts(db_path)

    con = _fresh(db_path, GLOBAL_EXTRA)
    con.executemany("INSERT INTO manifest(key,value) VALUES (?,?)", _manifest_rows(global_d))
    _write_global_extra(con, global_d)

    touched_udts: set = set()
    for dir_rel, ld in local_dbs.items():
        _ingest_one(con, ld, dir_rel)
        for u in (ld.get("udts") or []):
            if not isinstance(u, dict): continue
            uid = u.get("id") or u.get("file")
            if uid: touched_udts.add((_s(uid) if not isinstance(uid, str) else uid, dir_rel))

    # Carry forward archived UDT rows (source file gone, body preserved)
    archived = 0
    for key, row in snapshot.items():
        if key in touched_udts:
            continue
        con.execute(
            "INSERT OR REPLACE INTO udts(id,dir,file,udt_type,body) VALUES (?,?,?,?,?)",
            (row["id"], row["dir"], row["file"], row["udt_type"], row["body"]),
        )
        archived += 1
    con.execute(
        "INSERT OR REPLACE INTO manifest(key,value) VALUES ('archived_udt_count', ?)",
        (str(archived),),
    )
    con.commit()
    con.close()
