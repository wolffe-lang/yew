#!/usr/bin/env python3
"""perfan.py BASELINE MISSES --trunk S1.json S2.json ... [--head H1.json ...] [--emit OUT --why WHY]

The Fletch perf gate's two halves over compare.py's report.json files:
  * the old baseline (BASELINE, the committed tools/perf-fletch-baseline.txt)
    against each session: the margin of median and min, and the verdict;
  * a proposed baseline from the trunk sessions, each row the MAXIMUM of the
    sessions' medians and of their minimums (yw08's and yw09's rule);
  * the same-run ratio half per session: MISS / MISS-NAMED / PASS by row;
  * with --head: each head session against the proposed baseline, with
    compare.py's own two-condition rule and integer arithmetic.
--emit writes the proposed baseline in the committed file's format.
"""
import json, sys, statistics

def regressed(median, minimum, bmed, bmin):
    return median > bmed + bmed // 20 * 3 and minimum > bmin + bmin // 10

def read_baseline(path):
    rows = {}
    for line in open(path):
        if not line.strip() or line.startswith('#'):
            continue
        p = line.split()
        rows[p[0]] = (int(p[1]), int(p[2]))
    return rows

def read_misses(path):
    named = set()
    for line in open(path):
        if not line.strip() or line.startswith('#'):
            continue
        p = line.split()
        named.add((p[0], p[1]))
    return named

args = sys.argv[1:]
base = read_baseline(args[0])
named = read_misses(args[1])
groups, cur = {'trunk': [], 'head': []}, None
emit = why = None
i = 2
while i < len(args):
    a = args[i]
    if a in ('--trunk', '--head'):
        cur = a[2:]
    elif a == '--emit':
        emit = args[i + 1]; i += 1
    elif a == '--why':
        why = args[i + 1]; i += 1
    else:
        groups[cur].append(json.load(open(a)))
    i += 1

def rows_of(rep):
    return {r['name']: r for r in rep['rows'] if r['verdict'] != 'RECORDED'}

trunk = [rows_of(r) for r in groups['trunk']]
head = [rows_of(r) for r in groups['head']]
names = [n for n in trunk[0]]
print(f"host {groups['trunk'][0]['host']}; trunk sessions {len(trunk)}, head sessions {len(head)}")
print()
print('## The old baseline against the trunk sessions (median and min, % of the baseline)')
print(f"{'row':<18} {'base med':>12} {'base min':>12}  " + '  '.join(f's{k+1} med%  min%' for k in range(len(trunk))) + '  verdicts')
for n in names:
    bm, bn = base[n]
    cells, verd = [], []
    for s in trunk:
        r = s[n]
        cells.append(f"{100 * r['port_median_ns'] / bm:7.1f} {100 * r['port_min_ns'] / bn:6.1f}")
        verd.append('REG' if regressed(r['port_median_ns'], r['port_min_ns'], bm, bn) else 'ok')
    print(f"{n:<18} {bm:>12} {bn:>12}  " + '  '.join(cells) + '  ' + ','.join(verd))
print()
print('## Session spread at trunk (max/min of the session medians, %), and the proposed baseline (max of sessions)')
prop = {}
for n in names:
    meds = [s[n]['port_median_ns'] for s in trunk]
    mins = [s[n]['port_min_ns'] for s in trunk]
    prop[n] = (max(meds), max(mins))
    print(f"{n:<18} medians {','.join(str(m) for m in meds):<40} spread {100 * (max(meds) / min(meds) - 1):5.1f}%  proposed {prop[n][0]:>12} {prop[n][1]:>12}")
print()
print('## The same-run ratio half (port/C median; * = over 2x; N = named for the host)')
host = groups['trunk'][0]['host']
for label, sess in (('trunk', trunk), ('head', head)):
    if not sess:
        continue
    print(f"### {label}")
    for n in names:
        rs = [s[n]['ratio'] for s in sess if n in s]
        tag = 'N' if (n, host) in named else ' '
        print(f"{n:<18} {tag} " + ' '.join(f"{x:6.3f}{'*' if x > 2 else ' '}" for x in rs))
    for k, rep in enumerate(groups[label]):
        cj = rep.get('concat_join')
        if cj:
            print(f"  session {k+1} concat-join {cj['port_ratio']:.2f}x (needs >20): {cj['verdict']}")
        unnamed_miss = [r['name'] for r in rep['rows'] if r['verdict'] == 'MISS']
        print(f"  session {k+1} unnamed MISS: {unnamed_miss or 'none'}; failures {rep['failures']} errors {len(rep['errors'])}")
print()
if head:
    print('## The head sessions against the proposed baseline (median and min, % of it; REG = the two-condition rule)')
    for n in names:
        pm, pn = prop[n]
        cells, verd = [], []
        for s in head:
            r = s[n]
            cells.append(f"{100 * r['port_median_ns'] / pm:7.1f} {100 * r['port_min_ns'] / pn:6.1f}")
            verd.append('REG' if regressed(r['port_median_ns'], r['port_min_ns'], pm, pn) else 'ok')
        print(f"{n:<18} " + '  '.join(cells) + '  ' + ','.join(verd))
    print()
    print('## The head sessions against the old baseline')
    for n in names:
        bm, bn = base[n]
        verd = ['REG' if regressed(s[n]['port_median_ns'], s[n]['port_min_ns'], bm, bn) else 'ok' for s in head]
        print(f"{n:<18} " + ','.join(verd))
if emit:
    with open(emit, 'w') as f:
        for n in names:
            f.write(f"{n:<18} {prop[n][0]:>12} {prop[n][1]:>12}  {why}\n")
    print(f'wrote {emit}')
