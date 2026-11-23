#!/usr/bin/env python3
"""Controls for the narrowly pinned copied-oracle adaptations (no compiler run)."""
import copy
import hashlib
import importlib.util
import json
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


class HarnessAdaptation(unittest.TestCase):
    """The harness's read after the reap (yew#124), tests/oracle-harness/."""

    def setUp(self):
        base = ROOT/'target/oracle-vt-test-tmp'
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.tmp.cleanup)
        self.tree = Path(self.tmp.name)
        self.name = 'tests/pty/harness.c'
        self.original = b'void f(void)\n{\n}\n'
        self.spec = {'files': {self.name: {'before_sha256': hashlib.sha256(self.original).hexdigest(),
                                           'old': ['void f(void)', '{', '}'],
                                           'new': ['void f(void)', '{', '    wait();', '}']}}}
        (self.tree/'tests/pty').mkdir(parents=True)
        (self.tree/self.name).write_bytes(self.original)

    def expected(self):
        return module.expected_files(self.spec, {self.name: self.original},
                                     module.HARNESS_FILES, 'the oracle harness file')

    def test_patch_and_pin(self):
        expected = self.expected()
        manifest = module.install_files(self.tree, {self.name: self.original}, expected,
                                        files=module.HARNESS_FILES)
        self.assertEqual((self.tree/self.name).read_bytes(), b'void f(void)\n{\n    wait();\n}\n')
        self.assertEqual(manifest, hashlib.sha256(expected[self.name]).hexdigest()+'  '+self.name+'\n')

    def test_the_harness_spec_names_only_the_harness(self):
        bad = copy.deepcopy(self.spec)
        bad['files']['tests/pty/vt.c'] = bad['files'][self.name]
        with self.assertRaisesRegex(ValueError, 'only the oracle harness file'):
            module.expected_files(bad, {self.name: self.original, 'tests/pty/vt.c': self.original},
                                  module.HARNESS_FILES, 'the oracle harness file')

    def test_the_vt_spec_cannot_name_the_harness(self):
        with self.assertRaisesRegex(ValueError, 'only the two'):
            module.expected_files(self.spec, {self.name: self.original})

    def test_drifted_bytes_are_refused_before_a_write(self):
        (self.tree/self.name).write_bytes(b'foreign\n')
        with self.assertRaisesRegex(ValueError, 'working-copy bytes'):
            module.check_files(self.tree, {self.name: self.original}, self.expected(),
                               files=module.HARNESS_FILES)
        self.assertEqual((self.tree/self.name).read_bytes(), b'foreign\n')


class CheckedInSpecs(unittest.TestCase):
    """The two checked-in specifications, as tools/oracle-vt.py applies them."""

    def load(self, path):
        return json.loads(path.read_text())

    def test_both_pin_the_oracle_revision_of_sagitta_pin(self):
        pin = dict(line.split('=', 1) for line in (ROOT/'sagitta.pin').read_text().split('\n')
                   if line.startswith('SAGITTA_'))['SAGITTA_REV']
        for spec, _, _, _ in module.ADAPTATIONS:
            self.assertEqual(self.load(spec)['revision'], pin, spec.name)

    def test_each_names_exactly_its_files_and_one_literal_edit(self):
        seen = set()
        for spec, files, _, _ in module.ADAPTATIONS:
            data = self.load(spec)
            self.assertEqual(set(data['files']), set(files), spec.name)
            self.assertFalse(seen & set(files), 'two specifications name one file')
            seen |= set(files)
            for name, change in data['files'].items():
                self.assertRegex(change['before_sha256'], '^[0-9a-f]{64}$')
                self.assertTrue(change['old'] and change['new'] and change['old'] != change['new'], name)
        self.assertEqual([p for _, _, p, _ in module.ADAPTATIONS], ['vt.sha256', 'harness.sha256'])

    def test_the_harness_edit_keeps_the_message_and_names_why_the_wait_ended(self):
        change = self.load(module.HARNESS_SPEC)['files']['tests/pty/harness.c']
        old, new = '\n'.join(change['old']), '\n'.join(change['new'])
        self.assertTrue(old.startswith('void ptc_expect_output(PtyCtx *c, const void *bytes, size_t len)\n{'))
        self.assertIn('static int wait_for_output_after_reap(PtyCtx *c, const void *bytes,', new)
        self.assertIn('waited = wait_for_output_after_reap(c, bytes, len);', new)
        self.assertIn('"expected output |%s| was not observed%s"', new)
        for why in ('" after the terminal closed"', '" after a 2000 ms wait past the reap"'):
            self.assertIn(why, new)
        # Only the failing path after a reap waits: otherwise it returns at once.
        self.assertIn('if (!c->pty.reaped || c->eof)\n        return 0;', new)


if __name__ == '__main__':
    unittest.main()
