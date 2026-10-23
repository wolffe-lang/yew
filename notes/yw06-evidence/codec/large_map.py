#!/usr/bin/env python3
"""Bounded-work witness for ordered byte-key insertion (no golden edits)."""
from pathlib import Path
import subprocess, time, hashlib
base=Path('target/codec'); root=base/'large-maps';root.mkdir(exist_ok=True)
for n in [10000,20000,40000,499999,500000]:
 p=root/f'{n}.fl'
 with p.open('wb') as f:
  f.write(b'{')
  for i in range(n): f.write(f'k{i}:0,'.encode())
  f.write(b'}')
 expected=1 if n==500000 else 0
 rows=[]
 for engine in ['oracle','roundtrip']:
  output=root/f'{engine}-{n}.out'
  before=time.perf_counter();run=subprocess.run([str(base/engine),str(p),str(output)],capture_output=True);seconds=time.perf_counter()-before
  print(f'unique-map keys={n} bytes={p.stat().st_size} engine={engine} seconds={seconds:.6f} exit={run.returncode} stderr={run.stderr.decode().strip()}',flush=True)
  if run.returncode != expected: raise SystemExit(f'{engine}: unexpected node-cap classification')
  if expected==0: rows.append(output.read_bytes())
 if expected==0:
  if rows[0]!=rows[1]: raise SystemExit('large-map byte differential failed')
  print(f'unique-map keys={n} byte-identical sha256={hashlib.sha256(rows[0]).hexdigest()}',flush=True)
