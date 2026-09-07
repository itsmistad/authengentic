# Install the skill in the Claude apps

This covers the Chat and Cowork tabs of the Claude Desktop app, and claude.ai on
the web. The Code tab uses the plugin instead. See
[../claude-desktop.md](../claude-desktop.md).

## Requirements

- A Claude plan with code execution: Free, Pro, Max, Team, or Enterprise.
- **Code execution and file creation** turned on: **Settings → Capabilities →
  Code execution and file creation**. The skills menu stays greyed out until
  this is on.

## Build the zip

From the repository root:

```bash
./scripts/build-desktop-skill.sh
```

This writes `dist/authengentic-skill.zip`. The script checks the description
length, bundles the linter under `scripts/`, and self-tests it.

## Upload

1. Open **Customize → Skills** in the Desktop app, or **Settings → Capabilities**
   on the web. The exact path moves from time to time across Anthropic's docs.
2. Click **+**, then choose to upload a skill.
3. Select `dist/authengentic-skill.zip`.
4. Turn the skill on in the list.

## Check it works

Ask for a short piece of writing, for example: "write a two-sentence release note
for a bug fix, authengentic". The reply follows the rules, and the model runs
`scripts/authengentic_lint.py` on any file it creates.

## Limits

- The skill loads when your request matches a writing task. It does not govern
  every reply. Add the account profile block for that. See
  [personal-preferences.md](personal-preferences.md).
- Custom skills do not sync between claude.ai and the API. Upload separately for
  each.
- On claude.ai a custom skill is private to your account. It is not shared with
  your team.
