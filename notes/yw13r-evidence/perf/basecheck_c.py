#!/usr/bin/env python3
"""basecheck_c.py S1.json ... S5.json [--emit OUT --head SHA --group G]

R-yw13r-3 = (c), the re-homed Fletch baseline's rule: five fresh
consecutive sessions of tools/fl-headless/compare.py at trunk, on one
P-core block, each under the load gate. For each row, the sessions within
5 % of that row's median of the five (10 % for the two shortest rows,
`startup` and `parse_only`) are its kept sessions; its baseline median is
the maximum of their medians and its baseline minimum the maximum of their
minimums (yw08's and yw09's max rule, over the kept sessions). The group is
kept only if every row has at least three kept sessions. Prints each row's
medians, its dropped sessions and why, and the verdict; exits 1 when the
group fails (the next five are taken). With --emit, writes
tools/perf-fletch-baseline.txt.
"""
import json, statistics, sys

args = sys.argv[1:]
opts = {}
for k in ('--emit', '--head', '--group'):
    if k in args:
        i = args.index(k); opts[k] = args[i + 1]; del args[i:i + 2]
reps = [json.load(open(a)) for a in args]
assert len(reps) == 5, 'five sessions'
rows = [{r['name']: r for r in rep['rows'] if r['verdict'] != 'RECORDED'} for rep in reps]
SHORT = ('startup', 'parse_only')
names = list(rows[0])
out, failed = {}, []
for n in names:
    meds = [r[n]['port_median_ns'] for r in rows]
    mins = [r[n]['port_min_ns'] for r in rows]
    m = statistics.median(meds)
    lim = 0.10 if n in SHORT else 0.05
    kept, dropped = [], []
    for k, v in enumerate(meds):
        dev = v / m - 1
        if abs(dev) <= lim:
            kept.append(k)
        else:
            dropped.append(f's{k + 1} {100 * dev:+.1f}%')
    ok = len(kept) >= 3
    if not ok:
        failed.append(n)
    out[n] = (max(meds[k] for k in kept), max(mins[k] for k in kept)) if kept else (0, 0)
    print(f"{n:<18} medians {' '.join(f'{v:>11}' for v in meds)}  median {m:>12.0f}  kept {len(kept)} of 5"
          f"  dropped: {', '.join(dropped) if dropped else 'none'} (beyond {100 * lim:.0f}% of the median)  {'ok' if ok else 'FAIL'}")
print(f"basecheck_c: {len(names) - len(failed)} of {len(names)} rows keep three or more sessions"
      + (f"; short: {', '.join(failed)} (take the next five)" if failed else '; the group is kept'))
if '--emit' in opts and not failed:
    head, group = opts.get('--head', '?'), opts.get('--group', '?')
    why = f'yw13r i7-12700KF P-core block CPUs 0-5, trunk {head}, rule (c) group {group}'
    lines = [
        '# Port Fletch baselines: the regression gate of tools/fl-headless/compare.py (yw08,',
        "# deliverable 6), in sagitta tests/perf/baselines/fletch_dev.txt's format:",
        '#   <bench> <median_ns> <min_ns> <why>      (the why is required and checked)',
        '# A row regresses when BOTH its median > median x 1.15 AND its min > min x 1.10',
        '# (perf_fletch.c:862-874, integer arithmetic). gc_pause and insert_100k are recorded',
        '# only, as in C.',
        '#',
        '# RE-HOMED by yw13r (notes/yw13r-fuss-rehomed.md, R-yw13r-1 and R-yw13r-3): the',
        '# earlier rows were measured on a pool host that is no longer a lane host (the VM',
        "# rows at yw08's head, the editor rows at yw09's); on the lane host that replaced",
        '# it they were stale both ways (the VM rows ran at 74-97 % of them, the editor rows',
        '# at 100-114 %).',
        '#',
        '# MEASURED on Linux x86-64, an Intel Core i7-12700KF: one block of three P-cores',
        "# and their hyperthreads (CPUs 0-5, taskset), in yew CI's image, release tier,",
        f'# wolf 0.2.36, at trunk {head}: five fresh consecutive sessions, each in its own',
        "# take of the block's three locks (nothing else on the block), each after the",
        "# host's one-minute load fell to 3 or under. For each row, the sessions within 5 %",
        "# of that row's median of the five (10 % for startup and parse_only, the two",
        '# shortest rows) are kept and the rest dropped as host blips; each value is the',
        '# MAXIMUM over the kept sessions, and the group is kept only because every row',
        '# keeps three or more. The record\'s perf steps hold a head to these numbers on a',
        '# P-core block of the same host, each after the same load wait; the gate is',
        '# meaningful on this host only, and hosted CI runs it advisory (perf_fletch.c:20-30).',
        '# Sessions, the dropped ones and why: notes/yw13r-evidence/perf/.',
        '',
    ]
    for n in names:
        lines.append(f'{n:<18} {out[n][0]:>12} {out[n][1]:>12}  {why}')
    open(opts['--emit'], 'w').write('\n'.join(lines) + '\n')
    print(f"basecheck_c: wrote {opts['--emit']}")
sys.exit(1 if failed else 0)
