#!/usr/bin/env python3
"""Run each committed case of a test entry in its own strict checked machine.

usage: cases.py FILE [--stress] [--only NAME...]

Each zero-argument case main() calls runs alone (the file's helpers kept
verbatim) under `wolf test --deny-warnings --nocapture --no-native-fallback`,
with YEW_FL_GC_STRESS=1 under --stress. A checked-machine step-budget
exhaustion is UNSUPPORTED, never a pass. Writes one log per case and a TSV
under target/front/cases/.
"""
import os
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
args = sys.argv[1:]
stress = '--stress' in args
only = []
if '--only' in args:
    only = args[args.index('--only') + 1:]
    args = args[:args.index('--only')]
args = [a for a in args if a != '--stress']
src_file = root / args[0]
stage = root / 'target/front/cases'
stage.mkdir(parents=True, exist_ok=True)
for d in (root / 'src').iterdir():
    if d.is_dir():
        link = stage / d.name
        if not link.exists():
            link.symlink_to(d, target_is_directory=True)
source = src_file.read_text()
prefix = source[:source.index('fn main()')]
main = source[source.index('fn main()'):]
# The cases are the zero-argument calls main makes, in its order: t_* or
# sagitta's registry names alike.
defined = re.findall(r'^fn (\w+)\(\)', prefix, re.M)
names = sorted((n for n in defined if re.search(r'\b' + n + r'\(\)', main)),
               key=lambda n: re.search(r'\b' + n + r'\(\)', main).start())
if only:
    names = [n for n in names if n in only]
env = dict(os.environ)
env['WOLF_STD'] = '/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std'
if stress:
    env['YEW_FL_GC_STRESS'] = '1'
wolf = '/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf'
tag = src_file.stem + ('.stress' if stress else '')
rows = []
for case, name in enumerate(names):
    entry = stage / f'{src_file.stem}_case_test.lu'
    entry.write_text(prefix + f'fn main() {{ {name}(); print("PASS {name}") }}\n')
    result = subprocess.run([wolf, 'test', '--deny-warnings', '--nocapture', '--no-native-fallback', str(entry)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    log = stage / f'{tag}.{case:02}.{name}.log'
    log.write_bytes(result.stdout)
    out = result.stdout
    if result.returncode == 0 and f'PASS {name}'.encode() in out:
        verdict = 'PASS'
    elif b'budget exhausted' in out:
        verdict = 'UNSUPPORTED'
    else:
        verdict = 'FAIL'
    rows.append((tag, case, name, verdict, result.returncode))
    print(*rows[-1], flush=True)
    if verdict == 'FAIL':
        print(out.decode(errors='replace')[-3000:], flush=True)
(stage / f'{tag}.tsv').write_text('file\tcase\tname\tverdict\texit\n' +
                                  ''.join('\t'.join(map(str, r)) + '\n' for r in rows))
counts = {v: sum(1 for r in rows if r[3] == v) for v in ('PASS', 'UNSUPPORTED', 'FAIL')}
print(f'{tag}: {counts["PASS"]} PASS, {counts["UNSUPPORTED"]} UNSUPPORTED, {counts["FAIL"]} FAIL')
raise SystemExit(1 if counts['FAIL'] else 0)
