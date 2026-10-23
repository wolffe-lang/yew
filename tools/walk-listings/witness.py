#!/usr/bin/env python3
"""Run two fixture trees against C's finder backend; later compare the port.
No Git commands, no golden generation, no asserted prediction before observation.
"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile

binary = Path(sys.argv[1]).resolve()
base = Path(sys.argv[2]).resolve()
base.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="disk-ignore-", dir=base) as tmp:
    root = Path(tmp)
    exclude = root / "exclude"
    (exclude / ".git/info").mkdir(parents=True)
    (exclude / "blocked.txt").write_text("blocked\n")
    (exclude / "kept.txt").write_text("kept\n")
    (exclude / ".git/info/exclude").write_text("blocked.txt\n")
    nested = root / "nested"
    (nested / "sub/build").mkdir(parents=True)
    (nested / "sub/build/artifact.txt").write_text("artifact\n")
    (nested / "sub/kept.txt").write_text("kept\n")
    (nested / "sub/.gitignore").write_text("/build/\n")
    results = {}
    for name, path, args in (
        ("exclude-only", exclude, []),
        ("nested-anchored", nested, []),
        ("nested-scope-control", nested, ["--scope"]),
    ):
        r = subprocess.run([str(binary), str(path)] + args, capture_output=True, text=True)
        results[name] = {"exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
        if r.returncode:
            raise RuntimeError((name, results[name]))
    (exclude / ".git/info/exclude").rename(exclude / ".git/info/.gitignore")
    r = subprocess.run([str(binary), str(exclude)], capture_output=True, text=True)
    results["info-dotgitignore-control"] = {"exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    if r.returncode:
        raise RuntimeError(results["info-dotgitignore-control"])
    print(json.dumps(results, indent=2, sort_keys=True))
