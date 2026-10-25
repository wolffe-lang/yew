#!/usr/bin/env python3
"""The str natives' oracle table: one source for the C program and the wolf test.

  gen.py fl            > cases.fl      the program the pinned C yew runs
  gen.py lu cases.out  > src/fl_std_str_direct_test.lu
  wolf fmt src/fl_std_str_direct_test.lu

cases.out is the C yew's stdout for cases.fl: one hex line per case, the
case's outcome rendered as flfix renders it (a raise is `!kind: msg`), with
lists and floats spelled as R_* below. The wolf test calls
fl_std_str_dispatch directly and compares its own rendering with C's.
"""
import sys

FAMILY = '\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466'.encode()

class S:
    def __init__(self, b): self.b = b if isinstance(b, bytes) else b.encode()
class I:
    def __init__(self, n): self.n = n
class F:
    def __init__(self, x): self.x = x
class N:
    pass
class L:
    def __init__(self, items): self.items = items

def LS(xs): return L([S(x) for x in xs])
def LI(xs): return L([I(x) for x in xs])

NAMES = ['len', 'len_bytes', 'is_empty', 'at', 'slice', 'slice_bytes', 'find',
         'find_bytes', 'rfind', 'contains', 'starts_with', 'ends_with', 'upper',
         'lower', 'trim', 'trim_start', 'trim_end', 'split', 'split_lines', 'join',
         'replace', 'repeat', 'pad_start', 'pad_end', 'width', 'bytes', 'from_bytes',
         'to_int', 'to_float', 'cmp']

# (group, native, args, render): render s=str i=int b=bool n=int|nil
# f=float|nil ls=list of str li=list of int
G = []
def c(group, name, args, render):
    G.append((group, name, args, render))

E = 'é'
HE = 'héllo'
# length, access, width
for s in ['abc', '', FAMILY, E + 'x', b'a\xffb', b'\xc3', '日本', b'\r\n']:
    c('access', 'len', [S(s)], 'i')
    c('access', 'len_bytes', [S(s)], 'i')
    c('access', 'is_empty', [S(s)], 'b')
c('access', 'len', [I(5)], 'i')
c('access', 'is_empty', [N()], 'b')
for s, i in [(HE, 1), (HE, -1), (FAMILY + b'x', 0), (FAMILY + b'x', 1), ('abc', 3),
             ('abc', -4), ('abc', -3), ('', 0), (E + 'x', 0), (b'\xff\xfe', 1)]:
    c('access', 'at', [S(s), I(i)], 's')
c('access', 'at', [S('abc'), F(1.5)], 's')
c('access', 'at', [I(1), I(0)], 's')
for s, a in [('abc', []), ('日本', []), ('\tx', []), ('\tx', [4]), ('a\tb', [0]),
             ('a', [257]), ('a', [-1]), ('a', [256]), (FAMILY, []), (E, []), (b'\xff', []),
             ('', []), ('\x01', []), ('ab​', [])]:
    c('access', 'width', [S(s)] + [I(x) for x in a], 'i')
c('access', 'width', [S('a'), S('8')], 'i')
# slicing
for a in [(HE, 1, 3), (HE, 1), ('abc', 2, 1), ('abc', -2), ('abc', 0, 4), ('abc', 5),
          ('abc', -4), (E + 'x', 0, 1), (FAMILY + b'ab', 1, 2), ('abc', 3), ('', 0, 0),
          ('abc', 0, -1)]:
    c('slice', 'slice', [S(a[0])] + [I(x) for x in a[1:]], 's')
c('slice', 'slice', [S('abc'), I(0), F(1.0)], 's')
for a in [(HE, 1, 3), (HE, 1, 2), (FAMILY, 0, 4), (FAMILY, 0, 25), ('abc', -1), ('abc', 0, 9),
          ('abc', -9), (E, 1), ('abc', 2, 1), (b'a\xffb', 1, 2), (b'\xe6\x97', 1),
          ('abc', 3, 3), ('', 0)]:
    c('slice', 'slice_bytes', [S(a[0])] + [I(x) for x in a[1:]], 's')
c('slice', 'slice_bytes', [S('abc'), S('1')], 's')
# searching
for a in [(HE, 'l'), (HE, 'l', 3), ('abc', 'z'), ('abc', ''), ('abc', '', 2), ('abc', 'a', 4),
          ('abc', 'c', -1), (FAMILY + b'x', '‍'), (FAMILY + b'x', 'x'), ('abc', 'abcd'),
          ('', ''), ('aaa', 'aa', 1)]:
    c('search', 'find', [S(a[0]), S(a[1])] + [I(x) for x in a[2:]], 'i')
for a in [(HE, 'l'), (HE, 'l', 4), (HE, 'l', 2), ('abc', 'bc', -2), ('abc', 'x', 9),
          ('abc', '', 3), (FAMILY + b'x', 'x', 25), (FAMILY + b'x', 'x', 8)]:
    c('search', 'find_bytes', [S(a[0]), S(a[1])] + [I(x) for x in a[2:]], 'i')
for a in [('abcabc', 'bc'), ('abc', ''), (HE, 'l'), ('aaa', 'aa'), ('abc', 'z'), ('', ''),
          (FAMILY + FAMILY, '‍'), (b'\xff\xff', b'\xff')]:
    c('search', 'rfind', [S(a[0]), S(a[1])], 'i')
for a in [('abc', 'bc'), ('abc', ''), ('', 'a'), ('a\xffb', '\xff')]:
    c('search', 'contains', [S(a[0]), S(a[1])], 'b')
c('search', 'contains', [S('abc'), I(1)], 'b')
for a in [('abc', 'ab'), ('abc', 'abcd'), ('abc', ''), ('', ''), (HE, b'h\xc3')]:
    c('search', 'starts_with', [S(a[0]), S(a[1])], 'b')
for a in [('abc', 'bc'), ('abc', 'zabc'), ('', ''), (HE, b'\xa9llo')]:
    c('search', 'ends_with', [S(a[0]), S(a[1])], 'b')
c('search', 'find', [S('abc'), S('a'), S('0')], 'i')
# case and trimming
for s in [HE, 'straße', b'a\xffb', 'ǆ', 'ﬁ', 'ΐ', 'i̇', 'İ',
          'ΣΣ', 'ABC', '', E, b'\xc3', 'ẞ', 'ⱥ', 'KELVIN K']:
    c('case', 'upper', [S(s)], 's')
    c('case', 'lower', [S(s)], 's')
c('case', 'upper', [I(3)], 's')
for s in ['  a b  ', '\t\n a ', '　x　', ' ́a', 'a ́', '\u0085x',
          b'\x85x', b'\xff ', '   ', '', ' a ', '\x0bv\x0c', 'a​',
          ' ' + E + ' ', '᠎x']:
    c('trim', 'trim', [S(s)], 's')
    c('trim', 'trim_start', [S(s)], 's')
    c('trim', 'trim_end', [S(s)], 's')
c('trim', 'trim', [N()], 's')
# splitting and joining
for a in [('a,b,,c', ','), ('a,b,c', ',', 2), ('abc', ''), (FAMILY + b'ab', '', 2), ('', ','),
          ('', ''), ('a,b', ',', -1), ('a,b', ',', 1), ('aaa', 'aa'), ('a,b', ',', 0),
          ('a::b::', '::'), (E + E, ''), ('abc', '', 1), ('x', 'x')]:
    c('split', 'split', [S(a[0]), S(a[1])] + [I(x) for x in a[2:]], 'ls')
c('split', 'split', [S('a'), I(1)], 'ls')
for s in ['a\r\nb\n', '', 'a\r\r\n', '\n', 'a\rb', 'x', '\r\n\r\n', b'\xff\n\xfe']:
    c('split', 'split_lines', [S(s)], 'ls')
c('split', 'join', [LS(['a', 'b']), S('-')], 's')
c('split', 'join', [LS([]), S('-')], 's')
c('split', 'join', [LS(['a']), S('')], 's')
c('split', 'join', [L([S('a'), I(1)]), S('-')], 's')
c('split', 'join', [L([N()]), S('-')], 's')
c('split', 'join', [S('a'), S('-')], 's')
c('split', 'join', [LS(['a']), I(5)], 's')
c('split', 'join', [LS([b'\xff', '', 'c']), S(b'\xc3')], 's')
# building
for a in [('aaaa', 'aa', 'b'), ('abcabc', 'b', 'XY', 1), ('abc', '', 'x'), ('abc', 'z', 'x'),
          ('abc', 'abc', ''), ('a.b.c', '.', '', 0), ('abab', 'ab', 'ab', -1), ('aaa', 'a', 'aa', 2),
          ('', 'a', 'b'), (HE, b'\xc3', 'X')]:
    c('build', 'replace', [S(a[0]), S(a[1]), S(a[2])] + [I(x) for x in a[3:]], 's')
c('build', 'replace', [S('a'), S('a'), I(1)], 's')
for a in [('ab', 3), ('ab', 0), ('ab', -1), ('ab', 33554433), ('', 1000), ('x', 67108865),
          ('', 0), (E, 2)]:
    c('build', 'repeat', [S(a[0]), I(a[1])], 's')
c('build', 'repeat', [S('ab'), F(2.0)], 's')
for name in ['pad_start', 'pad_end']:
    for a in [('ab', 5), ('ab', 5, '*'), ('ab', 5, 'xy'), ('日本', 5), ('ab', 1),
              ('ab', 5, ''), ('ab', 5, '日'), ('ab', 4, '-'), ('ab', 67108865), ('\t', 10),
              ('ab', -3), ('ab', 6, 'xyz'), ('ab', 5, '́')]:
        c('build', name, [S(a[0]), I(a[1])] + [S(x) for x in a[2:]], 's')
    c('build', name, [S('ab'), I(5), I(1)], 's')
# conversion
for s in ['é', '', b'\x00\xff']:
    c('convert', 'bytes', [S(s)], 'li')
c('convert', 'from_bytes', [LI([104, 105])], 's')
c('convert', 'from_bytes', [LI([255, 0, 254])], 's')
c('convert', 'from_bytes', [LI([])], 's')
c('convert', 'from_bytes', [LI([256])], 's')
c('convert', 'from_bytes', [LI([1, -1])], 's')
c('convert', 'from_bytes', [L([I(1), S('a')])], 's')
c('convert', 'from_bytes', [L([F(1.0)])], 's')
c('convert', 'from_bytes', [I(5)], 's')
for a in [('42',), (' -17',), ('+5',), ('12abc',), ('',), ('-',), ('ff', 16), ('FF', 16),
          ('z', 36), ('102', 2), ('9223372036854775807',), ('9223372036854775808',),
          ('-9223372036854775808',), ('18446744073709551616',), ('99999999999999999999',),
          ('12 ',), ('\t7',), ('\n7',), ('7', 1), ('7', 37), ('٣',), ('0x10', 16),
          ('-0',), ('  +',), ('1_0',), ('Zz', 36), ('-18446744073709551615',)]:
    c('convert', 'to_int', [S(a[0])] + [I(x) for x in a[1:]], 'n')
c('convert', 'to_int', [S('1'), F(10.0)], 'n')
for s in ['1.5', '-0.25', '1e3', ' 2', '2 ', '', 'abc', 'inf', '-Infinity', 'nan', '0x1p3',
          '1e400', '1e-400', '4.9e-324', '.5', '5.', '.', b'1.5\x00junk', b'\x00', '1' * 63,
          '1' * 64, '1_000', '0x', '-0', '+.5e-2', '\t\n\v\f\r 3', '1e', '0x1.8p1', 'NAN',
          '2.2250738585072011e-308', '0.1', '123456789012345678901234567890', b'\xff1']:
    c('convert', 'to_float', [S(s)], 'f')
c('convert', 'to_float', [I(1)], 'f')
for a in [('a', 'b'), ('b', 'a'), ('a', 'a'), ('a', 'ab'), (b'\xff', 'a'), ('', ''), ('ab', 'a')]:
    c('convert', 'cmp', [S(a[0]), S(a[1])], 'i')
c('convert', 'cmp', [I(1), S('a')], 'i')
c('convert', 'cmp', [S('a'), N()], 'i')

def fl_str(b):
    out = '"'
    for x in b:
        ch = chr(x)
        if 0x20 <= x <= 0x7e and ch not in '"\\':
            out += ch
        else:
            out += '\\x%02x' % x
    return out + '"'

def fl_arg(a):
    if isinstance(a, S): return fl_str(a.b)
    if isinstance(a, I): return str(a.n)
    if isinstance(a, F): return repr(a.x)
    if isinstance(a, N): return 'nil'
    return '[' + ', '.join(fl_arg(x) for x in a.items) + ']'

RENDER_FL = {'s': 'rs', 'i': 'ri', 'b': 'rb', 'n': 'rn', 'f': 'rf', 'ls': 'rls', 'li': 'rli'}

def emit_fl():
    print('import str\nimport fmt\nimport io\nimport list\n'
          'fn hex(s) {\n  let out = ""\n  for b in str.bytes(s) { out = out + fmt.hex(b, 2) }\n  return out\n}\n'
          'fn rs(v) { return v }\n'
          'fn ri(v) { return fmt.str(v) }\n'
          'fn rb(v) {\n  if v { return "true" }\n  return "false"\n}\n'
          'fn rn(v) {\n  if v == nil { return "nil" }\n  return fmt.str(v)\n}\n'
          'fn rf(v) {\n  if v == nil { return "nil" }\n  if v != v { return "nan" }\n'
          '  if v == 1.0 / 0.0 { return "inf" }\n  if v == -1.0 / 0.0 { return "-inf" }\n'
          '  return fmt.repr(v)\n}\n'
          'fn rls(v) { return "L" + fmt.str(list.len(v)) + ":" + str.join(v, "\\x01") }\n'
          'fn rli(v) {\n  let out = "L" + fmt.str(list.len(v)) + ":"\n'
          '  for x in v { out = out + fmt.str(x) + "," }\n  return out\n}\n'
          'let r = nil')
    for group, name, args, render in G:
        call = 'str.%s(%s)' % (name, ', '.join(fl_arg(a) for a in args))
        print('r = nil\ntry { r = %s(%s) } catch e { r = "!" + e.kind + ": " + e.msg }\n'
              'io.print(hex(r))' % (RENDER_FL[render], call))

def lu_arg(a, lets, n):
    name = 'v%d' % len(lets)
    if isinstance(a, S):
        lets.append('let %s = s(mut vm, "%s")' % (name, a.b.hex()))
    elif isinstance(a, I):
        lets.append('let %s = fl.fl_int(%d)' % (name, a.n))
    elif isinstance(a, F):
        lets.append('let %s = fl.fl_float(%r)' % (name, a.x))
    elif isinstance(a, N):
        lets.append('let %s = fl.fl_nil()' % name)
    else:
        items = [lu_arg(x, lets, n) for x in a.items]
        lets.append('let %s = lv(mut vm, [%s])' % (name, ', '.join(items))
                    if items else 'let %s = fl.fl_list_new(mut vm)' % name)
    return name

def emit_lu(outfile):
    text = open(outfile).read()
    assert text.endswith('\n')
    want = text[:-1].split('\n')
    assert len(want) == len(G), (len(want), len(G))
    print(HEADER_REAL)
    groups = []
    for g, *_ in G:
        if g not in groups: groups.append(g)
    for g in groups:
        print('fn t_%s() {' % g)
        print('    var vm = vm_new()')
        for idx, (gg, name, args, render) in enumerate(G):
            if gg != g: continue
            lets = []
            names = [lu_arg(a, lets, idx) for a in args]
            print('    // %d: str.%s(%s)' % (idx, name, ', '.join(fl_arg(a) for a in args)[:150]))
            print('    {')
            for l in lets:
                print('        ' + l)
            print('        row(mut vm, %d, %d, [%s], "%s", "%s")' %
                  (idx, NAMES.index(name), ', '.join(names), render, want[idx]))
            print('    }')
        print('}\n')
    print('fn main() {')
    for g in groups:
        print('    t_%s()' % g)
    print('    print("PASS stdstr direct: %d rows, %d cases")' % (len(G), len(groups)))
    print('}')

HEADER_REAL = None

if __name__ == '__main__':
    if sys.argv[1] == 'fl':
        emit_fl()
    else:
        HEADER_REAL = open(__file__.replace('gen.py', 'header.lu')).read().rstrip('\n') + '\n'
        emit_lu(sys.argv[2])
