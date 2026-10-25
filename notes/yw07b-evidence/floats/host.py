#!/usr/bin/env python3
"""Record the unmodified public libc answer stream for host comparison."""
import gzip, hashlib, json, pathlib, subprocess, sys
corpus, executable, directory = sys.argv[1:]
out=pathlib.Path(directory); out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256(); count=0
with open(corpus,'rb') as source, gzip.open(out/'answers.gz','wb') as saved:
    proc=subprocess.Popen([executable],stdin=source,stdout=subprocess.PIPE)
    for line in proc.stdout:
        sha.update(line); saved.write(line); count+=1
    if proc.wait(): raise RuntimeError('oracle failed')
manifest=dict(lines=count,answer_sha256=sha.hexdigest(),input_sha256=hashlib.sha256(pathlib.Path(corpus).read_bytes()).hexdigest())
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
