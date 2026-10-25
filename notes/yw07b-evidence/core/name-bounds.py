#!/usr/bin/env python3
import pathlib,subprocess
root=pathlib.Path('/home/mfwolffe/lanes/yw07b/core')
name='x'*200
cases=[('global','return '+name,'name',("undefined name '"+name+"'")[:127]),('assignment',name+' = 1','name',("undefined name '"+name+"'")[:127]),('field','let m = {}\nreturn m.'+name,'key',("no field '"+name+"' on map")[:159])]
for case,src,kind,want in cases:
    p=subprocess.run([root/'target/oracle-core','-e',src],capture_output=True)
    (root/f'notes/yw07b-evidence/core/name-bounds-c-{case}.stderr').write_bytes(p.stderr)
    assert p.returncode==1
    first=p.stderr.splitlines()[0]
    assert first==f'error: {kind}: {want}'.encode(),first
    print(f'PASS C {case} message_bytes={len(want)} exit={p.returncode}')
