#!/usr/bin/env python3
"""Each benchmark process uses its own default runtime, not the caller's."""
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]


class RuntimeEnvTest(unittest.TestCase):
    def test_c_and_port_runtime_are_isolated_for_every_driver(self):
        module = runpy.run_path(str(ROOT / "tools/fl-headless/compare.py"))
        main = module["main"]
        (ROOT / "target").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="perf-runtime-", dir=ROOT / "target") as tmp:
            root = Path(tmp)
            oracle = root / "oracle"
            (oracle / "runtime").mkdir(parents=True)
            (root / "runtime").mkdir()
            seen = set()

            def run(cmd, **kwargs):
                who = "C" if "oracle" in Path(cmd[0]).name or Path(cmd[0]).name == "fl_smoke" else "port"
                expected = oracle / "runtime" if who == "C" else root / "runtime"
                env = kwargs.get("env", os.environ)
                self.assertEqual(env.get("YEW_RUNTIME_DIR"), str(expected),
                                 f"{who} inherited another editor's runtime: {cmd}")
                seen.add((who, Path(cmd[0]).name))
                if "--perf" in cmd:
                    if who == "C":
                        text = "fib24 0.001 ms gc=0 -> 46368\nmap10k 0.001 ms gc=0 -> 10000\nmotion100k 0.001 ms gc=155 -> 100000\n"
                    else:
                        text = "fib24 elapsed_ns=1000 gc=0 result=46368\nmap10k elapsed_ns=1000 gc=0 result=10000\nmotion100k elapsed_ns=1000 gc=155 result=100000\n"
                else:
                    text = f"{cmd[1]} median_ns=1000 min_ns=1000 budget_ns=5000000 raw=" + ",".join(["1000"] * 12) + "\n"
                return SimpleNamespace(returncode=0, stdout=text, stderr="")

            with patch.dict(main.__globals__, ROOT=root), patch.dict(os.environ, YEW_RUNTIME_DIR="foreign-runtime"), \
                    patch.object(sys, "argv", ["compare.py", "--oracle-tree", str(oracle), "--tier", "native",
                                               "--rows", "fib24,startup,config_reload_500", "--advisory"]), \
                    patch("subprocess.run", side_effect=run):
                with self.assertRaises(SystemExit) as exited:
                    main()
                self.assertEqual(exited.exception.code, 0)
                self.assertEqual(os.environ["YEW_RUNTIME_DIR"], "foreign-runtime")
            self.assertEqual(len(seen), 5)


if __name__ == "__main__":
    unittest.main()
