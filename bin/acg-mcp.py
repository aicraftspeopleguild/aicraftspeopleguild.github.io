#!/usr/bin/env python3
"""
acg-mcp — Model Context Protocol server exposing the ACG control plane.

Lets an external agent read/write the GitHub-Issues tag DB, fire
state-machine events, list scripts, and invoke control-deck actions
through a typed tool schema — the same surface the README buttons
give a human.

Transport: stdio, newline-delimited JSON-RPC 2.0 (standard MCP stdio
transport). Zero dependencies — stdlib only.

Tools
-----
  tag_read(path)
  tag_write(path, value, type?, quality?, description?)
  list_tags()
  fire_event(tag, from_state?, to_state?, kind?)
  list_scripts(tag?)
  list_actions()
  cmd_action(id)         -- files an issue that the cmd workflow runs
  site_base()
  peek_api(url?)         -- HEAD-probe a public endpoint

Install
-------
Add to ~/.config/claude-desktop.json (or similar):
  {
    "mcpServers": {
      "acg": {
        "command": "python",
        "args": ["<REPO>/bin/acg-mcp.py"],
        "env": {"GITHUB_TOKEN": "ghp_..."}
      }
    }
  }

See docs/engineering/acg-mcp.md for full setup + examples.
"""
import io, json, os, sys, traceback
from pathlib import Path

# MCP stdio transport REQUIRES utf-8; Windows consoles default to cp1252
# which chokes on any emoji/unicode in tool output. Rewrap stdio before
# anything else touches it.
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  write_through=True, newline="")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  write_through=True, newline="")
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding="utf-8",
                                  newline="")
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))

import gh_tag  # noqa: E402
try:
    import site_base  # noqa: E402
except ImportError:
    site_base = None

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME      = "acg"
SERVER_VERSION   = "0.1.0"


# ─── helpers ────────────────────────────────────────────────────────

def _base() -> str:
    if site_base:
        return site_base.site_base()
    return "https://aicraftspeopleguild.github.io"


def _text_result(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def _json_result(obj) -> dict:
    return _text_result(json.dumps(obj, indent=2, ensure_ascii=False))


# ─── tool implementations ───────────────────────────────────────────

def tool_tag_read(args: dict) -> dict:
    path = args["path"]
    return _json_result(gh_tag.read(path))


def tool_tag_write(args: dict) -> dict:
    return _json_result(gh_tag.write(
        path=args["path"],
        value=args["value"],
        type=args.get("type", "String"),
        quality=args.get("quality", "good"),
        description=args.get("description", "written via acg-mcp"),
    ))


def tool_list_tags(args: dict) -> dict:
    out, page = [], 1
    while True:
        rsp = gh_tag._req("GET", f"/repos/{gh_tag.REPO}/issues?labels=tag&state=open&per_page=100&page={page}")
        if not isinstance(rsp, list) or not rsp:
            break
        for issue in rsp:
            title = issue.get("title") or ""
            if title.startswith("tag:"):
                out.append({"path": title[4:], "issue": issue.get("number")})
        if len(rsp) < 100:
            break
        page += 1
    return _json_result({"count": len(out), "tags": sorted(out, key=lambda x: x["path"])})


def tool_fire_event(args: dict) -> dict:
    from state_machine import fire_event
    return _json_result(fire_event(
        tag=args["tag"],
        from_state=args.get("from_state", "*"),
        to_state=args.get("to_state", "CHANGED"),
        kind=args.get("kind", "on_transition"),
    ))


def tool_list_scripts(args: dict) -> dict:
    from state_machine import load_scripts
    scripts = load_scripts()
    tag = args.get("tag")
    if tag:
        scripts = [s for s in scripts if (s.get("trigger") or {}).get("tag") == tag]
    slim = [{
        "id":         s.get("id"),
        "source":     s.get("_source"),
        "script":     s.get("_script_file"),
        "kind":       (s.get("trigger") or {}).get("kind"),
        "tag":        (s.get("trigger") or {}).get("tag"),
        "from":       (s.get("trigger") or {}).get("from"),
        "to":         (s.get("trigger") or {}).get("to"),
        "tool_id":    (s.get("action")  or {}).get("tool_id"),
    } for s in scripts]
    return _json_result({"count": len(slim), "scripts": slim})


def tool_list_actions(args: dict) -> dict:
    actions_dir = REPO / "guild" / "apps" / "control-deck" / "actions"
    out = []
    try:
        manifest = json.loads((actions_dir / "index.json").read_text(encoding="utf-8"))
    except Exception:
        return _json_result({"error": "no action manifest"})
    for fn in manifest.get("actions", []):
        try:
            doc = json.loads((actions_dir / fn).read_text(encoding="utf-8"))
            p = doc.get("parameters", {})
            out.append({
                "id":     p.get("id") or Path(fn).stem,
                "label":  p.get("label"),
                "title":  p.get("title"),
                "body":   (p.get("body") or "")[:200],
            })
        except Exception:
            continue
    return _json_result({"count": len(out), "actions": out})


def tool_cmd_action(args: dict) -> dict:
    actions_dir = REPO / "guild" / "apps" / "control-deck" / "actions"
    aid = args["id"]
    try:
        doc = json.loads((actions_dir / f"{aid}.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _json_result({"ok": False, "error": f"unknown action {aid!r}"})
    p = doc.get("parameters", {})
    title = p.get("title") or f"cmd:{aid}"
    body  = p.get("body")  or ""
    tok = gh_tag._token()
    if not tok:
        return _json_result({
            "ok": False,
            "reason": "no PAT / gh auth — cannot POST an issue",
            "title": title, "body": body,
            "hint": f"set GITHUB_TOKEN or run `gh auth login`",
        })
    rsp = gh_tag._req("POST", f"/repos/{gh_tag.REPO}/issues",
                      {"title": title, "body": body, "labels": ["cmd"]})
    return _json_result({"ok": True, "issue": rsp.get("number"), "title": title})


def tool_site_base(args: dict) -> dict:
    return _text_result(_base())


def tool_peek_api(args: dict) -> dict:
    import urllib.request
    url = args.get("url") or f"{_base()}/guild/Enterprise/L4/api/health.json"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            body = r.read().decode("utf-8", errors="replace")
        try:
            return _json_result({"url": url, "status": 200, "body": json.loads(body)})
        except json.JSONDecodeError:
            return _json_result({"url": url, "status": 200, "body_text": body[:4096]})
    except Exception as e:
        return _json_result({"url": url, "error": str(e)})


# ─── tool registry + schemas ────────────────────────────────────────

TOOLS = [
    {
        "name": "tag_read",
        "description": "Read a tag from the GitHub-Issues-backed ACG tag DB.",
        "inputSchema": {"type": "object", "required": ["path"],
            "properties": {"path": {"type": "string", "description": "tag path, e.g. demo.heartbeat"}}},
        "fn": tool_tag_read,
    },
    {
        "name": "tag_write",
        "description": "Upsert a tag value. Requires GITHUB_TOKEN.",
        "inputSchema": {"type": "object", "required": ["path", "value"],
            "properties": {
                "path":        {"type": "string"},
                "value":       {},
                "type":        {"type": "string", "enum": ["String","Counter","Number","Boolean","DateTime","JSON"]},
                "quality":     {"type": "string", "enum": ["good","uncertain","bad","stale"]},
                "description": {"type": "string"},
            }},
        "fn": tool_tag_write,
    },
    {
        "name": "list_tags",
        "description": "List every open tag:* issue in the repo.",
        "inputSchema": {"type": "object", "properties": {}},
        "fn": tool_list_tags,
    },
    {
        "name": "fire_event",
        "description": "Inject a state-machine event. Returns matched + executed scripts.",
        "inputSchema": {"type": "object", "required": ["tag"],
            "properties": {
                "tag":        {"type": "string"},
                "from_state": {"type": "string", "default": "*"},
                "to_state":   {"type": "string", "default": "CHANGED"},
                "kind":       {"type": "string", "default": "on_transition"},
            }},
        "fn": tool_fire_event,
    },
    {
        "name": "list_scripts",
        "description": "List every StateMachineScript / Script UDT in the runner, optionally filtered by listens_tag.",
        "inputSchema": {"type": "object", "properties": {"tag": {"type": "string"}}},
        "fn": tool_list_scripts,
    },
    {
        "name": "list_actions",
        "description": "List the control-deck action catalogue.",
        "inputSchema": {"type": "object", "properties": {}},
        "fn": tool_list_actions,
    },
    {
        "name": "cmd_action",
        "description": "Invoke a control-deck action by id (files a cmd:<id> issue the cmd workflow handles).",
        "inputSchema": {"type": "object", "required": ["id"],
            "properties": {"id": {"type": "string", "description": "e.g. bump-heartbeat / rebuild-svgs"}}},
        "fn": tool_cmd_action,
    },
    {
        "name": "site_base",
        "description": "Return the public Pages URL for whichever repo the code is hosted from.",
        "inputSchema": {"type": "object", "properties": {}},
        "fn": tool_site_base,
    },
    {
        "name": "peek_api",
        "description": "GET a public L4 API endpoint and return the JSON body (default: /api/health.json).",
        "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}},
        "fn": tool_peek_api,
    },
]

TOOL_INDEX = {t["name"]: t for t in TOOLS}


# ─── JSON-RPC framing ───────────────────────────────────────────────

def _reply(id_, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": id_}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _notify(method, params=None):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(req: dict) -> None:
    method = req.get("method")
    id_    = req.get("id")
    params = req.get("params") or {}

    if method == "initialize":
        _reply(id_, {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo":      {"name": SERVER_NAME, "version": SERVER_VERSION},
            "capabilities":    {"tools": {"listChanged": False}},
        })
        return

    if method in ("notifications/initialized", "initialized"):
        return  # no response expected

    if method == "tools/list":
        _reply(id_, {
            "tools": [
                {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
                for t in TOOLS
            ],
        })
        return

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        tool = TOOL_INDEX.get(name)
        if not tool:
            _reply(id_, None, {"code": -32601, "message": f"unknown tool {name!r}"})
            return
        try:
            _reply(id_, tool["fn"](args))
        except Exception as e:
            _reply(id_, {
                "content": [{"type": "text", "text": f"tool error: {type(e).__name__}: {e}\n{traceback.format_exc()}"}],
                "isError": True,
            })
        return

    if method == "ping":
        _reply(id_, {})
        return

    if id_ is not None:
        _reply(id_, None, {"code": -32601, "message": f"method not found: {method}"})


def main() -> int:
    # Keep stderr for diagnostics, stdout reserved for JSON-RPC only.
    print(f"[acg-mcp] ready  repo={gh_tag.REPO}  pid={os.getpid()}  tools={len(TOOLS)}", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            print(f"[acg-mcp] parse err: {e}  line={line[:120]!r}", file=sys.stderr)
            continue
        try:
            handle(req)
        except Exception as e:
            print(f"[acg-mcp] handler crashed: {e}\n{traceback.format_exc()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
