# acg-mcp · Model Context Protocol server for the ACG control plane

`bin/acg-mcp.py` is a zero-dep (stdlib-only) MCP server that exposes
the GH-Issues tag DB, state-machine runner, and control-deck action
catalogue through the standard MCP tool schema. Any MCP-capable
client (Claude Desktop, Claude Code, the `mcp` CLI, custom agents) can
read/write tags, fire state-machine events, and invoke `cmd:*`
actions — the same things the README buttons do — through typed tool
calls.

## Transport

Standard MCP stdio transport: newline-delimited JSON-RPC 2.0 over
stdin/stdout. `stderr` is reserved for human-readable diagnostics.
utf-8 is forced on startup so Windows consoles don't drop emoji.

## Tools

| tool           | purpose                                                       |
|----------------|---------------------------------------------------------------|
| `tag_read`     | Read a tag from the GH-Issues tag DB                          |
| `tag_write`    | Upsert a tag value (requires `GITHUB_TOKEN`)                  |
| `list_tags`    | Enumerate every open `tag:*` issue                            |
| `fire_event`   | Inject a state-machine event, get matched + executed scripts  |
| `list_scripts` | Every StateMachineScript / Script UDT, optionally filtered    |
| `list_actions` | The control-deck action catalogue                             |
| `cmd_action`   | Invoke a cmd action by id (files a `cmd:<id>` issue)          |
| `site_base`    | The public Pages URL for the current repo                     |
| `peek_api`     | GET a public L4 API endpoint                                  |

Every tool returns `{content: [{type:"text", text:"<json>"}]}` per
MCP conventions.

## Install · Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "acg": {
      "command": "python",
      "args": ["<ABSOLUTE-PATH>/bin/acg-mcp.py"],
      "env": { "GITHUB_TOKEN": "ghp_..." }
    }
  }
}
```

Restart Claude Desktop. You should see `acg` in the 🔌 tools list.

## Install · Claude Code

```
claude mcp add acg -- python "<ABSOLUTE-PATH>/bin/acg-mcp.py"
# then set the token as an env var or add it to the .mcp.json entry
```

## Install · stdio from any agent

Launch the process with the working dir set to the repo root. The
server reads one JSON request per line and writes one JSON response
per line.

```
python bin/acg-mcp.py
```

## Example session

Drive the server manually with `printf | python`:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test","version":"0"}}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"tag_read","arguments":{"path":"demo.heartbeat"}}}' \
  | python bin/acg-mcp.py
```

Reply (abbreviated):

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","serverInfo":{"name":"acg","version":"0.1.0"},"capabilities":{"tools":{"listChanged":false}}}}
{"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"{\"ok\":true,\"path\":\"demo.heartbeat\",\"value\":1776509355,...}"}]}}
```

## Relationship to the rest of the stack

| MCP call         | What it really does                                                   |
|------------------|-----------------------------------------------------------------------|
| `tag_read`       | `gh_tag.read(path)` — HTTP GET on `/repos/<org>/issues?labels=tag`    |
| `tag_write`      | `gh_tag.write(...)` — POST/PATCH issue + comment (needs token)        |
| `fire_event`     | `state_machine.fire_event(...)` — runs each matched Tool UDT          |
| `list_scripts`   | `state_machine.load_scripts()`                                        |
| `list_actions`   | reads `guild/apps/control-deck/actions/*.json`                        |
| `cmd_action`     | POSTs a `cmd:*` issue; the `cmd` workflow runs the matching action   |

## Security

- All writes require `GITHUB_TOKEN` (or `gh auth token`). Without one,
  `tag_write` and `cmd_action` return `{ok:false, reason:"no PAT"}`.
- The server never prints the token.
- Reads are anonymous and rate-limited to 60 req/hr per IP by GitHub.
