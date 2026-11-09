#!/usr/bin/env python3
"""basecheck.py S1.json S2.json S3.json [--emit OUT --head SHA]

R-yw13r-1 = A's rule for the re-homed Fletch baseline: three sessions of
tools/fl-headless/compare.py at trunk on one P-core block, kept only if
every row's three medians agree within 5 % (max / min - 1), the two
shortest rows (`startup`, `parse_only`) within 10 %. Prints each row's
spread and verdict; exits 1 when the set fails, so it is retaken. With
--emit, writes tools/perf-fletch-baseline.txt: each row the MAXIMUM of the
sessions' medians and of their minimums (yw08's and yw09's rule).
"""
import json, sys

args = sys.argv[1:]
emit = head = None
if '--emit' in args:
    i = args.index('--emit'); emit = args[i + 1]; del args[i:i + 2]
if '--head' in args:
    i = args.index('--head'); head = args[i + 1]; del args[i:i + 2]
reps = [json.load(open(a)) for a in args]
assert len(reps) == 3, 'three sessions'
rows = [{r['name']: r for r in rep['rows'] if r['verdict'] != 'RECORDED'} for rep in reps]
SHORT = ('startup', 'parse_only')
names = list(rows[0])
bad = []
for n in names:
    meds = [r[n]['port_median_ns'] for r in rows]
    spread = max(meds) / min(meds) - 1
    lim = 0.10 if n in SHORT else 0.05
    ok = spread <= lim
    if not ok:
        bad.append(n)
    print(f"{n:<18} medians {' '.join(f'{m:>11}' for m in meds)}  spread {100 * spread:5.2f}% (<= {100 * lim:.0f}%) {'ok' if ok else 'OUT'}")
print(f"basecheck: {len(names) - len(bad)} of {len(names)} rows agree" + (f"; out: {', '.join(bad)} (retake the set)" if bad else '; the set is kept'))
if emit and not bad:
    why = f'yw13r i7-12700KF P-core block CPUs 0-5, trunk {head}, max of 3 quiet sessions'
    lines = [
        '# Port Fletch baselines: the regression gate of tools/fl-headless/compare.py (yw08,',
        "# deliverable 6), in sagitta tests/perf/baselines/fletch_dev.txt's format:",
        '#   <bench> <median_ns> <min_ns> <why>      (the why is required and checked)',
        '# A row regresses when BOTH its median > median x 1.15 AND its min > min x 1.10',
        '# (perf_fletch.c:862-874, integer arithmetic). gc_pause and insert_100k are recorded',
        '# only, as in C.',
        '#',
        '# RE-HOMED by yw13r (R-yw13r-1 = A, notes/yw13r-fuss-rehomed.md): the earlier',
        '# rows were measured on a pool host that is no longer a lane host (the VM rows at',
        "# yw08's head, the editor rows at yw09's), and on the lane host that replaced it",
        '# they were stale both ways: the VM rows ran at 74-97 % of them, the editor rows',
        '# at 100-114 %.',
        '#',
        '# MEASURED on Linux x86-64, an Intel Core i7-12700KF: one block of three P-cores',
        '# and their hyperthreads (CPUs 0-5, taskset), in yew CI\'s image, release tier,',
        f'# wolf 0.2.36, at trunk {head}. Each value is the MAXIMUM over three sessions,',
        "# each in its own take of the block's three locks (nothing else on the block),",
        "# each after the host's one-minute load fell to 3 or under. The set is kept only",
        "# because every row's three medians agree within 5 % (startup and parse_only, the",
        '# two shortest rows, within 10 %); a set that does not is retaken. The record\'s',
        '# perf steps hold a head to these numbers on a P-core block of the same host,',
        '# each after the same wait; the gate is meaningful on this host only, and hosted',
        '# CI runs it advisory (perf_fletch.c:20-30). Sessions and analysis:',
        '# notes/yw13r-evidence/perf/.',
        '',
    ]
    for n in names:
        med = max(r[n]['port_median_ns'] for r in rows)
        mn = max(r[n]['port_min_ns'] for r in rows)
        lines.append(f'{n:<18} {med:>12} {mn:>12}  {why}')
    open(emit, 'w').write('\n'.join(lines) + '\n')
    print(f'basecheck: wrote {emit}')
sys.exit(1 if bad else 0)
