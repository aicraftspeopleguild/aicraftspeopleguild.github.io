#!/usr/bin/env python3
"""
Build the static JSON API at guild/Enterprise/L4/api/ from the SQLite database.

Endpoints produced:
  /api/papers.json   Paper[]   — UDT-shaped with id/type/title/author/date/tags/slug
  /api/members.json  Member[]  — handle/name/role/org/signed/expertise_tags
  /api/health.json   {paperCount, memberCount, lastUpdated}

Matches the v1.0 ACG API spec in docs/engineering/standards/acg-api.md.
Runs as PackML process so failures are recorded + checks enforced.
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

HERE    = Path(__file__).resolve()
SCRIPTS = HERE.parents[1]
REPO    = HERE.parents[4]
DB_LIB  = REPO / "guild" / "Enterprise" / "L4" / "database" / "lib"
API_DIR = REPO / "guild" / "Enterprise" / "L4" / "api"

sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(DB_LIB))
from packml import Process, path_exists, has_files  # type: ignore
import db as acgdb  # type: ignore

def build_papers(conn):
    rows = conn.execute("""
        SELECT id, type_from_status(status) AS type, title,
               date, publication_date, status, abstract, slug, doc_number
        FROM (SELECT
                 p.id, p.status, p.title, p.date, p.publication_date,
                 p.summary AS abstract, p.slug, p.doc_number, p.site_href
              FROM papers p)
    """).fetchall() if False else None
    # Simpler: read straight from papers table and compose authors/tags.
    papers = []
    for p in conn.execute("SELECT * FROM papers ORDER BY publication_date DESC, title"):
        pid = p["id"]
        authors = [r["author"] for r in conn.execute(
            "SELECT author FROM paper_authors WHERE paper_id=? ORDER BY idx", (pid,))]
        tags = [r["tag"] for r in conn.execute(
            "SELECT tag FROM paper_tags WHERE paper_id=?", (pid,))]
        papers.append({
            "id":     p["doc_number"] or pid,
            "type":   infer_type(p["status"]),
            "title":  p["title"],
            "author": ", ".join(authors) if authors else "",
            "date":   p["publication_date"] or "",
            "status": normalize_status(p["status"]),
            "tags":   tags,
            "abstract": p["summary"] or "",
            "slug":   pid,
            "doc_number": p["doc_number"] or "",
            "publication_date": p["publication_date"] or ""
        })
    return papers

def infer_type(status_field):
    """The older ingest pipeline stored paper 'type' in the `status` column
    (position/experimental/research-note/published). Normalize to API v1.0 enum."""
    s = (status_field or "published").lower()
    mapping = {
        "position":          "position-paper",
        "experimental":      "experimental",
        "research-note":     "research-note",
        "knowledge-about-knowledge": "knowledge",
        "published":         "white-paper",
        "draft":             "white-paper",
    }
    return mapping.get(s, "white-paper")

def normalize_status(s):
    low = (s or "").lower()
    if low in ("draft", "review", "published", "archived"): return low
    return "published"

def build_members(conn):
    members = []
    for m in conn.execute("SELECT * FROM members ORDER BY name"):
        tags = [r["tag"] for r in conn.execute(
            "SELECT tag FROM member_tags WHERE member_id=?", (m["id"],))]
        members.append({
            "handle": m["slug"] or m["id"],
            "name":   m["name"],
            "role":   m["role"] or "",
            "org":    "",
            "signed": True,
            "joined": m["joined_date"] or "",
            "avatar_href":    m["avatar_href"] or "",
            "expertise_tags": tags
        })
    return members

def build_health(papers, members):
    return {
        "paperCount":  len(papers),
        "memberCount": len(members),
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "github.com/aicraftspeopleguild/aicraftspeopleguild.github.io",
        "apiVersion": "1.0"
    }

def main():
    API_DIR.mkdir(parents=True, exist_ok=True)
    conn = acgdb.connect()
    try:
        papers  = build_papers(conn)
        members = build_members(conn)
        health  = build_health(papers, members)
    finally:
        conn.close()

    (API_DIR / "papers.json").write_text(
        json.dumps(papers, indent=2, ensure_ascii=False), encoding="utf-8")
    (API_DIR / "members.json").write_text(
        json.dumps(members, indent=2, ensure_ascii=False), encoding="utf-8")
    (API_DIR / "health.json").write_text(
        json.dumps(health, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[api] papers.json  ({len(papers)} papers)")
    print(f"[api] members.json ({len(members)} members)")
    print(f"[api] health.json  (api v{health['apiVersion']})")

if __name__ == "__main__":
    with Process(
        "api--build-api_py",
        pre_checks=[path_exists(REPO / "guild" / "Enterprise" / "L4" / "database" / "acg.db")],
        post_checks=[
            path_exists(API_DIR / "papers.json"),
            path_exists(API_DIR / "members.json"),
            path_exists(API_DIR / "health.json"),
        ],
    ):
        main()
