#!/usr/bin/env python3
"""Apply the pinned adaptations to the copied oracle's test harness.

Two adaptations, each a checked-in literal edit specification:
  - the non-visual protocol extension of the test VT: tests/pty/vt.{c,h}
    (tests/oracle-vt/shift-capture.json), pins in target/oracle/vt.sha256;
  - the harness's read after the reap (yew#124): tests/pty/harness.c
    (tests/oracle-harness/restore-after-reap.json), pins in
    target/oracle/harness.sha256.
Only those three files beneath target/oracle/sagitta may change. Original git
blobs are checked by revision and SHA256; arbitrary working-copy edits are
refused. Expected patched bytes derive from the checked-in specifications.
The resulting SHA256 pins are printed and saved for the build rig to record.
The C editor, the cases and every original golden remain untouched.
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
HARNESS_FILES = frozenset(('tests/pty/harness.c',))
HARNESS_SPEC = ROOT/'tests/oracle-harness/restore-after-reap.json'
# (spec, the files it may change, its pin file, what the refusal names)
ADAPTATIONS = (
    (SPEC, FILES, 'vt.sha256', 'the two oracle test-VT files'),
    (HARNESS_SPEC, HARNESS_FILES, 'harness.sha256', 'the oracle harness file'),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def expected_files(spec, originals, files=FILES, what='the two oracle test-VT files'):
    if set(spec['files']) != files or set(originals) != files:
        raise ValueError('only '+what+' may be adapted')
    result = {}
    for name in sorted(files):
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


def check_files(tree, originals, expected, verify=False, files=FILES):
    """Refuse a symlink or unrecognized bytes in any of these files, writing nothing."""
    for name in sorted(files):
        path = tree/name
        if path.is_symlink():
            raise ValueError('refuse symlinked test-VT input: '+name)
        data = path.read_bytes()
        allowed = (expected[name],) if verify else (originals[name], expected[name])
        if data not in allowed:
            raise ValueError('unrecognized working-copy bytes: '+name)


def install_files(tree, originals, expected, verify=False, files=FILES):
    # Validate every input before writing either file. Atomic replacement also
    # avoids modifying an original inode if a copy was accidentally hardlinked.
    check_files(tree, originals, expected, verify, files)
    if not verify:
        for name in sorted(files):
            if (tree/name).read_bytes() != expected[name]:
                atomic_bytes(tree/name, expected[name])
    return ''.join(sha(expected[name])+'  '+name+'\n' for name in sorted(files))


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
    rev = subprocess.check_output(['git','-C',str(allowed),'rev-parse','HEAD'],text=True).strip()
    adaptable = frozenset().union(*(files for _, files, _, _ in ADAPTATIONS))
    changed = subprocess.check_output(['git','-C',str(allowed),'diff','--name-only','HEAD'],text=True).splitlines()
    if set(changed) - adaptable:
        raise ValueError('oracle files outside the adaptations were modified: '
                         +', '.join(sorted(set(changed)-adaptable)))
    plans = []
    for spec_path, files, pin, what in ADAPTATIONS:
        spec = json.loads(spec_path.read_text())
        if rev != spec['revision']:
            raise ValueError('oracle revision differs from the pin of '+spec_path.name)
        originals = {name:subprocess.check_output(['git','-C',str(allowed),'show',rev+':'+name])
                     for name in files}
        plans.append((files, pin, originals, expected_files(spec, originals, files, what)))
    # Every adaptation's inputs are checked before any file is written.
    for files, _, originals, expected in plans:
        check_files(allowed, originals, expected, a.verify, files)
    for files, pin, originals, expected in plans:
        manifest = install_files(allowed, originals, expected, a.verify, files)
        atomic_bytes(ROOT/'target/oracle'/pin, manifest.encode())
        for row in manifest.splitlines():
            print('oracle-vt: '+row, flush=True)
    print('oracle-vt: only the copied test VT and harness adapted; C editor, cases and goldens unchanged', flush=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print('oracle-vt: REFUSED '+str(error), file=sys.stderr)
        sys.exit(2)
