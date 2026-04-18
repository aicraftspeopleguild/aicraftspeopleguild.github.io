#!/usr/bin/env python3
"""
Build guild/Enterprise/L4/runtime/tags.json — Ignition-style live tags reflecting
current Guild enterprise state. Follows the Konomi Value UDT pattern:

  { "value": <v>, "quality": "good|stale|bad|uncertain", "type": "<UDT>" }

Inspired by ACGP2P's controls/db/tags.json. Regenerated on every build.
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "guild" / "web" / "scripts" / "lib"))
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L4" / "database" / "lib"))
from packml import Process, path_exists
import db as acgdb

OUT = REPO / "guild" / "Enterprise" / "L4" / "runtime" / "tags.json"

def now_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)

def count(conn, sql):
    return conn.execute(sql).fetchone()[0]

def scalar(conn, sql, default=None):
    row = conn.execute(sql).fetchone()
    return row[0] if row and row[0] is not None else default

def tag(v, quality="good", t="String"):
    return {"value": v, "quality": quality, "type": t}

def build_tags(conn):
    ts = now_ms()
    state_dir = REPO / "guild" / "Enterprise" / "L2" / "state"
    state_files = list(state_dir.glob("*.state.json")) if state_dir.exists() else []
    last_complete = 0
    aborts = 0
    for f in state_files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            t_ = d.get("parameters", {}).get("terminal")
            if t_ == "COMPLETE":
                last_complete += 1
            elif t_ == "ABORTED":
                aborts += 1
        except Exception:
            pass

    return {
        "_meta": {
            "schema":    "acg/dense-token · §0",
            "updatedAt": ts,
            "source":    "guild/web/scripts/api/build-runtime-tags.py",
            "about":     "Live runtime state of the ACG enterprise — regen on every build"
        },
        "sys": {
            "startedAt":  tag(ts, "good", "DateTime"),
            "buildAt":    tag(ts, "good", "DateTime"),
            "apiVersion": tag("1.0", "good", "String"),
        },
        "enterprise": {
            "paperCount":    tag(count(conn, "SELECT COUNT(*) FROM papers"),        "good", "Counter"),
            "memberCount":   tag(count(conn, "SELECT COUNT(*) FROM members"),       "good", "Counter"),
            "programCount":  tag(count(conn, "SELECT COUNT(*) FROM programs"),      "good", "Counter"),
            "runCount":      tag(count(conn, "SELECT COUNT(*) FROM packml_runs"),   "good", "Counter"),
            "tagEdges":      tag(count(conn, "SELECT COUNT(*) FROM paper_tags"),    "good", "Counter"),
            "authoredLinks": tag(count(conn, "SELECT COUNT(*) FROM member_papers"), "good", "Counter"),
        },
        "catalog": {
            "latestPaperDate": tag(scalar(conn, "SELECT MAX(publication_date) FROM papers", ""), "good", "DateTime"),
            "typeBreakdown":   tag({row[0]: row[1] for row in conn.execute(
                "SELECT status, COUNT(*) FROM papers GROUP BY status"
            )}, "good", "JSON"),
        },
        "pipeline": {
            "lastCompleteCount": tag(last_complete, "good", "Counter"),
            "lastAbortedCount":  tag(aborts,        "good" if aborts == 0 else "bad", "Counter"),
            "stateFileCount":    tag(len(state_files), "good", "Counter"),
        },
        "identity": {
            "host":       tag("aicraftspeopleguild.github.io", "good", "String"),
            "repoUrl":    tag("github.com/aicraftspeopleguild/aicraftspeopleguild.github.io", "good", "String"),
            "deployMode": tag("github-pages-static", "good", "String"),
        }
    }

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    conn = acgdb.connect()
    try:
        tags = build_tags(conn)
    finally:
        conn.close()
    OUT.write_text(json.dumps(tags, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[runtime-tags] wrote {OUT.relative_to(REPO)}")
    print(f"  enterprise: {tags['enterprise']['paperCount']['value']} papers, "
          f"{tags['enterprise']['memberCount']['value']} members, "
          f"{tags['enterprise']['runCount']['value']} PackML runs")

if __name__ == "__main__":
    with Process(
        "api--build-runtime-tags_py",
        pre_checks=[path_exists(REPO / "guild" / "Enterprise" / "L4" / "database" / "acg.db")],
        post_checks=[path_exists(OUT)],
    ):
        main()
