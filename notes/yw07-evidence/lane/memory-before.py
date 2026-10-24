#!/usr/bin/env python3
"""Strict wrapper around yw05's unchanged PTY RSS instrument; run inside ctr."""
from pathlib import Path
import hashlib
from datetime import datetime, timezone
import os
import re
import shutil
import subprocess
import sys

root = Path.cwd()
base = root / ("target/yw07/memory-before-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
base.mkdir(parents=True, exist_ok=False)
print("memory-before output:", base, flush=True)
driver = root / "notes/yw05-evidence/hot/ptymem-hot.py"
binaries = [("C", root / "target/oracle/sagitta/build/yew"),
            ("port", root / "target/release/yew")]
for label, binary in binaries:
    print(label, hashlib.sha256(binary.read_bytes()).hexdigest(), flush=True)
for phase in ("prompt-menu", "lines40", "pane-lines40"):
    for label, binary in binaries:
        run = base / (phase + "-" + label)
        run.mkdir(exist_ok=False)
        for part in ("home", "config", "state", "cache"):
            (run / part).mkdir()
        path = base / "m.txt"
        shutil.copyfile(root / "README.md", path)
        env = dict(os.environ, HOME=str(run / "home"), XDG_CONFIG_HOME=str(run / "config"),
                   XDG_STATE_HOME=str(run / "state"), XDG_CACHE_HOME=str(run / "cache"),
                   YEW_RUNTIME_DIR=str(root / "runtime"))
        result = subprocess.run([sys.executable, "-I", str(driver), str(binary), str(path), "1000", phase],
                                env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (run / "result.log").write_text(result.stdout)
        print(label, result.stdout, end="", flush=True)
        if result.returncode or "killed" in result.stdout or not re.search(r"n=1000 rss_kb before=\d+ after=\d+", result.stdout):
            raise SystemExit("memory-before: driver failed or editor did not quit: " + str(run))
print("memory-before: six observations recorded; not an after-change claim", flush=True)
