#!/usr/bin/env python3
"""Verify the inherited tab-session fix; sagitta perf_latency.c:21-22."""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
work = Path(sys.argv[2]).resolve()
work.mkdir(parents=True, exist_ok=True)
text = (root / "tools/run-perf-panes-tabs").read_text()
start = text.index("{\n  i=0\n")
end = text.index('\nn=0\n', start)
block = text[start:end]
expected = (([f"alt+{i}\n" for i in range(1, 10)] + ["t\n", "n\n"]) * 910)[:10000]
expected_bytes = "".join(expected).encode()
for label, code, should_match in (
    ("plant-908", block.replace("-lt 909", "-lt 908"), False),
    ("fixed-909", block, True),
):
    out = work / label
    (out / "tabswitch").mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["bash", "-eu", "-c", 'out="$1"\n' + code, "keys-test", str(out)], capture_output=True)
    data = (out / "tabswitch/navigate.keys").read_bytes()
    actual = result.returncode == 0 and not result.stderr and data == expected_bytes
    print(f"{label}: exit={result.returncode} lines={data.count(bytes([10]))} bytes={len(data)} stderr={result.stderr!r} equal_old_prefix={actual}", flush=True)
    assert actual == should_match, label
    if not should_match:
        assert result.returncode == 0 and not result.stderr, "plant must fail comparison, not shell execution"
print("tab-session: GREEN; plant seen red, fixed session byte-identical (10000 keys)")
