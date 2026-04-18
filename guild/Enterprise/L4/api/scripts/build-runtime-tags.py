#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-runtime-tags:on-state-change",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "state.db.updated",
#     "from": "*",
#     "to":   "CHANGED"
#   },
#   "writes": ["runtime.tags.json.rebuilt_at"]
# }
# @end-tag-event
"""
Build guild/Enterprise/L4/runtime/tags.json — Ignition-style live tags.

Catalog layout (matches the spec):

  CATALOG · health.json     papers · members · last build · api version
  ENTERPRISE · L4           paperCount memberCount programCount runCount
                            tagEdges authoredLinks
  PIPELINE · L3             complete · aborted · states
  IDENTITY · deploy         host · deployMode · sys.apiVersion · latestPaper

Sources: guild/Enterprise/L4/database/acg.db + L2/state/state.db +
L4/api/health.json. Regenerated every pipeline.build.status COMPLETE.
"""
import json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L4" / "database" / "lib"))

try:
    import db as acgdb  # L4 ERP store
except Exception:
    acgdb = None

STATE_DB = REPO / "guild" / "Enterprise" / "L2" / "state" / "state.db"
HEALTH   = REPO / "guild" / "Enterprise" / "L4" / "api" / "health.json"
OUT      = REPO / "guild" / "Enterprise" / "L4" / "runtime" / "tags.json"


def now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def tag(v, quality: str = "good", t: str = "String") -> dict:
    return {"value": v, "quality": quality, "type": t}


def _count(conn, sql):
    try:
        return conn.execute(sql).fetchone()[0]
    except Exception:
        return 0


def _scalar(conn, sql, default=None):
    try:
        r = conn.execute(sql).fetchone()
        return r[0] if r and r[0] is not None else default
    except Exception:
        return default


def build_tags() -> dict:
    ts = now_ms()

    # CATALOG — proxy health.json (source of truth for public counts)
    health = {}
    if HEALTH.exists():
        try:
            health = json.loads(HEALTH.read_text(encoding="utf-8"))
        except Exception:
            pass

    enterprise = {}
    catalog_extras = {}
    if acgdb is not None:
        try:
            conn = acgdb.connect()
        except Exception:
            conn = None
        if conn is not None:
            try:
                enterprise = {
                    "paperCount":    tag(_count(conn, "SELECT COUNT(*) FROM papers"),        "good", "Counter"),
                    "memberCount":   tag(_count(conn, "SELECT COUNT(*) FROM members"),       "good", "Counter"),
                    "programCount":  tag(_count(conn, "SELECT COUNT(*) FROM programs"),      "good", "Counter"),
                    "runCount":      tag(_count(conn, "SELECT COUNT(*) FROM packml_runs"),   "good", "Counter"),
                    "tagEdges":      tag(_count(conn, "SELECT COUNT(*) FROM paper_tags"),    "good", "Counter"),
                    "authoredLinks": tag(_count(conn, "SELECT COUNT(*) FROM member_papers"), "good", "Counter"),
                }
                catalog_extras["latestPaperDate"] = tag(
                    _scalar(conn, "SELECT MAX(publication_date) FROM papers", ""),
                    "good", "DateTime",
                )
                catalog_extras["latestPaperTitle"] = tag(
                    _scalar(conn, "SELECT title FROM papers ORDER BY publication_date DESC LIMIT 1", ""),
                    "good", "String",
                )
            finally:
                conn.close()

    # PIPELINE from state.db (primary) + L2/state/*.state.json (legacy)
    complete = aborted = states = 0
    if STATE_DB.exists():
        try:
            s = sqlite3.connect(str(STATE_DB))
            complete = _count(s, "SELECT COUNT(*) FROM pipeline_runs WHERE ok=1")
            aborted  = _count(s, "SELECT COUNT(*) FROM pipeline_runs WHERE ok=0")
            states   = _count(s, "SELECT COUNT(*) FROM events")
            s.close()
        except Exception:
            pass

    return {
        "_meta": {
            "schema":    "acg/dense-token · §0",
            "updatedAt": ts,
            "source":    "guild/Enterprise/L4/api/scripts/build-runtime-tags.py",
            "about":     "Live runtime state · CATALOG · ENTERPRISE · PIPELINE · IDENTITY"
        },
        "catalog": {
            "papers":     tag(health.get("paperCount"),  "good", "Counter"),
            "members":    tag(health.get("memberCount"), "good", "Counter"),
            "lastBuild":  tag(health.get("lastUpdated"), "good", "DateTime"),
            "apiVersion": tag(health.get("apiVersion"),  "good", "String"),
            **catalog_extras,
        },
        "enterprise": enterprise,
        "pipeline": {
            "complete": tag(complete, "good", "Counter"),
            "aborted":  tag(aborted,  "good" if aborted == 0 else "bad", "Counter"),
            "states":   tag(states,   "good", "Counter"),
        },
        "identity": {
            "host":        tag("aicraftspeopleguild.github.io", "good", "String"),
            "deployMode":  tag("github-pages-static",           "good", "String"),
            "apiVersion":  tag(health.get("apiVersion", "1.0"), "good", "String"),
            "latestPaper": catalog_extras.get("latestPaperTitle", tag("", "uncertain", "String")),
            "repoUrl":     tag("github.com/aicraftspeopleguild/aicraftspeopleguild.github.io", "good", "String"),
        },
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tags = build_tags()
    OUT.write_text(json.dumps(tags, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[runtime-tags] wrote {OUT.relative_to(REPO)}")
    print(f"  catalog:    papers={tags['catalog']['papers']['value']} members={tags['catalog']['members']['value']}")
    ent = ", ".join(f"{k}={v['value']}" for k, v in tags["enterprise"].items())
    print(f"  enterprise: {ent}")
    print(f"  pipeline:   complete={tags['pipeline']['complete']['value']} aborted={tags['pipeline']['aborted']['value']} states={tags['pipeline']['states']['value']}")


if __name__ == "__main__":
    main()
