#!/usr/bin/env python3
"""Same-run C/port Fletch timings and their gates (s33 §5; yw07b's harness,
yw08's regression gate).

Smoke: one warmup process, then 11 measured processes, one sample/program each.
Headless: pinned perf_fletch.c's one warmup plus 11 in-process samples.

Three verdicts per row, as pinned perf_fletch.c gives them (:1-30, :862-955,
:1215-1262) with the track's 2x bar (ruling #89 R3) in front:
  ratio       port/C median above 2.0 is a MISS (gc_pause is recorded only);
  budget      the hard rows' absolute budgets (startup 2 ms, motion_dispatch
              1 us/op); perf_policy.h's advisory policy: a zero or a value
              over 100x the budget fails everywhere, an ordinary overrun only
              when gating;
  regression  against the port's own baseline (tools/perf-fletch-baseline.txt,
              C's fletch_dev.txt format, measured on kasumi): BOTH median >
              base x 1.15 AND min > base x 1.10, in C's integer arithmetic.
              This is what holds a row already named MISS against C to the
              number it was named at.
A ratio or budget MISS listed for this host in tools/perf-fletch-misses.txt
is NAMED (owner and issue printed) and does not fail; any other MISS, any
regression and any error fails unless --advisory, which relaxes timing
verdicts only (sanity failures and errors stay hard, as C's --gate-budgets).
"""
import argparse, json, pathlib, platform, re, statistics, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SMOKE = ('fib24', 'map10k', 'motion100k')
HEADLESS = ('startup', 'parse_only', 'motion_dispatch', 'fib27', 'map_heavy', 'gc_pause',
            'strbuild_join', 'strbuild_concat', 'join5k', 'list_sort')
# yw09 (R-yw09-3 A): perf_fletch.c's six editor rows (:1076-1131) through
# tools/fl-editor-perf beside the same oracle; insert_100k is C's report-only
# row, one sample, recorded.
EDITOR = ('config_load', 'config_reload_500', 'macrolib_scan_200', 'motion_editor', 'query_cur_pos',
          'insert_100k')
REPORT_ONLY = ('gc_pause', 'insert_100k')
SANITY_MULTIPLIER = 100  # perf_policy.h YEW_PERF_ADVISORY_SANITY_MULTIPLIER


def regressed(median, minimum, base_median, base_min):
    """perf_fletch.c:870-874: +15% is +3/20 and +10% is +1/10, integers."""
    return median > base_median + base_median // 20 * 3 and minimum > base_min + base_min // 10


def timing_failed(value, budget, advisory):
    """perf_policy.h yew_perf_timing_failed."""
    sane = value != 0 and budget != 0 and value <= budget * SANITY_MULTIPLIER
    return not sane or (not advisory and value > budget)


def exit_status(failures, errors, advisory):
    return 1 if errors or (failures and not advisory) else 0


def read_baseline(text):
    """`<bench> <median_ns> <min_ns> <why>`; the why is required (fletch_dev.txt:5-9)."""
    rows = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        m = re.match(r'^(\S+)\s+(\d+)\s+(\d+)\s+(\S.*)$', line)
        if not m:
            raise ValueError(f'baseline line {n}: want "<bench> <median_ns> <min_ns> <why>": {line!r}')
        if m[1] in rows:
            raise ValueError(f'baseline line {n}: {m[1]} twice')
        rows[m[1]] = (int(m[2]), int(m[3]), m[4])
    return rows


def read_misses(text):
    """`<row> <host> <owner> <issue>`, the shape of tools/perf-editor-misses.txt."""
    named = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f'misses line {n}: want "<row> <host> <owner> <issue>": {line!r}')
        named[(parts[0], parts[1])] = (parts[2], parts[3])
    return named


def selftest():
    assert exit_status(0, 0, False) == 0
    assert exit_status(1, 0, False) == 1
    assert exit_status(1, 0, True) == 0
    assert exit_status(0, 1, True) == 1
    assert exit_status(1, 1, True) == 1
    # perf_fletch.c:887-951, the seven regression cases and their reasons.
    cases = [
        (1000000, 900000, 1200000, 1080000, True, '20% slower'),
        (1000000, 900000, 1050000, 945000, False, '5% slower'),
        (1000000, 900000, 1150000, 990000, False, 'exactly +15/+10'),
        (1000000, 900000, 1300000, 905000, False, 'median only'),
        (1000000, 900000, 1010000, 1200000, False, 'min only'),
        (1000000, 900000, 500000, 450000, False, 'twice as fast'),
        (1000000, 900000, 2000000, 1800000, True, 'twice as slow'),
    ]
    for bmed, bmin, med, mn, want, what in cases:
        assert regressed(med, mn, bmed, bmin) == want, what
    # The integer arithmetic, not a float: base 999 -> +15% is 999 + 49*3.
    assert not regressed(1146, 1100, 999, 999) and regressed(1147, 1099, 999, 999)
    budget = 1000000
    assert not timing_failed(budget, budget, False)
    assert timing_failed(budget + 1, budget, False)
    assert not timing_failed(budget + 1, budget, True)
    assert not timing_failed(budget * SANITY_MULTIPLIER, budget, True)
    assert timing_failed(budget * SANITY_MULTIPLIER + 1, budget, True)
    assert timing_failed(0, budget, True)
    base = read_baseline('# c\n\nfib27 10 9 s33 initial\n')
    assert base == {'fib27': (10, 9, 's33 initial')}
    for bad in ('fib27 10 9\n', 'fib27 10 9  \n', 'fib27 ten 9 why\n', 'a 1 1 x\na 2 2 y\n'):
        try:
            read_baseline(bad)
        except ValueError:
            continue
        raise AssertionError(f'baseline accepted {bad!r}')
    named = read_misses('# m\nfib27 linux-x86_64 wolf-lang yew#77\n')
    assert ('fib27', 'linux-x86_64') in named and ('fib27', 'darwin-arm64') not in named
    for bad in ('fib27 linux-x86_64 owner\n', 'fib27 a b c d\n'):
        try:
            read_misses(bad)
        except ValueError:
            continue
        raise AssertionError(f'misses accepted {bad!r}')
    print('fletch perf: gate selftest ok (exit policy, 7+2 regression cases, '
          'the advisory boundary, baseline and misses ledgers)')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--oracle-tree', type=pathlib.Path, required=True)
    p.add_argument('--tier', choices=('native', 'release'), default='release')
    p.add_argument('--rows', default='all')
    p.add_argument('--advisory', action='store_true')
    p.add_argument('--baseline', type=pathlib.Path, default=ROOT / 'tools/perf-fletch-baseline.txt')
    p.add_argument('--misses', type=pathlib.Path, default=ROOT / 'tools/perf-fletch-misses.txt')
    p.add_argument('--host', default=f'{platform.system().lower()}-{platform.machine()}')
    p.add_argument('--emit-baseline', type=pathlib.Path,
                   help='also write this run as a baseline (one why for every row)')
    p.add_argument('--why', default='')
    a = p.parse_args()
    known = SMOKE + HEADLESS + EDITOR
    selected = set(known if a.rows == 'all' else a.rows.split(','))
    if selected - set(known):
        p.error('unknown rows: ' + ','.join(sorted(selected - set(known))))
    if a.emit_baseline and not a.why.strip():
        p.error('--emit-baseline needs a --why (the baseline why column is required)')
    baseline = read_baseline(a.baseline.read_text()) if a.baseline.exists() else None
    named = read_misses(a.misses.read_text()) if a.misses.exists() else {}
    output = ROOT / 'target/perf-fletch' / a.tier
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    errors = []
    failures = 0

    def run(label, cmd, timeout=600):
        proc = subprocess.run([str(x) for x in cmd], cwd=ROOT, capture_output=True, text=True,
                              timeout=timeout)
        (output / (label + '.stdout')).write_text(proc.stdout)
        (output / (label + '.stderr')).write_text(proc.stderr)
        if proc.returncode:
            raise ValueError(f'{label}: exit={proc.returncode}; {proc.stderr.strip()[-500:]}')
        return proc.stdout

    def record(name, c, w, wmin, budget=0, record_only=False):
        nonlocal failures
        if c <= 0 or w <= 0 or wmin <= 0:
            raise ValueError(f'{name}: nonpositive timing C={c} port={w} min={wmin}')
        ratio = w / c
        over_budget = bool(budget) and w > budget
        miss = not record_only and (ratio > 2 or over_budget)
        owner = named.get((name, a.host))
        verdict = 'RECORDED' if record_only else 'MISS' if miss else 'PASS'
        if miss and owner:
            verdict = 'MISS-NAMED'
        elif miss and not a.advisory:
            failures += 1
        if budget and timing_failed(w, budget, True):  # sanity: hard everywhere
            errors.append(f'{name}: {w} ns fails the sanity bound of {budget} ns x {SANITY_MULTIPLIER}')
        base = baseline.get(name) if baseline else None
        reg = None
        if not record_only:
            if base is None:
                reg = 'NO-BASELINE'
                if not a.advisory:
                    failures += 1
            elif regressed(w, wmin, base[0], base[1]):
                reg = 'REGRESSION' if not a.advisory else 'WARN'
                if not a.advisory:
                    failures += 1
            else:
                reg = 'ok'
        row = dict(name=name, tier=a.tier, c_median_ns=c, port_median_ns=w, port_min_ns=wmin,
                   ratio=ratio, budget_ns=budget, verdict=verdict, regression=reg,
                   baseline=list(base[:2]) if base else None,
                   owner=list(owner) if owner and miss else None)
        rows.append(row)
        absolute = f' budget={budget}ns ' + ('MISS' if over_budget else 'PASS') if budget else ''
        named_by = f' named: {owner[0]} {owner[1]}' if verdict == 'MISS-NAMED' else ''
        against = (f' baseline={base[0]}/{base[1]}ns {reg}' if base else f' baseline: {reg}') if reg else ''
        print(f'{verdict} fletch/{name} {a.tier}: port={w}ns (min {wmin}ns) C={c}ns '
              f'ratio={ratio:.3f}x{absolute}{named_by}{against}', flush=True)
        if name == 'motion_dispatch':
            print(f'  null-host dispatch/raise/unwind: {w / 1000000:.3f} ns/op; NOT editing', flush=True)

    if selected.intersection(SMOKE):
        samples = {who: {n: [] for n in SMOKE} for who in ('C', 'port')}
        try:
            for rep in range(12):
                for who, bin in [('C', a.oracle_tree / 'build/fl_smoke'),
                                 ('port', ROOT / f'target/tools/fl-core-{a.tier}')]:
                    text = run(f'smoke-{who}-{rep:02d}', [bin, '--perf', '1'])
                    found = {}
                    for line in text.splitlines():
                        if who == 'C':
                            m = re.match(r'^(fib24|map10k|motion100k)\s+([0-9.]+) ms\s+gc=(\d+)\s+-> (\d+)$', line)
                            if m:
                                found[m[1]] = (round(float(m[2]) * 1000000), int(m[3]), int(m[4]))
                        else:
                            m = re.match(r'^(fib24|map10k|motion100k) elapsed_ns=(\d+) gc=(\d+) result=(\d+)$', line)
                            if m:
                                found[m[1]] = tuple(map(int, m.groups()[1:]))
                    if set(found) != set(SMOKE):
                        raise ValueError(f'{who}: missing smoke rows')
                    for name, (ns, gc, result) in found.items():
                        want_gc = 155 if name == 'motion100k' else 0
                        want = {'fib24': 46368, 'map10k': 10000, 'motion100k': 100000}[name]
                        if gc != want_gc or result != want:
                            raise ValueError(f'{who}/{name}: gc={gc}, result={result}')
                        samples[who][name].append(ns)
                print(f'smoke sample {rep}/11 complete' + (' (warmup)' if rep == 0 else ''), flush=True)
            for name in SMOKE:
                if name in selected:
                    measured = samples['port'][name][1:]
                    record(name, statistics.median(samples['C'][name][1:]), statistics.median(measured),
                           min(measured))
            (output / 'smoke-samples.json').write_text(json.dumps(samples, indent=2) + '\n')
        except (ValueError, subprocess.TimeoutExpired) as e:
            errors.append(str(e))
            print('ERROR ' + str(e), flush=True)

    for name in HEADLESS + EDITOR:
        if name not in selected:
            continue
        timings = {}
        driver = 'fl-editor-perf' if name in EDITOR else 'fl-headless'
        samples = 1 if name == 'insert_100k' else 12
        try:
            for who, bin in [('C', ROOT / 'target/tools/fl-headless-oracle'),
                             ('port', ROOT / f'target/tools/{driver}-{a.tier}')]:
                text = run(f'{name}-{who}', [bin, name, a.oracle_tree / 'runtime/init.fl'])
                m = re.search(r'^' + re.escape(name) +
                              r' median_ns=(\d+) min_ns=(\d+) budget_ns=(\d+)(?: gc=(\d+))? raw=([0-9,]+)$',
                              text, re.M)
                if not m:
                    raise ValueError(f'{who}/{name}: malformed result')
                median, minimum, budget = map(int, m.groups()[:3])
                raw = list(map(int, m[5].split(',')))
                measured = raw[1:] if samples == 12 else raw
                if len(raw) != samples or median != sorted(measured)[len(measured) // 2] or \
                        minimum != min(measured):
                    raise ValueError(f'{who}/{name}: sample/median mismatch')
                timings[who] = (median, budget, minimum)
            if timings['C'][1] != timings['port'][1]:
                raise ValueError(f'{name}: budget mismatch')
            record(name, timings['C'][0], timings['port'][0], timings['port'][2], timings['C'][1],
                   name in REPORT_ONLY)
        except (ValueError, subprocess.TimeoutExpired) as e:
            errors.append(str(e))
            print('ERROR ' + str(e), flush=True)

    by_name = {r['name']: r for r in rows}
    concat_join = None
    if 'strbuild_concat' in by_name and 'join5k' in by_name:
        ratio = by_name['strbuild_concat']['port_median_ns'] / by_name['join5k']['port_median_ns']
        concat_miss = ratio <= 20
        concat_join = dict(port_ratio=ratio, required_min=20, verdict='MISS' if concat_miss else 'PASS')
        if concat_miss and not a.advisory:
            failures += 1
        print(f'{concat_join["verdict"]} fletch/concat-join ratio={ratio:.3f}x (requires >20)', flush=True)
    if a.emit_baseline:
        lines = ['# Port Fletch baselines (tools/fl-headless/compare.py --emit-baseline).',
                 f'# host={a.host} tier={a.tier}; format <bench> <median_ns> <min_ns> <why>.']
        lines += [f"{r['name']:<18} {r['port_median_ns']:>12} {r['port_min_ns']:>12}  {a.why}"
                  for r in rows if r['verdict'] != 'RECORDED']
        a.emit_baseline.write_text('\n'.join(lines) + '\n')
        print(f'fletch perf: wrote {a.emit_baseline}', flush=True)
    report = dict(advisory=a.advisory, host=a.host, rows=rows, concat_join=concat_join, errors=errors,
                  failures=failures)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    misses = sum(r['verdict'] in ('MISS', 'MISS-NAMED') for r in rows)
    print(f'fletch perf: rows={len(rows)} MISS={misses} named={sum(r["verdict"] == "MISS-NAMED" for r in rows)} '
          f'failures={failures} errors={len(errors)} advisory={a.advisory} host={a.host}', flush=True)
    sys.exit(exit_status(failures, len(errors), a.advisory))


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        selftest()
        raise SystemExit(0)
    main()
