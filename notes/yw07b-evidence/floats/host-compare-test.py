#!/usr/bin/env python3
"""Negative controls for the narrowly allowed C-host NaN difference."""
import gzip, hashlib, json, pathlib, subprocess, sys, tempfile
parent = pathlib.Path(sys.argv[1]); parent.mkdir(parents=True, exist_ok=True)
checker = pathlib.Path(__file__).with_name('host-compare.py')

def case(name, linux, macos, expected, source=None):
    with tempfile.TemporaryDirectory(prefix=name+'-',dir=parent) as tmp:
        root=pathlib.Path(tmp)
        digest='fixture'
        if source is not None:
            (root/'corpus.txt').write_text(source)
            digest=hashlib.sha256(source.encode()).hexdigest()
        for host, lines in [('linux',linux),('macos',macos)]:
            d=root/host; d.mkdir()
            (d/'manifest.json').write_text(json.dumps(dict(input_sha256=digest,lines=len(lines))))
            with gzip.open(d/'answers.gz','wt') as out: out.writelines(lines)
        cp=subprocess.run([sys.executable,'-I',str(checker),str(root/'linux'),str(root/'macos'),str(root/'out.json')]+([str(root/'corpus.txt')] if source is not None else []),capture_output=True)
        assert (cp.returncode==0)==expected, (name,cp.stdout,cp.stderr)
        print(name, 'PASS')

case('nan-sign',['fixed:0:-nan\n'],['fixed:0:nan\n'],True)
case('nan-shortest',['shortest:0:-nan.0\n'],['shortest:0:nan.0\n'],True)
case('nan-payload',['parse:8:9221120237041090683\n'],['parse:8:9221120237041090560\n'],True)
case('finite-format',['fixed:0:1\n'],['fixed:0:2\n'],False)
case('nonfinite-not-nan',['fixed:0:-inf\n'],['fixed:0:inf\n'],False)
case('fake-nan-suffix',['fixed:0:-nanx\n'],['fixed:0:nan\n'],False)
case('different-precision',['fixed:1:-nan\n'],['fixed:0:nan\n'],False)
case('different-consumption',['parse:8:9221120237041090683\n'],['parse:7:9221120237041090560\n'],False)
case('nan-vs-inf',['parse:8:9221120237041090683\n'],['parse:8:9218868437227405312\n'],False)
case('raw-bits-differ',['bits:0:-2251799813685248\n'],['bits:0:9221120237041090560\n'],False)
case('different-length',['fixed:0:1\n'],[],False)

case('exact-signed-nan-payload',['parse:3:9221120237041090560\n'],['parse:7:9221120237041090560\n'],True,'P nan(+1)\n')
case('different-payload-spelling',['parse:3:9221120237041090560\n'],['parse:7:9221120237041090560\n'],False,'P nan(-1)\n')
case('different-payload-consumption',['parse:3:9221120237041090560\n'],['parse:8:9221120237041090560\n'],False,'P nan(+1)\n')
case('different-payload-value',['parse:3:9221120237041090560\n'],['parse:7:9218868437227405312\n'],False,'P nan(+1)\n')
