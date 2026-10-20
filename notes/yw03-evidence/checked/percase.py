#!/usr/bin/env python3
# yw03 percase — the per-case checked-machine run for a test file that
# `wolf test` runs natively whole (G29: past the 20M-step budget a file's
# `main` falls back to one native run and says `ok`). yw02's percase.py
# renamed each `fn t_x()` to `fn test_x()`; this one keeps the cases and
# writes one `fn test_x()` WRAPPER per call `main` makes — main's
# prologue (its environment setup, before the first case) then the call
# exactly as main writes it, so a case that takes an argument or answers
# a SKIP count runs as main runs it — into a scratch copy with `main`
# dropped, and runs it with `wolf test --json`: every case on its own
# checked machine. `exit(0)` WITHOUT `[native]` is a checked pass;
# `unsupported` is the step budget (the case then rests on the native
# run). Warnings are not denied in the scratch copy (a prologue binding a
# wrapper does not use is W-lint, not meaning). Scratch files removed.
#
# usage: percase.py FILE... (from the repository root; YEW_ROOT_DIR
# overrides). Run in the container (RULES §5: some cases signal a child).
import json, os, re, subprocess, sys
root = os.environ.get("YEW_ROOT_DIR", os.getcwd())
wolf = os.path.join(root, ".wolf-bin/wolf")
env = dict(os.environ, YEW_LOG="/dev/null", XDG_STATE_HOME=os.path.join(root, "target/test-state"))
os.makedirs(env["XDG_STATE_HOME"], exist_ok=True)
CALL = re.compile(r"\bt_\w+\([^()]*\)")
for f in sys.argv[1:]:
    src = open(os.path.join(root, f)).read()
    i = src.index("\nfn main(")
    j = src.index("\n}\n", i) + 3
    main = src[i:j]
    body = src[:i] + "\n" + src[j:]
    lines = main.strip("\n").splitlines()[1:-1]
    first = next(k for k, l in enumerate(lines) if CALL.search(l))
    prologue = [l for l in lines[:first] if not l.strip().startswith("//")]
    calls = []
    for l in lines[first:]:
        for m in CALL.finditer(l):
            if m.group(0) not in calls:
                calls.append(m.group(0))
    wrappers = []
    for c in calls:
        name = c[2:c.index("(")]
        sig = re.search(r"^fn t_" + re.escape(name) + r"\([^)]*\)( -> int)? \{", body, re.M)
        if sig is None:
            continue
        stmt = f"    let _ = {c}" if sig.group(1) else f"    {c}"
        wrappers.append("fn test_" + name + "() {\n" + "\n".join(prologue) + "\n" + stmt + "\n}\n")
    base = os.path.basename(f)[:-len("_test.lu")]
    inside = os.path.dirname(f) != "src"
    # A test inside a module directory (`src/unicode/utf8_test.lu`) is a
    # member of that module: a scratch beside it would define every name
    # twice (E0302), so the scratch takes the file's place for the run.
    scratch = os.path.join(root, f) if inside else os.path.join(root, "src", "zzck_" + base + "_test.lu")
    open(scratch, "w").write(body + "\n" + "\n".join(wrappers))
    try:
        out = subprocess.run([wolf, "test", "--json", scratch], cwd=root, env=env,
                             capture_output=True, text=True, timeout=7200)
    finally:
        if inside:
            open(scratch, "w").write(src)
        else:
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
    if not out.stdout:
        print(out.stderr[-3000:])
    print(f"percase: {f} totals cases={len(wrappers)} checked-pass={n['pass']} fail={n['fail']} unsupported={n['unsupported']} other={n['other']}", flush=True)
