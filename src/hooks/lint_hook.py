#!/usr/bin/env python3
"""Writing checks for Claude Code hooks.

The checks score changed prose against a baseline, not against zero. A
local file's baseline is its version at git HEAD. A doc-app page or a new
file has a baseline of zero, so the session owns the text it writes.

PostToolUse: run on every write to a prose file or a doc-app page. Prose
files are .md, .mdx, .txt, .rst, .adoc, and the like, plus an
extensionless file that reads as prose. Doc apps are Craft and Notion
(see the MCP tool names in `.claude-plugin/plugin.json`). The hook lints
the text the write produced, compares the count to the baseline, and when
the write adds violations it prints a summary to stderr and records the
target. Exit 2 is advisory: the tool already ran. A rule source is
skipped: a file under a `rules/` directory, or one whose first 1000
characters carry the marker `authengentic-lint: ignore`.

Stop: a reply-register note and a file check.

1. The reply-register check scores `last_assistant_message` with the full
   descriptive linter. It never blocks. Claude Code already showed the
   reply and a Stop block cannot hide it, so the check only prints one
   summary through `systemMessage`, prefixed `🧠: `. The summary skips the
   sentence-length rules. It names each slop word, quotes the first two
   words of each trailing if/when clause, and maps each synonym rotation
   as "<first> -> <alt>, <alt>". Prevention lives in the pre-send
   checklist in rules/core.md.
2. The file check re-scores every recorded target against its baseline. A
   target still over baseline blocks once with `{"decision": "block",
   "reason": ...}` and `suppressOutput` set. That is one fix pass. If the
   next stop still shows the target over baseline, the check releases and
   reports the leftover through `systemMessage`.

One payload can carry the reply note and a file block together.

The `decision` field is the only lever that makes a Stop hook enforce.
Without it the hook can print a note, but the turn already ended and the
model has moved on. `{"decision": "block", "reason": ...}` tells Claude
Code to keep the turn open and feed `reason` back to the model as a new
instruction. The model fixes the file and tries to stop again, and the
hook re-runs. Exit 2 on PostToolUse cannot do this: the write already
landed and the turn continues no matter what the model does.

Notion support ships unverified: the Notion MCP was not installed when
this was written. The tool names come from the Notion MCP docs. Test it
against a live workspace before you rely on it.
"""
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "evals"))

STATE_DIR = pathlib.Path(
    os.environ.get("AUTHENGENTIC_STATE_DIR") or (pathlib.Path(tempfile.gettempdir()) / "authengentic-hooks")
)
STATE_TTL_SECONDS = 24 * 60 * 60

PROSE_EXTS = {
    ".md", ".mdx", ".markdown", ".mkd", ".mkdn", ".mdown",
    ".txt", ".text", ".rst", ".adoc", ".asciidoc", ".org", ".rmd",
}
CODE_HINT_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".json", ".yaml",
    ".yml", ".toml", ".ini", ".cfg", ".sh", ".bash", ".zsh", ".go", ".rs",
    ".java", ".c", ".h", ".cpp", ".hpp", ".rb", ".php", ".css", ".scss",
    ".html", ".xml", ".sql", ".lock", ".svg", ".csv", ".tsv",
}
PROSE_BASENAMES = {
    "readme", "license", "licence", "notice", "authors", "contributors",
    "changelog", "changes", "history", "copying", "commit_editmsg",
    "pull_request_template", "issue_template", "codeowners",
}

CRAFT_TOOL = re.compile(r"craft_write$")
NOTION_WRITE = re.compile(
    r"(create-pages|create_pages|update-page|update_page|update-page-markdown|"
    r"append-block-children|patch-block-children|update-a-block|post-page|patch-page)",
    re.I,
)
NOTION_TEXT_KEYS = {
    "content", "markdown", "new_str", "text", "title", "plain_text",
    "rich_text", "caption", "name", "value",
}

OPENERS = re.compile(r"^\s*(certainly|great question|you're absolutely right|sure[,!]|absolutely[,!])", re.I)
CLOSERS = re.compile(r"(i hope this helps|let me know if|feel free to)", re.I)


def load_linter():
    try:
        import authengentic_lint  # noqa: WPS433
        return authengentic_lint
    except Exception:  # noqa: BLE001
        return None


def strip_code(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    return re.sub(r"`[^`]*`", " ", text)


def _lint_text(lint, text):
    """Return (total, summary) for a block of text."""
    report = lint.lint(text or "", "descriptive")
    hits = {k: v for k, v in report["violations"].items() if v}
    summary = ", ".join(f"{k} {v}" for k, v in hits.items())
    return report["violations_total"], summary


"""State helpers. One JSON file per session under STATE_DIR."""


def _blank_state():
    return {
        "targets": [],       # keys with unresolved excess (local path or "craft:"/"notion:" id)
        "baselines": {},     # key -> baseline violation count
        "captured": {},      # doc-app key -> last text the session wrote
        "fix_tried": False,  # the one file fix pass ran
        "files_done": False,
    }


def _state_path(session):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session or "default")
    return STATE_DIR / f"{safe}.json"


def _prune_stale():
    try:
        cutoff = time.time() - STATE_TTL_SECONDS
        for item in STATE_DIR.glob("*.json"):
            if item.stat().st_mtime < cutoff:
                item.unlink()
    except OSError:
        return


def _load_state(session):
    try:
        loaded = json.loads(_state_path(session).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _blank_state()
    state = _blank_state()
    state.update(loaded)
    return state


def _save_state(session, state):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        _state_path(session).write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        return


def _clear_state(session):
    try:
        _state_path(session).unlink()
    except OSError:
        return


"""Content extraction. Turn a write tool call into a list of
(key, text, is_remote) targets to score."""

# A rule source is not a deliverable. It must name the banned words to
# teach them, so linting it against a zero baseline is always a false
# positive. Skip a file under a `rules/` directory, and skip any file
# whose first 1000 characters carry the marker `authengentic-lint: ignore`.
IGNORE_MARKER = "authengentic-lint: ignore"
IGNORE_DIR_SEGMENTS = {"rules"}


def _is_ignored(path, text):
    parts = {seg.lower() for seg in pathlib.Path(path).parts}
    if parts & IGNORE_DIR_SEGMENTS:
        return True
    return IGNORE_MARKER in (text or "")[:1000]


def _looks_like_prose(path, text):
    p = pathlib.Path(path)
    ext = p.suffix.lower()
    if ext in PROSE_EXTS:
        return True
    if ext in CODE_HINT_EXTS:
        return False
    if p.name.lower() in PROSE_BASENAMES or p.stem.lower() in PROSE_BASENAMES:
        return True
    if ext:
        return False
    sample = (text or "")[:2000]
    if sample.startswith("#!") or "\t" in sample:
        return False
    letters = sum(c.isalpha() or c.isspace() for c in sample)
    return bool(sample) and letters / len(sample) > 0.85


def _harvest_strings(obj, keys, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in keys:
                out.append(v)
            else:
                _harvest_strings(v, keys, out)
    elif isinstance(obj, list):
        for v in obj:
            _harvest_strings(v, keys, out)


def _craft_targets(tool_input):
    command = (tool_input or {}).get("command", "")
    if not command:
        return []
    try:
        tokens = shlex.split(command)
    except ValueError:
        return []
    text_parts, doc_id = [], None
    for i, tok in enumerate(tokens[:-1]):
        nxt = tokens[i + 1]
        if tok in ("--markdown", "--title", "--name"):
            text_parts.append(nxt)
        elif tok in ("--id", "--siblingId", "--targetId", "--document", "--collection") and doc_id is None:
            doc_id = nxt
    if not text_parts:
        return []
    return [(f"craft:{doc_id or 'doc'}", "\n\n".join(text_parts), True)]


def _notion_targets(tool_name, tool_input):
    if not NOTION_WRITE.search(tool_name):
        return []
    parts = []
    _harvest_strings(tool_input, NOTION_TEXT_KEYS, parts)
    text = "\n\n".join(p for p in parts if p and not p.startswith("http"))
    if not text.strip():
        return []
    page_id = (tool_input or {}).get("page_id") or (tool_input or {}).get("pageId")
    parent = (tool_input or {}).get("parent")
    if not page_id and isinstance(parent, dict):
        page_id = parent.get("page_id") or parent.get("database_id") or parent.get("id")
    return [(f"notion:{page_id or 'new'}", text, True)]


def extract_targets(tool_name, tool_input):
    tool_input = tool_input or {}
    if tool_name in ("Write",):
        path = tool_input.get("file_path", "")
        text = tool_input.get("content", "")
        if path and _looks_like_prose(path, text) and not _is_ignored(path, text):
            return [(path, text, False)]
        return []
    if tool_name in ("Edit", "MultiEdit"):
        path = tool_input.get("file_path", "")
        if not path:
            return []
        try:
            text = pathlib.Path(path).read_text(encoding="utf-8")
        except OSError:
            return []
        if _looks_like_prose(path, text) and not _is_ignored(path, text):
            return [(path, text, False)]
        return []
    if CRAFT_TOOL.search(tool_name):
        return _craft_targets(tool_input)
    if "notion" in tool_name.lower():
        return _notion_targets(tool_name, tool_input)
    return []


def _baseline_total(lint, key, is_remote):
    """git HEAD count for a local prose file, else 0."""
    if is_remote:
        return 0
    p = pathlib.Path(key)
    try:
        blob = subprocess.run(
            ["git", "show", f"HEAD:./{p.name}"],
            cwd=str(p.parent),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return 0
    if blob.returncode != 0:
        return 0
    total, _ = _lint_text(lint, blob.stdout)
    return total


def _current_text(state, key):
    """The text to score now: the doc-app text the session last wrote, or
    the local file read from disk."""
    if key.startswith(("craft:", "notion:")):
        return state["captured"].get(key)
    try:
        return pathlib.Path(key).read_text(encoding="utf-8")
    except OSError:
        return None


def _excess_for(lint, state, key):
    text = _current_text(state, key)
    if text is None:
        return 0, ""
    total, summary = _lint_text(lint, text)
    return max(total - state["baselines"].get(key, 0), 0), summary


def _display(key):
    if key.startswith(("craft:", "notion:")):
        return key
    return pathlib.Path(key).name


def post_tool_use(event):
    tool_name = event.get("tool_name", "")
    targets = extract_targets(tool_name, event.get("tool_input"))
    if not targets:
        return 0
    lint = load_linter()
    if lint is None:
        return 0
    session = event.get("session_id")
    state = _load_state(session)

    flagged = []
    for key, text, is_remote in targets:
        if is_remote:
            state["captured"][key] = text
        if key not in state["baselines"]:
            state["baselines"][key] = _baseline_total(lint, key, is_remote)
        excess, summary = _excess_for(lint, state, key)
        if excess > 0:
            if key not in state["targets"]:
                state["targets"].append(key)
            flagged.append((key, excess, summary))
        elif key in state["targets"]:
            state["targets"].remove(key)
    _save_state(session, state)

    if not flagged:
        return 0
    detail = "; ".join(f"{_display(k)} +{x} ({s})" for k, x, s in flagged)
    sys.stderr.write(
        f"authengentic: this write adds violations over the baseline ({detail}). "
        f"Refactor the passage you changed before you deliver.\n"
    )
    return 2


"""Reply-register check. The Stop hook cannot edit or hide a message that
Claude Code already showed, and a blocking loop makes the user watch every
retry. So the reply check never blocks. It scores `last_assistant_message`
with the full descriptive linter and prints one non-blocking summary
through `systemMessage`. The pre-send checklist in rules/core.md
does the prevention."""


SKIP_REPLY_KEYS = {"sentence_over_limit"}


def _unique_lower(items):
    out = []
    for item in items:
        low = item.lower()
        if low not in out:
            out.append(low)
    return out


def _trailing_condition_starts(lint, body):
    """The first two words of each trailing if/when clause, lowercased and
    quoted. Mirrors the linter's per-sentence check."""
    starts = []
    for sentence in lint.sentences(body):
        match = lint.TRAILING_COND.search(sentence)
        if not match:
            continue
        line_start = sentence.rfind("\n", 0, match.start()) + 1
        if match.start() - line_start < 4:
            continue
        if re.match(r"^(if|when)\b", sentence, re.I):
            continue
        clause = sentence[match.start():].strip()
        words = re.findall(r"[A-Za-z']+", clause)[:2]
        if words:
            starts.append(" ".join(w.lower() for w in words))
    return starts


def _synonym_rotation_maps(lint, body):
    """One '<first> -> <alt>, <alt>' string per rotation set that fired."""
    maps = []
    for _, rx in lint.ROTATION_SETS:
        seen = []
        for match in rx.finditer(body):
            word = match.group(1).lower()
            if word not in seen:
                seen.append(word)
        if len(seen) > 1:
            maps.append(f"{seen[0]} -> {', '.join(seen[1:])}")
    return maps


def _reply_problems(event, lint):
    """Return a list of reply-register problems for the non-blocking note.
    Nothing here blocks the stop."""
    reply = event.get("last_assistant_message") or ""
    body = strip_code(reply)
    problems = []
    if OPENERS.search(reply):
        problems.append("a filler opener")
    if CLOSERS.search(reply):
        problems.append("a filler closer")
    if lint is None:
        return problems
    violations = lint.lint(body, "descriptive")["violations"]
    for key, count in violations.items():
        if not count or key in SKIP_REPLY_KEYS:
            continue
        if key == "slop_word":
            words = _unique_lower(lint.SLOP.findall(body))
            problems.append(f"slop word {count}: {', '.join(words)}")
        elif key == "trailing_condition":
            starts = _trailing_condition_starts(lint, body)
            if starts:
                quoted = ", ".join(f'"{s}"' for s in starts)
                problems.append(f"trailing condition: {quoted}")
            else:
                problems.append(f"trailing condition {count}")
        elif key == "synonym_rotation":
            maps = _synonym_rotation_maps(lint, body)
            if maps:
                quoted = ", ".join(f'"{m}"' for m in maps)
                problems.append(f"synonym rotation: {quoted}")
            else:
                problems.append(f"synonym rotation {count}")
        else:
            problems.append(f"{key.replace('_', ' ')} {count}")
    return problems


"""Message builders."""


def _file_block_reason(reports):
    lines = [
        "authengentic: file check, one pass. Your writes add writing-rule "
        "violations that the baseline did not have. Rewrite only the passages "
        "you changed so the target returns to its baseline count. Leave "
        "pre-existing debt in untouched sections alone. Apply the self-check in "
        "skills/authengentic/SKILL.md. Keep every code block, identifier, path, "
        "and quoted string exact.",
    ]
    for key, (excess, summary) in reports.items():
        lines.append(f"  - {_display(key)}: {excess} added violations ({summary})")
    return "\n".join(lines)


def _file_release_message(reports):
    total = sum(x for x, _ in reports.values())
    detail = "; ".join(f"{_display(k)}: {s}" for k, (_, s) in reports.items())
    return (
        f"authengentic: file check done after one pass. Your writes still add "
        f"{total} violations ({detail}). Review them by hand."
    )


def _emit(notes, block_reason):
    payload = {}
    if notes:
        payload["systemMessage"] = " ".join(notes)
    if block_reason:
        payload["decision"] = "block"
        payload["reason"] = block_reason
    if payload:
        # Keep the hook's own stdout out of the transcript. A block reason
        # still reaches the model, and a systemMessage still shows.
        payload["suppressOutput"] = True
        print(json.dumps(payload))


def stop(event):
    _prune_stale()
    lint = load_linter()
    session = event.get("session_id")
    state = _load_state(session)

    notes, block_parts = [], []

    # --- reply-register note (never blocks) -------------------------------
    # Claude Code already showed the reply and a Stop block cannot hide it,
    # so the reply check only prints a summary. Prevention lives in the
    # pre-send checklist in rules/core.md.
    problems = _reply_problems(event, lint)
    if problems:
        notes.append("🧠: " + " / ".join(problems) + ".")

    # --- file check (one fix pass) ---------------------------------------
    # If a recorded target still adds violations over its baseline, block
    # once for a fix pass. If the next stop still shows the target dirty,
    # release with a note. No multi-pass loop.
    if not state.get("files_done"):
        reports = {}
        if lint is not None:
            for key in list(state.get("targets", [])):
                if key not in state["baselines"]:
                    state["baselines"][key] = _baseline_total(
                        lint, key, key.startswith(("craft:", "notion:"))
                    )
                excess, summary = _excess_for(lint, state, key)
                if excess > 0:
                    reports[key] = (excess, summary)
        if not reports:
            state["fix_tried"] = False
            state["targets"] = []
        elif state.get("fix_tried"):
            notes.append(_file_release_message(reports))
            state["files_done"] = True
        else:
            state["fix_tried"] = True
            state["targets"] = list(reports.keys())
            block_parts.append(_file_block_reason(reports))

    quiet = not state["targets"] and not state.get("files_done")
    if quiet:
        _clear_state(session)
    else:
        _save_state(session, state)

    _emit(notes, "\n\n".join(block_parts) if block_parts else None)
    return 0


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        return 0
    name = event.get("hook_event_name", "")
    if name == "PostToolUse":
        return post_tool_use(event)
    if name == "Stop":
        return stop(event)
    return 0


if __name__ == "__main__":
    sys.exit(main())
