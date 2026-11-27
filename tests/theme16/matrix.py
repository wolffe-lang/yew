#!/usr/bin/env python3
"""Real-PTY theme selection, startup precedence and suppression matrix.

Rich auto is compared with an explicit old-theme capture from the same binary,
sample and judge, not a guessed quantizer. Reference captures are observations,
not indexed-palette passes. All output/receipts remain under a fresh --out.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', required=True)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    binary = str(Path(args.binary).resolve())
    cases = [
        ('auto16', []),
        ('forced16', ['--term', 'xterm-256color', '--env', 'YEW_COLORS=16']),
        ('explicit-dark16', ['--theme', 'quiver-dark', '--style-mode', 'dark16']),
        ('config-dark16', ['--config-theme', 'quiver-dark', '--style-mode', 'dark16']),
        ('env-over-config', ['--config-theme', 'quiver-dark', '--env', 'YEW_THEME=quiver-16']),
        ('cli-dark-over-env', ['--config-theme', 'quiver-16', '--env', 'YEW_THEME=quiver-16',
                               '--theme', 'quiver-dark', '--style-mode', 'dark16']),
        ('cli16-over-env', ['--config-theme', 'quiver-dark', '--env', 'YEW_THEME=quiver-dark',
                            '--theme', 'quiver-16']),
        ('custom16', ['--custom', '--theme', 'fixture-custom']),
        ('custom-truecolor', ['--custom', '--env', 'YEW_COLORS=truecolor', '--theme', 'fixture-custom']),
        ('no-color-empty', ['--env', 'NO_COLOR=', '--style-mode', 'mono']),
        ('no-color-set', ['--env', 'NO_COLOR=1', '--style-mode', 'mono']),
        ('dumb', ['--term', 'dumb', '--env', 'YEW_COLORS=16', '--style-mode', 'dumb']),
        ('explicit16-mono', ['--theme', 'quiver-16', '--env', 'NO_COLOR=', '--style-mode', 'mono']),
        ('explicit16-dumb', ['--theme', 'quiver-16', '--term', 'dumb', '--style-mode', 'dumb']),
        ('reference256', ['--term', 'xterm-256color', '--env', 'YEW_COLORS=256',
                           '--theme', 'quiver-dark', '--style-mode', 'observe']),
        ('auto256', ['--term', 'xterm-256color', '--env', 'YEW_COLORS=256',
                     '--reference', str(root / 'reference256/receipt.json')]),
        ('reference-truecolor', ['--env', 'YEW_COLORS=truecolor', '--theme', 'quiver-dark',
                                '--style-mode', 'observe']),
        ('auto-truecolor', ['--env', 'YEW_COLORS=truecolor',
                           '--reference', str(root / 'reference-truecolor/receipt.json')]),
    ]
    results = []
    for name, flags in cases:
        log = root / (name + '.log')
        command = [sys.executable, '-I', str(HERE / 'run.py'), '--binary', binary,
                   '--out', str(root / name), *flags]
        with log.open('w') as output:
            status = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                    env=dict(os.environ, SHELL='/bin/sh'), timeout=20).returncode
        receipt_path = root / name / 'receipt.json'
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        valid = receipt.get('document_verified') and receipt.get('editor_exit') == 0
        ok = status == 0 and valid
        observed = name.startswith('reference')
        results.append({'name': name, 'exit': status, 'document_verified': bool(valid),
                        'observation_only': observed, 'ok': bool(ok)})
        print(('OBSERVE ' if observed and ok else 'PASS ' if ok else 'FAIL ') + 'theme16-' + name,
              flush=True)
        if not ok:
            print(log.read_text(), flush=True)
    (root / 'matrix.json').write_text(json.dumps(results, indent=2) + '\n')
    return 0 if all(r['ok'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
