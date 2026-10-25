#!/usr/bin/env python3
"""Break only staged port copies; prove frontend invariant gates reject them."""
import os
from pathlib import Path
import shutil
import subprocess
root=Path(__file__).resolve().parents[3]
base=root/'target/fl-front'
out=root/'notes/yw07b-evidence/front'
for kind in ('lex','parse'):
    stage=root/f'target/front/plant-{kind}'
    if stage.exists(): shutil.rmtree(stage)
    shutil.copytree(base,stage)
    filename=stage/'fl'/f'{kind}.lu'
    text=filename.read_text()
    if kind=='lex':
        begin=text.index('pub fn fl_lex_next(')
        at=text.index('-> FlTok {',begin)+len('-> FlTok {')
        plant='\n    if src.len > 0 { return lex_token(FL_T_INT, lex_span(lx, lx.line, lx.col, lx.at)) }\n'
        text=text[:at]+plant+text[at:]
    else:
        old='p.prog.incomplete = !p.had_error &&'
        assert old in text
        text=text.replace(old,'p.prog.incomplete = true || !p.had_error &&',1)
    filename.write_text(text)
    binary=root/f'target/front/plant-{kind}-bin'
    built=subprocess.run([os.environ['WOLF_BIN'],'build','--release','--deny-warnings',str(stage/'main.lu'),'-o',str(binary)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/f'plant-{kind}-build.log').write_bytes(built.stdout)
    assert built.returncode==0,built.stdout.decode(errors='replace')
    mode='lex-fuzz' if kind=='lex' else 'parse-fuzz-front'
    run=subprocess.run([str(binary),mode,'--iters=1000','--seed=1'],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/f'plant-{kind}.log').write_bytes(run.stdout+b'\nexit='+str(run.returncode).encode()+b'\n')
    needle=b'lexer made no progress' if kind=='lex' else b'incomplete and had_error are both set'
    assert run.returncode==1 and needle in run.stdout,run.stdout.decode(errors='replace')
    print(f'PASS plant-{kind}: expected red exit1 ({needle.decode()})',flush=True)
