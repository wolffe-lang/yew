#!/usr/bin/env python3
"""Guard workload preservation and bounded fan-out of the macOS oracle split.

The old run's seeds, campaign switches, native selections, byte counts and
advisory/hard-gate distinction are unchanged. Negative controls below reject
missing work, smaller campaigns, larger fan-out and a stale artifact handoff.

yw13 split the linux oracle leg too: its perf_cmdcomp harness build and the
2x gate that runs it are the oracle-cmdcomp job's, which runs where the
linux oracle leg runs; macOS still builds the harness in oracle for
macos-perf. The controls also refuse the harness built on linux in both
jobs and the gate dropped from the new job.

yw13s: the git layer and F mode made the editor's builds heavier, and run
42921677875 (yew#120 at 157841a) cut against-c-1 at its 120-minute cap on
both hosts: linux fuzz_cmdparse 61.3 minutes, then fuzz_panes cut at 57.8;
macOS fuzz_cmdparse 55.1, fuzz_state 16.5, fuzz_mouse 3.7, then fuzz_panes
cut at 43.7. fuzz_panes is now a family of its own on both hosts
(against-c-4 on linux, against-c-3 on macOS). The linux harness build took
55.4 minutes on that run and was cut at its 60-minute step cap on run
42922808966 (60.2); its step cap is 90 and its job's 120. Every cap is at
least 30 % over the slowest time measured for what it holds (a cut time is
a lower bound, so the cap clears it by more).

yw13s, again: runs 42996095311 and 42996771451 cut linux against-c-2 at
its 120 (fuzz_tabs 66.7, then fuzz_groups cut at 52.3) and ran macOS
against-c-2 in 119 (fuzz_tabs 55.1, fuzz_groups 56.8). fuzz_groups is a
family of its own on both hosts (against-c-5 on linux, against-c-4 on
macOS). ci/legs-test.py's L6 holds every job's cap against its slowest
measured time.
"""
from pathlib import Path
import re

FUZZ = {
    "fuzz_cmdparse": ("against-c-1", "tools/run-fuzz-cmdparse --campaign --against-oracle"),
    "fuzz_panes": ("against-c-3", "tools/run-fuzz-panes --campaign --against-oracle"),
    "fuzz_state": ("against-c-1", "tools/run-fuzz-state --native --campaign --against-oracle --sessions=2000"),
    "fuzz_mouse": ("against-c-1", "tools/run-fuzz-mouse --native --campaign --against-oracle"),
    "fuzz_tabs": ("against-c-2", "tools/run-fuzz-tabs --campaign --against-oracle"),
    "fuzz_groups": ("against-c-4", "tools/run-fuzz-groups --campaign --against-oracle"),
    "fuzz_gitignore": ("against-c-2", "tools/run-fuzz-gitignore --native --campaign --against-oracle"),
}
PERF = {
    "perf_cmdcomp": ("components", "PERF_PREBUILT=1 tools/run-perf-cmdcomp --trials 100", 15),
    "the regex engine": ("components", "tools/run-perf-re --bytes 268435456", 20),
    "demo_paint": ("components", "tools/run-perf-latency --starts 10 --keys 100", 10),
    "the editor": ("editor", "tools/run-perf-editor", 60),
    "panes, many buffers": ("editor", "tools/run-perf-panes-tabs", 35),
    "the job stream": ("components", "tools/run-perf-jobstream", 10),
}


# Minutes measured on runs 42921677875 and 42922808966 for what each family
# holds now (setup included); a family whose step was cut counts its cut.
MEASURED = {
    ("fuzz", "against-c-1"): 1.0 + 61.3,             # C's drivers, fuzz_cmdparse
    ("fuzz", "against-c-4"): 1.0 + 57.8,             # fuzz_panes, cut: a lower bound
    ("fuzz", "against-c-2"): 1.0 + 66.7,             # fuzz_tabs
    ("fuzz", "against-c-5"): 1.0 + 55.1,             # fuzz_groups
    ("macos-fuzz", "against-c-2"): 0.8 + 57.1 + 6.9, # fuzz_tabs, fuzz_gitignore
    ("macos-fuzz", "against-c-4"): 0.8 + 56.8,       # fuzz_groups
    ("macos-fuzz", "against-c-1"): 0.8 + 55.1 + 16.5 + 3.7,
    ("macos-fuzz", "against-c-3"): 0.8 + 43.7,       # fuzz_panes, cut: a lower bound
}
CMDCOMP_BUILD = 60.2                                 # cut at the old 60: a lower bound


def job_cap(block, family=None):
    m = re.search(r"^    timeout-minutes: (\d+)$", block, re.M)
    if m:
        return int(m.group(1))
    e = re.search(r"^    timeout-minutes: \$\{\{ matrix\.family == '([^']+)' && (\d+) \|\| (\d+) \}\}$", block, re.M)
    assert e, "no job cap"
    return int(e.group(2)) if family == e.group(1) else int(e.group(3))


def job(text, key):
    match = re.search(r"^  " + re.escape(key) + r":\n(.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)", text, re.M | re.S)
    assert match, "missing job " + key
    return match[1]


def steps(block):
    return [(m[1], m[0]) for m in re.finditer(
        r"^      - name: ([^\n]+)\n(?:(?: {8,}[^\n]*|)\n)*", block, re.M)]


def validate(text):
    oracle = job(text, "oracle")
    cmdcomp = job(text, "oracle-cmdcomp")
    fuzz = job(text, "macos-fuzz")
    perf = job(text, "macos-perf")
    # The linux oracle leg's measurements: the oracle job's non-macOS steps
    # and the oracle-cmdcomp job's, which runs on that leg alone.
    linux = steps(oracle) + steps(cmdcomp)
    assert "    needs: legs\n" in fuzz
    assert "    needs: [legs, oracle]\n" in perf
    assert "family: [against-c-1, against-c-2, against-c-3, against-c-4]" in fuzz
    assert "family: [editor, components]" in perf
    for block in (fuzz, perf):
        assert "    runs-on: macos-latest\n" in block
        assert re.search(r"^    timeout-minutes: (\d+)$", block, re.M) and job_cap(block) >= 120
        assert "      fail-fast: false\n" in block
        assert len(re.findall(r"^        family:", block, re.M)) == 1
        assert "include:" not in block and "exclude:" not in block
    # yw13s: 310. The linux leg took 231 minutes in the nightly 42862922049
    # (270 left 17 %); macOS 198.
    assert "    timeout-minutes: 310\n" in oracle
    # yw11b: the port job's Linux legs are its `tools/build --all` and a
    # minute of checks. At 8967813 (run 42362461870) the ubuntu leg was cut
    # at its 60-minute cap mid-build on the first attempt and took 49
    # minutes on the second; 92e49f5's took 55, trunk's 7009fb2 37
    # (42190104067), the aarch64 leg 46. The cap clears the cut 60 by half
    # again; macOS keeps its 240.
    port = job(text, "port")
    cap = re.search(r"^    timeout-minutes: \$\{\{ matrix\.os == 'macos-latest' && (\d+) \|\| (\d+) \}\}$", port, re.M)
    # yw13s: macOS 250 (its leg took 189 in the nightly 42862922049).
    assert cap is not None and int(cap.group(1)) == 250
    assert int(cap.group(2)) >= 90
    # yw13s: fuzz_panes alone in its family on both hosts, fuzz_cmdparse
    # without it, every cap at least 30 % over the measured time.
    linux_fuzz = job(text, "fuzz")
    assert "        family: [port, port-2, against-c-1, against-c-2, against-c-3, against-c-4, against-c-5]\n" in linux_fuzz
    for name, fam in (("fuzz_cmdparse", "against-c-1"), ("fuzz_panes", "against-c-4"), ("fuzz_tabs", "against-c-2"), ("fuzz_groups", "against-c-5")):
        lb = [b for n, b in steps(linux_fuzz) if n.startswith(name + ",")]
        assert len(lb) == 1 and "matrix.family == '" + fam + "'" in lb[0], "linux " + name
    for key, minutes in MEASURED.items():
        assert job_cap(job(text, key[0]), key[1]) >= 1.3 * minutes, key
    fs = [(n, b) for n, b in steps(fuzz) if n.startswith("fuzz_")]
    assert len(fs) == len(FUZZ) == 7
    assert not any(n.startswith("fuzz_") for n, _ in steps(oracle))
    for prefix, (family, command) in FUZZ.items():
        matches = [b for n, b in fs if n.startswith(prefix + ",")]
        assert len(matches) == 1, prefix
        block = matches[0]
        assert "matrix.family == '" + family + "'" in block
        assert "        run: " + command + "\n" in block, prefix
        assert "continue-on-error" not in block
        assert command + "\n" in job(text, "fuzz"), "Linux campaign changed"
    ps = [(n, b) for n, b in steps(perf) if n.startswith("the 2× gate,")]
    assert len(ps) == len(PERF) == 6
    for prefix, (family, command, timeout) in PERF.items():
        matches = [(n, b) for n, b in ps if n.startswith("the 2× gate, " + prefix)]
        assert len(matches) == 1, prefix
        name, block = matches[0]
        assert "matrix.family == '" + family + "'" in block
        assert "          " + command + "\n" in block, prefix
        assert f"        timeout-minutes: {timeout}\n" in block
        assert "continue-on-error: true" in block and "::warning::continue-on-error:" in block
        original = [b for n, b in linux if n == name]
        assert len(original) == 1, "Linux measurement missing or doubled: " + prefix
        assert "runner.os != 'macOS'" in original[0] or original[0] in [b for _, b in steps(cmdcomp)]
        assert "          " + command + "\n" in original[0], "Linux measurement changed"
    for name, block in linux:
        if name.startswith("build "):
            assert "continue-on-error" not in block, "compile gate became advisory"
    assert "tools/run-perf-cmdcomp --build-only" in oracle
    # The harness is built once per leg: oracle on macOS, oracle-cmdcomp on linux.
    built = [b for n, b in steps(oracle) if n == "build perf_cmdcomp harnesses (hard gate)"]
    assert len(built) == 1 and "if: matrix.port && runner.os == 'macOS'\n" in built[0], "linux harness built twice"
    moved = [b for n, b in steps(cmdcomp) if n == "build perf_cmdcomp harnesses (hard gate)"]
    assert len(moved) == 1 and "tools/run-perf-cmdcomp --build-only\n" in moved[0]
    step_cap = re.search(r"^        timeout-minutes: (\d+)$", moved[0], re.M)
    assert "python3 -I tools/check-perf-cmdcomp-build\n" in moved[0] and step_cap is not None
    assert int(step_cap.group(1)) >= 1.3 * CMDCOMP_BUILD and int(step_cap.group(1)) == 90
    assert job_cap(cmdcomp) >= int(step_cap.group(1)) + 15 + 10, "the job's cap holds the build, the gate and setup"
    assert "    needs: legs\n" in cmdcomp and "    runs-on: ubuntu-latest\n" in cmdcomp
    assert "    if: ${{ contains(needs.legs.outputs.matrix_oracle, 'ubuntu-latest') }}\n" in cmdcomp
    assert "actions/upload-artifact@v4" in oracle and "if-no-files-found: error" in oracle
    assert "target/perf-cmdcomp/perf-cmdcomp" in oracle and "target/oracle/sagitta" in oracle
    assert "tar -czf target/macos-oracle.tar.gz" in oracle
    assert "actions/download-artifact@v4" in perf and "run-id:" not in perf
    assert 'test "$(cat target/macos-oracle-head)" = "$(git rev-parse HEAD)"' in perf
    assert "tar -xzf target/macos-input/macos-oracle.tar.gz" in perf
    assert "needs: [legs, port, unit, macos-unit, fuzz, checked-cases, oracle, oracle-cmdcomp, macos-fuzz, macos-perf]" in job(text, "nightly-red")


def main():
    text = (Path(__file__).resolve().parent.parent / ".github/workflows/ci.yml").read_text()
    validate(text)
    mutations = [
        ("--sessions=2000", "--sessions=20"),
        ("family: [against-c-1, against-c-2, against-c-3, against-c-4]", "family: [against-c-1, against-c-2, against-c-3]"),
        ("family: [editor, components]", "family: [editor, components, extra]"),
        ('test "$(cat target/macos-oracle-head)" = "$(git rev-parse HEAD)"', "true"),
        ("        timeout-minutes: 60\n", "        timeout-minutes: 15\n"),
    ]
    for old, new in mutations:
        # Mutate the macOS slice, not its unchanged Linux reference.
        start = text.index("  macos-fuzz:\n")
        assert old in text[start:]
        broken = text[:start] + text[start:].replace(old, new, 1)
        try:
            validate(broken)
        except AssertionError:
            continue
        raise AssertionError("control accepted regression: " + old)
    # The linux split's controls: the harness built on linux in oracle again
    # (twice per run), and the moved 2x gate dropped from oracle-cmdcomp.
    cmd_start = text.index("  oracle-cmdcomp:\n")
    linux_controls = [
        (0, "        if: matrix.port && runner.os == 'macOS'\n        timeout-minutes: 60\n", "        if: matrix.port\n        timeout-minutes: 60\n"),
        (cmd_start, "          PERF_PREBUILT=1 tools/run-perf-cmdcomp --trials 100\n", "          true\n"),
    ]
    for start, old, new in linux_controls:
        assert old in text[start:], old
        broken = text[:start] + text[start:].replace(old, new, 1)
        try:
            validate(broken)
        except AssertionError:
            continue
        raise AssertionError("control accepted regression: " + old)
    # yw13s's controls: fuzz_panes back beside fuzz_cmdparse on linux, and
    # the harness build's step cap back at 60.
    for old, new in (
        ("family: [port, port-2, against-c-1, against-c-2, against-c-3, against-c-4, against-c-5]", "family: [port, port-2, against-c-1, against-c-2, against-c-3, against-c-4]"),
        ("        if: ${{ !cancelled() && matrix.family == 'against-c-4' }}\n", "        if: ${{ !cancelled() && matrix.family == 'against-c-1' }}\n"),
    ):
        assert old in text, old
        broken = text.replace(old, new, 1)
        try:
            validate(broken)
        except AssertionError:
            continue
        raise AssertionError("control accepted regression: " + old)
    start = text.index("  oracle-cmdcomp:\n")
    old = "      - name: build perf_cmdcomp harnesses (hard gate)\n        timeout-minutes: 90\n"
    assert old in text[start:], old
    broken = text[:start] + text[start:].replace(old, old.replace("90", "60"), 1)
    try:
        validate(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("control accepted regression: the harness build's cap at 60")
    print("macos-split-test: seven campaigns, six measurements, five added jobs, the measured caps and ten negative controls PASS")


if __name__ == "__main__":
    main()
