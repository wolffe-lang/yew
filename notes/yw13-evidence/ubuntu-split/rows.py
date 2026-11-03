#!/usr/bin/env python3
"""rows.py REV [REV...]: for each revision of .github/workflows/ci.yml, the
steps each oracle leg runs (the `oracle` job's steps whose `if:` holds for
that leg, plus, for the linux leg, every step of `oracle-cmdcomp` when that
job exists), with the setup steps (checkout, the C tree, the toolchain)
marked. Each step's `if:` is evaluated for the leg: matrix.port, matrix.os
and runner.os set, cancelled() false, success()/failure() as for a green
run. Prints one line per step: REV LEG JOB NAME."""
import re, subprocess, sys
LEGS = {
    "linux": {"matrix.os": "ubuntu-latest", "runner.os": "Linux", "matrix.port": True},
    "macos": {"matrix.os": "macos-latest", "runner.os": "macOS", "matrix.port": True},
}
SETUP = ("actions/checkout", "the pinned toolchain, by digest", "the pinned C tree for C's perf_cmdcomp")

def job(text, key):
    m = re.search(r"^  " + re.escape(key) + r":\n(.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)", text, re.M | re.S)
    return m[1] if m else None

def steps(block):
    out = []
    for m in re.finditer(r"^      - (name: [^\n]+|uses: [^\n]+)\n((?:(?: {8,}[^\n]*|)\n)*)", block, re.M):
        head, body = m[1], m[2]
        name = head[6:] if head.startswith("name: ") else head[6:]
        cond = re.search(r"^        if: (.+)$", body, re.M)
        if head.startswith("uses: "):
            cond2 = None
        out.append((name, cond[1].strip() if cond else None))
    return out

def holds(cond, leg):
    if cond is None:
        return True
    e = cond.strip()
    if e.startswith("${{") and e.endswith("}}"):
        e = e[3:-2].strip()
    for k, v in sorted(LEGS[leg].items(), key=lambda kv: -len(kv[0])):
        e = e.replace(k, repr(v))
    e = e.replace("!cancelled()", "True").replace("cancelled()", "False")
    e = e.replace("success()", "True").replace("failure()", "False").replace("always()", "True")
    e = e.replace("&&", " and ").replace("||", " or ")
    e = re.sub(r"!(?!=)", " not ", e)
    return bool(eval(e, {}, {}))

for rev in sys.argv[1:]:
    text = subprocess.run(["git", "show", f"{rev}:.github/workflows/ci.yml"], capture_output=True, text=True, check=True).stdout
    for leg in LEGS:
        rows = [("oracle", n) for n, c in steps(job(text, "oracle")) if holds(c, leg)]
        cmd = job(text, "oracle-cmdcomp")
        if leg == "linux" and cmd is not None:
            rows += [("oracle-cmdcomp", n) for n, c in steps(cmd) if holds(c, leg)]
        for j, n in rows:
            tag = "setup" if n.startswith(SETUP) else "row"
            print(f"{rev} {leg} {tag} {j} {n}")
