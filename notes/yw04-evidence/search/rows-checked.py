#!/usr/bin/env python3
# yw04-search: test_replace's 43-row table on the checked machine, one row a
# run (the whole table is past wolf test's step budget, G29): a scratch copy
# of src/search_replace_test.lu whose row loop runs only row K, `main`
# replaced by one `fn test_row()` calling `t_replace_rows()`, run with
# `wolf test --json`. In the container (RULES 5). Scratch files removed.
import json, os, re, subprocess, sys
root = os.getcwd()
wolf = os.path.join(root, ".wolf-bin/wolf")
src = open("src/search_replace_test.lu").read()
i = src.index("\nfn main(")
body = src[:i] + "\n"
loop = "    for r in rows {\n"
assert loop in body
env = dict(os.environ, YEW_LOG="/dev/null")
passed = failed = other = 0
for k in range(43):
    s = body.replace(loop, loop + "        if i != %d {\n            i += 1\n            continue\n        }\n" % k, 1)
    s += "fn test_row() {\n    t_replace_rows()\n}\n"
    path = os.path.join(root, "src/zz_rows_%02d_test.lu" % k)
    open(path, "w").write(s)
    try:
        out = subprocess.run([wolf, "test", "--json", path], capture_output=True, text=True, env=env, timeout=3600).stdout
    finally:
        os.remove(path)
    detail = "?"
    for line in out.splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if j.get("event") == "test":
            detail = j.get("detail", "?") + " " + j.get("status", "")
    verdict = "pass" if detail.startswith("exit(0) pass") else ("fail" if "fail" in detail else "other")
    passed += verdict == "pass"; failed += verdict == "fail"; other += verdict == "other"
    print("rows-checked: row %d %s %s" % (k, verdict, detail), flush=True)
print("rows-checked: totals rows=43 checked-pass=%d fail=%d other=%d" % (passed, failed, other))
