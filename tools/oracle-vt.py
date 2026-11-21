#!/usr/bin/env python3
"""Apply the pinned non-visual protocol extension to the copied oracle test VT.

Only target/oracle/sagitta/tests/pty/vt.{c,h} may change. Original git blobs
are checked by revision and SHA256; arbitrary working-copy edits are refused.
Expected patched bytes derive from the checked-in literal edit specification.
The resulting SHA256 pins are printed and saved for the build rig to record.
The C editor and every original golden remain untouched.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FILES = frozenset(('tests/pty/vt.c', 'tests/pty/vt.h'))
SPEC = ROOT/'tests/oracle-vt/shift-capture.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def expected_files(spec, originals):
    if set(spec['files']) != FILES or set(originals) != FILES:
        raise ValueError('only the two oracle test-VT files may be adapted')
    result = {}
    for name in sorted(FILES):
        change = spec['files'][name]
        original = originals[name]
        if sha(original) != change['before_sha256']:
            raise ValueError('pinned original SHA256 changed: '+name)
        old = '\n'.join(change['old']).encode()
        new = '\n'.join(change['new']).encode()
        if not old or original.count(old) != 1:
            raise ValueError('literal patch context is not unique: '+name)
        result[name] = original.replace(old, new, 1)
    return result


def atomic_bytes(path, data):
    fd, temporary = tempfile.mkstemp(prefix=path.name+'.next-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
        os.chmod(temporary, path.stat().st_mode & 0o777 if path.exists() else 0o644)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install_files(tree, originals, expected, verify=False):
    # Validate every input before writing either file. Atomic replacement also
    # avoids modifying an original inode if a copy was accidentally hardlinked.
    for name in sorted(FILES):
        path = tree/name
        if path.is_symlink():
            raise ValueError('refuse symlinked test-VT input: '+name)
        data = path.read_bytes()
        allowed = (expected[name],) if verify else (originals[name], expected[name])
        if data not in allowed:
            raise ValueError('unrecognized working-copy bytes: '+name)
    if not verify:
        for name in sorted(FILES):
            if (tree/name).read_bytes() != expected[name]:
                atomic_bytes(tree/name, expected[name])
    return ''.join(sha(expected[name])+'  '+name+'\n' for name in sorted(FILES))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tree', type=Path, default=ROOT/'target/oracle/sagitta')
    p.add_argument('--verify', action='store_true')
    a = p.parse_args()
    allowed = ROOT/'target/oracle/sagitta'
    if a.tree.absolute() != allowed:
        raise ValueError('refuse a tree outside this checkout\'s copied oracle')
    for path in (ROOT/'target', ROOT/'target/oracle', allowed,
                 allowed/'tests', allowed/'tests/pty'):
        if path.is_symlink():
            raise ValueError('refuse symlinked oracle path: '+str(path))
    spec = json.loads(SPEC.read_text())
    rev = subprocess.check_output(['git','-C',str(allowed),'rev-parse','HEAD'],text=True).strip()
    if rev != spec['revision']:
        raise ValueError('oracle revision differs from test-VT patch pin')
    changed = subprocess.check_output(['git','-C',str(allowed),'diff','--name-only','HEAD'],text=True).splitlines()
    if set(changed) - FILES:
        raise ValueError('non-VT oracle files were modified: '+', '.join(sorted(set(changed)-FILES)))
    originals = {name:subprocess.check_output(['git','-C',str(allowed),'show',rev+':'+name])
                 for name in FILES}
    expected = expected_files(spec, originals)
    manifest = install_files(allowed, originals, expected, a.verify)
    atomic_bytes(ROOT/'target/oracle/vt.sha256', manifest.encode())
    for row in manifest.splitlines():
        print('oracle-vt: '+row, flush=True)
    print('oracle-vt: only copied test VT adapted; C editor and goldens unchanged', flush=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print('oracle-vt: REFUSED '+str(error), file=sys.stderr)
        sys.exit(2)
