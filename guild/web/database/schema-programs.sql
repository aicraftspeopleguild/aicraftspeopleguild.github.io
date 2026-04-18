-- Build pipeline programs (scripts wrapped by PackML state machines).
CREATE TABLE IF NOT EXISTS programs (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    path            TEXT NOT NULL,
    language        TEXT NOT NULL,
    category        TEXT NOT NULL,
    purpose         TEXT,
    last_state      TEXT DEFAULT 'IDLE',
    last_run_at     TEXT,
    last_duration   TEXT,
    schema_version  TEXT
);

-- Full history of PackML runs — each run of any program appends one row.
CREATE TABLE IF NOT EXISTS packml_runs (
    run_id          TEXT PRIMARY KEY,
    program_id      TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    terminal        TEXT,
    duration_s      TEXT,
    error           TEXT,
    transitions_json TEXT,
    pre_checks_json  TEXT,
    post_checks_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_packml_program ON packml_runs(program_id);
CREATE INDEX IF NOT EXISTS idx_packml_terminal ON packml_runs(terminal);

-- Program tags (category grouping inverted index mirror).
CREATE TABLE IF NOT EXISTS program_tags (
    program_id  TEXT NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    tag         TEXT NOT NULL,
    PRIMARY KEY (program_id, tag)
);
