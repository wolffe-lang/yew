#!/usr/bin/env python3
"""The runtime PTY row must reap a correct child after its PTY closes."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAKE = '''#!{python}
import os
from pathlib import Path
import sys
import time
import tty

tty.setraw(0)
warning = "runtime at /usr/local/share/yew/runtime is not this build's; using the built-in runtime\\n"
Path(os.environ["YEW_LOG"]).write_text(warning)
os.write(1, warning.encode())
wire = bytearray()
while True:
    data = os.read(0, 65536)
    if not data: sys.exit(2)
    wire.extend(data)
    if b"ed.quit_force\\r" in wire:
        Path(sys.argv[-1]).write_bytes(b"first\\nproofsecond\\n")
        os.write(1, b"FINAL_FRAME: quitting\\n")
        # A PTY hangup is not waitpid: the child still has exit work left.
        os.close(0)
        os.close(1)
        os.close(2)
        time.sleep(1.0)
        sys.exit({exit_code})
'''


class RuntimePtyTest(unittest.TestCase):
    def run_fixture(self, exit_code):
        (ROOT / "target").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="runtime-pty-", dir=ROOT / "target") as tmp:
            root = Path(tmp)
            fake = root / "fake-editor"
            fake.write_text(FAKE.format(python=sys.executable, exit_code=exit_code))
            fake.chmod(0o700)
            return subprocess.run([sys.executable, "-I", str(ROOT / "notes/yw09b-evidence/runtime-pty.py"),
                                   "--yew", str(fake), "--runtime", str(ROOT / "runtime"),
                                   "--root", str(root / "row"), "--prefix"],
                                  capture_output=True, text=True, timeout=20,
                                  env=dict(os.environ, SHELL="/bin/sh", TMPDIR=str(root)))

    def test_delayed_exit_after_pty_close_is_not_a_quit_failure(self):
        result = self.run_fixture(0)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("quit_latency_ms=", result.stdout)
        self.assertIn("runtime_prefix_warn_once: ok", result.stdout)

    def test_nonzero_exit_remains_red_and_prints_the_final_wire(self):
        result = self.run_fixture(7)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FINAL_FRAME: quitting", result.stdout)
        self.assertIn("wire_bytes=", result.stdout)
        self.assertIn("quit binding did not answer", result.stderr)


if __name__ == "__main__":
    unittest.main()
