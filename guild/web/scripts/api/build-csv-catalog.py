#!/usr/bin/env python3
"""
Export dense CSV catalogs of Guild tags and relations to guild/Enterprise/L4/csv/.

Dense format: one header row + one data row per record, no quoting unless
needed. These files are the token-efficient alternative to the JSON
catalogs for agent consumption and large-scale queries.

Outputs:
  csv/papers.csv           id,title,author,date,status,doc_number
  csv/paper_tags.csv       paper_id,tag
  csv/members.csv          handle,name,role,title
  csv/member_tags.csv      member_id,tag
  csv/member_papers.csv    member_id,paper_id
  csv/programs.csv         id,name,category,language,last_state
  csv/packml_runs.csv      run_id,program_id,terminal,duration_s,started_at
  csv/paths.csv            id,path,section,parent,depth,dynamic
"""
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
CSV_DIR = REPO / "guild" / "Enterprise" / "L4" / "csv"
DB_LIB  = REPO / "guild" / "Enterprise" / "L4" / "database" / "lib"
PATHS_DIR = REPO / "guild" / "web" / "components" / "udts" / "instances" / "paths"

sys.path.insert(0, str(REPO / "guild" / "web" / "scripts" / "lib"))
sys.path.insert(0, str(DB_LIB))
from packml import Process, path_exists
import db as acgdb

def dump(conn, sql, fieldnames, out):
    rows = [dict(r) for r in conn.execute(sql)]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (r.get(k) if r.get(k) is not None else "") for k in fieldnames})
    return len(rows)

def dump_paths(out):
    rows = []
    for f in sorted(PATHS_DIR.glob("*.json")):
        if f.name.startswith("_"): continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if d.get("udtType") != "Path": continue
            p = d.get("parameters", {}); t = d.get("tags", {})
            rows.append({
                "id":      t.get("id"),
                "path":    p.get("path"),
                "section": p.get("section") or "",
                "parent":  p.get("parent") or "",
                "depth":   t.get("depth", 0),
                "dynamic": 1 if p.get("dynamic") else 0,
            })
        except Exception:
            pass
    fields = ["id", "path", "section", "parent", "depth", "dynamic"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    return len(rows)

def main():
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    conn = acgdb.connect()
    try:
        n_papers = dump(conn, "SELECT id, title, status, doc_number, publication_date AS date FROM papers ORDER BY id",
                        ["id","title","status","doc_number","date"], CSV_DIR / "papers.csv")
        n_ptags  = dump(conn, "SELECT paper_id, tag FROM paper_tags ORDER BY paper_id, tag",
                        ["paper_id","tag"], CSV_DIR / "paper_tags.csv")
        n_pauth  = dump(conn, "SELECT paper_id, idx, author FROM paper_authors ORDER BY paper_id, idx",
                        ["paper_id","idx","author"], CSV_DIR / "paper_authors.csv")
        n_m      = dump(conn, "SELECT id AS handle, name, role, title FROM members ORDER BY name",
                        ["handle","name","role","title"], CSV_DIR / "members.csv")
        n_mtag   = dump(conn, "SELECT member_id, tag FROM member_tags ORDER BY member_id, tag",
                        ["member_id","tag"], CSV_DIR / "member_tags.csv")
        n_mp     = dump(conn, "SELECT member_id, paper_id FROM member_papers ORDER BY member_id, paper_id",
                        ["member_id","paper_id"], CSV_DIR / "member_papers.csv")
        n_prog   = dump(conn, "SELECT id, name, category, language, last_state FROM programs ORDER BY id",
                        ["id","name","category","language","last_state"], CSV_DIR / "programs.csv")
        n_runs   = dump(conn, "SELECT run_id, program_id, terminal, duration_s, started_at FROM packml_runs ORDER BY started_at DESC",
                        ["run_id","program_id","terminal","duration_s","started_at"], CSV_DIR / "packml_runs.csv")
    finally:
        conn.close()

    n_paths = dump_paths(CSV_DIR / "paths.csv")

    # Report bytes saved vs JSON equivalent
    sizes = sorted([(f.name, f.stat().st_size) for f in CSV_DIR.glob("*.csv")])
    print("[csv] catalogs written to", CSV_DIR.relative_to(REPO))
    for name, size in sizes:
        print(f"  {name:24} {size:6} bytes")
    print(f"[csv] totals: papers={n_papers}, paper_tags={n_ptags}, "
          f"members={n_m}, programs={n_prog}, runs={n_runs}, paths={n_paths}")

if __name__ == "__main__":
    with Process(
        "api--build-csv-catalog_py",
        pre_checks=[path_exists(REPO / "guild" / "Enterprise" / "L4" / "database" / "acg.db")],
        post_checks=[
            path_exists(CSV_DIR / "papers.csv"),
            path_exists(CSV_DIR / "members.csv"),
            path_exists(CSV_DIR / "paths.csv"),
        ],
    ):
        main()
