"""
PackML (ISA-TR88.00.02) state machine wrapper for build pipeline programs.

Use as a context manager:

    from packml import Process

    with Process("extract-components",
                 pre_checks=[lambda: docs_dir.exists()],
                 post_checks=[lambda: len(list(out.glob("*.json"))) > 0]) as p:
        # your work here; raises abort the state machine
        extract()

States (core subset):
    IDLE      - initial
    STARTING  - pre_checks running
    EXECUTE   - user work running
    COMPLETING- post_checks running
    COMPLETE  - success, terminal
    ABORTING  - error being recorded
    ABORTED   - failure, terminal
    HELD      - checks failed pre-execute (terminal w/o run)

Each run writes a PackMLState instance to guild/web/scripts/state/<program>.state.json
listing every transition plus pre/post check outcomes. Re-running overwrites
the previous run log (one canonical state per program).
"""
import json, os, sys, time, traceback, uuid
from datetime import datetime, timezone
from pathlib import Path

# Resolve state dir relative to this module
LIB_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = LIB_DIR.parent
STATE_DIR = SCRIPTS_DIR / "state"

# Core PackML states we use
IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE, ABORTING, ABORTED, HELD, STOPPED = (
    "IDLE", "STARTING", "EXECUTE", "COMPLETING",
    "COMPLETE", "ABORTING", "ABORTED", "HELD", "STOPPED"
)

TERMINAL = {COMPLETE, ABORTED, HELD, STOPPED}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CheckFailed(Exception):
    """Raised by a check callable to signal failure; message is the reason."""


class Process:
    """Context manager running a program under PackML supervision."""

    def __init__(self, program_id, pre_checks=None, post_checks=None, verbose=True):
        self.program_id = program_id
        self.run_id = f"{int(time.time())}-{uuid.uuid4().hex[:6]}"
        self.pre_checks = pre_checks or []
        self.post_checks = post_checks or []
        self.verbose = verbose

        self.state = IDLE
        self.started_at = None
        self.start_ts = None
        self.ended_at = None
        self.terminal = None
        self.transitions = []
        self.pre_check_results = {}
        self.post_check_results = {}
        self.error = None

    # ── State transitions ────────────────────────────────────────────
    def _transition(self, new_state, note=""):
        self.transitions.append({"state": new_state, "at": _now(), "note": note})
        if self.verbose:
            print(f"  [packml] {self.program_id}: {self.state} -> {new_state}"
                  + (f" ({note})" if note else ""))
        self.state = new_state

    def _run_checks(self, checks, results):
        """Run a list of check callables; returns True if all pass."""
        all_ok = True
        for c in checks:
            name = getattr(c, "__name__", repr(c))
            try:
                ok = c()
                note = "" if (ok or ok is None) else str(ok)
                results[name] = {"ok": True if ok is not False else False, "note": note}
                if ok is False:
                    all_ok = False
            except CheckFailed as e:
                results[name] = {"ok": False, "note": str(e)}
                all_ok = False
            except Exception as e:
                results[name] = {"ok": False, "note": f"{type(e).__name__}: {e}"}
                all_ok = False
        return all_ok

    # ── Context manager ──────────────────────────────────────────────
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
            self._finalize()
            return False  # re-raise

        self._transition(COMPLETING, "running post_checks")
        if not self._run_checks(self.post_checks, self.post_check_results):
            self._transition(ABORTING, "post_checks failed")
            self.error = "post_checks failed: " + json.dumps(
                {k: v for k, v in self.post_check_results.items() if not v["ok"]}
            )
            self._transition(ABORTED, "finalized with failed post_checks")
            self.terminal = ABORTED
        else:
            self._transition(COMPLETE, "all checks ok")
            self.terminal = COMPLETE

        self._finalize()
        return False

    def _finalize(self):
        self.ended_at = _now()
        self._write_state()

    # ── Persistence ──────────────────────────────────────────────────
    def _write_state(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        duration = f"{time.time() - self.start_ts:.3f}" if self.start_ts else ""
        instance = {
            "udtType": "PackMLState",
            "parameters": {
                "program_id": self.program_id,
                "run_id":     self.run_id,
                "started_at": self.started_at,
                "ended_at":   self.ended_at,
                "terminal":   self.terminal,
                "transitions": self.transitions,
                "pre_check_results":  self.pre_check_results,
                "post_check_results": self.post_check_results,
                "error":      self.error,
            },
            "tags": {
                "id":             f"{self.program_id}-{self.run_id}",
                "duration_s":     duration,
                "schema_version": "1.0.0",
            }
        }
        out = STATE_DIR / f"{self.program_id}.state.json"
        out.write_text(json.dumps(instance, indent=2), encoding="utf-8")


# ── Prebuilt check helpers ──────────────────────────────────────────
def path_exists(path):
    """Return a check that asserts the given path exists."""
    p = Path(path)
    def _check():
        if not p.exists():
            raise CheckFailed(f"missing: {path}")
        return True
    _check.__name__ = f"path_exists({p.name})"
    return _check


def has_files(pattern, min_count=1):
    """Return a check that asserts <pattern> globs >= min_count files."""
    pat = Path(pattern)
    def _check():
        found = list(pat.parent.glob(pat.name)) if pat.parent.exists() else []
        if len(found) < min_count:
            raise CheckFailed(f"{pattern}: found {len(found)}, need >= {min_count}")
        return True
    _check.__name__ = f"has_files({pattern})"
    return _check
