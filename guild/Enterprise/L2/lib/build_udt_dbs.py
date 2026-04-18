"""
Walk the repo, and for every directory that contains one or more *.udt.json
files, create (or refresh) a local `udt.db` SQLite holding the UDT types
defined in that directory. Mirrors the per-directory tag.db pattern.

Run via Tool UDT: `bin/acg build:udt-dbs`.
"""
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]

SKIP_DIRS = {"node_modules", "__pycache__", ".git", "dist"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS udts (
  id         TEXT PRIMARY KEY,
  udt_type   TEXT,
  version    TEXT,
  description TEXT,
  file       TEXT,
  raw        TEXT,
  updated_at TEXT
);
CREATE INDEX IF NOT EXISTS udts_type_idx ON udts(udt_type);
"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build() -> dict:
    dirs_with_udts: dict[Path, list[Path]] = {}
    for p in REPO.rglob("*.udt.json"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        dirs_with_udts.setdefault(p.parent, []).append(p)

    created, updated, total_udts = 0, 0, 0
    for d, udt_files in sorted(dirs_with_udts.items()):
        db_path = d / "udt.db"
        existed = db_path.exists()
        con = sqlite3.connect(db_path)
        con.executescript(SCHEMA)
        for f in sorted(udt_files):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            uid = f.stem.replace(".udt", "")
            udt_type = doc.get("udtType", "")
            version  = str(doc.get("version", ""))
            desc     = doc.get("description", "")
            raw      = json.dumps(doc, ensure_ascii=False, sort_keys=True)
            con.execute(
                "INSERT OR REPLACE INTO udts(id, udt_type, version, description, file, raw, updated_at) "
                "VALUES (?,?,?,?,?,?,?)",
                (uid, udt_type, version, desc, f.name, raw, _now()),
            )
            total_udts += 1
        con.commit()
        con.close()
        if existed:
            updated += 1
        else:
            created += 1

    return {
        "ok": True,
        "dirs_with_udts": len(dirs_with_udts),
        "created_dbs":    created,
        "updated_dbs":    updated,
        "total_udts":     total_udts,
    }
