#!/usr/bin/env python3
"""Independent editing-intent checks for the common LSP corpus.

The mirror server's view==disk assertion remains necessary but is not an
expected-file oracle. This checker does not normalize the C/port comparator.
"""
import argparse
import importlib.util
from pathlib import Path
import re
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('lsp_compare', HERE / 'compare.py')
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)

ORIGINAL = ['fn main() -> int {', '    let a: int = 1', '    let b: int = 2', '    a + b', '}']
EDITED = ['fn main() -> int {', 'z    let a: int = 1', 'z    let b: int = 2', '    a + b', '}']
MIRROR_START = ['fn main() -> int {', '    // \U0001d11e clef!',
                '    let a: int = 1w    let b: int = 2', '    a + b', '}']
MIRROR_END = ['fn main() -> int {', '    // \U0001d11e clef!',
              '    let a: int = 1    let b: int = 2w', '    a + b', '}']


def document_errors(text, expected, count_two=False):
    got = [line[compare.GUTTER:].rstrip() for line in text[1:1+len(expected)]]
    errors = []
    if got != expected:
        errors.append('document bytes/lines differ from independent editing intent: ' + repr(got))
    # The fixture contains no such marker in document text; this is a footer
    # assertion, not a substring search through escape output or the source.
    if count_two and (len(text) < 24 or re.search(r'×2(?![0-9])', text[23]) is None):
        errors.append('footer does not declare exactly two carets')
    return errors


def saved_errors(data, expected):
    want = ('\n'.join(expected) + '\n').encode()
    return [] if data == want else ['saved file differs from independent expected UTF-8 bytes']


class Controls(unittest.TestCase):
    def frame(self, lines, count='×2'):
        rows = ['tabs'] + [' '*6 + s for s in lines]
        rows += ['']*(23-len(rows))
        return rows + [' L main.lu ' + count]

    def test_accepts_exact_two_site_edit_and_undo(self):
        self.assertEqual(document_errors(self.frame(EDITED), EDITED, True), [])
        self.assertEqual(document_errors(self.frame(ORIGINAL), ORIGINAL, True), [])

    def test_rejects_wrong_text(self):
        wrong = list(EDITED); wrong[1] += 'wrong'
        self.assertTrue(document_errors(self.frame(wrong), EDITED, True))

    def test_rejects_single_site_fanout(self):
        wrong = list(EDITED); wrong[2] = ORIGINAL[2]
        self.assertTrue(document_errors(self.frame(wrong), EDITED, True))

    def test_rejects_incomplete_undo(self):
        wrong = list(ORIGINAL); wrong[2] = EDITED[2]
        self.assertTrue(document_errors(self.frame(wrong), ORIGINAL, True))

    def test_rejects_one_or_three_carets(self):
        for count in ('', '×1', '×3', '×20'):
            self.assertTrue(document_errors(self.frame(EDITED, count), EDITED, True))

    def test_rejects_self_consistent_but_wrong_mirror_file(self):
        self.assertTrue(saved_errors(b'wrong but matches its server\n', MIRROR_START))
        self.assertEqual(saved_errors(('\n'.join(MIRROR_START)+'\n').encode(), MIRROR_START), [])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('keep', type=Path, nargs='?')
    p.add_argument('--filter', default='')
    p.add_argument('--mirror-end', action='store_true')
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Controls))
        return 0 if result.wasSuccessful() else 1
    if args.keep is None:
        p.error('KEEP required')
    ok = True
    mirror = MIRROR_END if args.mirror_end else MIRROR_START
    for tag in ('c', 'port'):
        for run in ('run1', 'run2'):
            root = args.keep / tag / run
            for name, expected, count in (
                ('lspw_multicursor.1-two', EDITED, True),
                ('lspw_multicursor.2-undo', ORIGINAL, True),
                ('lspf_mirror_sync.1-saved', mirror, False),
            ):
                case = name.split('.')[0]
                if args.filter and args.filter not in case:
                    continue
                path = root / (name + '.snap')
                errors = ['missing required snapshot'] if not path.is_file() else document_errors(compare.parse(path)[1], expected, count)
                if case == 'lspf_mirror_sync':
                    saved = root / (case + '.saved')
                    errors += ['missing saved-byte receipt'] if not saved.is_file() else saved_errors(saved.read_bytes(), mirror)
                print(('FAIL ' if errors else 'PASS ') + 'lsp-intent-' + tag + '-' + run + '-' + name)
                for error in errors:
                    print('  ' + error)
                ok = not errors and ok
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
