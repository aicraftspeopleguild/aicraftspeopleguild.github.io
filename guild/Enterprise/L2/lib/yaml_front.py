"""YAML frontmatter writer for extracted markdown originals."""
import re

def yaml_value(v) -> str:
    """Serialize a scalar for a YAML frontmatter line."""
    if v is None:
        return '""'
    s = str(v)
    if re.search(r"[:'\"\n]", s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s

def frontmatter(d: dict) -> str:
    """Render a dict as `---\nkey: value\n---\n` YAML front-matter."""
    lines = ["---"]
    for k, v in d.items():
        if v is None or (isinstance(v, list) and not v):
            continue
        if isinstance(v, list):
            if all(isinstance(x, str) for x in v):
                lines.append(f"{k}: [{', '.join(yaml_value(x) for x in v)}]")
            else:
                lines.append(f"{k}:")
                for x in v:
                    lines.append(f"  - {yaml_value(x)}")
        else:
            lines.append(f"{k}: {yaml_value(v)}")
    lines.append("---\n")
    return "\n".join(lines)
