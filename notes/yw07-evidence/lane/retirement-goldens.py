#!/usr/bin/env python3
"""Run current CI's gated campaign cases unchanged, Linux only, inside ctr."""
from pathlib import Path
import re
import shutil
import subprocess
import sys

root = Path.cwd()
workflow = (root / ".github/workflows/ci.yml").read_text()
cohorts = [
    ("goldens, campaign 01 (yw01's gate; osc52_frame from yw02)", 18),
    ("goldens, campaign 03 (yw03's gate, M-YW3)", 62),
    ("goldens, campaign 04 (yw04's gate, M-YW4)", 104),
    ("goldens, campaign 05 (yw05's gate)", 22),
]
cases = []
for title, expected in cohorts:
    block = workflow.split("      - name: " + title + "\n", 1)[1].split("      - name:", 1)[0]
    names = []
    for words in re.findall(r'^          cases="([^"]*)"$', block, re.M):
        names += words.replace("$cases", "").split()
    assert len(names) == expected and len(set(names)) == expected, (title, len(names))
    cases += names
workspace = (root / "tools/goldens-yw06-cases.txt").read_text().split()
assert len(workspace) == 81
cases += workspace
assert len(cases) == len(set(cases)) == 287
assert all(re.fullmatch(r"[a-z0-9_]+", c) for c in cases)
if "--list-only" in sys.argv:
    print("retirement-goldens: 287 unique gated CI cases")
    raise SystemExit(0)
out = root / "target/yw07/retirement-goldens"
out.mkdir(parents=True, exist_ok=True)
subprocess.run(["tools/goldens", "--yew", "target/release/yew", "--suite", "version,help"], check=True)
for i, case in enumerate(cases, 1):
    print("retirement-goldens", i, len(cases), case, flush=True)
    result = subprocess.run(["tools/goldens", "--yew", "target/release/yew", "--demo", "target/tools/demo_paint",
                             "--suite", "pty", "--case", case])
    log = root / "target/oracle/goldens/pty.log"
    shutil.copyfile(log, out / (case + ".log"))
    if result.returncode or "pty: " + case + ": ok" not in log.read_text().splitlines():
        raise SystemExit("golden STOP: " + case)
print("retirement-goldens: 287/287 GREEN", flush=True)
