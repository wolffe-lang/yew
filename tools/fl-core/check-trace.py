#!/usr/bin/env python3
"""21 executed-opcode streams, exact except dispatch header; two processes/mode."""
import difflib,os,pathlib,subprocess,sys
def normalize(stdout):
    return b''.join(line for line in stdout.splitlines(keepends=True) if not line.startswith(b'# dispatch:'))

def all_equal(traces):
    return bool(traces) and all(t==traces[0] for t in traces[1:])

def first_difference(a,b):
    """The fixture header and 1-based line of the first line where b leaves a."""
    al,bl=a.splitlines(),b.splitlines()
    n=next((i for i in range(max(len(al),len(bl))) if i>=len(al) or i>=len(bl) or al[i]!=bl[i]),None)
    if n is None: return None
    head=next((l for l in reversed(al[:n+1]) if l.startswith(b'== ')),b'(before the first fixture)')
    return head.decode('utf8','backslashreplace'),n+1

def selftest():
    base=b'# dispatch: switch\n'+b''.join(b'== fixture%d\nCONST RETURN\n'%i for i in range(21))
    same=base.replace(b'switch',b'port')
    assert all_equal([normalize(base),normalize(same)])
    broken=base.replace(b'CONST',b'NIL',1)
    assert not all_equal([normalize(base),normalize(broken)])
    late=base.replace(b'== fixture7\nCONST',b'== fixture7\nNIL',1)
    assert first_difference(normalize(base),normalize(late))==('== fixture7',16)
    assert first_difference(normalize(base),normalize(base))is None
    assert not all_equal([normalize(base),normalize(base[:-1])])
    assert not all_equal([normalize(base),normalize(base.replace(b'fixture0',b'wrong',1))])
    print('check-fl-trace: selftest ok (opcode, newline, fixture changes refused)')
    return 0

def main(argv):
    if argv == ['--selftest']: return selftest()
    if len(argv) != 3: raise SystemExit('usage: check-trace.py C PORT OUTPUT | --selftest')
    oracle,port,directory=map(pathlib.Path,argv)
    directory.mkdir(parents=True,exist_ok=True)
    failed=False
    for mode in ('normal','stress'):
        env=dict(os.environ)
        env.pop('YEW_FL_GC_STRESS',None);env.pop('FL_GC_STRESS',None)
        if mode=='stress':env['YEW_FL_GC_STRESS']='1'
        traces=[]
        valid=True
        for name,binary in [('C',oracle),('port',port)]:
            for repeat in (1,2):
                p=subprocess.run([str(binary.resolve()),'--trace'],env=env,capture_output=True,timeout=120)
                (directory/f'{mode}-{name}-{repeat}.stdout').write_bytes(p.stdout)
                (directory/f'{mode}-{name}-{repeat}.stderr').write_bytes(p.stderr)
                clean=normalize(p.stdout)
                count=sum(line.startswith(b'== ') for line in clean.splitlines())
                if p.returncode or p.stderr or count!=21:
                    print(f'FAIL {mode} {name} run{repeat}: exit={p.returncode}, fixtures={count}, stderr={p.stderr!r}')
                    failed=True
                    valid=False
                traces.append(clean)
        equal=valid and all_equal(traces)
        print(f'{"PASS" if equal else "FAIL"} fl-trace {mode}: 21 fixtures, C/port, two processes each',flush=True)
        if not equal:
            failed=True
            for i,t in enumerate(traces[1:],1):
                if t!=traces[0]:
                    head,line=first_difference(traces[0],t)
                    who=['C run1','C run2','port run1','port run2'][i]
                    print(f'check-fl-trace: {mode}: {who} first differs from C run1 in {head}, line {line}',flush=True)
                    diff=''.join(difflib.unified_diff(traces[0].decode('utf8','backslashreplace').splitlines(True),t.decode('utf8','backslashreplace').splitlines(True),fromfile='C',tofile=f'comparison-{i}'))
                    (directory/f'{mode}-difference-{i}.diff').write_text(diff)
    return int(failed)

if __name__=='__main__':sys.exit(main(sys.argv[1:]))
