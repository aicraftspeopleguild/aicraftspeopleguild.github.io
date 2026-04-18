#!/usr/bin/env python3
"""
Scan guild/web/scripts/ for executable programs and generate:

  - guild/web/scripts/udts/instances/<id>.json   (one Program UDT per script)
  - guild/web/scripts/tags/index.json            (category -> program_ids)
  - guild/web/scripts/index.json                 (manifest)

Skips: udts/, tags/, state/, lib/, README.*.
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
# State logs moved to L2 SCADA layer (ISA-95)
STATE_DIR = HERE.parent.parent / "Enterprise" / "L2" / "state"
INSTANCES_DIR = HERE / "udts" / "instances"
TAGS_DIR = HERE / "tags"
TEMPLATE = HERE / "udts" / "templates" / "program.udt.json"

SKIP_DIRS = {"udts", "tags", "state", "lib", "__pycache__"}
SKIP_FILES = {"README.sh", "README.md"}

# Map directory name -> category
CATEGORY_BY_SUBDIR = {
    "white-papers":  "white-papers-pipeline",
    "members":       "members-pipeline",
    "components":    "components-pipeline",
    "pages":         "pages-pipeline",
    "apps":          "apps-pipeline",
    "docs":          "docs-pipeline",
}

def language_of(path):
    suf = path.suffix.lower()
    return {".py": "python", ".js": "node", ".sh": "bash"}.get(suf, "unknown")

def category_of(path):
    """Category from parent subdir or from the script's action verb."""
    rel = path.relative_to(HERE)
    if len(rel.parts) > 1:
        return CATEGORY_BY_SUBDIR.get(rel.parts[0], "misc")
    stem = path.stem
    for verb in ("build", "render", "extract", "regen", "test", "decompose",
                 "split", "fix"):
        if verb in stem:
            return f"{verb}-orchestrator"
    return "orchestrator"

def load_template_version():
    if TEMPLATE.exists():
        return json.loads(TEMPLATE.read_text(encoding="utf-8")).get("version", "1.0.0")
    return "1.0.0"

def read_state(program_id):
    """Read the last PackML state for this program if one exists."""
    f = STATE_DIR / f"{program_id}.state.json"
    if not f.exists():
        return {}
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        return {
            "state_log":     f"state/{program_id}.state.json",
            "last_state":    d.get("parameters", {}).get("terminal", "UNKNOWN"),
            "last_run_at":   d.get("parameters", {}).get("ended_at") or d.get("parameters", {}).get("started_at", ""),
            "last_duration": d.get("tags", {}).get("duration_s", ""),
        }
    except Exception:
        return {}

def find_scripts():
    for path in HERE.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in (".py", ".js", ".sh"):
            continue
        if path.name in SKIP_FILES:
            continue
        # Skip SKIP_DIRS anywhere in path
        if any(part in SKIP_DIRS for part in path.relative_to(HERE).parts[:-1]):
            continue
        # Skip this file itself
        if path == Path(__file__).resolve():
            continue
        # Skip the test scripts and library
        if path.name in ("build-programs.py",):
            continue
        yield path

def build():
    schema = load_template_version()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    INSTANCES_DIR.mkdir(parents=True, exist_ok=True)
    TAGS_DIR.mkdir(parents=True, exist_ok=True)

    programs = []
    by_category = {}

    for script in sorted(find_scripts()):
        rel_to_repo = script.relative_to(REPO).as_posix()
        rel_to_here = script.relative_to(HERE)
        pid = rel_to_here.as_posix().replace("/", "--").replace(".", "_")
        cat = category_of(script)
        lang = language_of(script)

        state_tags = read_state(pid)
        instance = {
            "udtType": "Program",
            "parameters": {
                "name":     script.stem.replace("-", " ").title(),
                "path":     rel_to_repo,
                "language": lang,
                "category": cat,
                "purpose":  _first_docstring_line(script),
                "inputs":   [],
                "outputs":  [],
                "depends_on": [],
                "pre_checks":  [],
                "post_checks": [],
                "tags":     [cat, lang],
            },
            "tags": {
                "id":             pid,
                "state_log":      state_tags.get("state_log", ""),
                "last_state":     state_tags.get("last_state", "IDLE"),
                "last_run_at":    state_tags.get("last_run_at", ""),
                "last_duration":  state_tags.get("last_duration", ""),
                "schema_version": schema,
            }
        }
        (INSTANCES_DIR / f"{pid}.json").write_text(
            json.dumps(instance, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        programs.append({"id": pid, "name": instance["parameters"]["name"],
                         "category": cat, "path": rel_to_repo,
                         "last_state": instance["tags"]["last_state"]})
        by_category.setdefault(cat, []).append(pid)

    # Tag catalog (one Tag UDT per category)
    tag_catalog = {"generated_at": now, "tags": {}}
    for cat, ids in sorted(by_category.items()):
        tag_catalog["tags"][cat] = {
            "udtType": "Tag",
            "parameters": {
                "name": cat, "label": cat.replace("-", " ").title(),
                "description": f"{cat} programs"
            },
            "tags": {
                "program_ids": sorted(ids),
                "count":       len(ids),
                "last_updated": now
            }
        }
    (TAGS_DIR / "index.json").write_text(
        json.dumps(tag_catalog, indent=2), encoding="utf-8"
    )

    # Manifest
    manifest = {
        "version": "1.0.0",
        "generated_at": now,
        "schema_version": schema,
        "counts": {"programs": len(programs), "categories": len(by_category)},
        "programs": programs
    }
    (HERE / "index.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(f"[programs] {len(programs)} programs, {len(by_category)} categories")
    for cat, ids in sorted(by_category.items()):
        print(f"  {cat:<30} {len(ids)} programs")

def _first_docstring_line(path):
    """Read the first non-trivial line of the docstring as a one-line purpose."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    # Python triple-quoted
    if '"""' in text:
        start = text.find('"""') + 3
        end = text.find('"""', start)
        if end > start:
            for line in text[start:end].splitlines():
                s = line.strip()
                if s and not s.startswith("#"):
                    return s[:200]
    # Shell/bash comment header
    for line in text.splitlines()[:10]:
        if line.startswith("#") and not line.startswith("#!"):
            s = line.lstrip("#").strip()
            if s:
                return s[:200]
    return ""

if __name__ == "__main__":
    build()
