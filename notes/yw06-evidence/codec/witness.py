#!/usr/bin/env python3
"""Pinned shipping-C rejection witnesses; no source or golden modifications."""
from pathlib import Path
import subprocess
words='and as break catch continue edit else false fn for if import in let macro nil not or return true try while'.split()
root=Path('target/codec/witnesses');root.mkdir(exist_ok=True)
cases=[('min',b'-9223372036854775808'),('minplus1',b'-9223372036854775807')]
for word in words:
 cases.extend([(word,b'{'+word.encode()+b':1,}'),('quoted-'+word,b'{"'+word.encode()+b'":1,}')])
for name,data in cases:
 p=root/(name+'.fl');p.write_bytes(data);out=root/(name+'.out')
 cmd=['target/codec/oracle',str(p),str(out)]
 r=subprocess.run(cmd,capture_output=True)
 print('COMMAND', ' '.join(cmd)); print('INPUT',repr(data));print('EXIT',r.returncode,'STDERR',r.stderr.decode().strip());
 if r.returncode==0: print('OUTPUT',repr(out.read_bytes()))
