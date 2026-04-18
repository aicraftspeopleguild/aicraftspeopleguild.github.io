#!/usr/bin/env python3
"""
Build per-directory tag.db files.

Every major entity-bearing directory gets a local SQLite `tag.db` with:

  udts        one row per UDT instance in that subtree
  tags        flat name/value records indexable by scope
  manifest    metadata (count, last build, schema version)

Gives each directory self-description: you can query a subtree's tag.db
without loading the whole enterprise DB. Regenerable — gitignored.
"""
import json, sqlite3, sys, time
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "guild" / "web" / "scripts" / "lib"))
from packml import Process, path_exists  # type: ignore

# Directories that hold UDT instances and should get a tag.db
TARGETS = [
    REPO / "guild" / "web" / "white-papers",
    REPO / "guild" / "web" / "members",
    REPO / "guild" / "web" / "components",
    REPO / "guild" / "web" / "scripts",
    REPO / "guild" / "apps" / "whitepapers",
    REPO / "guild" / "Enterprise" / "L2",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS udts (
    id            TEXT PRIMARY KEY,
    udt_type      TEXT,
    source_path   TEXT,
    instance_json TEXT,
    ingested_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_udts_type ON udts(udt_type);

CREATE TABLE IF NOT EXISTS tags (
    scope   TEXT NOT NULL,
    key     TEXT,
    value   TEXT,
    udt_id  TEXT REFERENCES udts(id) ON DELETE CASCADE,
    quality TEXT DEFAULT 'good',
    ts      INTEGER,
    PRIMARY KEY (scope, key, udt_id)
);
CREATE INDEX IF NOT EXISTS idx_tags_scope ON tags(scope);
CREATE INDEX IF NOT EXISTS idx_tags_value ON tags(value);

CREATE TABLE IF NOT EXISTS manifest (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""

def iter_udts(root: Path):
    """Yield (path, udt_dict) for every *.json that looks like a UDT instance."""
    for f in root.rglob("*.json"):
        rel = f.relative_to(root).as_posix()
        # Skip templates, generated catalogs, graph outputs
        if "udts/templates/" in rel: continue
        if rel.startswith("_") or "/tags/index.json" in rel: continue
        if rel == "index.json": continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict): continue
        if "udtType" not in d: continue
        yield f, d

def build_one(target: Path):
    db_path = target / "tag.db"
    # Rebuild from scratch
    if db_path.exists(): db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    now_ms  = int(time.time() * 1000)

    udt_count = 0
    tag_count = 0
    by_type = {}

    for f, inst in iter_udts(target):
        udt_id = inst.get("tags", {}).get("id") or f.stem
        udt_type = inst.get("udtType", "Unknown")
        conn.execute(
            "INSERT OR REPLACE INTO udts (id, udt_type, source_path, instance_json, ingested_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (udt_id, udt_type, f.relative_to(target).as_posix(),
             json.dumps(inst, ensure_ascii=False), now_iso)
        )
        udt_count += 1
        by_type[udt_type] = by_type.get(udt_type, 0) + 1

        # Flatten selected tag-like fields for quick lookup
        params = inst.get("parameters", {}) or {}
        tags   = inst.get("tags", {}) or {}

        # Topic tags if present
        for t in (params.get("tags") or []):
            conn.execute("INSERT OR REPLACE INTO tags VALUES (?,?,?,?,?,?)",
                         ("topic", t, t, udt_id, "good", now_ms))
            tag_count += 1
        # Category
        if params.get("category"):
            conn.execute("INSERT OR REPLACE INTO tags VALUES (?,?,?,?,?,?)",
                         ("category", params["category"], params["category"], udt_id, "good", now_ms))
            tag_count += 1
        # Status
        if params.get("status"):
            conn.execute("INSERT OR REPLACE INTO tags VALUES (?,?,?,?,?,?)",
                         ("status", params["status"], params["status"], udt_id, "good", now_ms))
            tag_count += 1
        # Section (for Path UDTs)
        if params.get("section"):
            conn.execute("INSERT OR REPLACE INTO tags VALUES (?,?,?,?,?,?)",
                         ("section", params["section"], params["section"], udt_id, "good", now_ms))
            tag_count += 1

    # Manifest rows
    conn.executemany("INSERT OR REPLACE INTO manifest(key,value) VALUES (?,?)", [
        ("built_at",       now_iso),
        ("target",         target.relative_to(REPO).as_posix()),
        ("udt_count",      str(udt_count)),
        ("tag_count",      str(tag_count)),
        ("types",          json.dumps(by_type, sort_keys=True)),
        ("schema_version", "1.0.0"),
    ])
    conn.commit()
    conn.close()

    return udt_count, tag_count, by_type

def main():
    total_udts = total_tags = 0
    for target in TARGETS:
        if not target.exists():
            print(f"  [skip] {target.relative_to(REPO).as_posix()} (missing)")
            continue
        u, t, types = build_one(target)
        total_udts += u
        total_tags += t
        types_str = ", ".join(f"{k}:{v}" for k, v in sorted(types.items()))
        rel = target.relative_to(REPO).as_posix()
        print(f"  {rel:40} {u:4} UDTs, {t:4} tags  [{types_str}]")
    print(f"[tagdbs] total: {total_udts} UDTs, {total_tags} tags across {len(TARGETS)} dirs")

if __name__ == "__main__":
    with Process(
        "db--build-local-tagdbs_py",
        pre_checks=[path_exists(REPO / "guild")],
        post_checks=[path_exists(REPO / "guild" / "web" / "white-papers" / "tag.db")],
    ):
        main()
