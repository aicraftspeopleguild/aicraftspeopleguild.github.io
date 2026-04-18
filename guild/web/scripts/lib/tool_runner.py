"""
Tool runner: load a Tool UDT instance and invoke it with CLI/API/logger wrappers.
"""
import importlib.util, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
TOOLS_DIR = REPO / "guild" / "Enterprise" / "L3" / "tools" / "instances"
LOG_ROOT  = REPO / "guild" / "Enterprise" / "L2" / "logs"

def _now_iso(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def _today():   return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def load_tool(tool_id: str) -> dict:
    """Find a Tool instance by id."""
    f = TOOLS_DIR / f"{tool_id.replace(':','-')}.json"
    if not f.exists():
        raise FileNotFoundError(f"no Tool instance for '{tool_id}' at {f}")
    return json.loads(f.read_text(encoding="utf-8"))

def list_tools() -> list:
    items = []
    for f in TOOLS_DIR.glob("*.json"):
        doc = json.loads(f.read_text(encoding="utf-8"))
        if doc.get("udtType") == "Tool" and doc.get("parameters", {}).get("id"):
            items.append(doc)
    return sorted(items, key=lambda t: t["parameters"]["id"])

def _invoke(tool: dict, inputs: dict) -> dict:
    """Run the Tool entry with given inputs. Returns dict with stdout/returncode."""
    p = tool["parameters"]
    entry = p["entry"]
    lang  = p["language"]
    category = p.get("category", "")
    api = p.get("api") or {}

    if category == "query" and (api.get("static") or entry.endswith(".json")):
        f = REPO / entry
        if not f.exists():
            return {"ok": False, "rc": 2, "stderr": f"static entry not found: {entry}\n", "stdout": ""}
        return {"ok": True, "rc": 0, "stdout": f.read_text(encoding="utf-8"), "stderr": ""}

    cmd = None
    if lang == "python":
        if ":" in entry:  # module:callable
            mod_path, fn_name = entry.split(":")
            full_path = REPO / mod_path
            spec = importlib.util.spec_from_file_location("tool_mod", full_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result = getattr(mod, fn_name)(**inputs)
            return {"ok": True, "result": result}
        cmd = [sys.executable, str(REPO / entry)]
    elif lang == "node":
        cmd = ["node", str(REPO / entry)]
    elif lang == "bash":
        cmd = ["bash", str(REPO / entry)]
    env = os.environ.copy()
    for k, v in (inputs or {}).items():
        env[f"ACG_ARG_{k.upper()}"] = str(v)
    r = subprocess.run(cmd, env=env, cwd=REPO, capture_output=True, text=True)
    return {"ok": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr, "rc": r.returncode}

def run_with_logger(tool: dict, inputs: dict) -> dict:
    """Invoke tool, emit one JSONL record per call."""
    tid = tool["parameters"]["id"]
    log_dir = LOG_ROOT / tid.replace(":", "-")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{_today()}.jsonl"
    start = time.time()
    started_at = _now_iso()
    result = None
    try:
        result = _invoke(tool, inputs or {})
        return result
    finally:
        duration = time.time() - start
        rec = {
            "tool":       tid,
            "started_at": started_at,
            "ended_at":   _now_iso(),
            "duration_s": round(duration, 3),
            "inputs":     inputs or {},
            "ok":         bool(result and result.get("ok")),
            "rc":         result.get("rc") if result else None,
        }
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
