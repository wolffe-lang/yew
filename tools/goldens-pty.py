#!/usr/bin/env python3
"""Run C's PTY runner; named, digest-pinned divergences use port snapshots.

The oracle checkout is read-only. Only divergent cases run in a shadow cwd,
whose golden entries point at the port's snapshots. Every other case runs
in the original oracle cwd against the original C golden.
"""
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def entries(tree, listing):
    rows = {}
    names = set(re.findall(r"^\s*C\(([a-z0-9_]+),", (tree / "tests/pty/registry.c").read_text(), re.M))
    for n, line in enumerate(listing.read_text().splitlines(), 1):
        if not line.strip() or line.startswith("#"): continue
        fields = line.split("\t")
        if len(fields) != 4: raise ValueError(f"{listing}:{n}: expected four tab-separated fields")
        case, ruling, expected, sha = fields
        if case not in names or case in rows: raise ValueError(f"invalid/duplicate divergence {case}")
        if not re.fullmatch(r"ruling #[0-9]+", ruling): raise ValueError(f"invalid ruling for {case}")
        path = (ROOT / expected).resolve()
        if not path.is_relative_to((ROOT / "tests/divergences").resolve()) or not path.is_file():
            raise ValueError(f"invalid port snapshot for {case}")
        golden = tree / f"tests/pty/goldens/{case}.golden"
        actual = hashlib.sha256(golden.read_bytes()).hexdigest()
        if not re.fullmatch(r"[0-9a-f]{64}", sha) or actual != sha:
            raise ValueError(f"C golden changed for {case}: expected {sha}, got {actual}; re-evaluate divergence")
        rows[case] = (ruling, path)
    return names, rows

def shadow(tree, out, rows):
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    for item in tree.iterdir():
        if item.name != "tests": (out / item.name).symlink_to(item, target_is_directory=item.is_dir())
    (out / "tests/pty/goldens").mkdir(parents=True)
    for item in (tree / "tests").iterdir():
        if item.name != "pty": (out / "tests" / item.name).symlink_to(item, target_is_directory=item.is_dir())
    for item in (tree / "tests/pty").iterdir():
        if item.name != "goldens": (out / "tests/pty" / item.name).symlink_to(item, target_is_directory=item.is_dir())
    for item in (tree / "tests/pty/goldens").iterdir():
        replacement = rows.get(item.stem)
        (out / "tests/pty/goldens" / item.name).symlink_to(replacement[1] if replacement else item)
    return out

def run(tree, binary, demo, filt, excluded, listing):
    names, rows = entries(tree, listing)
    selected = {name for name in names if filt in name and name not in excluded}
    if not selected: raise ValueError("filter selected no cases")
    env = dict(os.environ, YEW_PTY_BUDGET_MS="1350000", YEW_PTY_CASE_BUDGET_MS="20000")
    # The harness never updates a snapshot, including through inherited env.
    env.pop("YEW_PTY_UPDATE", None)
    cmd = [str(tree / "build/pty_runner"), "--demo", demo, "--yew", binary]
    status = 0
    normal = selected - rows.keys()
    if normal:
        env.update(YEW_PTY_FILTER=filt, YEW_PTY_EXCLUDE=",".join(sorted(excluded | rows.keys())))
        status |= subprocess.run(cmd, cwd=tree, env=env).returncode
    divergent = selected & rows.keys()
    if divergent:
        cwd = shadow(tree, ROOT / "target/oracle/divergent-pty", rows)
        for case in sorted(divergent):
            ruling, _ = rows[case]
            env.update(YEW_PTY_FILTER=case, YEW_PTY_EXCLUDE=",".join(sorted(names - {case})))
            status |= subprocess.run(cmd, cwd=cwd, env=env).returncode
            print(f"DIVERGES ({ruling}) {case}", flush=True)
    return status

if __name__ == "__main__":
    try:
        tree, binary, demo, filt, exclude = sys.argv[1:]
        sys.exit(run(Path(tree).resolve(), binary, demo, filt, set(filter(None, exclude.split(","))), ROOT / "tools/goldens-divergences.txt"))
    except (ValueError, OSError) as error:
        print(f"goldens: divergence configuration error: {error}", file=sys.stderr)
        sys.exit(2)
