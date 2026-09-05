#!/usr/bin/env python3
"""Tests for src/hooks/lint_hook.py. Run: python3 src/hooks/test_lint_hook.py"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
HOOK = HERE / "lint_hook.py"


def run_hook(event):
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
    )
    return proc


class PostToolUseTests(unittest.TestCase):
    def test_non_markdown_file_is_ignored(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as fh:
            fh.write("You should leverage this in order to proceed.")
            path = fh.name
        proc = run_hook({"hook_event_name": "PostToolUse", "tool_input": {"file_path": path}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stderr, "")

    def test_slop_markdown_file_flags_violations(self):
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as fh:
            fh.write(
                "You should leverage our robust system in order to seamlessly "
                "facilitate onboarding; it is important to note this is crucial.\n"
            )
            path = fh.name
        proc = run_hook({"hook_event_name": "PostToolUse", "tool_input": {"file_path": path}})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("authengentic:", proc.stderr)

    def test_clean_markdown_file_is_silent(self):
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as fh:
            fh.write("The service retries a failed upload automatically.\n")
            path = fh.name
        proc = run_hook({"hook_event_name": "PostToolUse", "tool_input": {"file_path": path}})
        self.assertEqual(proc.returncode, 0)

    def test_contractions_in_markdown_do_not_trigger_violation(self):
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as fh:
            fh.write("It's done. The build didn't fail this time, and we're glad.\n")
            path = fh.name
        proc = run_hook({"hook_event_name": "PostToolUse", "tool_input": {"file_path": path}})
        self.assertEqual(proc.returncode, 0, proc.stderr)


class StopTests(unittest.TestCase):
    def test_short_clean_reply_is_silent(self):
        proc = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "The migration completed. The database rebuilt the table.",
        })
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")

    def test_filler_opener_is_flagged(self):
        proc = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "Certainly! Here is the answer you asked for.",
        })
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIn("filler opener", payload["systemMessage"])

    def test_contractions_do_not_trigger_a_problem(self):
        proc = run_hook({
            "hook_event_name": "Stop",
            "last_assistant_message": "It's done. The build didn't fail this time.",
        })
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
