#!/usr/bin/env python3
"""compare: hold the lsp rows' kept screens to each other.

    compare.py KEEP

KEEP holds c/run1, c/run2, port/run1 and port/run2, each a directory of
`<case>.<screen>.snap` files in tests/pty/snapshot.c's format (the
goldens' own: a header, `--- text`, `--- style` rows of style tokens and
the style legend). Three checks, one line each screen:

  stable   each binary's two runs kept the same screens: the port's
           byte for byte but the header's frame count; C's over what
           `same` compares (C's syntax colouring is left out of both, as
           it settles on its own clock); an unstable screen prints the
           cells that moved
  same     C's screen and the port's, cell for cell: every glyph, the
           header (size, cursor, modes; not `sync_pairs`, the count of
           frames so far, since C's syntax engine paints frames of its own
           as it settles, ed.c:1383-1389), and every cell's style, except
           that in the document area (below the tab line, above the
           statusline, right of the gutter) a cell's foreground colour,
           bold and italic are not compared: they are syntax colouring,
           which is yw10's and not ported. Underline, undercurl, strike,
           dim, reverse and the background are compared everywhere, so a
           diagnostic's attributes are held exactly.

Prints `lsp-rows: <case>.<screen>: same` or `DIFFERS` with the first
cells that differ, then exits 0 only when every screen is stable and
same and both binaries kept the same set.
"""
import os
import re
import sys

GUTTER = 6  # the rows' gutter: sign column, four digits, one space


def parse(path):
    lines = open(path, "rb").read().decode("utf-8").split("\n")
    head, text, style, legend = [], [], [], {}
    part = "head"
    for line in lines:
        if line == "--- text":
            part = "text"
            continue
        if line == "--- style":
            part = "style"
            continue
        if part == "head":
            head.append(line)
        elif part == "text":
            text.append(line)
        else:
            m = re.match(r"^([A-Za-z]|#[0-9]+) fg=(\S+) bg=(\S+) attrs=(\S+)$", line)
            if m:
                legend[m.group(1)] = (m.group(2), m.group(3), m.group(4))
            elif line:
                style.append(line)
    return head, text, style, legend


def tokens(row):
    # A style token (snapshot.c's token_write): A..Z, a..z, then #N.
    return re.findall(r"[A-Za-z]|#[0-9]+", row)


def cell_style(legend, tok, in_document):
    fg, bg, attrs = legend.get(tok, ("?", "?", "?"))
    if in_document:
        attrs = "".join("-" if i in (0, 2) else ch for i, ch in enumerate(attrs))
        return ("*", bg, attrs)
    return (fg, bg, attrs)


def header(lines):
    return [re.sub(r" sync_pairs=[0-9]+", "", line) for line in lines]


def compare(a_path, b_path):
    a = parse(a_path)
    b = parse(b_path)
    out = []
    if header(a[0]) != header(b[0]):
        out.append("header: %r != %r" % (header(a[0]), header(b[0])))
    if a[1] != b[1]:
        for r, (x, y) in enumerate(zip(a[1], b[1])):
            if x != y:
                out.append("text row %d: %r != %r" % (r, x, y))
        if len(a[1]) != len(b[1]):
            out.append("text rows %d != %d" % (len(a[1]), len(b[1])))
    rows = len(a[2])
    if rows != len(b[2]):
        out.append("style rows %d != %d" % (rows, len(b[2])))
    for r in range(min(rows, len(b[2]))):
        ta, tb = tokens(a[2][r]), tokens(b[2][r])
        if len(ta) != len(tb):
            out.append("style row %d: %d cells != %d" % (r, len(ta), len(tb)))
            continue
        document = 0 < r < rows - 1
        for col, (x, y) in enumerate(zip(ta, tb)):
            doc = document and col >= GUTTER
            sx = cell_style(a[3], x, doc)
            sy = cell_style(b[3], y, doc)
            if sx != sy:
                out.append("style row %d col %d: %s != %s" % (r, col, sx, sy))
    return out


def stable_text(path):
    # The whole screen but its frame count (see `same` above).
    return re.sub(rb" sync_pairs=[0-9]+", b"", open(path, "rb").read())


def listing(d):
    return sorted(f for f in os.listdir(d) if f.endswith(".snap")) if os.path.isdir(d) else []


def main():
    keep = sys.argv[1]
    ok = True
    names = {}
    for tag in ("c", "port"):
        r1 = listing(os.path.join(keep, tag, "run1"))
        r2 = listing(os.path.join(keep, tag, "run2"))
        if r1 != r2:
            print("lsp-rows: %s: the two runs kept different screens" % tag)
            ok = False
        for f in r1:
            if f in r2:
                a = os.path.join(keep, tag, "run1", f)
                b = os.path.join(keep, tag, "run2", f)
                moved = compare(a, b)
                exact = stable_text(a) == stable_text(b)
                if moved or (tag == "port" and not exact):
                    print("lsp-rows: %s %s: unstable between runs" % (tag, f[:-5]))
                    for d in (moved or ["the bytes differ outside the compared cells"])[:12]:
                        print("lsp-rows:   " + d)
                    ok = False
        names[tag] = r1
    if names["c"] != names["port"]:
        print("lsp-rows: C kept %s; the port kept %s" % (names["c"], names["port"]))
        ok = False
    if not names["c"]:
        print("lsp-rows: no screens kept")
        ok = False
    for f in names["c"]:
        name = f[:-5]
        b = os.path.join(keep, "port", "run1", f)
        if not os.path.exists(b):
            print("lsp-rows: %s: DIFFERS (the port kept no such screen)" % name)
            ok = False
            continue
        diffs = compare(os.path.join(keep, "c", "run1", f), b)
        if diffs:
            print("lsp-rows: %s: DIFFERS" % name)
            for d in diffs[:12]:
                print("lsp-rows:   " + d)
            ok = False
        else:
            print("lsp-rows: %s: same" % name)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
