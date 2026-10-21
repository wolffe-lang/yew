#!/usr/bin/env python3
"""cat-fixture — sagitta's generated src/unicode/tables_cat.c as the
decimal fixture tools/check-tables and src/unicode/tables_cat_test.lu
compare the port's category tables against
(tests/fixtures/unicode/tables_cat-c.txt), in the shape
`tools/gen-unicode-tables --dump --category` prints its own.

Usage: cat-fixture.py SAGITTA_TREE > tests/fixtures/unicode/tables_cat-c.txt
"""
import re
import sys

src = open(sys.argv[1] + "/src/unicode/tables_cat.c").read()


def body(name):
    return src.split(name, 1)[1].split("= {", 1)[1].split("};", 1)[0]


def nums(text):
    return [int(x, 0) for x in re.findall(r"0x[0-9A-Fa-f]+|\d+", text.replace("u", ""))]


stage1 = nums(body("yew_cat_stage1["))
stage2 = nums(body("yew_cat_stage2[]"))
pal = nums(body("yew_cat_pal[]"))
hi = re.findall(r"\{0x([0-9A-F]+)u, 0x([0-9A-F]+)u, 0x([0-9A-F]+)u\}", body("yew_cat_hi[]"))
print("# yew's Unicode 16.0.0 category trie as sagitta 9ace98c2's scripts/gen-unicode-tables --category emitted it")
print("# (src/unicode/tables_cat.c): the cross-check for tools/gen-unicode-tables. Decimal, one array per line.")
print("stage1 " + " ".join(str(v) for v in stage1))
print("stage2 " + " ".join(str(v) for v in stage2))
print("pal " + " ".join(str(v) for v in pal))
print("hi " + " ".join("%d,%d,%d" % (int(a, 16), int(b, 16), int(c, 16)) for a, b, c in hi))
