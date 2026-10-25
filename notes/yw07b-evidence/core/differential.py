#!/usr/bin/env python3
import hashlib,pathlib,subprocess,sys
root=pathlib.Path('/home/mfwolffe/lanes/yw07b/core')
oracle=pathlib.Path('/home/mfwolffe/lanes/yw07b/yew/target/oracle/sagitta')
out=root/'notes/yw07b-evidence/core/bytecode';out.mkdir(exist_ok=True)
paths=sorted((oracle/'tests/fletch').rglob('*.fl'))
for name in ['fl_parse','fl_std','fl_vm']:
    paths.extend(sorted(p for p in (oracle/'tests/fuzz/corpus'/name).iterdir() if p.is_file()))
rows=[];failed=0
for i,p in enumerate(paths):
    c=subprocess.run([root/'target/oracle-core','--dump-bytecode',p],capture_output=True)
    w=subprocess.run([root/'target/core-driver-bin','--dump-bytecode',p],capture_output=True)
    ok=(c.returncode,c.stdout,c.stderr)==(w.returncode,w.stdout,w.stderr)
    failed+=not ok
    row=f'{"PASS" if ok else "FAIL"}\t{p.relative_to(oracle)}\tC={c.returncode}\tW={w.returncode}\t{hashlib.sha256(c.stdout).hexdigest()}\t{hashlib.sha256(w.stdout).hexdigest()}'
    print(row,flush=True);rows.append(row)
    if not ok:
        for who,res in [('c',c),('w',w)]:
            (out/f'{i:02d}-{who}.stdout').write_bytes(res.stdout)
            (out/f'{i:02d}-{who}.stderr').write_bytes(res.stderr)
(out/'rows.tsv').write_text('\n'.join(rows)+'\n')
print(f'bytecode: total={len(paths)} pass={len(paths)-failed} fail={failed}',flush=True)
sys.exit(bool(failed))
