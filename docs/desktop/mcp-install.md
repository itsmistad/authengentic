# Install the MCP linter for the Chat tab

The MCP server adds one tool, `authengentic_lint`, and two prompts,
`authengentic-review` and `authengentic-rewrite`, to the Claude Desktop chat
surface. The chat surface has no post-write hook, so this tool is the only
mechanical check available there.

## Requirements

- `python3` on the machine. The linter needs it. macOS and most Linux ship it.
  Windows users install Python 3 first.
- Node 18 or later for the manual setup. The bundle carries its own Node runtime.

## Option A: the one-click bundle

```bash
./scripts/build-mcpb.sh
```

This writes `dist/authengentic.mcpb`. Open that file with Claude Desktop. The app
shows an install dialog. If `python3` is not on `PATH`, set its absolute path in
the bundle's **Python interpreter** field during install.

## Option B: a manual stdio server

Add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "authengentic": {
      "command": "node",
      "args": ["/absolute/path/to/authengentic/mcp/server/index.js"],
      "env": {
        "AUTHENGENTIC_PYTHON": ""
      }
    }
  }
}
```

Before the first run:

```bash
cd mcp
npm install --omit=dev
mkdir -p linter
cp ../evals/authengentic_lint.py ../evals/slop.tsv linter/
```

Set `AUTHENGENTIC_PYTHON` to an absolute interpreter path if `python3` is not on
`PATH`. Restart the app.

## Use it

- Ask Claude to "lint this with authengentic" and it calls the tool.
- Type `/` and pick `authengentic-review` or `authengentic-rewrite` to run a
  prompt over a block of text.

## Limits

- Nothing calls the tool automatically. The model calls it when you ask, or when
  the skill or your instructions tell it to.
- The linter is a regex pass. It is a floor, not a compliance verdict.
- The MCP `instructions` field is not read by Claude Desktop, so this server
  cannot inject an always-on ruleset. Use the account profile block for that.
