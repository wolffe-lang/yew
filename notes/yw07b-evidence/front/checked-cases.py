#!/usr/bin/env python3
"""Run the exact committed case bodies in fresh strict checked machines."""
import os
from pathlib import Path
import re
import subprocess
root = Path(__file__).resolve().parents[3]
stage = root / 'target/front/checked'
stage.mkdir(parents=True, exist_ok=True)
for name in ('fl', 'util', 'unicode'):
    link = stage / name
    if not link.exists():
        link.symlink_to(root / 'src' / name, target_is_directory=True)
rows = []
for suite in ('lex', 'parse'):
    source = (root / f'src/fl_{suite}_test.lu').read_text()
    prefix = source[:source.index('fn main()')]
    names = re.findall(r'fn (t_\w+)\(\)', prefix)
    for case, name in enumerate(names):
        entry = stage / f'{suite}_case_test.lu'
        entry.write_text(prefix + f'fn main() {{ {name}(); print("PASS {name}") }}\n')
        result = subprocess.run([os.environ['WOLF_BIN'], 'test', '--deny-warnings', '--nocapture', '--no-native-fallback', str(entry)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log = root / f'notes/yw07b-evidence/front/{suite}-case-{case:02}.log'
        log.write_bytes(result.stdout)
        verdict = 'PASS' if result.returncode == 0 else 'UNSUPPORTED' if b'call depth budget exhausted' in result.stdout else 'FAIL'
        rows.append((suite, case, name, verdict, result.returncode))
        print(*rows[-1], flush=True)
        if verdict == 'FAIL':
            print(result.stdout.decode(errors='replace'), flush=True)
(root / 'notes/yw07b-evidence/front/checked-cases.tsv').write_text('suite\tcase\tname\tverdict\texit\n' + ''.join('\t'.join(map(str,row))+'\n' for row in rows))
raise SystemExit(any(row[3] != 'PASS' for row in rows))
