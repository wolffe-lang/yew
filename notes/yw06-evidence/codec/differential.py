#!/usr/bin/env python3
"""Exact-pin C/Wolf bytes, accepted-key cases and same-run perf. No goldens written."""
from pathlib import Path
import subprocess, time, statistics
base = Path('target/codec')
extra = base / 'extra'
extra.mkdir(exist_ok=True)
cases = {
 'key-quotes.fl': b'{"Upper": 1,"dot.key":2,"sp ace":3,"":nil,"a\\0b":true,"\\xff":false,lower_9:4,}',
 'duplicates.fl': b'{a:1,b:2,a:3,"b":4,}',
 'extrema.fl': b'[-9223372036854775808,9223372036854775807,0,]',
 'accepted-extrema.fl': b'[-9223372036854775807,9223372036854775807,0,]',
 'all-bytes.fl': b'{value:"' + b''.join((b'\\x%02x' % i) for i in range(256)) + b'",}',
 'reserved-keys.fl': b'{"nil":1,"true":2,"false":3,"if":4,}',
 'root-nil.fl': b'nil', 'root-bool.fl': b'true', 'root-int.fl': b'-1',
 'root-bytes.fl': b'"\\xff\\0"', 'empty-keys.fl': b'{"":[],}',
 'bare-key-4096.fl': b'{version:1,' + b'A'*4096 + b':0}',
 'bare-key-4097.fl': b'{version:1,' + b'A'*4097 + b':0}',
}
for name, data in cases.items(): (extra / name).write_bytes(data)
inputs = sorted(Path('tests/unit/fixtures/wsstate/v1').rglob('*.fl')) + sorted(extra.glob('*.fl'))
accepted = rejected = 0
mismatches = []
for path in inputs:
 outputs=[]; codes=[]
 for engine in ['oracle', 'roundtrip']:
  out = base / (engine + '.out')
  run = subprocess.run([str(base / engine), str(path), str(out)], capture_output=True)
  codes.append(run.returncode)
  outputs.append(out.read_bytes() if run.returncode == 0 else b'')
 if codes[0] != codes[1]:
  mismatches.append(f'DIFFERENTIAL ACCEPT {path}: C/Wolf={codes}')
  print(mismatches[-1], flush=True)
  continue
 if codes[0] == 0:
  if outputs[0] != outputs[1]:
   (base/'C-mismatch.out').write_bytes(outputs[0]);(base/'Wolf-mismatch.out').write_bytes(outputs[1])
   raise SystemExit(f'DIFFERENTIAL BYTES {path}')
  # The shipping writer emits reserved string keys bare; its reader rejects
  # those outputs. Compatibility requires equal cross-read outcomes, not a
  # silently repaired writer or a falsely asserted universal fixpoint.
  crosscodes=[]; crossbytes=[]
  for engine, source in [('oracle','roundtrip.out'),('roundtrip','oracle.out')]:
   cross=base/(engine+'-cross.out')
   run=subprocess.run([str(base/engine),str(base/source),str(cross)],capture_output=True)
   crosscodes.append(run.returncode)
   crossbytes.append(cross.read_bytes() if run.returncode==0 else b'')
  if crosscodes != [0,0] and crosscodes != [1,1]:
   mismatches.append(f'DIFFERENTIAL CROSSREAD {path}: C/Wolf={crosscodes}')
   print(mismatches[-1],flush=True)
  elif crosscodes==[0,0] and (crossbytes[0]!=outputs[0] or crossbytes[1]!=outputs[0]):
   mismatches.append(f'DIFFERENTIAL CROSSREAD BYTES {path}')
  elif crosscodes==[1,1]:
   print(f'PINNED-C NONFIXPOINT {path}: both reject identical emitted bytes',flush=True)
  accepted+=1
 elif codes[0]==1: rejected+=1
 else: raise SystemExit(f'HARNESS ERROR {path}: {codes}')
 print(f'differential {path}: {"byte-identical" if codes[0] == 0 else "both reject"}', flush=True)
print(f'differential accepted={accepted} rejected={rejected}',flush=True)
path='tests/unit/fixtures/wsstate/v1/18-maximal-512-tabs.fl'
times={}
for engine in ['oracle','roundtrip']:
 values=[]
 for rep in range(4):
  before=time.perf_counter();run=subprocess.run([str(base/engine),'--bench',path,'20'],capture_output=True,check=True);elapsed=time.perf_counter()-before
  if rep: values.append(elapsed)
  print(f'perf {engine} repetition={rep} seconds={elapsed:.6f} checksum={run.stdout.decode().strip()}',flush=True)
 times[engine]=statistics.median(values)
ratio=times['roundtrip']/times['oracle']
print(f'perf median C={times["oracle"]:.6f} Wolf={times["roundtrip"]:.6f} ratio={ratio:.3f}',flush=True)
if ratio > 2: mismatches.append('PERF OVER 2x: report, never waive')
if mismatches: raise SystemExit('\n'.join(mismatches))
