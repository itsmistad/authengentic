#!/usr/bin/env python3
"""Tests for src/hooks/lint_hook.py. Run: python3 src/hooks/test_lint_hook.py"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HOOK = HERE / "lint_hook.py"

SLOP = (
    "You should leverage our robust system in order to seamlessly "
    "facilitate onboarding; it is important to note this is crucial.\n"
)
CLEAN = "The service retries a failed upload automatically.\n"


def run_hook(event, state_dir=None):
    env = dict(os.environ)
    if state_dir:
        env["AUTHENGENTIC_STATE_DIR"] = str(state_dir)
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
    )
    return proc


def write_md(text):
    fh = tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False)
    fh.write(text)
    fh.close()
    return fh.name


def post(state, tool_name, tool_input, session="s"):
    return run_hook({
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "session_id": session,
        "tool_input": tool_input,
    }, state)


def stop(state, session="s", reply=None):
    event = {"hook_event_name": "Stop", "session_id": session}
    if reply is not None:
        event["last_assistant_message"] = reply
    return run_hook(event, state)


class PostToolUseLocalTests(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()

    def test_code_file_is_ignored(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as fh:
            fh.write("x = 'you should leverage this in order to proceed'\n")
            path = fh.name
        proc = post(self.state, "Edit", {"file_path": path})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stderr, "")

    def test_slop_markdown_write_flags_violations(self):
        proc = post(self.state, "Write", {"file_path": write_md(SLOP), "content": SLOP})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("authengentic:", proc.stderr)

    def test_clean_markdown_write_is_silent(self):
        proc = post(self.state, "Write", {"file_path": write_md(CLEAN), "content": CLEAN})
        self.assertEqual(proc.returncode, 0)

    def test_extensionless_prose_file_is_checked(self):
        d = tempfile.mkdtemp()
        path = str(pathlib.Path(d) / "COMMIT_EDITMSG")
        pathlib.Path(path).write_text(SLOP, encoding="utf-8")
        proc = post(self.state, "Edit", {"file_path": path})
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_rules_directory_file_is_ignored(self):
        d = pathlib.Path(tempfile.mkdtemp()) / "rules"
        d.mkdir()
        path = str(d / "core.md")
        pathlib.Path(path).write_text(SLOP, encoding="utf-8")
        proc = post(self.state, "Write", {"file_path": path, "content": SLOP})
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_ignore_marker_file_is_skipped(self):
        body = "<!-- authengentic-lint: ignore -->\n" + SLOP
        proc = post(self.state, "Write", {"file_path": write_md(body), "content": body})
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_contractions_do_not_trigger_violation(self):
        body = "It's done. The build didn't fail this time, and we're glad.\n"
        proc = post(self.state, "Write", {"file_path": write_md(body), "content": body})
        self.assertEqual(proc.returncode, 0, proc.stderr)


class DocAppTests(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()

    def test_craft_write_flags_and_blocks(self):
        cmd = f'blocks update --id ABC-1 --markdown "{SLOP.strip()}"'
        proc = post(self.state, "mcp__craft__craft_write", {"command": cmd}, session="c")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("craft:ABC-1", proc.stderr)
        payload = json.loads(stop(self.state, session="c").stdout)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("craft:ABC-1", payload["reason"])

    def test_craft_read_is_ignored(self):
        proc = post(self.state, "mcp__craft__craft_read", {"command": "documents list"}, session="c")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stderr, "")

    def test_clean_craft_write_is_silent(self):
        cmd = f'blocks add --id P1 --markdown "{CLEAN.strip()}"'
        proc = post(self.state, "mcp__craft__craft_write", {"command": cmd}, session="c")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_notion_update_page_flags_and_blocks(self):
        proc = post(self.state, "mcp__notion__notion-update-page", {
            "page_id": "p1", "command": "replace_content", "new_str": SLOP.strip(),
        }, session="n")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("notion:p1", proc.stderr)
        payload = json.loads(stop(self.state, session="n").stdout)
        self.assertIn("notion:p1", payload["reason"])

    def test_notion_search_is_ignored(self):
        proc = post(self.state, "mcp__notion__notion-search", {"query": "leverage robust"}, session="n")
        self.assertEqual(proc.returncode, 0)

    def test_file_check_blocks_once_then_releases(self):
        bad = f'blocks update --id F1 --markdown "{SLOP.strip()}"'
        post(self.state, "mcp__craft__craft_write", {"command": bad}, session="f1")
        first = json.loads(stop(self.state, session="f1").stdout)
        self.assertEqual(first["decision"], "block")
        self.assertIn("one pass", first["reason"])
        second = json.loads(stop(self.state, session="f1").stdout)
        self.assertNotIn("decision", second)
        self.assertIn("file check done", second["systemMessage"])

    def test_revised_craft_write_clears_the_block(self):
        bad = f'blocks update --id D9 --markdown "{SLOP.strip()}"'
        post(self.state, "mcp__craft__craft_write", {"command": bad}, session="c")
        self.assertEqual(json.loads(stop(self.state, session="c").stdout)["decision"], "block")
        good = f'blocks update --id D9 --markdown "{CLEAN.strip()}"'
        post(self.state, "mcp__craft__craft_write", {"command": good}, session="c")
        self.assertEqual(stop(self.state, session="c").stdout.strip(), "")


class ReplyNoteTests(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()

    def test_clean_reply_is_silent(self):
        proc = stop(self.state, reply="The migration finished and the database rebuilt its table.")
        self.assertEqual(proc.stdout.strip(), "")

    def test_judgment_violation_is_a_note_not_a_block(self):
        proc = stop(self.state, session="soft", reply="The build passed. The tests ran green.")
        payload = json.loads(proc.stdout)
        self.assertNotIn("decision", payload)
        self.assertIn("🧠:", payload["systemMessage"])
        self.assertIn("consecutive same start", payload["systemMessage"])

    def test_reply_never_blocks(self):
        bad = "Certainly! It is worth noting you should leverage the robust pipeline."
        for _ in range(3):
            payload = json.loads(stop(self.state, session="r", reply=bad).stdout)
            self.assertNotIn("decision", payload)
            self.assertIn("🧠:", payload["systemMessage"])
            self.assertTrue(payload["suppressOutput"])

    def test_note_counts_and_lists_slop_words(self):
        bad = "You should leverage our robust and comprehensive pipeline, it is powerful."
        payload = json.loads(stop(self.state, session="slop", reply=bad).stdout)
        self.assertNotIn("decision", payload)
        msg = payload["systemMessage"]
        self.assertIn("slop word 4:", msg)
        for word in ("leverage", "robust", "comprehensive", "powerful"):
            self.assertIn(word, msg)

    def test_note_omits_sentence_length_checks(self):
        long_sentence = " ".join(f"word{i}" for i in range(40)) + "."
        bad = "One here now. Two here now. Three here now. " + long_sentence
        payload = json.loads(stop(self.state, session="len", reply=bad).stdout or "{}")
        msg = payload.get("systemMessage", "")
        self.assertNotIn("sentence over limit", msg)
        self.assertNotIn("sentences outside code and lists", msg)

    def test_note_quotes_trailing_condition_starts(self):
        bad = "Read the log if you need to. Restart the worker when the queue drains."
        payload = json.loads(stop(self.state, session="tc", reply=bad).stdout)
        self.assertIn('trailing condition: "if you", "when the"', payload["systemMessage"])

    def test_note_maps_synonym_rotation(self):
        bad = "You must check the value, verify the config, and confirm the settings."
        payload = json.loads(stop(self.state, session="sr", reply=bad).stdout)
        msg = payload["systemMessage"]
        self.assertIn('synonym rotation: "check -> verify, confirm", "config -> settings"', msg)


class BaselineScopingTests(unittest.TestCase):
    """The file loop scores an edit against the committed version, not zero."""

    def setUp(self):
        self.state = tempfile.mkdtemp()
        self.repo = pathlib.Path(tempfile.mkdtemp())
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.repo, check=True)
        self.doc = self.repo / "doc.md"
        self.doc.write_text(SLOP, encoding="utf-8")
        subprocess.run(["git", "add", "doc.md"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=self.repo, check=True)

    def test_editing_debt_without_adding_violations_is_silent(self):
        self.doc.write_text(SLOP + CLEAN, encoding="utf-8")
        proc = post(self.state, "Edit", {"file_path": str(self.doc)}, session="b")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(stop(self.state, session="b").stdout.strip(), "")

    def test_only_added_violations_are_flagged(self):
        self.doc.write_text(SLOP + SLOP, encoding="utf-8")
        proc = post(self.state, "Edit", {"file_path": str(self.doc)}, session="b")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("over the baseline", proc.stderr)
        payload = json.loads(stop(self.state, session="b").stdout)
        self.assertEqual(payload["decision"], "block")


class CombinedTests(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp()

    def test_one_payload_carries_reply_note_and_file_block(self):
        cmd = f'blocks update --id X1 --markdown "{SLOP.strip()}"'
        post(self.state, "mcp__craft__craft_write", {"command": cmd}, session="both")
        payload = json.loads(stop(
            self.state, session="both",
            reply="Certainly! It is worth noting you should leverage the robust pipeline.",
        ).stdout)
        self.assertEqual(payload["decision"], "block")
        self.assertIn("file check", payload["reason"])
        self.assertIn("🧠:", payload["systemMessage"])


if __name__ == "__main__":
    unittest.main()
