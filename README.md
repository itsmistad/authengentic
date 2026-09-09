# authengentic

Write non-fiction English that a smart reader outside your field understands on one read, and that reads as though a person wrote it, not a language model.

authengentic merges four writing-rule projects into one non-fiction ruleset:

- [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) gives the ASD-STE100 Simplified Technical English base: short sentences, active voice, simple tenses, one word one meaning, condition before command, and the plugin, hook, and linter mechanism.
- [agent-style](https://github.com/yzhao062/agent-style) gives the RULE-01 through RULE-12 and RULE-A through RULE-I directives, plus the mechanical detectors for dash clusters, title-case headings, and repeated sentence openers.
- [humanizer](https://github.com/blader/humanizer) gives the Wikipedia "Signs of AI writing" pattern catalog and the voice-matching-from-a-sample mechanism.
- [sepia](https://github.com/Nanako0129/sepia) gives the professional-pass checklist, the per-domain rule files, the calibration principles, and the model-fingerprint tables.

None of their code is vendored. Their prose and detector logic is re-expressed here. Full attribution and licenses are in [SOURCES.md](SOURCES.md).

Scope is non-fiction: documentation, technical prose, and professional prose. It does not touch fiction or marketing copy, on purpose.

## Install

**Claude Code plugin** (skill, session hook, output style):

```bash
claude plugin marketplace add /Users/dj/Documents/Personal/Code/authengentic
claude plugin install authengentic@authengentic
```

The plugin also ships an [output style](https://code.claude.com/docs/en/output-styles), named `authengentic:authengentic`. The short name does not resolve. For one project, run `/config`, open **Output style**, and select it. For all projects, put `{"outputStyle": "authengentic:authengentic"}` in `~/.claude/settings.json` and start Claude Code again.

**Codex plugin** (skill, session hook):

```bash
codex plugin marketplace add /Users/dj/Documents/Personal/Code/authengentic
codex plugin add authengentic@authengentic
```

Then ask for any technical or professional writing, or say: *"rewrite this with authengentic"*.

**Claude Desktop.** The app has three tabs, and they load extensions differently:

- **Code tab.** It reads the same settings files as the CLI, so the plugin works
  with no port. Install it through **+ → Plugins → Add plugin**, then set
  `{"outputStyle": "authengentic:authengentic"}` in `~/.claude/settings.json`,
  because `/config` opens a pane here, not a picker.
- **Chat and Cowork tabs.** These have no hooks and no output style. Upload the
  skill as a zip (`./scripts/build-desktop-skill.sh`), paste the account profile
  block for an always-on register, and install the MCP linter bundle
  (`./scripts/build-mcpb.sh`) for a one-call check.

Full steps and the fidelity limits are in [docs/claude-desktop.md](docs/claude-desktop.md).

## How the checks run

The Claude Code plugin runs two hooks against the linter (`src/hooks/lint_hook.py`). Both score changed prose against a baseline, never against zero. For a local file, the baseline is the version at git `HEAD`. A doc-app page or a new file starts from zero, so the session owns whatever text it writes. The `PostToolUse` matcher and the doc-app tool names live in [`hooks/hooks.json`](hooks/hooks.json), the single hook file that every host loads.

A prose target is one of three things.

- A local file with a prose extension: `.md`, `.mdx`, `.txt`, `.rst`, `.adoc`, and similar.
- An extensionless file that reads as prose.
- A Craft or Notion page.

Code and configuration files are skipped. A rule source is skipped too, because it must name the banned words to teach them. That means a file under a `rules/` directory, or one whose first 1000 characters carry the marker `authengentic-lint: ignore`.

`PostToolUse` runs after a write to a prose target. It lints the new text. If the write adds violations over the baseline, it prints a summary and records the target.

`Stop` runs a reply-register note and a file check.

- The reply-register check scores `last_assistant_message` with the full linter. It never blocks. Claude Code already showed the reply and a `Stop` block cannot hide it, so the check prints one summary through a note, prefixed `🧠: `. The summary skips the sentence-length rules. It names each slop word, quotes the first two words of each trailing `if`/`when` clause, and maps each synonym rotation as `<first> -> <alt>, <alt>`. Prevention lives in the pre-send checklist in `rules/core.md`.
- The file check re-scores every recorded target against its baseline. A target still over baseline blocks the stop once and returns a `reason` with `suppressOutput` set. That is one fix pass. If the next stop still shows the target over baseline, the check releases and reports the leftover through a note.

One stop can carry the reply note and a file block together. The `decision` field is what makes a `Stop` hook enforce: it holds the turn open and feeds `reason` back to the model. Exit 2 on `PostToolUse` is advisory, because the write already landed.

Notion support ships unverified. The Notion MCP was absent from the build machine, so its tool names come from the Notion MCP docs. Test it against a live workspace first.

## How the plugin learns

After a hook prints a non-zero violation summary, it folds the counts into a profile under `${CLAUDE_CONFIG_DIR:-~/.claude}/authengentic/`. The plugin never writes inside its own folder, because that folder is a cache Claude Code can wipe.

- `observations.jsonl` — one line per rule per event, capped at 2000 lines.
- `profile.json` — a score per rule. The score halves every 30 days, so the digest tracks recent habits.
- `digest.md` — regenerated on every event. It ranks the rules you break most and names the words you repeat. The SessionStart hook injects it after `rules/core.md`.

`digest.md` never adds or removes a rule. It re-ranks your attention over the frozen core, so it carries no false-positive risk.

The `/authengentic-learn` command finds words and phrases the regex missed. It reads your recent replies, asks a Haiku subagent for terms that break the rules, and writes them to `candidates.jsonl`. A term seen a second time moves to `learned.json`. The linter and the hook read `learned.json` and flag its terms like the built-in lists.

## What's different from SimpleEnglish

authengentic overrules its parent on four points. Each is stated in full in [SKILL.md, "Where authengentic differs from its sources"](skills/authengentic/SKILL.md#where-authengentic-differs-from-its-sources).

1. **Contractions are restored.** SimpleEnglish and agent-style ban them. authengentic requires them where a person would use them, because instruction-tuned models under-use them. The modal ladder is unchanged, so "shouldn't" stays banned.
2. **Headings are sentence case.** Always, in every mode, overriding agent-style's title-case rule for academic and engineering venues.
3. **Dashes are judged by cluster.** A lone, well-placed em-dash or en-dash is fine. Only a cluster is a violation: two or more as punctuation in one sentence, or three or more in one paragraph.
4. **Every other pattern is fix-on-first-hit.** One occurrence of a banned modal, a semicolon, a perfect tense, an `-ing` clause, or a slop word is a violation to fix now, not something to tally.

## See it

Left is representative unedited AI output. Right is the same prompt with authengentic loaded. The right column keeps two contractions and one em-dash, and all three are correct, so authengentic leaves them alone (differences 1 and 3 above).

<table>
<tr>
<th width="50%">Without authengentic</th>
<th width="50%">With authengentic</th>
</tr>
<tr>
<td valign="top">

> Leveraging sqlpipe's robust architecture, users can seamlessly synchronize their Postgres tables to S3 with minimal configuration overhead. Before getting started, you should ensure that your AWS credentials have been properly configured — this is crucial for avoiding frustrating permission issues down the line.

</td>
<td valign="top">

> sqlpipe copies your Postgres tables to S3. It needs one configuration file, and you don't have to create the bucket first.
>
> Before you start, make sure that your AWS credentials are correct — the upload runs as your IAM user, not as sqlpipe. If they aren't, S3 rejects the write with a permission error.

</td>
</tr>
</table>

## The rules

53 numbered rules across sections 1 through 9, paraphrased with software examples in [`SKILL.md`](skills/authengentic/SKILL.md). Those sections are the ASD-STE100 Issue 9 catalog, extended in place with the merged material. A tenth section is authengentic's own: reader, parallelism, word order, end weight, evidence-matched claims, and the middle-of-document choke point.

Around the catalog:

- **The merged AI-tells catalog.** 38 numbered patterns from the Wikipedia "Signs of AI writing" list and the three source projects, each with a before and after, in [`references/ai-tells.md`](skills/authengentic/references/ai-tells.md).
- **Four operations.** `write` is new content. `review` diagnoses only and changes nothing. `refactor` is a minimal in-place revision that keeps the structure and voice. `recreate` is a full rewrite from an extracted fact list. Operations and modes are independent axes.
- **Two modes.** Plain (default) writes for a smart reader outside the field. Strict adds the STE dictionary discipline when you name STE, ASD-STE100, or compliance.
- **Domain files.** Release notes, dev replies, postmortems, tickets, technical articles, error messages, and API docs, in [`references/domains/`](skills/authengentic/references/domains).

## License

authengentic's own files are MIT (see [LICENSE](LICENSE)). Merged rule text adapted from agent-style's `RULES.md` remains under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); see [SOURCES.md](SOURCES.md).

authengentic re-expresses rule content from four upstream projects. [SOURCES.md](SOURCES.md) lists each one, its license, and what was used. agent-style's `RULES.md` rule text is CC-BY-4.0, so SOURCES.md is a required attribution wherever authengentic's rule text draws on it. The other three sources are MIT.
