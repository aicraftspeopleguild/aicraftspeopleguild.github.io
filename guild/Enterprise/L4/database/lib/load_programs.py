"""Load Program UDT instances + PackML run history into the database."""
import json
from pathlib import Path

REPO_DIR     = Path(__file__).resolve().parents[5]
INSTANCES    = REPO_DIR / "guild" / "Enterprise" / "L4" / "programs" / "instances"
STATE_DIR    = REPO_DIR / "guild" / "Enterprise" / "L2" / "state"

def load(conn):
    conn.execute("DELETE FROM program_tags")
    conn.execute("DELETE FROM packml_runs")
    conn.execute("DELETE FROM programs")

    count = 0
    for f in sorted(INSTANCES.glob("*.json")):
        pr = json.loads(f.read_text(encoding="utf-8"))
        if pr.get("udtType") != "Program":
            continue
        p = pr.get("parameters", {}); t = pr.get("tags", {})
        conn.execute("""
            INSERT INTO programs (id, name, path, language, category, purpose,
                                  last_state, last_run_at, last_duration, schema_version)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            t.get("id"), p.get("name"), p.get("path"), p.get("language"),
            p.get("category"), p.get("purpose"), t.get("last_state", "IDLE"),
            t.get("last_run_at"), t.get("last_duration"), t.get("schema_version"),
        ))
        for tag in p.get("tags") or []:
            conn.execute(
                "INSERT OR IGNORE INTO program_tags(program_id, tag) VALUES (?,?)",
                (t.get("id"), tag))
        count += 1

    # Each state log file currently holds the latest run. In a richer
    # future we'd append to a run history; for now, one row per program.
    for f in sorted(STATE_DIR.glob("*.state.json")):
        st = json.loads(f.read_text(encoding="utf-8"))
        p = st.get("parameters", {}); t = st.get("tags", {})
        conn.execute("""
            INSERT OR REPLACE INTO packml_runs (run_id, program_id, started_at,
                ended_at, terminal, duration_s, error,
                transitions_json, pre_checks_json, post_checks_json)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", (
            p.get("run_id"), p.get("program_id"), p.get("started_at"),
            p.get("ended_at"), p.get("terminal"), t.get("duration_s"), p.get("error"),
            json.dumps(p.get("transitions") or []),
            json.dumps(p.get("pre_check_results") or {}),
            json.dumps(p.get("post_check_results") or {}),
        ))
    conn.commit()
    return count
