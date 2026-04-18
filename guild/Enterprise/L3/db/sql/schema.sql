-- ═══ ACG tag catalog · SQLite schema ═══
-- Canonical store for every UDT, tag, subsystem, and scada program in
-- the project. Built from the JSON manifests by build.py; rebuilt on
-- each commit. Git-diff-friendly: the SQL dump (seed.sql) is text-only,
-- the .sqlite binary is a convenience artifact for direct querying.

PRAGMA foreign_keys = ON;

-- ─── subsystems · providers/registry.json ──────────────────────────
CREATE TABLE IF NOT EXISTS subsystems (
  id            TEXT PRIMARY KEY,      -- e.g. '💬 chat'
  name          TEXT,                  -- slug, e.g. 'chat'
  dir           TEXT,
  provider      TEXT,
  udts_path     TEXT,
  tags_path     TEXT,
  host          TEXT,                  -- gateway host if module
  registered_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subsystem_namespaces (
  subsystem_id TEXT NOT NULL,
  namespace    TEXT NOT NULL,
  PRIMARY KEY (subsystem_id, namespace),
  FOREIGN KEY (subsystem_id) REFERENCES subsystems(id) ON DELETE CASCADE
);

-- ─── UDT catalog ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS udts (
  name         TEXT PRIMARY KEY,
  subsystem_id TEXT,
  glyph        TEXT,
  base         TEXT,
  desc         TEXT,
  layer        TEXT,                    -- Konomi layer if known
  raw          TEXT,                    -- full JSON blob for round-trip
  FOREIGN KEY (subsystem_id) REFERENCES subsystems(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS udt_fields (
  udt        TEXT NOT NULL,
  name       TEXT NOT NULL,
  type       TEXT,
  nullable   INTEGER DEFAULT 0,
  is_array   INTEGER DEFAULT 0,
  position   INTEGER,
  desc       TEXT,
  PRIMARY KEY (udt, name),
  FOREIGN KEY (udt) REFERENCES udts(name) ON DELETE CASCADE
);

-- ─── Tag catalog ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tags (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  path         TEXT,                    -- exact path (one of)
  path_pattern TEXT,                    -- pattern path (cardinality=many)
  type         TEXT,
  cardinality  TEXT DEFAULT 'one',      -- 'one' | 'many'
  unit         TEXT,
  desc         TEXT,
  subsystem_id TEXT,
  FOREIGN KEY (subsystem_id) REFERENCES subsystems(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS tags_path_idx       ON tags(path);
CREATE INDEX IF NOT EXISTS tags_pattern_idx    ON tags(path_pattern);
CREATE INDEX IF NOT EXISTS tags_subsystem_idx  ON tags(subsystem_id);

-- ─── Scada program manifests · controls/scada/programs/**.json ────
CREATE TABLE IF NOT EXISTS programs (
  file     TEXT PRIMARY KEY,
  section  TEXT,
  glyph    TEXT,
  name     TEXT,
  module   TEXT,
  desc     TEXT,
  raw      TEXT
);

-- ─── Konvenience views ────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS v_tags_full AS
  SELECT t.id,
         COALESCE(t.path, t.path_pattern) AS path_or_pattern,
         t.path, t.path_pattern,
         t.type, t.cardinality, t.unit, t.desc,
         s.id AS subsystem, s.name AS subsystem_name, s.provider
  FROM tags t
  LEFT JOIN subsystems s ON t.subsystem_id = s.id
  ORDER BY COALESCE(t.path, t.path_pattern);

CREATE VIEW IF NOT EXISTS v_udt_rollup AS
  SELECT u.name       AS udt,
         u.subsystem_id,
         u.base,
         u.layer,
         GROUP_CONCAT(f.name || ':' || f.type, ', ') AS fields
  FROM udts u LEFT JOIN udt_fields f ON u.name = f.udt
  GROUP BY u.name, u.subsystem_id, u.base, u.layer
  ORDER BY u.name;

CREATE VIEW IF NOT EXISTS v_subsystem_summary AS
  SELECT s.id, s.name, s.provider,
         (SELECT COUNT(*) FROM udts u WHERE u.subsystem_id = s.id) AS udt_count,
         (SELECT COUNT(*) FROM tags t WHERE t.subsystem_id = s.id) AS tag_count,
         (SELECT GROUP_CONCAT(namespace,', ')
            FROM subsystem_namespaces n WHERE n.subsystem_id = s.id) AS namespaces
  FROM subsystems s
  ORDER BY s.name;
