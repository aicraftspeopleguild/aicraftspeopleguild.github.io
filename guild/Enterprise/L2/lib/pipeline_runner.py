"""
pipeline_runner — execute a Pipeline UDT sequentially. For each step:

  1. write `<ns>.step.<i>.status`  = RUNNING   (emits on_transition)
  2. invoke step.tool_id via run_with_logger
  3. write `<ns>.step.<i>.status`  = COMPLETE or FAILED
     write `<ns>.step.<i>.duration_ms` = elapsed
     write `<ns>.step.<i>.rc`       = return-code
  4. write `<ns>.status`           = overall state (RUNNING/COMPLETE/FAILED)

Every tag-write flows through tag_state.write → tag_history, and each
value-change automatically fires state_machine.fire_event so Script UDTs
can subscribe to step-level transitions.
"""
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

LIB = Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))
from tool_runner import load_tool, run_with_logger
from tag_state import write as tag_write, read as tag_read
import state_machine  # for fire_event
import state_db


def _iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

REPO = Path(__file__).resolve().parents[4]
PIPELINES_DIR = REPO / "guild" / "Enterprise" / "L3" / "automation" / "instances"


def load_pipeline(pipeline_id: str) -> dict:
    # match by parameters.id, not filename
    for f in sorted(PIPELINES_DIR.glob("*.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if doc.get("udtType") == "Pipeline" and doc.get("parameters", {}).get("id") == pipeline_id:
            return doc
    raise FileNotFoundError(f"no Pipeline UDT with id='{pipeline_id}' in {PIPELINES_DIR}")


def _emit_transition(tag: str, prev: str, new: str) -> None:
    """Let Scripts react to a status transition."""
    try:
        state_machine.fire_event(tag=tag, from_state=prev or "", to_state=new)
    except Exception:
        pass  # never let script handlers break the pipeline


def _write_status(tag: str, new: str) -> None:
    prev = tag_read(tag).get("value")
    tag_write(tag, new)
    if prev != new:
        _emit_transition(tag, prev or "IDLE", new)


def run(id: str = "", dry_run: str = "") -> dict:
    """Execute Pipeline with parameters.id==id. dry_run='1' skips the tool call."""
    dry = str(dry_run).lower() in ("1", "true", "yes", "y")
    pipe = load_pipeline(id)
    p    = pipe["parameters"]
    ns   = pipe.get("tags", {}).get("namespace") or f"pipeline.{p['id']}"
    on_fail = (p.get("on_fail") or "abort").lower()
    steps = p.get("steps") or []

    pipe_status_tag = f"{ns}.status"
    _write_status(pipe_status_tag, "RUNNING")
    run_id   = f"pipeline:{p['id']}:{int(time.time()*1000)}"
    started  = time.time()
    started_at = _iso()

    results = []
    overall_ok = True
    for i, step in enumerate(steps, start=1):
        sid   = step.get("id") or f"step-{i:02d}"
        sns   = f"{ns}.step.{i:02d}"
        tid   = step.get("tool_id")
        ins   = step.get("inputs") or {}
        stag  = f"{sns}.status"

        _write_status(stag, "RUNNING")
        tag_write(f"{sns}.id",      sid)
        tag_write(f"{sns}.tool_id", tid)

        started = time.time()
        entry = {"index": i, "id": sid, "tool_id": tid, "ok": False}
        if dry:
            entry["ok"] = True
            entry["note"] = "dry-run, skipped"
        else:
            try:
                tool = load_tool(tid) if tid else None
                if tool is None:
                    entry["error"] = f"no Tool UDT for '{tid}'"
                else:
                    outcome = run_with_logger(tool, ins)
                    entry["ok"] = bool(outcome.get("ok"))
                    entry["rc"] = outcome.get("rc")
                    if outcome.get("stderr"): entry["stderr_tail"] = outcome["stderr"][-400:]
            except Exception as e:
                entry["error"] = str(e)

        dur_ms = int((time.time() - started) * 1000)
        tag_write(f"{sns}.duration_ms", dur_ms)
        tag_write(f"{sns}.rc",          entry.get("rc"))

        _write_status(stag, "COMPLETE" if entry["ok"] else "FAILED")
        results.append(entry)

        if not entry["ok"]:
            overall_ok = False
            if (step.get("on_fail") or on_fail) == "abort":
                break

    _write_status(pipe_status_tag, "COMPLETE" if overall_ok else "FAILED")

    ended_at = _iso()
    duration = time.time() - started
    try:
        state_db.log_pipeline_run(
            run_id=run_id, pipeline_id=p["id"],
            ok=overall_ok, steps_total=len(steps), steps_run=len(results),
            started_at=started_at, ended_at=ended_at, duration_s=duration,
            detail={"dry_run": dry, "results": results},
        )
        if not overall_ok:
            failed = [r for r in results if not r.get("ok")]
            state_db.raise_fault(
                kind="pipeline_abort", severity="error",
                tag=pipe_status_tag,
                message=f"pipeline {p['id']} failed at step {len(results)}/{len(steps)}",
                detail={"run_id": run_id, "failed_steps": failed[:5]},
            )
    except Exception:
        pass

    return {
        "ok": overall_ok,
        "pipeline": p["id"],
        "run_id":   run_id,
        "namespace": ns,
        "steps_total": len(steps),
        "steps_run":   len(results),
        "results":     results,
    }


def list_pipelines() -> dict:
    out = []
    for f in sorted(PIPELINES_DIR.glob("*.json")):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if doc.get("udtType") == "Pipeline":
            p = doc.get("parameters", {})
            out.append({"id": p.get("id"), "name": p.get("name"), "steps": len(p.get("steps") or [])})
    return {"ok": True, "count": len(out), "pipelines": out}
