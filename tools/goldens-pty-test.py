#!/usr/bin/env python3
"""Controls for explicit PTY divergence routing, identity and visibility."""
import contextlib
import hashlib
import io
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("goldens_pty", Path(__file__).with_name("goldens-pty.py"))
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)

class Divergences(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        harness.ROOT = self.root
        self.tree = self.root / "oracle"
        for d in ("tests/pty/goldens", "build", ".docs"):
            (self.tree / d).mkdir(parents=True)
        (self.tree / "tests/pty/registry.c").write_text(" C(plain, x)\n C(ruled, y)\n")
        self.cgold = self.tree / "tests/pty/goldens/ruled.golden"
        self.cgold.write_text("C snapshot\n")
        (self.tree / "tests/pty/goldens/plain.golden").write_text("plain\n")
        self.expected = self.root / "tests/divergences/ruled.golden"
        self.expected.parent.mkdir(parents=True)
        self.expected.write_text("port snapshot\n")
        self.listing = self.root / "divergences.txt"
        self.row = "ruled\truling #135\ttests/divergences/ruled.golden\t" + hashlib.sha256(self.cgold.read_bytes()).hexdigest() + "\n"
        self.listing.write_text(self.row)

    def test_routing_is_named_and_oracle_unchanged(self):
        calls = []
        def run(cmd, cwd, env):
            calls.append((cwd, dict(env)))
            path = cwd / "tests/pty/goldens/ruled.golden"
            self.assertEqual(path.read_text(), "C snapshot\n" if cwd == self.tree else "port snapshot\n")
            self.assertNotIn("YEW_PTY_UPDATE", env)
            return type("Result", (), {"returncode": 0})()
        output = io.StringIO()
        with patch.object(harness.subprocess, "run", side_effect=run), patch.dict(os.environ, YEW_PTY_UPDATE="1"), contextlib.redirect_stdout(output):
            self.assertEqual(harness.run(self.tree, "port", "demo", "", set(), self.listing), 0)
        self.assertIn("DIVERGES (ruling #135) ruled", output.getvalue())
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][0], self.tree)
        self.assertIn("ruled", calls[0][1]["YEW_PTY_EXCLUDE"])
        self.assertEqual(calls[1][1]["YEW_PTY_FILTER"], "ruled")
        self.assertEqual(self.cgold.read_text(), "C snapshot\n")

    def test_changed_c_golden_is_fatal(self):
        self.cgold.write_text("new C rule\n")
        with self.assertRaisesRegex(ValueError, "C golden changed for ruled"):
            harness.entries(self.tree, self.listing)

    def test_unknown_case_is_fatal(self):
        self.listing.write_text(self.row.replace("ruled\t", "typo\t", 1))
        with self.assertRaisesRegex(ValueError, "invalid/duplicate"):
            harness.entries(self.tree, self.listing)

    def test_duplicate_is_fatal(self):
        self.listing.write_text(self.row * 2)
        with self.assertRaisesRegex(ValueError, "invalid/duplicate"):
            harness.entries(self.tree, self.listing)

    def test_snapshot_must_belong_to_port_divergences(self):
        self.listing.write_text(self.row.replace("tests/divergences/ruled.golden", "oracle/tests/pty/goldens/ruled.golden"))
        with self.assertRaisesRegex(ValueError, "invalid port snapshot"):
            harness.entries(self.tree, self.listing)

    def test_unlisted_failure_stays_red(self):
        with patch.object(harness.subprocess, "run", return_value=type("Result", (), {"returncode": 1})()):
            self.assertEqual(harness.run(self.tree, "port", "demo", "plain", set(), self.listing), 1)

if __name__ == "__main__": unittest.main()
