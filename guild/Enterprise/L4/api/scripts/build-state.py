#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-state:on-state-change",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "pipeline.build.status",
#     "from": "*",
#     "to":   "COMPLETE"
#   },
#   "writes": ["api.state.json"]
# }
# @end-tag-event
"""
Write guild/Enterprise/L4/api/state.json — a public summary of state.db
that the repo-state-badge widget can fetch at runtime.
"""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))

import state_db  # noqa: E402

OUT = REPO / "guild" / "Enterprise" / "L4" / "api" / "state.json"


def main():
    summary = state_db.summary()
    faults  = state_db.list_faults(active_only="1")
    doc = {
        "summary":       summary,
        "faults_active": faults.get("faults") or [],
        "generated_at":  summary.get("last_event", {}).get("at") if summary.get("last_event") else None,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[state] wrote {OUT.relative_to(REPO)}  "
          f"tags={summary['tag_values']} events={summary['events']} "
          f"tool_runs={summary['tool_runs']}  faults_active={summary['faults_active']}")


if __name__ == "__main__":
    main()
