"""
state_machine — the runner that makes Script UDT instances fire when their
triggers match an event. Equivalent to Ignition's Tag Change Scripts + Gateway
Events, built on the existing Tool UDT + run_with_logger layer.

Key entry points (both exposed as Tool UDTs):
  fire_event(tag, from_state, to_state) -> dict
      Inject an event manually. Returns a report with matched + executed scripts.
  tick() -> dict
      Poll git:state, detect transition since last snapshot, fire matching scripts.

State persistence lives at:
  guild/Enterprise/L2/state/sm-last.json   (last-seen tag values per tag)
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

LIB   = Path(__file__).resolve().parent
REPO  = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPO / "guild" / "Enterprise" / "L3" / "automation" / "instances"
STATE_FILE  = REPO / "guild" / "Enterprise" / "L2" / "state" / "sm-last.json"

sys.path.insert(0, str(LIB))
from tool_runner import load_tool, run_with_logger


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _script_file_to_tool_id(rel_path: str) -> str:
    """Mirror build_script_tools id derivation: script:<sub>:<stem>."""
    p = Path(rel_path)
    try:
        sub = p.relative_to(Path("guild/Enterprise/L3/scripts")).parent.parts
    except ValueError:
        sub = ()
    return f"script:{':'.join(sub)}:{p.stem}" if sub else f"script:{p.stem}"


def load_scripts() -> list:
    """Load every Script binding. Two sources:
      1. Script UDT JSON files under L3/automation/instances/
      2. script_events table in root tag.db (from @tag-event headers)
    Both normalize to the same shape consumed by _match / _fire."""
    out = []
    for f in sorted(SCRIPTS_DIR.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        if doc.get("udtType") != "Script":
            continue
        p = doc.get("parameters", {})
        if p.get("enabled", True):
            out.append(p)

    import sqlite3
    tag_db = REPO / "tag.db"
    if tag_db.exists():
        try:
            con = sqlite3.connect(str(tag_db))
            con.row_factory = sqlite3.Row
            tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "script_events" in tables:
                for row in con.execute("SELECT * FROM script_events WHERE enabled=1"):
                    rel = row["script_file"]
                    tool_id = row["action_tool_id"] or _script_file_to_tool_id(rel)
                    out.append({
                        "id":      row["id"],
                        "enabled": True,
                        "trigger": {
                            "kind": row["kind"] or "on_transition",
                            "tag":  row["listens_tag"],
                            "from": row["listens_from"],
                            "to":   row["listens_to"],
                        },
                        "action":       {"tool_id": tool_id, "inputs": {}},
                        "_source":      "script_events",
                        "_script_file": rel,
                    })
            con.close()
        except sqlite3.Error:
            pass
    return out


def _match(script: dict, event: dict) -> bool:
    """Does the event satisfy script.trigger?  '*' acts as a wildcard on from/to."""
    trig = script.get("trigger", {})
    if trig.get("kind") != event.get("kind"):
        return False
    if trig.get("tag") and trig["tag"] != event.get("tag"):
        return False
    if event["kind"] == "on_transition":
        f = trig.get("from")
        t = trig.get("to")
        if f and f != "*" and f != event.get("from"):
            return False
        if t and t != "*" and t != event.get("to"):
            return False
    return True


def _fire(script: dict) -> dict:
    action = script.get("action", {})
    tool_id = action.get("tool_id")
    inputs  = action.get("inputs") or {}
    try:
        tool = load_tool(tool_id)
    except FileNotFoundError as e:
        return {"script": script["id"], "ok": False, "error": str(e)}
    outcome = run_with_logger(tool, inputs)
    return {
        "script":  script["id"],
        "tool":    tool_id,
        "inputs":  inputs,
        "ok":      bool(outcome.get("ok")),
        "rc":      outcome.get("rc"),
    }


def fire_event(tag: str = "", from_state: str = "", to_state: str = "", kind: str = "on_transition") -> dict:
    """Inject an event. All args accepted as strings (for bin/acg key=value passing)."""
    event = {"kind": kind, "tag": tag, "from": from_state, "to": to_state, "at": _now_iso()}
    scripts = load_scripts()
    matched = [s for s in scripts if _match(s, event)]
    results = [_fire(s) for s in matched]
    # Persist the event so state.db has the full audit trail.
    try:
        import state_db  # noqa: WPS433
        state_db.log_event(
            kind=kind, tag=tag, from_state=from_state, to_state=to_state,
            source="fire_event", matched=len(matched),
            detail={"matched": [s["id"] for s in matched]},
        )
    except Exception:
        pass
    return {
        "ok": all(r.get("ok") for r in results) if results else True,
        "event":    event,
        "matched":  [s["id"] for s in matched],
        "executed": results,
        "total_scripts": len(scripts),
    }


def _load_last() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_last(data: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def tick() -> dict:
    """Poll git:state, detect transition vs last-seen, fire matching scripts, update snapshot."""
    import git_ops
    status = git_ops.status()
    now_state = status.get("state") or "UNKNOWN"
    last = _load_last()
    prev_state = last.get("git:state")
    transitions = []
    fired = []
    if prev_state and prev_state != now_state:
        ev = fire_event(tag="git:state", from_state=prev_state, to_state=now_state)
        transitions.append({"tag": "git:state", "from": prev_state, "to": now_state})
        fired = ev.get("executed", [])
    last["git:state"] = now_state
    last["git:state:last_tick_at"] = _now_iso()
    _save_last(last)
    return {
        "ok": True,
        "current_state": now_state,
        "prev_state": prev_state,
        "transitions": transitions,
        "fired": fired,
        "branch": status.get("branch"),
    }
