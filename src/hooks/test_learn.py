#!/usr/bin/env python3
"""Tests for src/hooks/learn.py. Run: python3 src/hooks/test_learn.py"""
import json
import os
import pathlib
import sys
import tempfile
import time
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent / "evals"))

import authengentic_lint as lint  # noqa: E402
import learn  # noqa: E402


class LearnTests(unittest.TestCase):
    def setUp(self):
        self.bucket = pathlib.Path(tempfile.mkdtemp())
        os.environ["AUTHENGENTIC_CONFIG_DIR"] = str(self.bucket)
        self.auth = self.bucket / "authengentic"

    def tearDown(self):
        os.environ.pop("AUTHENGENTIC_CONFIG_DIR", None)

    def _digest(self):
        return (self.auth / "digest.md").read_text(encoding="utf-8")

    def test_record_writes_the_three_files(self):
        learn.record("stop", lint, "You should leverage the robust pipeline.", "s1")
        self.assertTrue((self.auth / "profile.json").exists())
        self.assertTrue((self.auth / "observations.jsonl").exists())
        self.assertTrue((self.auth / "digest.md").exists())
        self.assertIn("slop word", self._digest())

    def test_clean_text_records_nothing(self):
        learn.record("stop", lint, "The service retries a failed upload automatically.", "s1")
        self.assertFalse((self.auth / "profile.json").exists())

    def test_score_accumulates_across_events(self):
        for _ in range(3):
            learn.record("stop", lint, "We should ship it. You should test it.", "s")
        profile = json.loads((self.auth / "profile.json").read_text())
        self.assertGreaterEqual(profile["rules"]["banned_modal"]["score"], 5.0)

    def test_digest_lists_repeated_tokens(self):
        extras = {"slop_word": ["leverage", "robust"]}
        for _ in range(3):
            learn.record("stop", lint, "Leverage the robust thing.", "s", extras)
        self.assertIn("You keep writing: leverage, robust", self._digest())

    def test_digest_is_removed_when_nothing_remains(self):
        learn.record("stop", lint, "You should ship it. You should test it. You should verify it.", "s")
        self.assertTrue((self.auth / "digest.md").exists())
        # Backdate the profile far enough that the score decays below the floor.
        path = self.auth / "profile.json"
        profile = json.loads(path.read_text())
        old = time.time() - 400 * 24 * 60 * 60
        for entry in profile["rules"].values():
            entry["last"] = old
        path.write_text(json.dumps(profile))
        learn.regenerate_digest()
        self.assertFalse((self.auth / "digest.md").exists())

    def test_load_learned_reads_categories(self):
        (self.auth).mkdir(parents=True, exist_ok=True)
        (self.auth / "learned.json").write_text(json.dumps({
            "slop": ["showcase", "boasts"],
            "openers": ["to be clear"],
            "junk": ["ignored"],
        }))
        got = learn.load_learned()
        self.assertEqual(got["slop"], ["showcase", "boasts"])
        self.assertEqual(got["openers"], ["to be clear"])
        self.assertNotIn("junk", got)

    def test_observations_are_capped(self):
        learn.OBSERVATION_CAP = 5
        try:
            for _ in range(10):
                learn.record("stop", lint, "You should ship it.", "s")
            lines = (self.auth / "observations.jsonl").read_text().strip().splitlines()
            self.assertLessEqual(len(lines), 5)
        finally:
            learn.OBSERVATION_CAP = 2000


if __name__ == "__main__":
    unittest.main()
