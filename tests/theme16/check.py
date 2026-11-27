#!/usr/bin/env python3
"""Exact runtime key/payload conservation, explicit pens and reference contrast."""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
GROUPS = {
    2: 'comment quote',
    6: 'comment.doc',
    7: 'text variable variable.param punct punct.bracket punct.delim emphasis',
    8: 'ui.invisible',
    9: 'variable.builtin variable.member tag diff.del error whitespace.special',
    10: 'character string string.special code diff.add',
    11: 'type type.builtin constant constant.builtin number boolean comment.todo attribute tag.attr warning motion.count',
    13: 'keyword keyword.control keyword.storage preproc label list motion.unit',
    14: 'keyword.op operator string.escape string.interp function function.builtin function.macro method namespace link motion.arrow motion.cmd',
    15: 'heading strong',
}
EXPECTED = {name: index for index, names in GROUPS.items() for name in names.split()}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unliteral(text):
    out, i = [], 0
    escapes = {'\\': '\\', '"': '"', 't': '\t', 'r': '\r'}
    while i < len(text):
        c = text[i]
        if c in '{}':
            assert text[i:i+2] == c*2, 'unescaped interpolation brace'
            out.append(c)
            i += 2
        elif c == '\\':
            n = text[i+1]
            if n == 'x':
                out.append(chr(int(text[i+2:i+4], 16)))
                i += 4
            else:
                out.append(escapes[n])
                i += 2
        else:
            out.append(c)
            i += 1
    return ''.join(out).encode()


def check_assets(blob_path):
    receipt = json.loads((HERE / 'runtime-assets.json').read_text())
    unchanged = receipt['unchanged']
    expected = set(unchanged) | {'init.fl', 'themes/quiver-16.fl'}
    blob = blob_path.read_text()
    constants = dict(re.findall(r'const (RUNTIME_FILE_[0-9]+): str = """\n(.*?)"""', blob, re.S))
    arms = re.findall(r'"([^"]+)" => \(true, (RUNTIME_FILE_[0-9]+)\)', blob)
    names = re.findall(r'\(mut out\)\.push\("([^"]+)"\)', blob)
    assert len(arms) == len(set(p for p, _ in arms)), 'duplicate embedded lookup'
    assert len(names) == len(set(names)), 'duplicate embedded name'
    assert {p for p, _ in arms} == set(names) == expected, 'key sets differ in either direction'
    assert len(constants) == len(arms), 'orphan/missing embedded constants'
    for relative, constant in arms:
        source = (ROOT / 'runtime' / relative).read_bytes()
        assert unliteral(constants[constant]) == source, 'embedded payload drift: ' + relative
        if relative in unchanged:
            assert sha(source) == unchanged[relative], 'old asset changed: ' + relative
        elif relative == 'init.fl':
            assert sha(source) == receipt['auto_init_sha256'], 'unapproved init default delta'
    print('PASS theme16-runtime-keys-both-directions (' + str(len(expected)) + ')')
    print('PASS theme16-old-assets-unchanged (' + str(len(unchanged)) + ')')


def check_palette():
    src = (ROOT / 'runtime/themes/quiver-16.fl').read_text()
    old = (ROOT / 'runtime/themes/quiver-dark.fl').read_text()
    attrs = src.split('    attrs: {', 1)[1]
    entries = re.findall(r'^\s*(?:"([^"]+)"|([a-z][\w.]*)):\s*\{\s*fg:\s*\{\s*idx:\s*(\d+)\s*\}', attrs, re.M)
    got = {(a or b): int(index) for a, b, index in entries}
    assert len(entries) == len(got) == len(EXPECTED) == 54
    assert got == EXPECTED, 'explicit syntax pen mismatch'
    assert 'dim:' not in attrs and not re.search(r'fg:\s*["@]', attrs)
    def ui(text):
        return text.split('    palette: ', 1)[1].split('    attrs: ', 1)[0]
    assert ui(src).replace('bg: { idx: 0 }, fg: { idx: 7 },', 'bg: "@bg", fg: "@fg",') == ui(old), 'shared palette/UI source changed'
    reference = json.loads((HERE / 'vt-reference.json').read_text())
    palette = reference['rgb']
    assert len(palette) == 16
    def luminance(rgb):
        def linear(c):
            s = c/255
            return s/12.92 if s <= .04045 else ((s+.055)/1.055)**2.4
        return sum(w*linear(c) for w, c in zip((.2126, .7152, .0722), rgb))
    ratios = {i: (luminance(palette[i])+.05)/(luminance(palette[0])+.05) for i in range(16)}
    assert all(ratios[index] >= 4.5 for name, index in EXPECTED.items() if name != 'ui.invisible')
    assert 4.12 < ratios[12] < 4.14 and 12 not in got.values(), 'blue12 negative control'
    assert palette[7] == [170, 170, 170] and palette[8] == [85, 85, 85]
    assert palette[11] == [255, 255, 85] and palette[13] == [255, 85, 255]
    print('PASS theme16-explicit-palette (54)')
    print('PASS theme16-ui-source-conserved')
    print('PASS theme16-reference-contrast (blue12=' + format(ratios[12], '.3f') + ', excluded)')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blob', type=Path, default=ROOT / 'src/edit/runtime_blob.lu')
    args = p.parse_args()
    check_assets(args.blob)
    check_palette()


if __name__ == '__main__':
    main()
