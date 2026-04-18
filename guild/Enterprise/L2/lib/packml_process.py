"""PackML Process context manager — state machine wrapping a build step."""
import json, time, uuid, traceback
from datetime import datetime, timezone
from pathlib import Path
try:
    from .packml_states import (IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE,
                                ABORTING, ABORTED, HELD)
    from .packml_checks import CheckFailed
except ImportError:
    # When loaded via sys.path (lib/ directly on path), siblings are
    # top-level modules — fall back to absolute imports.
    from packml_states import (IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE,
                               ABORTING, ABORTED, HELD)
    from packml_checks import CheckFailed

# File at guild/web/scripts/lib/packml_process.py
# parents[0]=lib, parents[1]=scripts, parents[2]=web, parents[3]=guild
STATE_DIR = Path(__file__).resolve().parents[3] / "Enterprise" / "L2" / "state"

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class Process:
    """Context manager. See docs/engineering/standards/packml.md for states."""

    def __init__(self, program_id, pre_checks=None, post_checks=None, verbose=True):
        self.program_id = program_id
        self.run_id = f"{int(time.time())}-{uuid.uuid4().hex[:6]}"
        self.pre_checks = pre_checks or []
        self.post_checks = post_checks or []
        self.verbose = verbose
        self.state = IDLE
        self.started_at = self.ended_at = self.terminal = None
        self.start_ts = None
        self.transitions = []
        self.pre_check_results = {}
        self.post_check_results = {}
        self.error = None

    def _transition(self, new_state, note=""):
        self.transitions.append({"state": new_state, "at": _now(), "note": note})
        if self.verbose:
            tag = f" ({note})" if note else ""
            print(f"  [packml] {self.program_id}: {self.state} -> {new_state}{tag}")
        self.state = new_state

    def _run_checks(self, checks, results):
        ok_all = True
        for c in checks:
            name = getattr(c, "__name__", repr(c))
            try:
                ok = c()
                results[name] = {"ok": ok is not False, "note": ""}
                if ok is False:
                    ok_all = False
            except CheckFailed as e:
                results[name] = {"ok": False, "note": str(e)}
                ok_all = False
            except Exception as e:
                results[name] = {"ok": False, "note": f"{type(e).__name__}: {e}"}
                ok_all = False
        return ok_all

    def __enter__(self):
        self.started_at = _now()
        self.start_ts = time.time()
        self._transition(STARTING, "running pre_checks")
        if not self._run_checks(self.pre_checks, self.pre_check_results):
            self._transition(HELD, "pre_checks failed")
            self.terminal = HELD
            self._write_state()
            raise CheckFailed(f"{self.program_id}: pre_checks failed")
        self._transition(EXECUTE, "work starting")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._transition(ABORTING, f"exception: {exc_type.__name__}")
            self.error = f"{exc_type.__name__}: {exc_val}\n{''.join(traceback.format_tb(exc_tb))}"
            self._transition(ABORTED, "run failed")
            self.terminal = ABORTED
        else:
            self._transition(COMPLETING, "running post_checks")
            if self._run_checks(self.post_checks, self.post_check_results):
                self._transition(COMPLETE, "all checks ok")
                self.terminal = COMPLETE
            else:
                self._transition(ABORTING, "post_checks failed")
                self.error = "post_checks failed"
                self._transition(ABORTED, "post-check failure")
                self.terminal = ABORTED
        self.ended_at = _now()
        self._write_state()
        return False

    def _write_state(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        duration = f"{time.time() - self.start_ts:.3f}" if self.start_ts else ""
        inst = {
            "udtType": "PackMLState",
            "parameters": {
                "program_id": self.program_id,
                "run_id": self.run_id,
                "started_at": self.started_at,
                "ended_at": self.ended_at,
                "terminal": self.terminal,
                "transitions": self.transitions,
                "pre_check_results": self.pre_check_results,
                "post_check_results": self.post_check_results,
                "error": self.error,
            },
            "tags": {
                "id": f"{self.program_id}-{self.run_id}",
                "duration_s": duration,
                "schema_version": "1.0.0",
            }
        }
        (STATE_DIR / f"{self.program_id}.state.json").write_text(
            json.dumps(inst, indent=2), encoding="utf-8")
