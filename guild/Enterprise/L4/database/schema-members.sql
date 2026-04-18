-- Member profiles (one row per guild/web/members/udts/instances/*.json).
CREATE TABLE IF NOT EXISTS members (
    id              TEXT PRIMARY KEY,
    slug            TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    role            TEXT,
    title           TEXT,
    bio             TEXT,
    avatar_href     TEXT,
    joined_date     TEXT,
    instance_path   TEXT,
    schema_version  TEXT
);

-- Member expertise tags (many-to-many).
CREATE TABLE IF NOT EXISTS member_tags (
    member_id  TEXT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    tag        TEXT NOT NULL,
    PRIMARY KEY (member_id, tag)
);
CREATE INDEX IF NOT EXISTS idx_member_tags_tag ON member_tags(tag);

-- Member <-> paper authorship link (computed from paper_authors + members.name).
CREATE TABLE IF NOT EXISTS member_papers (
    member_id  TEXT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    paper_id   TEXT NOT NULL REFERENCES papers(id)  ON DELETE CASCADE,
    PRIMARY KEY (member_id, paper_id)
);
