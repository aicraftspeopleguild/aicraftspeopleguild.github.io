#!/usr/bin/env python3
"""
debug-server.py — Local debug API server for the ACG repo.

Serves debug.html at / and exposes the acg CLI as a REST API.
Python stdlib only — no dependencies.

Usage:
  python debug-server.py [port]   (default: 7070)

Routes:
  GET  /                        → debug.html
  GET  /api/tools               → list all Tool instances
  POST /api/run                 → run a tool  { tool_id, inputs }
  GET  /api/logs[?tool=X&n=50]  → read JSONL logs (or list log dirs)
  GET  /api/db                  → docs.db summary (no doc list)
  GET  /api/db/broken           → broken_local_refs list
"""
import json, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent

for _candidate in (
    HERE / "guild" / "Enterprise" / "L2" / "lib",
    HERE / "guild" / "Enterprise" / "L2" / "lib",
):
    if (_candidate / "tool_runner.py").exists():
        sys.path.insert(0, str(_candidate))
        break

from tool_runner import load_tool, list_tools, run_with_logger

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 7070


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default access log; we print minimal output instead

    # ── helpers ────────────────────────────────────────────────────

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _static(self, rel: str, mime: str = "text/html; charset=utf-8"):
        f = HERE / rel
        if not f.exists():
            self.send_response(404)
            self.end_headers()
            return
        body = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type",   mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── OPTIONS (preflight) ────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    # ── GET ────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        route  = parsed.path
        qs     = parse_qs(parsed.query)

        # ── static UI ──────────────────────────────────────────────
        if route in ("/", "/debug.html"):
            self._static("debug.html")
            return

        # ── /api/tools ─────────────────────────────────────────────
        if route == "/api/tools":
            tools = []
            for t in list_tools():
                p = t["parameters"]
                tools.append({
                    "id":          p["id"],
                    "name":        p.get("name", p["id"]),
                    "description": p.get("description", ""),
                    "category":    p.get("category", ""),
                    "inputs":      p.get("inputs", []),
                    "tags":        p.get("tags", []),
                    "adapters":    p.get("adapters", []),
                })
            self._json(200, {"tools": tools})
            return

        # ── /api/logs ──────────────────────────────────────────────
        if route == "/api/logs":
            log_root = HERE / "guild" / "Enterprise" / "L2" / "logs"
            tool_id  = (qs.get("tool") or [None])[0]
            n        = int((qs.get("n") or ["50"])[0])

            if not tool_id:
                dirs = sorted(p.name for p in log_root.iterdir() if p.is_dir()) \
                       if log_root.exists() else []
                self._json(200, {"log_dirs": dirs})
                return

            log_dir = log_root / tool_id.replace(":", "-")
            files   = sorted(log_dir.glob("*.jsonl")) if log_dir.exists() else []
            if not files:
                self._json(200, {"tool": tool_id, "records": []})
                return

            records = []
            for raw in files[-1].read_text(encoding="utf-8").splitlines()[-n:]:
                try:
                    records.append(json.loads(raw))
                except json.JSONDecodeError:
                    pass
            self._json(200, {"tool": tool_id, "file": files[-1].name, "records": records})
            return

        # ── /api/db ────────────────────────────────────────────────
        if route == "/api/db":
            db_file = HERE / "docs.db"
            if not db_file.exists():
                self._json(404, {"error": "docs.db not found"})
                return
            db = json.loads(db_file.read_text(encoding="utf-8"))
            summary = {k: v for k, v in db.items() if k != "docs"}
            # replace index lists with counts so the payload stays small
            summary["indexes"] = {
                k: (len(v) if isinstance(v, list) else v)
                for k, v in db.get("indexes", {}).items()
            }
            self._json(200, summary)
            return

        # ── /api/db/broken ─────────────────────────────────────────
        if route == "/api/db/broken":
            db_file = HERE / "docs.db"
            if not db_file.exists():
                self._json(404, {"error": "docs.db not found"})
                return
            db   = json.loads(db_file.read_text(encoding="utf-8"))
            refs = db.get("indexes", {}).get("broken_local_refs", [])
            self._json(200, {"count": len(refs), "broken_local_refs": refs})
            return

        self._json(404, {"error": f"unknown route: {route}"})

    # ── POST ───────────────────────────────────────────────────────

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            self._json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length)) if length else {}
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid JSON body"})
            return

        tool_id = body.get("tool_id", "").strip()
        inputs  = body.get("inputs") or {}

        if not tool_id:
            self._json(400, {"error": "tool_id required"})
            return
        if not isinstance(inputs, dict):
            self._json(400, {"error": "inputs must be an object"})
            return

        try:
            tool = load_tool(tool_id)
        except FileNotFoundError as exc:
            self._json(404, {"error": str(exc)})
            return

        try:
            result = run_with_logger(tool, inputs)
            print(f"  ran {tool_id!r}  ok={result.get('ok')}")
            self._json(200, result)
        except Exception as exc:
            self._json(500, {"error": str(exc)})


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"ACG debug server → http://localhost:{PORT}/")
    print("Ctrl-C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
