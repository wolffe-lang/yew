#!/usr/bin/env python3
"""Bounded compiler-memory calibration; never invokes a real compiler."""
import json
import mmap
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PAYLOAD = 128 * 1024 * 1024
ROOT = Path(__file__).resolve().parent.parent


def fixture():
    memory = mmap.mmap(-1, PAYLOAD)
    page = os.sysconf("SC_PAGESIZE")
    for at in range(0, PAYLOAD, page):
        memory[at:at + page] = bytes([(at // page) % 251 + 1]) * page
    assert sum(memory[::page]) > 0
    print("fixture: touched and retained 134217728 bytes")


def lower_bound(work):
    records = work / "fixture-records"
    command = [sys.executable, "-I", str(ROOT / "ci/build-memory.py"),
               "run", "--records", str(records), "--name", "fixture",
               "--", sys.executable, "-I", str(Path(__file__).resolve()), "--fixture"]
    child = subprocess.run(command, check=False)
    completed = list(records.glob("*.done.json"))
    observed = 0
    floor = 0
    if child.returncode == 0 and len(completed) == 1:
        record = json.loads(completed[0].read_text())
        observed = record["peak_bytes"]
        floor = max(record["parent_floor_bytes"], record["child_floor_bytes"])
    if observed < PAYLOAD:
        raise AssertionError("build-memory-fixture-lower-bound observed=%d expected-at-least=%d" %
                             (observed, PAYLOAD))
    if floor >= 32 * 1024 * 1024:
        raise AssertionError("build-memory-reader-floor floor=%d must-be-less-than=33554432" % floor)
    print("PASS build-memory-fixture-lower-bound observed=%d floor=%d" % (observed, floor))


def main():
    if sys.argv[1:] == ["--fixture"]:
        fixture()
        return
    base = Path(os.environ.get("YEW_MEMORY_TEST_ROOT", str(ROOT / "target/build-memory-selftest")))
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reader-", dir=base) as scratch:
        lower_bound(Path(scratch))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print("FAIL " + str(error), flush=True)
        raise SystemExit(1)
