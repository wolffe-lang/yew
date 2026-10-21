#!/usr/bin/env python3
# yw04-regex golden-slices — the golden table on the checked machine in
# slices. test_re_golden_table_bytes / _textbuf run 188 rows each, past
# the checked machine's 20M-step budget (G29: wolf test then falls back
# to a native run), so this writes a scratch copy of
# src/search_re_match_test.lu with `main` dropped and one `fn test_...`
# per slice of N rows per backing, and runs it with `wolf test --json`:
# every slice on its own checked machine. `exit(0)` without `[native]` is
# a checked pass; `unsupported` is the step budget (that slice then rests
# on the native run, which runs every row). Scratch removed after.
#
# usage: golden-slices.py [N]   (from the repository root, in the container)
import json, os, subprocess, sys
root = os.getcwd()
n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
wolf = os.path.join(root, ".wolf-bin/wolf")
src = open(os.path.join(root, "src/search_re_match_test.lu")).read()
i = src.index("\nfn main(")
j = src.index("\n}\n", i) + 3
body = src[:i] + "\n" + src[j:]
rows = [l for l in open(os.path.join(root, "tests/fixtures/search/re_golden.txt")) if l.strip() and not l.startswith("#")]
wrappers = []
for backing, flag in (("bytes", "false"), ("textbuf", "true")):
    for lo in range(0, len(rows), n):
        hi = min(lo + n, len(rows))
        wrappers.append(f"""fn test_golden_{backing}_{lo:03d}_{hi:03d}() {{
    env_set("YEW_LOG", "/dev/null") else |_| {{}}
    var t = Tally {{ n: 0 }}
    let rows = golden_rows()
    var i = {lo}
    while i < {hi} {{
        check_row(mut t, rows[i], {flag})
        i += 1
    }}
}}
""")
scratch = os.path.join(root, "src", "zzck_golden_slices_test.lu")
open(scratch, "w").write(body + "\n" + "\n".join(wrappers))
try:
    out = subprocess.run([wolf, "test", "--json", scratch], cwd=root, capture_output=True, text=True, timeout=14400)
finally:
    os.remove(scratch)
tot = {"pass": 0, "fail": 0, "unsupported": 0, "other": 0}
for line in out.stdout.splitlines():
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("event") == "test":
        st = r.get("status")
        det = r.get("detail", "")
        key = st if st in tot else "other"
        if "[native]" in det:
            key = "other"
        tot[key] += 1
        print(f"golden-slices: {r.get('name')} {st} {det}")
print(f"golden-slices: slices={len(wrappers)} rows={len(rows)} per-slice={n} checked-pass={tot['pass']} fail={tot['fail']} unsupported={tot['unsupported']} other={tot['other']}")
if out.returncode != 0 and tot["fail"] == 0 and tot["pass"] == 0:
    print(out.stdout[-2000:], out.stderr[-2000:])
