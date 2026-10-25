#!/usr/bin/env python3
"""Same-run C/port Fletch timings. Advisory relaxes timing MISSes, never failures.
Smoke: one warmup process, then 11 measured processes, one sample/program each.
Headless: pinned perf_fletch.c's one warmup plus 11 in-process samples.
"""
import argparse,json,pathlib,re,statistics,subprocess,sys
def exit_status(misses, errors, advisory):
    return 1 if errors or (misses and not advisory) else 0

if sys.argv[1:]==['--selftest']:
    assert exit_status(0,0,False)==0
    assert exit_status(1,0,False)==1
    assert exit_status(1,0,True)==0
    assert exit_status(0,1,True)==1
    assert exit_status(1,1,True)==1
    print('fletch perf: advisory selftest ok (timing-only relaxation)')
    raise SystemExit(0)

ROOT=pathlib.Path(__file__).resolve().parents[2]
SMOKE=('fib24','map10k','motion100k')
HEADLESS=('startup','parse_only','motion_dispatch','fib27','map_heavy','gc_pause','strbuild_join','strbuild_concat','join5k','list_sort')
p=argparse.ArgumentParser()
p.add_argument('--oracle-tree',type=pathlib.Path,required=True)
p.add_argument('--tier',choices=('native','release'),default='release')
p.add_argument('--rows',default='all')
p.add_argument('--advisory',action='store_true')
a=p.parse_args()
selected=set(SMOKE+HEADLESS if a.rows=='all' else a.rows.split(','))
if selected-set(SMOKE+HEADLESS):p.error('unknown rows: '+','.join(sorted(selected-set(SMOKE+HEADLESS))))
output=ROOT/'target/perf-fletch'/a.tier;output.mkdir(parents=True,exist_ok=True)
rows=[];errors=[]
def run(label,cmd,timeout=600):
    proc=subprocess.run([str(x) for x in cmd],cwd=ROOT,capture_output=True,text=True,timeout=timeout)
    (output/(label+'.stdout')).write_text(proc.stdout)
    (output/(label+'.stderr')).write_text(proc.stderr)
    if proc.returncode:
        raise ValueError(f'{label}: exit={proc.returncode}; {proc.stderr.strip()[-500:]}')
    return proc.stdout

def record(name,c,w,budget=0,record_only=False):
    if c<=0 or w<=0:raise ValueError(f'{name}: nonpositive timing C={c} port={w}')
    ratio=w/c
    miss=not record_only and (ratio>2 or (budget and w>budget))
    row=dict(name=name,tier=a.tier,c_median_ns=c,port_median_ns=w,ratio=ratio,budget_ns=budget,verdict='RECORDED' if record_only else 'MISS' if miss else 'PASS')
    rows.append(row)
    absolute=f' budget={budget}ns '+('MISS' if w>budget else 'PASS') if budget else ''
    print(f'{row["verdict"]} fletch/{name} {a.tier}: port={w}ns C={c}ns ratio={ratio:.3f}x{absolute}',flush=True)
    if name=='motion_dispatch':print(f'  null-host dispatch/raise/unwind: {w/1000000:.3f} ns/op; NOT editing',flush=True)

if selected.intersection(SMOKE):
    samples={who:{n:[] for n in SMOKE} for who in ('C','port')}
    try:
        for rep in range(12):
            for who,bin in [('C',a.oracle_tree/'build/fl_smoke'),('port',ROOT/f'target/tools/fl-core-{a.tier}')]:
                text=run(f'smoke-{who}-{rep:02d}',[bin,'--perf','1'])
                found={}
                for line in text.splitlines():
                    if who=='C':
                        m=re.match(r'^(fib24|map10k|motion100k)\s+([0-9.]+) ms\s+gc=(\d+)\s+-> (\d+)$',line)
                        if m:found[m[1]]=(round(float(m[2])*1000000),int(m[3]),int(m[4]))
                    else:
                        m=re.match(r'^(fib24|map10k|motion100k) elapsed_ns=(\d+) gc=(\d+) result=(\d+)$',line)
                        if m:found[m[1]]=tuple(map(int,m.groups()[1:]))
                if set(found)!=set(SMOKE):raise ValueError(f'{who}: missing smoke rows')
                for name,(ns,gc,result) in found.items():
                    want_gc=155 if name=='motion100k' else 0
                    want={'fib24':46368,'map10k':10000,'motion100k':100000}[name]
                    if gc!=want_gc or result!=want:raise ValueError(f'{who}/{name}: gc={gc}, result={result}')
                    samples[who][name].append(ns)
            print(f'smoke sample {rep}/11 complete'+(' (warmup)' if rep==0 else ''),flush=True)
        for name in SMOKE:
            if name in selected:record(name,statistics.median(samples['C'][name][1:]),statistics.median(samples['port'][name][1:]))
        (output/'smoke-samples.json').write_text(json.dumps(samples,indent=2)+'\n')
    except (ValueError,subprocess.TimeoutExpired) as e:errors.append(str(e));print('ERROR '+str(e),flush=True)

for name in HEADLESS:
    if name not in selected:continue
    timings={}
    try:
        for who,bin in [('C',ROOT/'target/tools/fl-headless-oracle'),('port',ROOT/f'target/tools/fl-headless-{a.tier}')]:
            text=run(f'{name}-{who}',[bin,name,a.oracle_tree/'runtime/init.fl'])
            m=re.search(r'^'+re.escape(name)+r' median_ns=(\d+) min_ns=(\d+) budget_ns=(\d+)(?: gc=(\d+))? raw=([0-9,]+)$',text,re.M)
            if not m:raise ValueError(f'{who}/{name}: malformed result')
            median,minimum,budget=map(int,m.groups()[:3]);raw=list(map(int,m[5].split(',')))
            if len(raw)!=12 or median!=statistics.median(raw[1:]) or minimum!=min(raw[1:]):raise ValueError(f'{who}/{name}: sample/median mismatch')
            timings[who]=(median,budget)
        if timings['C'][1]!=timings['port'][1]:raise ValueError(f'{name}: budget mismatch')
        record(name,timings['C'][0],timings['port'][0],timings['C'][1],name=='gc_pause')
    except (ValueError,subprocess.TimeoutExpired) as e:errors.append(str(e));print('ERROR '+str(e),flush=True)

by_name={r['name']:r for r in rows}
concat_join=None
concat_miss=0
if 'strbuild_concat' in by_name and 'join5k' in by_name:
    ratio=by_name['strbuild_concat']['port_median_ns']/by_name['join5k']['port_median_ns']
    concat_miss=int(ratio<=20)
    concat_join=dict(port_ratio=ratio,required_min=20,verdict='MISS' if concat_miss else 'PASS')
    print(f'{concat_join["verdict"]} fletch/concat-join ratio={ratio:.3f}x (requires >20)',flush=True)
report=dict(advisory=a.advisory,rows=rows,concat_join=concat_join,errors=errors)
(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
misses=sum(r['verdict']=='MISS' for r in rows)+concat_miss
print(f'fletch perf: rows={len(rows)} MISS={misses} errors={len(errors)} advisory={a.advisory}',flush=True)
sys.exit(exit_status(misses,len(errors),a.advisory))
