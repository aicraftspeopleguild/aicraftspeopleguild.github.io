"""Load WhitePaper UDT instances into the papers / paper_authors / paper_tags tables."""
import json
from pathlib import Path

INSTANCES = Path(__file__).resolve().parents[5] / "guild" / "Enterprise" / "L4" / "api" / "white-papers" / "udts" / "instances"

def load(conn):
    """Upsert every paper UDT instance. Clears existing rows first."""
    conn.execute("DELETE FROM paper_tags")
    conn.execute("DELETE FROM paper_authors")
    conn.execute("DELETE FROM papers")
    count = 0
    for f in sorted(INSTANCES.glob("*.json")):
        wp = json.loads(f.read_text(encoding="utf-8"))
        if wp.get("udtType") != "WhitePaper":
            continue
        p = wp.get("parameters", {}); t = wp.get("tags", {})
        conn.execute("""
            INSERT INTO papers (id, title, doc_number, publication_date, source_medium,
                summary, status, site_href, original_path, original_format,
                instance_path, body, ingested_at, schema_version)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            t.get("id"), p.get("title"), p.get("doc_number"), p.get("publication_date"),
            p.get("source_medium"), p.get("summary"), p.get("status", "published"),
            p.get("site_href"), t.get("original_path"), t.get("original_format"),
            t.get("instance_path"), t.get("body"), t.get("ingested_at"), t.get("schema_version"),
        ))
        for i, a in enumerate(p.get("authors") or []):
            conn.execute(
                "INSERT INTO paper_authors(paper_id, idx, author) VALUES (?,?,?)",
                (t.get("id"), i, a))
        for tag in p.get("tags") or []:
            conn.execute(
                "INSERT OR IGNORE INTO paper_tags(paper_id, tag) VALUES (?,?)",
                (t.get("id"), tag))
        count += 1
    conn.commit()
    return count
