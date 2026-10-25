#!/usr/bin/env python3
"""First five C-stable paired triples; preserve all trials, never select by port."""
import json
import pathlib
import re
import statistics
import subprocess
import sys

out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
shapes = ('fib24', 'map10k', 'motion100k')
keys = [(tier, mode, shape) for tier in ('native', 'release')
        for mode in ('compact', 'nonmoving') for shape in shapes]
accepted = {key: [] for key in keys}
trials = []

def run(argv):
    return subprocess.run(argv, check=True, text=True, capture_output=True).stdout

def c_rows(text):
    return {name: float(ms) * 1e6 for name, ms in
            re.findall(r'^(fib24|map10k|motion100k)\s+([\d.]+) ms', text, re.M)}

for trial in range(1, 21):
    before = run(['target/oracle/sagitta/build/fl_smoke', '--perf', '5'])
    port = {}
    raw = [f'TRIAL={trial} C-before\n{before}']
    for tier, mode, shape in keys:
        text = run([f'target/toyvm/{tier}', 'perf', mode, shape, '5'])
        raw.append(f'TIER={tier} MODE={mode}\n{text}')
        port[tier, mode, shape] = int(re.search(r'best_ns=(\d+)', text)[1])
    after = run(['target/oracle/sagitta/build/fl_smoke', '--perf', '5'])
    raw.append(f'C-after\n{after}')
    (out / f'trial-{trial:02}.log').write_text(''.join(raw))
    a, b = c_rows(before), c_rows(after)
    assert set(a) == set(b) == set(shapes)
    rows = []
    for key in keys:
        tier, mode, shape = key
        stable = max(a[shape], b[shape]) / min(a[shape], b[shape]) <= 1.25
        selected = stable and len(accepted[key]) < 5
        row = dict(trial=trial, tier=tier, mode=mode, shape=shape,
                   c_before_ns=a[shape], c_after_ns=b[shape], port_ns=port[key],
                   stable=stable, selected=selected, ratio=port[key] / a[shape])
        if selected:
            accepted[key].append(row)
        rows.append(row)
    trials.extend(rows)
    print(f'trial={trial} accepted=' + ','.join(str(len(accepted[k])) for k in keys), flush=True)
    if all(len(v) == 5 for v in accepted.values()):
        break
summary = []
for key, rows in accepted.items():
    summary.append(dict(tier=key[0], mode=key[1], shape=key[2],
        trials=[r['trial'] for r in rows], samples=len(rows),
        ratio=statistics.median(r['ratio'] for r in rows) if rows else None,
        c_ns=statistics.median(r['c_before_ns'] for r in rows) if rows else None,
        port_ns=statistics.median(r['port_ns'] for r in rows) if rows else None))
(out / 'measurements.json').write_text(json.dumps(dict(summary=summary, trials=trials), indent=2) + '\n')
print(json.dumps(summary, indent=2))
if any(row['samples'] != 5 for row in summary):
    sys.exit('ERROR: insufficient stable C triples; no performance verdict')
# Deliberately do not convert an observed MISS to a pass. This tool collects
# evidence; the recommendation names native misses separately from release.
for row in summary:
    print(('PASS' if row['ratio'] <= 2 else 'MISS') +
          f" {row['tier']}/{row['mode']}/{row['shape']} ratio={row['ratio']:.3f}")
