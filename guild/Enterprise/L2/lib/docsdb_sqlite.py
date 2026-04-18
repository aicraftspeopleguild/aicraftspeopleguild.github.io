"""
docsdb_sqlite — serialize the gen-docs-db dicts into a consolidated root
docs.db SQLite. Mirrors the tagdb_sqlite pattern: per-directory docs.db
files are retired; every row carries a `dir` attribution column so the
whole repo is query-able from one file.
"""
import json, sqlite3
from pathlib import Path


SCHEMA = """
DROP TABLE IF EXISTS manifest;
DROP TABLE IF EXISTS docs;
DROP TABLE IF EXISTS headings;
DROP TABLE IF EXISTS links;
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS code_langs;
DROP TABLE IF EXISTS frontmatter;
DROP TABLE IF EXISTS broken_refs;
DROP TABLE IF EXISTS by_ext;

CREATE TABLE manifest (
    key   TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE docs (
    dir         TEXT NOT NULL,
    path        TEXT NOT NULL,
    ext         TEXT,
    size        INTEGER,
    lines       INTEGER,
    sha1        TEXT,
    parser      TEXT,
    h1          TEXT,
    word_count  INTEGER,
    body        TEXT,
    PRIMARY KEY (dir, path)
);
CREATE INDEX idx_docs_ext ON docs(ext);
CREATE INDEX idx_docs_dir ON docs(dir);

CREATE TABLE headings (
    dir   TEXT NOT NULL,
    path  TEXT NOT NULL,
    level INTEGER NOT NULL,
    text  TEXT,
    line  INTEGER
);
CREATE INDEX idx_headings_doc   ON headings(dir, path);
CREATE INDEX idx_headings_level ON headings(level);

CREATE TABLE links (
    dir      TEXT NOT NULL,
    path     TEXT NOT NULL,
    url      TEXT,
    line     INTEGER,
    external INTEGER DEFAULT 0
);
CREATE INDEX idx_links_doc  ON links(dir, path);
CREATE INDEX idx_links_ext  ON links(external);

CREATE TABLE images (
    dir  TEXT NOT NULL,
    path TEXT NOT NULL,
    src  TEXT,
    line INTEGER
);
CREATE INDEX idx_images_doc ON images(dir, path);

CREATE TABLE code_langs (
    dir   TEXT NOT NULL,
    path  TEXT NOT NULL,
    lang  TEXT NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (dir, path, lang)
);

CREATE TABLE frontmatter (
    dir   TEXT NOT NULL,
    path  TEXT NOT NULL,
    key   TEXT NOT NULL,
    value TEXT
);
CREATE INDEX idx_frontmatter_doc ON frontmatter(dir, path);
CREATE INDEX idx_frontmatter_key ON frontmatter(key);

CREATE TABLE broken_refs (
    dir  TEXT NOT NULL,
    path TEXT NOT NULL,
    ref  TEXT,
    line INTEGER
);

CREATE TABLE by_ext (
    ext   TEXT PRIMARY KEY,
    count INTEGER NOT NULL
);
"""


def _fresh(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.executescript(SCHEMA)
    return con


def _s(v):
    if v is None: return None
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, sort_keys=True)


def _manifest_rows(d: dict) -> list:
    keys = ("dir", "scope", "generated_at", "schema_version",
            "dir_count", "doc_count", "total_bytes")
    return [(k, str(d[k])) for k in keys if k in d]


def _ingest_dir(con: sqlite3.Connection, dir_rel: str, local: dict) -> None:
    for doc in local.get("docs") or []:
        if not isinstance(doc, dict): continue
        path = doc.get("path") or doc.get("file")
        if not path: continue
        f = doc.get("fields") or {}
        con.execute(
            "INSERT OR REPLACE INTO docs(dir,path,ext,size,lines,sha1,parser,h1,word_count,body) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (dir_rel, path, doc.get("ext"), doc.get("size"), doc.get("lines"),
             doc.get("sha1"), doc.get("parser"),
             f.get("h1") or f.get("title"),
             f.get("word_count"),
             doc.get("body")),
        )
        for h in f.get("headings") or []:
            con.execute(
                "INSERT INTO headings(dir,path,level,text,line) VALUES (?,?,?,?,?)",
                (dir_rel, path, int(h.get("level", 0)),
                 _s(h.get("text")), h.get("line")),
            )
        for L in f.get("links") or []:
            if isinstance(L, dict):
                con.execute(
                    "INSERT INTO links(dir,path,url,line,external) VALUES (?,?,?,?,?)",
                    (dir_rel, path, L.get("url") or L.get("href"),
                     L.get("line"),
                     1 if L.get("external") else 0),
                )
            elif isinstance(L, str):
                con.execute(
                    "INSERT INTO links(dir,path,url,line,external) VALUES (?,?,?,?,?)",
                    (dir_rel, path, L, None,
                     1 if L.startswith(("http://", "https://", "mailto:")) else 0),
                )
        for img in f.get("images") or []:
            src = img.get("src") if isinstance(img, dict) else img
            con.execute(
                "INSERT INTO images(dir,path,src,line) VALUES (?,?,?,?)",
                (dir_rel, path, _s(src),
                 img.get("line") if isinstance(img, dict) else None),
            )
        for lang, cnt in (f.get("code_langs") or {}).items():
            con.execute(
                "INSERT OR REPLACE INTO code_langs(dir,path,lang,count) VALUES (?,?,?,?)",
                (dir_rel, path, lang, int(cnt)),
            )
        for k, v in (f.get("frontmatter") or {}).items():
            con.execute(
                "INSERT INTO frontmatter(dir,path,key,value) VALUES (?,?,?,?)",
                (dir_rel, path, k, _s(v)),
            )
        for ref in f.get("broken_refs") or []:
            con.execute(
                "INSERT INTO broken_refs(dir,path,ref,line) VALUES (?,?,?,?)",
                (dir_rel, path, _s(ref.get("ref") if isinstance(ref, dict) else ref),
                 ref.get("line") if isinstance(ref, dict) else None),
            )


def _snapshot_docs(db_path: Path) -> dict:
    """Read existing (dir,path) -> full-row dict from an existing docs.db so we can
    preserve archived bodies for source files that are no longer on disk."""
    if not db_path.exists():
        return {}
    out = {}
    try:
        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        for row in con.execute(
            "SELECT dir,path,ext,size,lines,sha1,parser,h1,word_count,body FROM docs"
        ):
            out[(row["dir"], row["path"])] = dict(row)
        con.close()
    except sqlite3.Error:
        pass
    return out


def write_consolidated(db_path, global_d: dict, local_dbs: dict) -> None:
    """Write the single root docs.db. Archived bodies for paths no longer on disk
    are preserved from the prior docs.db so deletion of source files is safe."""
    db_path = Path(db_path)
    snapshot = _snapshot_docs(db_path)

    # Collect keys that the current scan touched; everything else from the
    # snapshot gets carried forward as-is.
    touched: set = set()
    for dir_rel, ld in local_dbs.items():
        for d in (ld.get("docs") or []):
            if isinstance(d, dict) and d.get("path"):
                touched.add((dir_rel, d["path"]))

    con = _fresh(db_path)
    con.executemany("INSERT INTO manifest(key,value) VALUES (?,?)", _manifest_rows(global_d))
    for ext, v in (global_d.get("by_ext") or {}).items():
        cnt = len(v) if isinstance(v, list) else int(v or 0)
        con.execute("INSERT OR REPLACE INTO by_ext(ext,count) VALUES (?,?)",
                    (ext, cnt))

    # Fresh from disk
    for dir_rel, ld in local_dbs.items():
        _ingest_dir(con, dir_rel, ld)

    # Carry forward archived rows whose source file no longer exists
    archived = 0
    for key, row in snapshot.items():
        if key in touched:
            continue  # disk wins
        con.execute(
            "INSERT OR REPLACE INTO docs(dir,path,ext,size,lines,sha1,parser,h1,word_count,body) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (row["dir"], row["path"], row["ext"], row["size"], row["lines"],
             row["sha1"], row["parser"], row["h1"], row["word_count"], row["body"]),
        )
        archived += 1

    # Stamp the archived count into the manifest so callers can see it.
    con.execute(
        "INSERT OR REPLACE INTO manifest(key,value) VALUES ('archived_count', ?)",
        (str(archived),),
    )
    con.commit()
    con.close()
