#!/usr/bin/env python3
"""Controls for the narrowly pinned copied-VT adaptation (no compiler run)."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('oracle_vt', ROOT/'tools/oracle-vt.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Adaptation(unittest.TestCase):
    def setUp(self):
        base = ROOT/'target/oracle-vt-test-tmp'
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.tmp.cleanup)
        self.tree = Path(self.tmp.name)
        self.originals = {'tests/pty/vt.c': b'before C\n', 'tests/pty/vt.h': b'before H\n'}
        self.spec = {'files': {}}
        for name, data in self.originals.items():
            self.spec['files'][name] = {'before_sha256': hashlib.sha256(data).hexdigest(),
                                       'old': [data.decode().rstrip('\n')],
                                       'new': ['after '+name]}
            path = self.tree/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.expected = module.expected_files(self.spec, self.originals)

    def test_exact_patch_idempotence_and_recorded_hashes(self):
        first = module.install_files(self.tree, self.originals, self.expected)
        second = module.install_files(self.tree, self.originals, self.expected, verify=True)
        self.assertEqual(first, second)
        self.assertEqual(module.install_files(self.tree, self.originals, self.expected), first)
        for name, data in self.expected.items():
            self.assertEqual((self.tree/name).read_bytes(), data)
            self.assertIn(hashlib.sha256(data).hexdigest()+'  '+name, first)

    def test_original_hash_drift_is_refused(self):
        changed = dict(self.originals)
        changed['tests/pty/vt.c'] += b'drift'
        with self.assertRaisesRegex(ValueError, 'SHA256 changed'):
            module.expected_files(self.spec, changed)

    def test_non_unique_context_is_refused(self):
        bad = copy.deepcopy(self.spec)
        bad['files']['tests/pty/vt.c']['old'] = ['absent']
        with self.assertRaisesRegex(ValueError, 'not unique'):
            module.expected_files(bad, self.originals)

    def test_other_files_cannot_be_named(self):
        bad = copy.deepcopy(self.spec)
        bad['files']['src/main.c'] = bad['files']['tests/pty/vt.c']
        with self.assertRaisesRegex(ValueError, 'only the two'):
            module.expected_files(bad, self.originals)

    def test_working_copy_drift_refuses_before_any_write(self):
        changed = self.tree/'tests/pty/vt.h'
        changed.write_bytes(b'foreign edit')
        with self.assertRaisesRegex(ValueError, 'working-copy bytes'):
            module.install_files(self.tree, self.originals, self.expected)
        self.assertEqual((self.tree/'tests/pty/vt.c').read_bytes(), self.originals['tests/pty/vt.c'])
        self.assertEqual(changed.read_bytes(), b'foreign edit')

    def test_verify_refuses_an_unpatched_copy(self):
        with self.assertRaisesRegex(ValueError, 'working-copy bytes'):
            module.install_files(self.tree, self.originals, self.expected, verify=True)
        for name, data in self.originals.items():
            self.assertEqual((self.tree/name).read_bytes(), data)

    def test_editor_and_goldens_are_untouched(self):
        protected = ['src/main.c', 'tests/pty/goldens/example.golden']
        for name in protected:
            path = self.tree/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'protected original\n')
        module.install_files(self.tree, self.originals, self.expected)
        for name in protected:
            self.assertEqual((self.tree/name).read_bytes(), b'protected original\n')

    def test_symlinked_file_is_refused(self):
        outside = self.tree/'original-copy.c'
        outside.write_bytes(self.originals['tests/pty/vt.c'])
        path = self.tree/'tests/pty/vt.c'
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlinked'):
            module.install_files(self.tree, self.originals, self.expected)
        self.assertEqual(outside.read_bytes(), self.originals['tests/pty/vt.c'])


if __name__ == '__main__':
    unittest.main()
