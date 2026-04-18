"""svg_build_all — run every SvgOrganism generator in tag.db and return a
report. Convenience wrapper around the per-widget build:*-svg Tools."""
import importlib.util, json, sqlite3, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
TAG_DB = REPO / "tag.db"


def build() -> dict:
    if not TAG_DB.exists():
        return {"ok": False, "error": "tag.db missing; run build:tag-dbs"}
    con = sqlite3.connect(str(TAG_DB))
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT id, body FROM udts WHERE udt_type='SvgOrganism' ORDER BY id"
    )]
    con.close()
    results = []
    for r in rows:
        try:
            body = json.loads(r["body"])
            if "$schema" in body:  # skip the UDT template itself
                continue
            entry = body.get("parameters", {}).get("entry")
            if not isinstance(entry, str) or not entry:
                continue
            full = REPO / entry
            spec = importlib.util.spec_from_file_location("svgmod", full)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "main"):
                mod.main()
                results.append({"id": r["id"], "ok": True, "entry": entry})
            else:
                results.append({"id": r["id"], "ok": False, "error": "no main()"})
        except Exception as e:
            results.append({"id": r["id"], "ok": False, "error": str(e)})
    return {"ok": all(x.get("ok") for x in results), "count": len(results), "results": results}
