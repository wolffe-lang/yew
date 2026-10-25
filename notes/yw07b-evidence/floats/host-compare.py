#!/usr/bin/env python3
"""R-yw07b-2: Linux libc is oracle; only proved NaN host differences exempt."""
import collections
import gzip
import hashlib
import itertools
import json
import pathlib
import sys


def nan_bits(text):
    try:
        bits = int(text) & ((1 << 64) - 1)
    except ValueError:
        return False
    return (bits & 0x7ff0000000000000) == 0x7ff0000000000000 and (bits & 0xfffffffffffff) != 0


def allowed_nan(left, right):
    a, b = left.strip().split(':', 2), right.strip().split(':', 2)
    if len(a) != 3 or len(b) != 3 or a[:2] != b[:2]:
        return False
    if a[0] == 'parse':
        # Same consumed length; both results must actually be IEEE NaNs.
        return nan_bits(a[2]) and nan_bits(b[2])
    if a[0] in ('fixed', 'exp', 'general'):
        return a[2] in ('nan', '-nan') and b[2] in ('nan', '-nan')
    if a[0] == 'shortest':
        return a[2] in ('nan.0', '-nan.0') and b[2] in ('nan.0', '-nan.0')
    # A raw bits row must be byte-identical; no other class is excused.
    return False


left, right, destination = map(pathlib.Path, sys.argv[1:4])
corpus = pathlib.Path(sys.argv[4]) if len(sys.argv) == 5 else None
a = json.loads((left / 'manifest.json').read_text())
b = json.loads((right / 'manifest.json').read_text())
assert a['input_sha256'] == b['input_sha256'] and a['lines'] == b['lines']
def input_rows():
    if corpus is None:
        while True: yield None
    else:
        assert hashlib.sha256(corpus.read_bytes()).hexdigest() == a['input_sha256']
        with corpus.open() as source:
            for row in source:
                row = row.removesuffix('\n')
                assert row.startswith(('B ', 'P '))
                for _ in range(41 if row.startswith('B ') else 1):
                    yield row
inputs = input_rows()
counts = collections.Counter()
classified = collections.Counter()
samples, fatal_samples = [], []
seen = 0
with gzip.open(left / 'answers.gz', 'rt') as x, gzip.open(right / 'answers.gz', 'rt') as y:
    for line, (u, v) in enumerate(itertools.zip_longest(x, y), 1):
        if u is None or v is None:
            raise RuntimeError('different answer stream lengths')
        seen += 1
        source_row = next(inputs)
        if u == v:
            continue
        kind = u.split(':', 1)[0]
        counts[kind] += 1
        category = 'fatal'
        if allowed_nan(u, v):
            category = 'nan_presentation'
        elif (source_row == 'P nan(+1)' and
              u == 'parse:3:9221120237041090560\n' and
              v == 'parse:7:9221120237041090560\n'):
            category = 'nan_payload_grammar'
        allowed = category != 'fatal'
        classified[category] += 1
        sample = dict(line=line, input=source_row, linux=u.strip(), macos=v.strip(), allowed_class=category)
        if len(samples) < 60:
            samples.append(sample)
        if not allowed and len(fatal_samples) < 60:
            fatal_samples.append(sample)
assert seen == a['lines'], (seen, a['lines'])
if corpus is not None:
    assert next(inputs, None) is None
result = dict(oracle='Linux glibc', ruling='R-yw07b-2 and R-yw07b-3', counts=dict(counts),
              classified=dict(classified), samples=samples, fatal_samples=fatal_samples,
              linux=a, macos=b)
destination.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
if classified['fatal']:
    sys.exit('STOP R-yw07-4: non-NaN C host difference')
print(f"float-hosts: nan_presentation={classified['nan_presentation']} nan_payload_grammar={classified['nan_payload_grammar']} fatal=0; Linux remains port oracle")
