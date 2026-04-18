-- ACG site SQLite schema.
-- Populated from guild/web/**/udts/instances/ by scripts/database/init.py.
-- The .db file is gitignored; regenerate any time from the JSON source of truth.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- White paper publications (one row per guild/Enterprise/L4/api/white-papers/udts/instances/*.json).
CREATE TABLE IF NOT EXISTS papers (
    id                TEXT PRIMARY KEY,
    title             TEXT NOT NULL,
    doc_number        TEXT,
    publication_date  TEXT,
    source_medium     TEXT,
    summary           TEXT,
    status            TEXT DEFAULT 'published',
    site_href         TEXT,
    original_path     TEXT,
    original_format   TEXT,
    instance_path     TEXT,
    body              TEXT,
    ingested_at       TEXT,
    schema_version    TEXT
);

-- Paper authors (many-to-many; preserves author order via idx).
CREATE TABLE IF NOT EXISTS paper_authors (
    paper_id  TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    idx       INTEGER NOT NULL,
    author    TEXT NOT NULL,
    PRIMARY KEY (paper_id, idx)
);

-- Paper topic tags.
CREATE TABLE IF NOT EXISTS paper_tags (
    paper_id  TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    tag       TEXT NOT NULL,
    PRIMARY KEY (paper_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_paper_tags_tag ON paper_tags(tag);
