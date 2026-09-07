# authengentic on Claude Desktop

The Claude Desktop app has three tabs: Chat, Cowork, and Code. Each one loads
extensions differently, so authengentic reaches each one differently.

| Tab | What it is | How authengentic loads | Enforcement you get |
| --- | --- | --- | --- |
| Code | Claude Code with a graphical shell | The full plugin: skill, hooks, output style, linter | Same as the Claude Code CLI |
| Cowork | Dispatch and longer agentic runs | The skill, if you enable it for your account | Skill-level only. Hooks are unverified here |
| Chat | The plain Claude assistant | An uploaded skill, an MCP server, and always-on instructions | Skill plus a one-call linter. No automatic post-write check |

## Code tab

The Code tab reads the same settings files as the CLI, so the plugin works with
no port.

1. Install the plugin. Click the **+** button next to the prompt box, then
   **Plugins**, then **Add plugin**. Pick `authengentic` from the marketplace.
   You can also add it in a settings file under `enabledPlugins`.
2. Set the output style. `/config` opens a settings pane here, not a picker, so
   add this to `~/.claude/settings.json`:

   ```json
   { "outputStyle": "authengentic:authengentic" }
   ```

3. Start a new session. The SessionStart hook, the `PostToolUse` and `Stop`
   linter, and the skill all run with no extra step.

## Cowork tab

Cowork loads skills, plugins, and connectors from the **Customize** area, which
syncs through your claude.ai account. It does not read `~/.claude`.

1. Upload the skill zip to your account. See [skill-install.md](desktop/skill-install.md).
2. Turn the skill on in **Customize → Skills**.

Whether a plugin's hooks run in Cowork is not documented. Test it in your own
workspace. The skill covers Cowork on its own if the hooks do not run.

## Chat tab

The Chat tab has no hook system. Nothing runs the linter automatically after the
model writes a file or finishes a turn. Three layers get as close as the platform
allows.

### Layer 1: the skill

Upload the skill zip. It carries the full rule catalog and the bundled linter.
The model loads it when your request matches a writing task. See
[skill-install.md](desktop/skill-install.md).

### Layer 2: always-on instructions

The skill body loads only on a match. To hold the register on every reply, paste
a condensed ruleset into your account profile, and a fuller one into any Project
you use for writing.

- Account profile: [personal-preferences.md](desktop/personal-preferences.md)
- Project instructions: [project-instructions.md](desktop/project-instructions.md)

### Layer 3: the MCP linter

Install the MCP bundle for a one-call deterministic check and two slash-command
prompts (`authengentic-review`, `authengentic-rewrite`). See
[mcp-install.md](desktop/mcp-install.md).

## What Claude Desktop cannot do

The Claude Code plugin runs the linter automatically after every write, and
checks the register of the final reply. The Chat tab has no equivalent hook. The
layers above reduce the gap. They do not close it. Treat the linter as a check
you or the model runs, not as a guarantee.
