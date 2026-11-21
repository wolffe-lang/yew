#!/usr/bin/env python3
"""Build and run the copied test-VT protocol rows, optionally on real captures.

Call only on an approved build slot. --capture paths are raw editor PTY output,
not mouse-input logs. No request filtering or relay is involved.
"""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cc', default=os.environ.get('CC', 'cc'))
    p.add_argument('--capture', type=Path, action='append', default=[])
    a = p.parse_args()
    tree = ROOT/'target/oracle/sagitta'
    subprocess.run([sys.executable, '-I', str(ROOT/'tools/oracle-vt.py'), '--verify'], check=True)
    output = ROOT/'target/oracle/shift-capture-test'
    sources = [ROOT/'tests/oracle-vt/shift_capture.c', tree/'tests/pty/vt.c']
    sources += [tree/'src'/name for name in (
        'util/base.c', 'util/buf.c', 'util/log.c',
        'unicode/utf8.c', 'unicode/grapheme.c', 'unicode/width.c', 'unicode/tables.c')]
    cmd = shlex.split(a.cc) + ['-std=c11', '-Wall', '-Wextra', '-Werror', '-O2',
                               '-I'+str(tree/'src'), '-I'+str(tree/'tests/pty')]
    cmd += [str(s) for s in sources] + ['-o', str(output)]
    subprocess.run(cmd, check=True)
    home = ROOT/'target/oracle/vt-home'
    home.mkdir(exist_ok=True)
    env = dict(os.environ, HOME=str(home), XDG_STATE_HOME=str(home/'state'),
               XDG_CONFIG_HOME=str(home/'config'), SHELL='/bin/sh')
    status = subprocess.run([str(output)], env=env).returncode
    for capture in a.capture:
        status = max(status, subprocess.run([str(output), '--capture', str(capture.resolve())], env=env).returncode)
    return status


if __name__ == '__main__':
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode or 2)
    except (OSError, ValueError) as error:
        print('oracle-vt-check: '+str(error), file=sys.stderr)
        sys.exit(2)
