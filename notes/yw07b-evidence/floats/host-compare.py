#!/usr/bin/env python3
import collections, gzip, json, pathlib, sys
left,right,destination=map(pathlib.Path,sys.argv[1:])
a=json.loads((left/'manifest.json').read_text()); b=json.loads((right/'manifest.json').read_text())
assert a['input_sha256']==b['input_sha256'] and a['lines']==b['lines']
counts=collections.Counter(); samples=[]
with gzip.open(left/'answers.gz','rt') as x, gzip.open(right/'answers.gz','rt') as y:
    for line,(u,v) in enumerate(zip(x,y),1):
        if u!=v:
            kind=u.split(':',1)[0]; counts[kind]+=1
            if len(samples)<60: samples.append(dict(line=line,linux=u.strip(),macos=v.strip()))
result=dict(counts=dict(counts),samples=samples,linux=a,macos=b)
destination.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if counts: sys.exit('STOP R-yw07-4: pinned conversion sites differ by host')
