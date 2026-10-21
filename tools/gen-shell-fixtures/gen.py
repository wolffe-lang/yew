#!/usr/bin/env python3
"""gen-shell-fixtures — sagitta's shell-completion corpora as data.

Reads the C tables of sagitta's unit tests at `sagitta.pin`
(`tests/unit/shctx_corpus.h`: `sh_corpus`, `sh_cwd_corpus`;
`tests/unit/compspec_corpus.h`: `spec_corpus`) and writes one text
fixture per table under `tests/fixtures/shell/`, one row per line, the
fields TAB-separated (a line starting `#` is a comment, so a row's own
leading `#` is written `\\x23`). A string field is its BYTES with `\\`, TAB, LF, CR
and every byte outside 0x20..0x7e written `\\xNN`; C's NULL is `\\N`. A
constant (`SC_ARG`, `SC_TILDE | SC_EXPANDS`) is its integer. The port's
tests (`src/edit_shctx_test.lu`, `src/edit_compspec_test.lu`) read these;
`tools/check-shell-fixtures` regenerates them from the oracle tree and
diffs, so the data is sagitta's, never edited.

Usage: gen.py SAGITTA_TREE OUT_DIR
"""
import re
import sys

CONSTS = {
    "SC_CMD": 0, "SC_ARG": 1, "SC_RED": 2, "SC_ASG": 3, "SC_VAR": 4, "SC_NON": 5,
    "SC_QN": 0, "SC_QS": 1, "SC_QD": 2, "SC_QL": 3,
    "SC_DASHDASH": 1, "SC_BRACE": 2, "SC_TILDE": 4, "SC_EXPANDS": 8,
    "SC_UNKNOWN": None, "NULL": None,
}

ESC = {"n": 10, "t": 9, "r": 13, "\\": 92, '"': 34, "'": 39, "0": 0, "a": 7,
       "b": 8, "f": 12, "v": 11, "e": 27, "?": 63}


def strip_comments(text):
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("/*", i):
            j = text.index("*/", i + 2)
            i = j + 2
            out.append(" ")
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text[i] == '"':
            j = i + 1
            while text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def c_string(body):
    """Decode one C string literal's body (between quotes) to bytes."""
    raw = body.encode("utf-8")
    out = bytearray()
    i = 0
    while i < len(raw):
        c = raw[i]
        if c != 92:
            out.append(c)
            i += 1
            continue
        e = chr(raw[i + 1])
        if e == "x":
            j = i + 2
            while j < len(raw) and chr(raw[j]) in "0123456789abcdefABCDEF":
                j += 1
            out.append(int(raw[i + 2:j], 16) & 255)
            i = j
        elif e in "01234567":
            j = i + 1
            while j < len(raw) and j < i + 4 and chr(raw[j]) in "01234567":
                j += 1
            out.append(int(raw[i + 1:j], 8) & 255)
            i = j
        else:
            out.append(ESC[e])
            i += 2
    return bytes(out)


def tokens(s):
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            while s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            yield ("str", s[i + 1:j])
            i = j + 1
        elif c in "{},|":
            yield (c, c)
            i += 1
        else:
            m = re.match(r"[A-Za-z0-9_]+", s[i:])
            yield ("id", m.group(0))
            i += len(m.group(0))


def table(text, name):
    m = re.search(r"\b" + re.escape(name) + r"\s*\[\s*\]\s*=\s*\{", text)
    if m is None:
        raise SystemExit(f"gen-shell-fixtures: no table {name}")
    depth = 1
    i = m.end()
    start = i
    while depth:
        if text[i] == '"':
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    body = text[start:i - 1]
    rows = []
    row = None
    field = None
    for kind, val in tokens(body):
        if kind == "{":
            row = []
            field = []
        elif kind == "}":
            if field:
                row.append(field)
            rows.append(row)
            row = None
        elif kind == ",":
            if row is not None:
                row.append(field)
                field = []
        else:
            field.append((kind, val))
    return [[value(f) for f in r] for r in rows]


def value(parts):
    strs = [v for k, v in parts if k == "str"]
    if strs:
        return b"".join(c_string(s) for s in strs)
    acc = 0
    for k, v in parts:
        if k == "|":
            continue
        if v in CONSTS:
            if CONSTS[v] is None:
                return None
            acc |= CONSTS[v]
        elif re.fullmatch(r"[0-9]+U?", v):
            acc |= int(v.rstrip("U"))
        else:
            raise SystemExit(f"gen-shell-fixtures: unknown constant {v}")
    return acc


def field_text(v):
    if v is None:
        return "\\N"
    if isinstance(v, int):
        return str(v)
    out = []
    for b in v:
        if b == 92:
            out.append("\\\\")
        elif 0x20 <= b <= 0x7E:
            out.append(chr(b))
        else:
            out.append("\\x%02x" % b)
    return "".join(out)


def emit(path, rows, header):
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f"# {header}\n")
        for r in rows:
            line = "\t".join(field_text(v) for v in r)
            if line.startswith("#"):
                # A row's own leading `#` is data, never a comment line.
                line = "\\x23" + line[1:]
            f.write(line + "\n")


def main():
    tree, out = sys.argv[1], sys.argv[2]
    sh = strip_comments(open(f"{tree}/tests/unit/shctx_corpus.h", encoding="utf-8").read())
    spec = strip_comments(open(f"{tree}/tests/unit/compspec_corpus.h", encoding="utf-8").read())
    emit(f"{out}/shctx_corpus.txt", table(sh, "sh_corpus"),
         "GENERATED by tools/gen-shell-fixtures from sagitta tests/unit/shctx_corpus.h sh_corpus: in pos quote argv0 arg_index raw stem flags depth")
    emit(f"{out}/shctx_cwd.txt", table(sh, "sh_cwd_corpus"),
         "GENERATED by tools/gen-shell-fixtures from sagitta tests/unit/shctx_corpus.h sh_cwd_corpus: in cwd")
    emit(f"{out}/compspec_corpus.txt", table(spec, "spec_corpus"),
         "GENERATED by tools/gen-shell-fixtures from sagitta tests/unit/compspec_corpus.h spec_corpus: in kind rows")


main()
