#!/usr/bin/env python3
"""Bounded compiler-memory calibration; never invokes a real compiler."""
import contextlib
import hashlib
import importlib.util
import io
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


def module():
    spec = importlib.util.spec_from_file_location("build_memory", ROOT / "ci/build-memory.py")
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    return reader


def controls(work):
    reader = module()
    assert reader.rss_bytes(123, "linux") == 123 * 1024
    assert reader.rss_bytes(123, "darwin") == 123
    try:
        reader.rss_bytes(1, "unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported platform accepted")
    assert reader.status_code(2 << 8) == 2
    assert reader.status_code(9) == -9
    assert reader.physical_total("linux", "MemTotal: 123 kB\n") == 125952
    if reader.exceeds(85, 100, 85) or not reader.exceeds(86, 100, 85):
        raise AssertionError("build-memory-share-gate threshold equality/one-byte-over")
    assert reader.build_name(["build", "src/a.lu", "-o", "out"]) == ("src/a.lu -> out", "native")
    assert reader.build_name(["build", "--release", "src/a.lu"])[1] == "release"
    records = work / "fixture-records"
    started, rows, errors = reader.read_records(records)
    assert started == len(rows) == 1 and not errors
    original = rows[0]
    larger = dict(original, name="larger", peak_bytes=original["peak_bytes"] + 1)
    assert reader.largest([original, original, larger]) == larger
    assert reader.largest([dict(original, name="z"), dict(original, name="a")])["name"] == "a"
    summary = work / "summary"
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        assert reader.report(records, "fixture", "{}", str(summary), False, 1) == 0
    line = output.getvalue().strip()
    assert line.startswith("build-memory ") and line in summary.read_text()
    result = json.loads(line.removeprefix("build-memory "))
    assert result["policy"] == "report-only"
    assert result["margin_bytes"] == result["runner_total_bytes"] - result["peak_bytes"]
    assert result["native_largest"] == "fixture"
    assert json.loads((records / "report.json").read_text()) == result
    print("PASS build-memory-share-gate")
    # Policy boundaries below use a synthetic denominator, never an assumption
    # about this host's physical memory.
    empty = work / "empty"
    empty.mkdir()
    with contextlib.redirect_stdout(io.StringIO()) as output:
        assert reader.report(empty, "checked-cases", "{}", None, True, 85) == 0
    assert json.loads(output.getvalue().removeprefix("build-memory "))["peak_bytes"] is None
    reader.atomic_json(records / "missing.start.json", {"schema": 1})
    assert reader.read_records(records)[2]
    with contextlib.redirect_stdout(io.StringIO()):
        assert reader.report(records, "fixture", "{}", None, True, 85) == 1
    (records / "missing.start.json").unlink()
    completion = next(records.glob("*.done.json"))
    completion.write_text("{broken")
    assert reader.read_records(records)[2]
    reader.atomic_json(completion, original)
    # Synthetic denominator and complete records exercise negative margins and
    # exact policy boundaries without a second allocation or hardware fiction.
    real_total, real_effective = reader.physical_total, reader.effective_total
    reader.physical_total = lambda: 100
    reader.effective_total = lambda total: 100
    saved = dict(original)
    for peak, expected in ((85, 0), (86, 1), (101, 1)):
        record = dict(original, platform="darwin", raw_unit="bytes", raw_maxrss=peak, peak_bytes=peak)
        start = {key: record[key] for key in ("schema", "id", "name", "tier", "argv", "cwd", "compiler", "platform", "raw_unit")}
        reader.atomic_json(records / (record["id"] + ".start.json"), start)
        reader.atomic_json(completion, record)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            assert reader.report(records, "fixture", "{}", None, True, 85) == expected
        assert json.loads(output.getvalue().removeprefix("build-memory "))["margin_bytes"] == 100 - peak
    reader.physical_total, reader.effective_total = real_total, real_effective
    reader.atomic_json(completion, saved)
    reader.atomic_json(records / (saved["id"] + ".start.json"),
                       {key: saved[key] for key in ("schema", "id", "name", "tier", "argv", "cwd", "compiler", "platform", "raw_unit")})
    print("PASS build-memory-reader-controls")
    parallel = work / "parallel"
    children = [subprocess.Popen([sys.executable, "-I", str(ROOT / "ci/build-memory.py"),
                                 "run", "--records", str(parallel), "--name", str(index),
                                 "--", sys.executable, "-I", "-c", "pass"])
                for index in range(2)]
    assert [child.wait() for child in children] == [0, 0]
    started, rows, errors = reader.read_records(parallel)
    assert started == len(rows) == 2 and not errors
    print("PASS build-memory-concurrent-records")


def transport(work):
    root = work / "fake"
    (root / "tools").mkdir(parents=True)
    (root / "ci").mkdir()
    (root / ".wolf-bin/std").mkdir(parents=True)
    for name in ("lib-toolchain.sh", "lib-toml.sh", "wolf-memory", "build", "check-test"):
        (root / "tools" / name).write_bytes((ROOT / "tools" / name).read_bytes())
        (root / "tools" / name).chmod(0o755)
    (root / "ci/build-memory.py").write_bytes((ROOT / "ci/build-memory.py").read_bytes())
    manifest = (ROOT / "wolf-toolchain.toml").read_text()
    (root / "wolf-toolchain.toml").write_text(manifest)
    def pin(section, key):
        block = manifest.split("[" + section + "]", 1)[1].split("[", 1)[0]
        return next(line.split('"')[1] for line in block.splitlines() if line.startswith(key + " ="))
    fake = '''#!{python}
import json,os,sys
if sys.argv[1:] == ["--version"]:
    print({identity!r}); raise SystemExit(0)
if sys.argv[1:2] == ["probe"]:
    assert sys.stdin.read() == "input", "stdin changed"
with open(os.environ["FAKE_COMMANDS"], "a") as stream:
    stream.write(json.dumps({{"argv":sys.argv[1:],"cwd":os.getcwd(),"std":os.environ.get("WOLF_STD")}})+"\\n")
if sys.argv[1:2] == ["build"]:
    output=sys.argv[sys.argv.index("-o")+1]
    with open(output,"w") as stream: stream.write("#!/bin/sh\\nexit 0\\n")
    os.chmod(output,0o755)
print("fake stdout")
print("fake stderr",file=sys.stderr)
raise SystemExit(int(os.environ.get("FAKE_EXIT","0")))
'''
    for tool in ("wolf", "lupin"):
        path = root / ".wolf-bin" / tool
        path.write_text(fake.format(python=sys.executable, identity=pin(tool, "version_line")))
        path.chmod(0o755)
    (root / ".wolf-bin/libwolf_rt.a").touch()
    (root / ".wolf-bin/std/STD-REV").write_text(pin("std", "rev") + "\n")
    (root / "src").mkdir()
    for name in ("a_test.lu", "b_test.lu", "c_test.lu"):
        (root / "src" / name).touch()
    sequences = []
    for enabled in ("0", "1"):
        commands = work / ("commands-" + enabled)
        env = dict(os.environ, YEW_ROOT=str(root), WOLF_STD=str(root / ".wolf-bin/std"),
                   WOLF_BIN=str(root / ".wolf-bin/wolf"), LUPIN_BIN=str(root / ".wolf-bin/lupin"),
                   YEW_BUILD_MEMORY=enabled, YEW_BUILD_MEMORY_DIR=str(work / ("transport-" + enabled)),
                   FAKE_COMMANDS=str(commands), SHELL="/bin/sh", HOME=str(work))
        for script in (["sh", "tools/build", "--all"],
                       ["sh", "tools/check-test", "--native", "--shard", "1/2"]):
            result = subprocess.run(script, cwd=root, env=env, capture_output=True, text=True)
            assert result.returncode == 0, result.stderr
        # Re-source and prove exit 2, streams, quoting and non-build pass-through.
        env["FAKE_EXIT"] = "2"
        script = '. tools/lib-toolchain.sh; . tools/lib-toolchain.sh; "$WOLF" probe "space argument"'
        result = subprocess.run(["sh", "-c", script], cwd=root, env=env, input="input", capture_output=True, text=True)
        assert result.returncode == 2 and "fake stdout" in result.stdout and "fake stderr" in result.stderr
        script = '. tools/lib-toolchain.sh; "$WOLF" build --deny-warnings src/a_test.lu -o target/tests/exit2'
        result = subprocess.run(["sh", "-c", script], cwd=root, env=env, capture_output=True, text=True)
        assert result.returncode == 2, "build exit 2 was masked"
        sequences.append(commands.read_text())
        if enabled == "1":
            started, rows, errors = module().read_records(Path(env["YEW_BUILD_MEMORY_DIR"]))
            assert started == len(rows) == 5 and not errors  # 2 tiers, 2 shard files, exit-2 build
            assert [row["exit_code"] for row in rows].count(2) == 1
            assert len([row for row in rows if row["tier"] == "release"]) == 1
    assert sequences[0] == sequences[1], "opt-in changed argv/cwd/std or shard selection"
    print("PASS build-memory-command-transport")


def path_only_caller(work):
    """$WOLF handed on as a bare path, the way tools/check-test-cases hands it on.

    That tool sources the toolchain library in a subshell and keeps only the
    printed path, so nothing else the library exported reaches the compiler's
    environment. The observer must still run the real compiler unchanged."""
    root = work / "path-only"
    (root / "tools").mkdir(parents=True)
    (root / "ci").mkdir()
    (root / ".wolf-bin/std").mkdir(parents=True)
    for name in ("lib-toolchain.sh", "lib-toml.sh", "wolf-memory", "check-test-cases"):
        (root / "tools" / name).write_bytes((ROOT / "tools" / name).read_bytes())
        (root / "tools" / name).chmod(0o755)
    (root / "ci/build-memory.py").write_bytes((ROOT / "ci/build-memory.py").read_bytes())
    manifest = (ROOT / "wolf-toolchain.toml").read_text()
    (root / "wolf-toolchain.toml").write_text(manifest)
    def pin(section, key):
        block = manifest.split("[" + section + "]", 1)[1].split("[", 1)[0]
        return next(line.split('"')[1] for line in block.splitlines() if line.startswith(key + " ="))
    fake = '''#!{python}
import json,sys
if sys.argv[1:] == ["--version"]:
    print({identity!r}); raise SystemExit(0)
if sys.argv[1:2] == ["conform-run"]:
    print(json.dumps({{"verdict":"exit(0)","stdout_inline":"a case: PASS"}})); raise SystemExit(0)
if sys.argv[1:2] == ["build"]:
    with open(sys.argv[sys.argv.index("-o")+1],"w") as stream: stream.write("built\\n")
    raise SystemExit(0)
raise SystemExit(3)
'''
    for tool in ("wolf", "lupin"):
        path = root / ".wolf-bin" / tool
        path.write_text(fake.format(python=sys.executable, identity=pin(tool, "version_line")))
        path.chmod(0o755)
    (root / ".wolf-bin/libwolf_rt.a").touch()
    (root / ".wolf-bin/std/STD-REV").write_text(pin("std", "rev") + "\n")
    (root / "tools/check-test-cases.txt").write_text("src/a_test.lu YEW_A_FIXTURE @wsstate-invalid\n")
    invalid = root / "tests/unit/fixtures/wsstate/v1/invalid"
    invalid.mkdir(parents=True)
    for name in ("one.fl", "two.fl"):
        (invalid / name).touch()
    (root / "src").mkdir()
    (root / "src/a_test.lu").touch()
    # Only what a job step has: no WOLF_BIN, nothing the library exports.
    records = work / "path-only-records"
    env = {"PATH": os.environ["PATH"], "HOME": str(work), "SHELL": "/bin/sh", "LANG": "C.UTF-8",
           "YEW_BUILD_MEMORY": "1", "YEW_BUILD_MEMORY_DIR": str(records)}
    child = subprocess.run([sys.executable, "-I", "tools/check-test-cases", "src/a_test.lu"],
                           cwd=root, env=env, capture_output=True, text=True)
    if child.returncode != 0 or "2 cases over 1 files, 0 red" not in child.stdout:
        red = next((line for line in child.stdout.splitlines() if ": RED " in line), child.stderr.strip()[-200:])
        raise AssertionError("build-memory-path-only-caller check-test-cases exit=%d %s" % (child.returncode, red))
    env["YEW_ROOT"] = str(root)
    probe = subprocess.run(["sh", "-c", '. tools/lib-toolchain.sh && printf "%s" "$WOLF"'],
                           cwd=root, env=env, capture_output=True, text=True)
    wolf = probe.stdout
    if probe.returncode != 0 or wolf != str(root / "tools/wolf-memory"):
        raise AssertionError("build-memory-path-only-caller probe exit=%d wolf=%r" % (probe.returncode, wolf))
    built = work / "path-only-built"
    child = subprocess.run([wolf, "build", "src/a_test.lu", "-o", str(built)],
                           cwd=root, env=env, capture_output=True, text=True)
    started, rows, errors = module().read_records(records)
    real = [row["argv"][0] for row in rows]
    if child.returncode != 0 or not built.exists() or started != 1 or errors or real != [str(root / ".wolf-bin/wolf")]:
        raise AssertionError("build-memory-path-only-caller build exit=%d started=%d real=%r errors=%r" %
                             (child.returncode, started, real, errors))
    # A compiler that cannot be found, or that is the observer itself, is
    # refused in one line; never a traceback, never a loop.
    child = subprocess.run([wolf, "conform-run"], cwd=root, env=dict(env, WOLF_BIN=wolf),
                           capture_output=True, text=True, timeout=30)
    if child.returncode != 127 or "Traceback" in child.stderr or not child.stderr.startswith("wolf-memory: "):
        raise AssertionError("build-memory-path-only-caller refusal exit=%d stderr=%r" %
                             (child.returncode, child.stderr.strip()[-200:]))
    print("PASS build-memory-path-only-caller")


def no_build_families(work):
    """A job that builds nothing by design says so, with nothing an enforcing
    gate could fail on; a job that should build and observed none is not-run."""
    cases = (("checked-cases", {"shard": 1}, "no-explicit-wolf-builds", 0),
             ("oracle", {"os": "ubuntu-24.04-arm", "port": False}, "no-explicit-wolf-builds", 0),
             ("macos-perf", {"family": "editor"}, "no-explicit-wolf-builds", 0),
             ("macos-perf", {"family": "components"}, "not-run", 1),
             ("unit", {"shard": 1}, "not-run", 1))
    env = {"PATH": os.environ["PATH"], "HOME": str(work), "LANG": "C.UTF-8",
           "YEW_BUILD_MEMORY_ENFORCE": "1", "YEW_BUILD_MEMORY_LIMIT_PERCENT": "85"}
    for index, (job, matrix, state, code) in enumerate(cases):
        child = subprocess.run([sys.executable, "-I", str(ROOT / "ci/build-memory.py"), "report",
                                "--records", str(work / ("families-%d" % index)),
                                "--job", job, "--matrix", json.dumps(matrix)],
                               env=env, capture_output=True, text=True)
        line = next((l for l in child.stdout.splitlines() if l.startswith("build-memory ")), "")
        got = json.loads(line.removeprefix("build-memory ")) if line else {}
        if got.get("state") != state or child.returncode != code or (code == 0 and got.get("errors")):
            raise AssertionError("build-memory-no-build-families %s %s state=%s exit=%d" %
                                 (job, json.dumps(matrix), got.get("state"), child.returncode))
    print("PASS build-memory-no-build-families")


WORKFLOWS = {
    ".github/workflows/ci.yml": "99b6b77edccab30f4e9e0fc97fc5d98adc3955436fbc74967b1d0b2b403667ed",
    ".github/workflows/toyvm.yml": "dd36e8c9db62dfe80a252f6a064524b528762d0a48646984fbca54a7d70dd89f",
    ".github/workflows/float-hosts.yml": "73ee4db9283aedc1c4c782dbbd1320a5f29305e1fb612410be013278c4347373",
}
JOBS = {"port", "unit", "macos-unit", "fuzz", "checked-cases", "oracle", "oracle-cmdcomp", "macos-fuzz", "macos-perf"}


def workflow_workload(text):
    kept = []
    observer = False
    root_env = False
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line == "env:":
            root_env = True
            continue
        if root_env and line.startswith("  "):
            assert line.split(":", 1)[0].strip() in {
                "YEW_BUILD_MEMORY", "YEW_BUILD_MEMORY_ENFORCE", "YEW_BUILD_MEMORY_LIMIT_PERCENT"}
            continue
        root_env = False
        if line.startswith("      - name: compiler memory "):
            observer = True
            continue
        if observer and line.startswith("        "):
            continue
        observer = False
        kept.append(line.rstrip())
    return hashlib.sha256("\n".join(kept).encode()).hexdigest()


def workflow_controls():
    import re
    for path, digest in WORKFLOWS.items():
        text = (ROOT / path).read_text()
        assert workflow_workload(text) == digest, "build-memory-workload-preserved " + path
        if path.endswith("float-hosts.yml"):
            continue
        assert "  YEW_BUILD_MEMORY_ENFORCE: '0'" in text, "share gate must remain OFF"
        jobs = re.split(r"^  ([a-z][a-z0-9-]*):\n", text, flags=re.M)
        reporters = set()
        for index in range(1, len(jobs), 2):
            name, block = jobs[index:index + 2]
            if "- name: compiler memory report" in block:
                reporters.add(name)
                assert block.count("- name: compiler memory report") == 1
                assert "        if: ${{ always() }}" in block
                assert block.count("- name: compiler memory baseline artifact") == 1
                assert "          retention-days: 30" in block
                assert "          path: ${{ runner.temp }}/yew-build-memory/" in block
        assert reporters == (JOBS if path.endswith("ci.yml") else {"collector"}), reporters
        if path.endswith("ci.yml"):
            broken = text.replace("        run: tools/build --all", "        run: tools/build --native", 1)
            assert workflow_workload(broken) != digest, "native-build mutation was accepted"
    # Existing planner/split guards are pure controls, never compiler builds.
    for name in ("legs-test.py", "macos-split-test.py"):
        child = subprocess.run([sys.executable, "-I", str(ROOT / "ci" / name)], capture_output=True, text=True)
        assert child.returncode == 0, child.stdout + child.stderr
        print(child.stdout.strip())
    print("PASS build-memory-workload-preserved")


def main():
    if sys.argv[1:] == ["--fixture"]:
        fixture()
        return
    base = Path(os.environ.get("YEW_MEMORY_TEST_ROOT", str(ROOT / "target/build-memory-selftest")))
    base.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reader-", dir=base) as scratch:
        work = Path(scratch)
        lower_bound(work)
        controls(work)
        transport(work)
        path_only_caller(work)
        no_build_families(work)
        if "--workflows" in sys.argv[1:]:
            workflow_controls()


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print("FAIL " + str(error), flush=True)
        raise SystemExit(1)
