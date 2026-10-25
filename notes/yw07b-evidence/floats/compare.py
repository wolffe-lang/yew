#!/usr/bin/env python3
import collections, hashlib, json, pathlib, subprocess, sys
corpus, cexe, wexe, outfile = sys.argv[1:]
counts = collections.Counter()
samples = {}
sha_c, sha_w = hashlib.sha256(), hashlib.sha256()
with open(corpus,'rb') as cinput, open(corpus,'rb') as winput:
    c = subprocess.Popen([cexe],stdin=cinput,stdout=subprocess.PIPE)
    w = subprocess.Popen([wexe],stdin=winput,stdout=subprocess.PIPE)
    lines = 0
    while True:
        a,b = c.stdout.readline(),w.stdout.readline()
        if not a and not b: break
        if not a or not b: raise RuntimeError('different output lengths')
        sha_c.update(a); sha_w.update(b)
        kind = a.split(b':',1)[0].decode()
        counts[kind+'.total'] += 1
        if a!=b:
            aa,bb=a.decode().strip().split(':',2),b.decode().strip().split(':',2)
            if kind in ('bits','parse'):
                def isnan(n):
                    n=int(n)&((1<<64)-1)
                    return n&0x7ff0000000000000==0x7ff0000000000000 and n&0xfffffffffffff!=0
                named_nan=aa[:2]==bb[:2] and isnan(aa[2]) and isnan(bb[2])
            else:
                named_nan=aa[:2]==bb[:2] and aa[2] in ('-nan','-nan.0') and bb[2]==aa[2][1:]
            counts['nan_differences' if named_nan else 'other_differences']+=1
            counts[kind+'.mismatch'] += 1
            samples.setdefault(kind,[])
            if len(samples[kind])<30:
                samples[kind].append(dict(line=lines,c=a.decode().strip(),wolf=b.decode().strip()))
        lines+=1
        if lines%100000==0: print(f'lines={lines} mismatches={sum(v for k,v in counts.items() if k.endswith("mismatch"))}',flush=True)
    cr,wr=c.wait(),w.wait()
    if cr or wr: raise RuntimeError(f'child exits C={cr} wolf={wr}')
result=dict(lines=lines,counts=dict(counts),samples=samples,c_sha256=sha_c.hexdigest(),wolf_sha256=sha_w.hexdigest())
pathlib.Path(outfile).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
