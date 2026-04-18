"""SQLite connection helper for the ACG site database."""
import sqlite3
from pathlib import Path

DB_DIR  = Path(__file__).resolve().parents[1]
DB_PATH = DB_DIR / "acg.db"
SCHEMAS = ["schema.sql", "schema-members.sql", "schema-programs.sql"]

def connect(path: Path = None) -> sqlite3.Connection:
    """Open a connection with foreign keys enabled and row_factory=Row."""
    p = path or DB_PATH
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def apply_schemas(conn: sqlite3.Connection):
    """Execute every .sql schema file in order; idempotent (CREATE IF NOT EXISTS)."""
    for name in SCHEMAS:
        sql = (DB_DIR / name).read_text(encoding="utf-8")
        conn.executescript(sql)
    conn.commit()
