#!/usr/bin/env python3
"""Initialize guild/Enterprise/L4/database/acg.db from UDT instances.

Creates (or refreshes) the schema, then seeds papers + members + programs +
packml_runs from the canonical JSON source. Idempotent: running it again
reloads from the latest instance files.

Usage:  python guild/Enterprise/L4/database/init-db.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))

import db
import load_papers, load_members, load_programs

def main():
    print(f"[db] opening {db.DB_PATH.relative_to(HERE.parents[3])}")
    conn = db.connect()
    try:
        print("[db] applying schemas")
        db.apply_schemas(conn)

        n_papers = load_papers.load(conn)
        print(f"[db] loaded {n_papers} papers")

        n_members = load_members.load(conn)
        print(f"[db] loaded {n_members} members (+ derived member_papers)")

        n_programs = load_programs.load(conn)
        print(f"[db] loaded {n_programs} programs + run history")

        # Summary
        cur = conn.execute("SELECT COUNT(*) c FROM packml_runs")
        runs = cur.fetchone()["c"]
        cur = conn.execute("SELECT COUNT(*) c FROM paper_tags")
        paper_tags = cur.fetchone()["c"]
        cur = conn.execute("SELECT COUNT(*) c FROM member_papers")
        mp = cur.fetchone()["c"]
        print(f"[db] rows: {runs} PackML runs, {paper_tags} paper-tag edges, "
              f"{mp} member-paper links")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
