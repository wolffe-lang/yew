#!/usr/bin/env python3
# yw05-wait percase (yw04-prompt's, unchanged) — the per-case checked-machine run (G29) for the
# prompt's three test files, which `wolf test` runs natively whole (each
# builds an editor per case past the 20M-step budget). yw03's percase.py
# (notes/yw03-evidence/checked/) keyed on `t_` names; these files name
# their cases as C does and call them bare from `main`, each after an
# `eprint` trace line. This writes one `fn test_x()` wrapper per bare call
# into a scratch copy with `main` dropped and runs `wolf test --json`:
# every case on its own checked machine. `exit(0)` WITHOUT `[native]` is a
# checked pass; `unsupported` is the step budget (the case then rests on
# the native run). Scratch files removed. Run in the container from the
# repository root (RULES §5).
import json, os, re, subprocess, sys
root = os.environ.get("YEW_ROOT_DIR", os.getcwd())
wolf = os.path.join(root, ".wolf-bin/wolf")
env = dict(os.environ, YEW_LOG="/dev/null")
CALL = re.compile(r"^\s+([a-z_][a-z0-9_]*)\(\)\s*$")
for f in sys.argv[1:]:
    src = open(os.path.join(root, f)).read()
    i = src.index("\nfn main(")
    j = src.index("\n}\n", i) + 3
    main = src[i:j]
    body = src[:i] + "\n" + src[j:]
    calls = []
    for l in main.splitlines():
        m = CALL.match(l)
        if m and m.group(1) not in calls:
            calls.append(m.group(1))
    wrappers = ["fn test_" + c + "() {\n    let _ = " + c + "()\n}\n" for c in calls]
    base = os.path.basename(f)[:-len("_test.lu")]
    scratch = os.path.join(root, "src", "zzck_" + base + "_test.lu")
    open(scratch, "w").write(body + "\n" + "\n".join(wrappers))
    try:
        out = subprocess.run([wolf, "test", "--json", scratch], cwd=root, env=env,
                             capture_output=True, text=True, timeout=14400)
    finally:
        os.remove(scratch)
    n = {"pass": 0, "fail": 0, "unsupported": 0, "other": 0}
    for line in out.stdout.splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("event") == "test":
            st = r.get("status")
            det = r.get("detail", "")
            key = st if st in n else "other"
            if "[native]" in det:
                key = "other"
            n[key] += 1
            print(f"percase: {f} {r.get('name')} {st} {det}", flush=True)
    if not out.stdout or n["pass"] == 0:
        print(out.stderr[-3000:])
    print(f"percase: {f} totals cases={len(wrappers)} checked-pass={n['pass']} fail={n['fail']} unsupported={n['unsupported']} other={n['other']}", flush=True)
