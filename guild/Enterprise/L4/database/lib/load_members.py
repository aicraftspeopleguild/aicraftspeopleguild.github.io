"""Load Member UDT instances into the members / member_tags / member_papers tables."""
import json
from pathlib import Path

INSTANCES = Path(__file__).resolve().parents[5] / "guild" / "Enterprise" / "L4" / "members" / "udts" / "instances"


def _is_member(doc: dict) -> bool:
    return doc.get("udtType") == "Member"

def load(conn):
    conn.execute("DELETE FROM member_papers")
    conn.execute("DELETE FROM member_tags")
    conn.execute("DELETE FROM members")
    count = 0
    for f in sorted(INSTANCES.glob("*.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        if not _is_member(m):
            continue
        p = m.get("parameters", {}); t = m.get("tags", {})
        conn.execute("""
            INSERT INTO members (id, slug, name, role, title, bio, avatar_href,
                                 joined_date, instance_path, schema_version)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            t.get("id"), t.get("slug") or t.get("id"), p.get("name"),
            p.get("role"), p.get("title"), p.get("bio"), p.get("avatar_href"),
            p.get("joined_date"), t.get("instance_path"), t.get("schema_version"),
        ))
        for tag in p.get("expertise_tags") or []:
            conn.execute(
                "INSERT OR IGNORE INTO member_tags(member_id, tag) VALUES (?,?)",
                (t.get("id"), tag))
        count += 1

    # Derive member_papers by matching member.name to paper_authors.author
    conn.execute("""
        INSERT OR IGNORE INTO member_papers(member_id, paper_id)
        SELECT m.id, pa.paper_id
        FROM members m
        JOIN paper_authors pa ON LOWER(pa.author) LIKE '%' || LOWER(m.name) || '%'
    """)
    conn.commit()
    return count
