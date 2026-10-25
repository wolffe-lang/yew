#!/usr/bin/env python3
"""Regression for iterative unary/else-if folds, compared to actual C CLI."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[3]
stage=root/'target/front/deep';stage.mkdir(exist_ok=True)
fixtures={'else-if-1024':'if 0 {} '+('else if 0 {} '*1024)+'else {}\n','unary-10000':'not '*10000+'false\n'}
rows=[]
for name,text in fixtures.items():
    file=stage/(name+'.fl');file.write_text(text)
    c=subprocess.run([str(root/'target/front/oracle-front'),'ast',str(file)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    w=subprocess.run([str(root/'target/tools/fl-front'),'ast',str(file)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    assert c.returncode==w.returncode==0,(name,c.returncode,w.returncode,c.stderr,w.stderr)
    assert c.stdout==w.stdout and c.stderr==w.stderr,name
    row=f'PASS {name} source_bytes={len(text)} dump_bytes={len(c.stdout)}'
    rows.append(row);print(row,flush=True)
(root/'notes/yw07b-evidence/front/deep-differential.log').write_text('\n'.join(rows)+'\n')
