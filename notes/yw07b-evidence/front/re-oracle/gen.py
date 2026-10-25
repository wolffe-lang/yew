#!/usr/bin/env python3
"""The re natives' oracle table: one Fletch program per case, run unchanged
in the pinned C yew and in the port.

  gen.py fl DIR            writes DIR/case-NNN.fl (C: prints the rendering)
  gen.py lu DIR > src/fl_std_re_direct_test.lu   (then wolf fmt it)

Each case's body runs inside `fn body()`; its value, or its raise as
`!kind: msg`, is rendered BY FLETCH (R below: str 'quoted', list [a,b],
map {k=v,...} in insertion order, int digits, nil, true, false) using
only str/list/map natives, so neither side's renderer is trusted. C
prints the rendering with io.print; the port returns it to flfix.run_bytes.
DIR/case-NNN.out is C's stdout for case NNN.
"""
import os
import sys

PRELUDE = r'''import re
import str
import list
import map
import io
fn istr(n) {
  if n == 0 { return "0" }
  let neg = n < 0
  let digits = "0123456789"
  let out = ""
  while n != 0 {
    let d = n % 10
    if d < 0 { d = 0 - d }
    out = str.at(digits, d) + out
    n = n / 10
  }
  if neg { return "-" + out }
  return out
}
fn R(v) {
  if v == nil { return "nil" }
  if v == true { return "true" }
  if v == false { return "false" }
  let k = 0
  try {
    str.len_bytes(v)
    k = 1
  } catch e { k = 0 }
  if k == 1 { return "'" + v + "'" }
  try {
    list.len(v)
    k = 2
  } catch e { k = 0 }
  if k == 2 {
    let out = "["
    let first = true
    for x in v {
      if first == false { out = out + "," }
      first = false
      out = out + R(x)
    }
    return out + "]"
  }
  try {
    map.len(v)
    k = 3
  } catch e { k = 0 }
  if k == 3 {
    let out = "{"
    let first = true
    for key, val in v {
      if first == false { out = out + "," }
      first = false
      out = out + key + "=" + R(val)
    }
    return out + "}"
  }
  return istr(v)
}
'''

CASES = []
def c(body):
    CASES.append(body)
def e(expr):
    CASES.append('return ' + expr)

# re.test: flags, anchors, decoding, errors
for x in [r're.test("abc", "b")', r're.test("abc", "z")', r're.test("ABC", "b", "i")',
          r're.test("a\nb", "a.b", "s")', r're.test("a\nb", "a.b")', r're.test("a.c", "a.c", "l")',
          r're.test("abc", "a.c", "l")', r're.test("abc", "B", nil)', r're.test("", "")',
          r're.test("abc", "^b")', r're.test("ab\ncd", "^c")', r're.test("\xc3\xa9", "^.$")',
          r're.test("\xff", "^.$")', r're.test("abc", "A", "isl")', r're.test("abc", "a", "ii")',
          r're.test("a", "(")', r're.test("a", "a", "q")', r're.test("a", "a", 5)',
          r're.test(5, "a")', r're.test("a", 5)', r're.test("a", "[z-a]")',
          r're.test("a", "a{1001}")', r're.test("a", "(?=a)")', r're.test("a", "\\1")',
          r're.test("a", "a", "\x00z")', r're.test("a", "a", "\xc3\xa9")', r're.test("a", "a", "i\x80")',
          r're.test("a", ")")', r're.test("a", "a**")', r're.test("x", "[[:alpha:]]")',
          r're.test("\xce\xa3", "\xcf\x83", "i")', r're.test("a\r\nb", "a$")', r're.test("ab", "\\bb")',
          r're.test("aB", "ab", "")', r're.test("abc", "abc", "l")', r're.test("a+b", "a+b", "il")']:
    e(x)
# re.find: the map, from, groups
for x in [r're.find("hello", "l+")', r're.find("hello", "z")', r're.find("hello", "l", nil, 3)',
          r're.find("ab", "a", nil, 9)', r're.find("ab", "a", nil, -1)', r're.find("ab", "a", nil, 2)',
          r're.find("ab", "", nil, 2)', r're.find("a1", "([a-z])([0-9])")', r're.find("xb", "x(q)?(b)")',
          r're.find("\xc3\xa9", "", nil, 1)', r're.find("ab", "a", "i", "1")', r're.find(5, "a", nil, "x")',
          r're.find("abc", "(a)|(b)", nil, 1)', r're.find("aaa", "(a)*")', r're.find("", "x?")',
          r're.find("ab", "(?:a)(b)")', r're.find("ab", "(a)(b)(c)?")', r're.find("ab", "a", nil, nil)',
          r're.find("AB", "b", "i")', r're.find("x\xffy", "\xff")', r're.find("abc", "c", nil, 3)',
          r're.find("hello", "(l)(l)?", nil, 3)', r're.find("ab", "(a)", 7)', r're.find("ab", "((a)(b))")']:
    e(x)
# re.find_all: non-overlapping, the empty-match rule, limits
for x in [r're.find_all("a1b22c", "[0-9]+")', r're.find_all("abc", "x*")',
          r're.find_all("\u{6F22}\u{5B57}", "x*")', r're.find_all("aaaa", "a", nil, 2)',
          r're.find_all("aaaa", "a", nil, -1)', r're.find_all("aaaa", "a", nil, 0)',
          r're.find_all("a\xffb", "x*")', r're.find_all("abab", "ab|")', r're.find_all("aaa", "a*")',
          r're.find_all("", "x*")', r're.find_all("ab", "(a)|b")', r're.find_all("aaaa", "aa")',
          r're.find_all("aaa", "a", nil, "2")', r're.find_all("AaA", "a", "i", 2)',
          r're.find_all("e\xcc\x81", "")']:
    e(x)
# re.replace: the template language
for x in [r're.replace("a1b", "[0-9]", "#")', r're.replace("a1b", "([a-z])([0-9])", "$2$1")',
          r're.replace("a1b", "([a-z])([0-9])", "${2}x")', r're.replace("ab", "b", "$$")',
          r're.replace("ab", "a(q)?", "[$1]")', r're.replace("abc", "x*", "-")',
          r're.replace("aaa", "a", "b", nil, 2)', r're.replace("ab", "a", "$")',
          r're.replace("ab", "a", "$z")', r're.replace("ab", "a", "${x}")', r're.replace("ab", "a", "$3")',
          r're.replace("a1b", "([a-z])([0-9])", "${12}")', r're.replace("ab", "a", "${123}")',
          r're.replace("ab", "a", "${1234}")', r're.replace("ab", "a", "${}")', r're.replace("ab", "a", "${1")',
          r're.replace("ab", "a", "$\xff")', r're.replace("ab", "a", "$\x00x")', r're.replace("aaa", "a", "b", nil, 0)',
          r're.replace("aaa", "a", "b", nil, -5)', r're.replace("a\x80b", "a", "A")', r're.replace("abc", "", "-")',
          r're.replace("ab", "(a)|(b)", "[$1$2]")', r're.replace("h\xc3\xa9llo", "", ".")', r're.replace("ab", "b", "$0$0")',
          r're.replace("aa", "a", "$z")', r're.replace("ab", "z", "$z")', r're.replace("ab", "a", 5)',
          r're.replace("ab", 5, 5)', r're.replace("abc", "B", "x", "i")', r're.replace("ab", "a", "${01}")',
          r're.replace("ab", "a", "${0}${00}")', r're.replace("a.b", ".", "!", "l")', r're.replace("", "x*", "-")',
          r're.replace("ab", "b", "x", nil, "1")', r're.replace("ab", "a", "$1", nil, 0)']:
    e(x)
# re.replace_fn: callbacks, re-entry, the pin
for x in [r're.replace_fn("a1b", "[0-9]", fn(m) { return "<" + m.text + ">" })',
          r're.replace_fn("a1b", "[0-9]", fn(m) { if re.test(m.text, "[0-9]") { return "N" } return "?" })',
          r're.replace_fn("a", "a", fn(m) { return 1 })', r're.replace_fn("a", "a", fn(m) { return nil })',
          r're.replace_fn("abc", "x*", fn(m) { return "-" })', r're.replace_fn("aaa", "a", fn(m) { return "b" }, nil, 2)',
          r're.replace_fn("a1", "([a-z])([0-9])", fn(m) { return m.groups[2].text + m.groups[1].text })',
          r're.replace_fn("ab", "a", fn(m, n) { return "x" })', r're.replace_fn("ab", "a", 5)',
          r're.replace_fn("a1b2", "[0-9]", fn(m) { return re.replace_fn(m.text, ".", fn(k) { return "(" + k.text + ")" }) })',
          r're.replace_fn("ab", "a", fn(m) { return 1 / 0 })', r're.replace_fn("ab", "(q)?b", fn(m) { return R(m.groups) })',
          r're.replace_fn("xyz", "y", fn(m) { return R(m) })', r're.replace_fn("ab", "b", str.upper)',
          r're.replace_fn("ab", "b", fn(m) { return m.text }, "q")']:
    e(x)
c(r'return re.replace_fn("a1b2c3", "[0-9]", fn(m) { let i = 0; while i < 70 { re.test("x", "p" + str.repeat("q", i)); i = i + 1 }; return "<" + m.text + ">" })')
c(r'''let seen = []
  let out = re.replace_fn("abcd", "[bd]", fn(m) { list.push(seen, m.lo); return str.upper(m.text) })
  return [out, seen]''')
# re.split
for x in [r're.split("a,b,,c", ",")', r're.split("a1b22c", "[0-9]+")', r're.split("abc", "x*")',
          r're.split("a,b,c", ",", nil, 1)', r're.split("a1b", "([0-9])")', r're.split("", ",")',
          r're.split("", "x*")', r're.split("a,b,c", ",", nil, 0)', r're.split("a,b,c", ",", nil, -1)',
          r're.split(",a,", ",")', r're.split("\xc3\xa9", "x*")', r're.split("aXbxc", "x", "i")',
          r're.split("a\xffb", "")', r're.split("abc", "c")', r're.split("abc", "a")']:
    e(x)
# re.escape
for x in [r're.escape("a.b*c")', r're.escape("")', r're.escape("\n\t\x00\xff")',
          r're.escape("()[]{}|^$\\.+*?")', r're.escape("\xc3\xa9#- /")', r're.escape(5)',
          r're.test("a.b*c", re.escape("a.b*c"))', r're.test("axbyc", re.escape("a.b*c"))']:
    e(x)
# the compile cache past 64 patterns
c(r'''let ok = true
  let i = 0
  while i < 200 {
    let p = "x" + str.repeat("y", i % 40) + "z"
    if re.test(p, p, "l") == false { ok = false }
    if re.test("no", p) == true { ok = false }
    i = i + 1
  }
  return ok''')
c(r'''let pats = []
  let i = 0
  while i < 130 {
    list.push(pats, "(a)" + str.repeat("b", i) + "c")
    i = i + 1
  }
  let out = []
  for p in pats { list.push(out, re.find("a" + str.repeat("b", 3) + "c", p) != nil) }
  for p in pats { list.push(out, re.test("zz", p)) }
  return list.len(list.filter(out, fn(x) { return x }))''')
c(r'''let s = str.repeat("\n", 16385)
  return re.test(s, re.escape(s))''')

def fl_case(i, wolf):
    body = CASES[i]
    tail = 'return r\n' if wolf else 'io.print(r)\n'
    return (PRELUDE + 'fn body() {\n  ' + body + '\n}\nlet r = nil\n'
            'try { r = R(body()) } catch e { r = "!" + e.kind + ": " + e.msg }\n' + tail)

def lu_str(s):
    # a wolf string literal: braces doubled, escapes for quote/backslash/controls
    out = '"'
    for ch in s:
        o = ord(ch)
        if ch == '"': out += '\\"'
        elif ch == '\\': out += '\\\\'
        elif ch == '{': out += '{{'
        elif ch == '}': out += '}}'
        elif ch == '\n': out += '\\n'
        elif o < 0x20 or o == 0x7f: raise SystemExit('control in case source')
        else: out += ch
    return out + '"'

HEADER = '''//! member: false
//! Direct coverage of the re natives, every case's answer the pinned C
//! yew's. sagitta 9ace98c2 src/fl/stdre.c:41-690. GENERATED by
//! notes/yw07b-evidence/front/re-oracle/gen.py: each case is ONE Fletch
//! program, run unchanged by the C yew (case-NNN.fl, its stdout case-NNN.out
//! there) and here through flfix; the program renders its own outcome with
//! str/list/map natives (str 'quoted', list [a,b], map {k=v} in insertion
//! order, ints, nil, true, false, a raise `!kind: msg`), so neither side's
//! renderer is trusted. Edit the table and regenerate (then wolf fmt).

use flfix

fn tohex(b: List[byte]) -> str {
    let digits = "0123456789abcdef"
    var out = List[byte]()
    for x in b {
        (mut out).push(digits.bytes()[x as int / 16])
        (mut out).push(digits.bytes()[x as int % 16])
    }
    str_from_utf8(out) else ""
}

fn prelude() -> str {
    PRELUDE_LITERAL
}

fn case(mut f: flfix.FlFix, idx: int, body: str, want: str) {
    let src = prelude() + "fn body() {{\\n  " + body + "\\n}}\\nlet r = nil\\n" +
        "try {{ r = R(body()) }} catch e {{ r = \\"!\\" + e.kind + \\": \\" + e.msg }}\\nreturn r\\n"
    let got = tohex(flfix.run_bytes(mut f, src))
    if got != want { eprint("case {idx}: got {got} want {want}") }
    assert(got == want)
}
'''

def emit_lu(d):
    groups = [('test', 0), ]
    print(HEADER.replace('PRELUDE_LITERAL', lu_str(PRELUDE)).rstrip('\n'))
    print()
    # one t_ function per 20 cases, so the per-case runner can split them
    per = int(os.environ.get('RE_GROUP', '1'))
    names = []
    for start in range(0, len(CASES), per):
        name = 't_case_%03d' % start if per == 1 else 't_cases_%03d' % start
        names.append(name)
        print('fn %s() {' % name)
        print('    var f = flfix.open()')
        for i in range(start, min(start + per, len(CASES))):
            out = open(os.path.join(d, 'case-%03d.out' % i), 'rb').read()
            assert out.endswith(b'\n'), i
            want = out[:-1].hex()
            print('    case(mut f, %d, %s, "%s")' % (i, lu_str(CASES[i]), want))
        print('    flfix.close(mut f)')
        print('}')
        print()
    print('fn main() {')
    for n in names:
        print('    %s()' % n)
    print('    print("PASS stdre direct: %d cases")' % len(CASES))
    print('}')

if __name__ == '__main__':
    if sys.argv[1] == 'fl':
        d = sys.argv[2]
        os.makedirs(d, exist_ok=True)
        for i in range(len(CASES)):
            open(os.path.join(d, 'case-%03d.fl' % i), 'w').write(fl_case(i, False))
        print(len(CASES))
    else:
        emit_lu(sys.argv[2])
