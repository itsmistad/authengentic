---
name: authengentic-learn
description: >
  Manual maintenance action for the authengentic plugin. Scan recent assistant
  replies for writing-rule breaks that the regex misses, then record the terms
  in the learning store so the linter flags them next time. Invoke this ONLY
  when the user types /authengentic-learn or asks for it by name. Do not
  trigger it on your own and do not run it as part of another task. Argument:
  a whole number of recent assistant replies to scan (default 5), or "all".
license: MIT
compatibility: Runs in Claude Code with the authengentic plugin installed. Needs python3 for src/hooks/learn.py.
metadata:
  version: "1.3.0"
---

<!-- authengentic-lint: ignore -->

# authengentic-learn

Find words and phrases that break the authengentic rules but a regex cannot catch, then hand them to the learning store. A term seen once becomes a candidate. A term seen a second time gets promoted, and the linter flags it from then on.

## When to run this

Run it only when the user asks. It mutates the learning store and makes one subagent call. It is not part of writing, reviewing, or any other authengentic operation.

## Steps

1. Read the argument this skill was invoked with. It is a whole number, or the word `all`, or empty. Empty means 5. `all` means every assistant reply in this conversation.

2. Collect the last N of your own assistant replies from this conversation, in order, most recent last. Use `all` of them if the argument says so. Keep the raw text of each, code blocks and quoted errors included.

3. Read the current rules and state. Set `ROOT="${CLAUDE_PLUGIN_ROOT:-.}"` and `STORE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/authengentic"`.
   - The ruleset: `cat "$ROOT/rules/core.md"`.
   - Current candidates: `cat "$STORE/candidates.jsonl" 2>/dev/null` (the file may not exist yet).
   - Current learned terms: `cat "$STORE/learned.json" 2>/dev/null`.

4. Dispatch one subagent to do the scan. Use the `Agent` tool with `subagent_type: "general-purpose"` and `model: "haiku"`. Give it the ruleset text, the collected replies, the current candidate and learned terms, and this instruction:

   > You check text against a plain-English style rule set. Find words and short phrases that break the spirit of the rules but a simple word-list regex would miss. Look only for three categories:
   > - `slop`: an empty or inflated word that carries no fact, beyond the ones already listed.
   > - `openers`: a filler sentence opener addressed to the user.
   > - `closers`: a filler sign-off.
   > Be strict about evidence. Return a term only if it actually appears in the replies and clearly breaks a rule. Do not return a term that is already in the learned list. Do not return normal technical vocabulary.
   > Return a JSON array only, no prose. Each item: `{"term": "<lowercase surface form>", "category": "slop|openers|closers", "example": "<the sentence it appeared in, trimmed to 200 characters>"}`. Return `[]` if nothing qualifies.

5. Take the subagent's JSON array and pass it to the store:

   ```bash
   echo '<the JSON array>' | python3 "$ROOT/src/hooks/learn.py" ingest
   ```

6. Report the result to the user in a short list: which terms were promoted to `learned.json`, which were added as new candidates, and which were ignored because they were already learned. If the subagent returned `[]`, say that nothing new was found.

## Notes

- The store lives at `${CLAUDE_CONFIG_DIR:-~/.claude}/authengentic/`, never inside the plugin folder.
- `learn.py ingest` applies the promotion rules and regenerates `digest.md`. The new learned terms take effect at the next session start.
- This skill reads and writes local files only, plus one subagent call.
