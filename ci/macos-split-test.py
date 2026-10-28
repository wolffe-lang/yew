#!/usr/bin/env python3
"""Guard workload preservation and bounded fan-out of the macOS oracle split.

The old run's seeds, campaign switches, native selections, byte counts and
advisory/hard-gate distinction are unchanged. Negative controls below reject
missing work, smaller campaigns, larger fan-out and a stale artifact handoff.
"""
from pathlib import Path
import re

FUZZ = {
    "fuzz_cmdparse": ("against-c-1", "tools/run-fuzz-cmdparse --campaign --against-oracle"),
    "fuzz_panes": ("against-c-1", "tools/run-fuzz-panes --campaign --against-oracle"),
    "fuzz_state": ("against-c-1", "tools/run-fuzz-state --native --campaign --against-oracle --sessions=2000"),
    "fuzz_mouse": ("against-c-1", "tools/run-fuzz-mouse --native --campaign --against-oracle"),
    "fuzz_tabs": ("against-c-2", "tools/run-fuzz-tabs --campaign --against-oracle"),
    "fuzz_groups": ("against-c-2", "tools/run-fuzz-groups --campaign --against-oracle"),
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


def job(text, key):
    match = re.search(r"^  " + re.escape(key) + r":\n(.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)", text, re.M | re.S)
    assert match, "missing job " + key
    return match[1]


def steps(block):
    return [(m[1], m[0]) for m in re.finditer(
        r"^      - name: ([^\n]+)\n(?:(?: {8,}[^\n]*|)\n)*", block, re.M)]


def validate(text):
    oracle = job(text, "oracle")
    fuzz = job(text, "macos-fuzz")
    perf = job(text, "macos-perf")
    assert "    needs: legs\n" in fuzz
    assert "    needs: [legs, oracle]\n" in perf
    assert "family: [against-c-1, against-c-2]" in fuzz
    assert "family: [editor, components]" in perf
    for block in (fuzz, perf):
        assert "    runs-on: macos-latest\n" in block
        assert "    timeout-minutes: 120\n" in block
        assert "      fail-fast: false\n" in block
        assert len(re.findall(r"^        family:", block, re.M)) == 1
        assert "include:" not in block and "exclude:" not in block
    assert "matrix.os == 'macos-latest' && 180 || 210" in oracle
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
        original = [b for n, b in steps(oracle) if n == name]
        assert len(original) == 1 and "runner.os != 'macOS'" in original[0]
        assert "          " + command + "\n" in original[0], "Linux measurement changed"
    for name, block in steps(oracle):
        if name.startswith("build "):
            assert "continue-on-error" not in block, "compile gate became advisory"
    assert "tools/run-perf-cmdcomp --build-only" in oracle
    assert "actions/upload-artifact@v4" in oracle and "if-no-files-found: error" in oracle
    assert "target/perf-cmdcomp/perf-cmdcomp" in oracle and "target/oracle/sagitta" in oracle
    assert "tar -czf target/macos-oracle.tar.gz" in oracle
    assert "actions/download-artifact@v4" in perf and "run-id:" not in perf
    assert 'test "$(cat target/macos-oracle-head)" = "$(git rev-parse HEAD)"' in perf
    assert "tar -xzf target/macos-input/macos-oracle.tar.gz" in perf
    assert "needs: [legs, port, unit, fuzz, checked-cases, oracle, macos-fuzz, macos-perf]" in job(text, "nightly-red")


def main():
    text = (Path(__file__).resolve().parent.parent / ".github/workflows/ci.yml").read_text()
    validate(text)
    mutations = [
        ("--sessions=2000", "--sessions=20"),
        ("family: [against-c-1, against-c-2]", "family: [against-c-1]"),
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
    print("macos-split-test: seven campaigns, six measurements, four added jobs and five negative controls PASS")


if __name__ == "__main__":
    main()
