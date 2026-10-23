#!/usr/bin/env python3
"""State-only differential; normalize only the informational saved_at."""
import pathlib, re, subprocess
root=pathlib.Path.cwd()
out=root/'notes/yw06-evidence/state'
for name in ('negative-wire','negative-multi-wire'):
    for mutate in (False,True):
        suffix='-edited' if mutate else '-unchanged'
        paths=[]
        for impl in ('oracle','roundtrip'):
            dst=out/f'{name}{suffix}-{impl}.fl'
            cmd=[str(root/f'target/state/state-{impl}'),str(out/f'{name}.fl'),str(dst)]
            if mutate:cmd.append('--mutate')
            subprocess.run(cmd,check=True)
            data=dst.read_bytes()
            paths.append(re.sub(rb'(?m)^    saved_at: [0-9]+,',b'    saved_at: 0,',data))
        if paths[0]!=paths[1]:
            import difflib
            print(''.join(difflib.unified_diff(paths[0].decode().splitlines(True),paths[1].decode().splitlines(True))),flush=True)
            raise SystemExit(f'FAIL {name}{suffix}')
        print(f'PASS C-Wolf {name}{suffix}',flush=True)
