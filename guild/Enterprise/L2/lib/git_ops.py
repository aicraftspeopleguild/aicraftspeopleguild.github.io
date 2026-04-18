"""
git_ops — thin read-only wrapper around git, invoked by Tool UDT instances.

Every function returns a JSON-serializable dict. The PackML state machine
around git lives in guild/Enterprise/L2/scada/programs/git/state-map.json:
    IDLE      → clean tree (no staged, no unstaged, no untracked)
    RUNNING   → working-tree changes pending
    HOLD      → staged changes awaiting commit
    COMPLETE  → HEAD ahead of upstream / push pending
    ABORTED   → merge conflict or detached-HEAD
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]


def _git(*args) -> str:
    r = subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)
    return r.stdout.rstrip("\n") if r.returncode == 0 else ""


def status() -> dict:
    porcelain = _git("status", "--porcelain=v1", "--branch")
    lines = porcelain.splitlines() if porcelain else []
    branch_line = lines[0] if lines and lines[0].startswith("##") else ""
    entries = lines[1:] if branch_line else lines
    staged = [l for l in entries if l[:1].strip() and l[:1] not in ("?", " ")]
    unstaged = [l for l in entries if l[1:2].strip() and l[:1] != "?"]
    untracked = [l for l in entries if l.startswith("??")]
    conflict = any(l[:2] in ("UU", "AA", "DD") or "U" in l[:2] for l in entries)

    if conflict:
        state = "ABORTED"
    elif _git("rev-list", "@{u}..HEAD", "--count") and _git("rev-list", "@{u}..HEAD", "--count") != "0":
        state = "COMPLETE"
    elif staged:
        state = "HOLD"
    elif unstaged or untracked:
        state = "RUNNING"
    else:
        state = "IDLE"

    return {
        "ok": True,
        "branch": branch_line.replace("## ", "") if branch_line else "",
        "state": state,
        "counts": {
            "staged":    len(staged),
            "unstaged":  len(unstaged),
            "untracked": len(untracked),
        },
        "entries": entries[:40],
    }


def branches() -> dict:
    raw = _git("for-each-ref", "--format=%(refname:short)|%(objectname:short)|%(upstream:short)|%(HEAD)", "refs/heads/")
    out = []
    for line in raw.splitlines():
        name, sha, upstream, head = (line.split("|") + ["", "", ""])[:4]
        out.append({"name": name, "sha": sha, "upstream": upstream, "current": head == "*"})
    return {"ok": True, "branches": out, "count": len(out)}


def log(n: int = 10) -> dict:
    try:
        n = int(n)
    except Exception:
        n = 10
    fmt = "%h%x09%ad%x09%an%x09%s"
    raw = _git("log", f"-{n}", "--date=short", f"--pretty=format:{fmt}")
    commits = []
    for line in raw.splitlines():
        parts = line.split("\t", 3)
        if len(parts) == 4:
            commits.append({"sha": parts[0], "date": parts[1], "author": parts[2], "subject": parts[3]})
    return {"ok": True, "commits": commits, "count": len(commits)}


def diff_stat() -> dict:
    unstaged = _git("diff", "--stat")
    staged   = _git("diff", "--cached", "--stat")
    return {
        "ok": True,
        "unstaged": unstaged.splitlines()[-1] if unstaged else "clean",
        "staged":   staged.splitlines()[-1] if staged else "clean",
    }
