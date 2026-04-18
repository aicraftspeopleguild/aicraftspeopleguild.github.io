"""
build_script_tools — scan guild/Enterprise/L3/scripts for every *.py / *.sh /
*.js executable and create a Tool UDT instance wrapping it. Idempotent:
skips scripts that already have a Tool UDT pointing at them.

Tool id derivation:
    script:<relative-subdir>:<stem>
  e.g. guild/Enterprise/L3/scripts/apps/build-whitepaper-apps.py
       -> id = script:apps:build-whitepaper-apps
"""
import json
from pathlib import Path

REPO        = Path(__file__).resolve().parents[4]
SCRIPTS_DIR = REPO / "guild" / "Enterprise" / "L3" / "scripts"
TOOLS_DIR   = REPO / "guild" / "Enterprise" / "L3" / "tools" / "instances"

LANG_EXT = {".py": "python", ".sh": "bash", ".js": "node"}


def _existing_entries() -> set:
    out = set()
    for f in TOOLS_DIR.glob("*.json"):
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        entry = doc.get("parameters", {}).get("entry") or ""
        path = entry.split(":", 1)[0]
        if path:
            out.add(path)
    return out


def build() -> dict:
    existing = _existing_entries()
    created = skipped = 0
    new_tools = []
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    for p in sorted(SCRIPTS_DIR.rglob("*")):
        if not p.is_file():                     continue
        if p.suffix not in LANG_EXT:            continue
        if p.name.startswith(("README", ".")):  continue

        rel = p.relative_to(REPO).as_posix()
        if rel in existing:
            skipped += 1
            continue

        sub_parts = p.relative_to(SCRIPTS_DIR).parent.parts
        sub = ":".join(sub_parts) if sub_parts else "root"
        tool_id = f"script:{sub}:{p.stem}" if sub != "root" else f"script:{p.stem}"
        file_id = tool_id.replace(":", "-")
        out = {
            "udtType": "Tool",
            "parameters": {
                "id":          tool_id,
                "name":        f"script · {p.stem}",
                "description": f"Auto-wrapped script {rel}. Invoked via the state-machine pipeline.",
                "category":    "script",
                "entry":       rel,
                "language":    LANG_EXT[p.suffix],
                "inputs":      [],
                "outputs":     [{"name":"stdout","type":"text"}],
                "adapters":    ["CliAdapter", "LoggerWrapper"],
                "tags":        ["script", "auto-wrap", sub if sub != "root" else p.stem],
            },
            "tags": {"id": file_id, "schema_version": "1.0.0"},
        }
        (TOOLS_DIR / f"{file_id}.json").write_text(
            json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        created += 1
        new_tools.append(tool_id)

    return {
        "ok":       True,
        "created":  created,
        "skipped":  skipped,
        "new_ids":  new_tools[:25],
    }
