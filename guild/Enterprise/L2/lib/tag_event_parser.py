"""
tag_event_parser — extract @tag-event JSON declarations from script files.

A script carries one or more declarations between `# @tag-event` and
`# @end-tag-event` markers. The lines in between are JSON (the comment
prefix `# ` is stripped). Example (Python):

    # @tag-event
    # {
    #   "id": "components-extract-on-build-start",
    #   "listens": {
    #     "kind": "on_transition",
    #     "tag": "pipeline.build.step.00.status",
    #     "from": "IDLE", "to": "RUNNING"
    #   },
    #   "reads":  ["docs.engineering.catalog"],
    #   "writes": ["components.count", "components.extracted_at"],
    #   "fires":  [{"tag": "pipeline.build.step.01.status", "to": "RUNNING"}]
    # }
    # @end-tag-event

parse_file(path) -> list of declaration dicts
parse_tree(root) -> list of (path, declaration) tuples
"""
import json
from pathlib import Path

START = "@tag-event"
END   = "@end-tag-event"


def _strip_comment(line: str, prefix: str) -> str:
    s = line.lstrip()
    if s.startswith(prefix):
        s = s[len(prefix):]
    if s.startswith(" "):
        s = s[1:]
    return s


def _comment_prefix_for(ext: str) -> str:
    if ext in (".py", ".sh", ".yml", ".yaml"):
        return "#"
    if ext in (".js", ".ts", ".css"):
        return "//"
    return "#"


def parse_file(path: Path) -> list:
    """Return all @tag-event declarations in the file."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception:
        return []
    prefix = _comment_prefix_for(Path(path).suffix.lower())
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.lstrip(prefix).strip() == START:
            i += 1
            body_lines = []
            while i < len(lines):
                cur = lines[i].strip()
                if cur.lstrip(prefix).strip() == END:
                    break
                body_lines.append(_strip_comment(lines[i], prefix))
                i += 1
            body = "\n".join(body_lines).strip()
            if body:
                try:
                    parsed = json.loads(body)
                    if isinstance(parsed, list):
                        out.extend(parsed)
                    else:
                        out.append(parsed)
                except Exception:
                    pass
        i += 1
    return out


def parse_tree(root: Path, exts=(".py", ".sh", ".js")) -> list:
    root = Path(root)
    hits = []
    for ext in exts:
        for f in root.rglob("*" + ext):
            for decl in parse_file(f):
                hits.append((f, decl))
    return hits
