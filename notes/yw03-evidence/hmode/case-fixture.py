#!/usr/bin/env python3
"""case-fixture — sagitta's generated src/unicode/tables_case.c as the
decimal fixture tools/check-tables and src/unicode/tables_case_test.lu
compare the port's tables against (tests/fixtures/unicode/tables_case-c.txt).

Usage: case-fixture.py SAGITTA_TREE > tests/fixtures/unicode/tables_case-c.txt
"""
import re
import sys

src = open(sys.argv[1] + "/src/unicode/tables_case.c").read()
data_body = src.split("static const u32 yew_case_data[] = {", 1)[1].split("};", 1)[0]
data = [int(x, 16) for x in re.findall(r"0x([0-9A-F]+)u", data_body)]
recs_body = src.split("static const struct YewCaseRec yew_case_recs[] = {", 1)[1].split("};", 1)[0]
recs = re.findall(r"\{0x([0-9A-F]+)u, (\d+)u, (\d+)u, (\d+)u, (\d+)u\}", recs_body)
print("# yew's Unicode 16.0.0 case tables as sagitta 9ace98c2's scripts/gen-unicode-tables --case emitted them")
print("# (src/unicode/tables_case.c): the cross-check for tools/gen-unicode-tables. Decimal, one array per line.")
print("data " + " ".join(str(v) for v in data))
print("recs " + " ".join("%d,%s,%s,%s,%s" % (int(r[0], 16), r[1], r[2], r[3], r[4]) for r in recs))
