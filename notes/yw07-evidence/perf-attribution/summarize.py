#!/usr/bin/env python3
"""Print measured first-event rows and medians; make no causal claim."""
import csv
from pathlib import Path
import re
import statistics
import sys

root = Path(sys.argv[1])
metrics = ("cold_open_to_first_paint", "wolf_kitty_first_backspace_to_paint")
rows = []
for trial in range(1, 4):
    for cell in ("a", "b-prime", "c"):
        text = (root / f"trial-{trial}-{cell}.log").read_text()
        for metric in metrics:
            pattern = (r"^ratio\." + re.escape(metric) +
                       r" wolf/c=([0-9.]+) \(c=(\d+)ns, wolf=(\d+)ns, c again=(\d+)ns, drift=([0-9.]+)\) limit=2.0 verdict=(PASS|FAIL)$")
            matches = re.findall(pattern, text, re.M)
            if len(matches) != 1:
                raise SystemExit(f"missing/duplicate row: trial {trial}, {cell}, {metric}")
            ratio, c, w, c2, drift, verdict = matches[0]
            rows.append((cell, trial, metric, int(c), int(w), int(c2), float(ratio), float(drift), verdict))
with (root / "rows.tsv").open("w") as out:
    writer = csv.writer(out, delimiter="\t")
    writer.writerow(("cell", "trial", "metric", "c_ns", "wolf_ns", "c_again_ns", "ratio", "drift", "verdict"))
    writer.writerows(rows)
print("Cell b-prime = pin + compile compatibility, NOT pin only.")
print("Literal b = BUILD-RED. Backspace follows five motions, Insert, newlines and an idle pause.")
print("cell\tmetric\twolf_ns_median\tc_ns_median\tc_again_ns_median\tpaired_ratio_median\traw_ratios")
for cell in ("a", "b-prime", "c"):
    for metric in metrics:
        subset = [r for r in rows if r[0] == cell and r[2] == metric]
        med = statistics.median
        print(cell, metric, med(r[4] for r in subset), med(r[3] for r in subset),
              med(r[5] for r in subset), f"{med(r[4] / r[3] for r in subset):.3f}",
              ",".join(str(r[6]) for r in subset), sep="\t")
