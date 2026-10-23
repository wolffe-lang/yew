#!/usr/bin/env python3
"""The C oracle calls yew_fl_parse_fletch before fl_data_read/write."""
from pathlib import Path
import subprocess
root=Path('target/codec/key-caps');root.mkdir(exist_ok=True)
for size in (4096,4097):
 for letter in (b'A',b'a'):
  p=root/f'{letter.decode()}-{size}.fl';p.write_bytes(b'{version:1,'+letter*size+b':0}')
  out=p.with_suffix('.out')
  cmd=['target/codec/oracle',str(p),str(out)]
  r=subprocess.run(cmd,capture_output=True)
  print('COMMAND',' '.join(cmd));print('KEY',letter,'BYTES',size,'EXIT',r.returncode,'STDERR',r.stderr.decode().strip())
  if r.returncode==0:
   rr=subprocess.run(['target/codec/oracle',str(out),str(out)+'.again'],capture_output=True)
   print('REPARSE_EXIT',rr.returncode,'CANONICAL_SIZE',out.stat().st_size)
