#!/usr/bin/env python3
# yw03-word — run src/edit_wordbreak_test.lu on the CHECKED machine in row
# slices. `wolf test` falls the whole file back to one native run (its
# corpus is past the checked machine's 20M-step budget, G29), and the file
# has one case, so the per-case shape (yw02's percase.py) cannot split it:
# a scratch copy gets the corpus loop restricted to rows [lo, hi) and one
# `fn test_rows_<lo>()` per slice, `main` and the whole-corpus counts
# dropped; every slice must report `exit(0)` WITHOUT `[native]`, and the
# slices' rows must cover all 1,826. Scratch file removed.
import json, os, re, subprocess, sys
root = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/lanes/yw03/word/yew")
step = int(sys.argv[2]) if len(sys.argv) > 2 else 100
wolf = os.path.join(root, ".wolf-bin/wolf")
env = dict(os.environ, YEW_LOG="/dev/null", XDG_STATE_HOME=os.path.join(root, "target/test-state"))
os.makedirs(env["XDG_STATE_HOME"], exist_ok=True)
src = open(os.path.join(root, "src/edit_wordbreak_test.lu")).read()
i = src.index("\nfn main(")
body = src[:i] + "\n"
body = body.replace("fn t_wordbreak_unicode_16_corpus() {", "fn corpus_rows(lo: int, hi: int) {")
body = body.replace("        region row {", "        if rows < lo || rows >= hi {\n            rows += 1\n            continue\n        }\n        region row {")
body = re.sub(r"    assert\(rows == EXPECTED_ROWS.*\n    assert\(marks_total == EXPECTED_MARKS.*\n", "    assert(marks_total > 0 || lo >= EXPECTED_ROWS, \"slice [{lo}, {hi}) checked marks\")\n", body)
assert "corpus_rows" in body and "if rows < lo" in body and "marks_total > 0" in body
total = 1826
for lo in range(0, total, step):
    body += f"\nfn test_rows_{lo}() {{\n    corpus_rows({lo}, {min(total, lo + step)})\n}}\n"
scratch = os.path.join(root, "src", "zzck_wordbreak_test.lu")
open(scratch, "w").write(body)
try:
    out = subprocess.run([wolf, "test", "--json", "--deny-warnings", scratch], cwd=root, env=env,
                         capture_output=True, text=True, timeout=7200)
finally:
    os.remove(scratch)
n = {"checked": 0, "native": 0, "fail": 0, "unsupported": 0}
for line in out.stdout.splitlines():
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("event") == "test":
        st, det = r.get("status"), r.get("detail", "")
        if st == "pass" and "[native]" not in det:
            n["checked"] += 1
        elif st == "pass":
            n["native"] += 1
        elif st == "unsupported":
            n["unsupported"] += 1
        else:
            n["fail"] += 1
        print(f"slices: {r.get('name')} {st} {det}")
    elif r.get("event") == "summary":
        print(f"slices: summary {r}")
if out.returncode != 0 and not out.stdout:
    print(out.stderr[-3000:])
print(f"slices: rows 0..{total} in slices of {step}: checked-pass={n['checked']} native={n['native']} unsupported={n['unsupported']} fail={n['fail']}")
