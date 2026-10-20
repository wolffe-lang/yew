#!/usr/bin/env python3
# yw03-view percase — yw02's percase.py (notes/yw02-evidence/checked/) at
# the view fork's clone: each `fn t_x()` of a test file renamed
# `fn test_x()`, `main` dropped, a scratch copy run by `wolf test --json`
# so every case gets its own checked machine (no whole-file native
# fallback). A case reported `exit(0)` WITHOUT `[native]` passed checked;
# `unsupported` is the step budget. Scratch files removed.
import json, os, re, subprocess, sys
root = os.path.expanduser(os.environ.get("YEW_ROOT_DIR", "~/lanes/yw03/view"))
wolf = os.path.join(root, ".wolf-bin/wolf")
env = dict(os.environ, YEW_LOG="/dev/null", XDG_STATE_HOME=os.path.join(root, "target/test-state"))
os.makedirs(env["XDG_STATE_HOME"], exist_ok=True)
for f in sys.argv[1:]:
    src = open(os.path.join(root, f)).read()
    i = src.index("\nfn main(")
    j = src.index("\n}\n", i) + 3
    body = src[:i] + "\n" + src[j:]
    body = re.sub(r"^fn t_", "fn test_", body, flags=re.M)
    base = os.path.basename(f)[:-len("_test.lu")]
    scratch = os.path.join(root, "src", "zzck_" + base + "_test.lu")
    open(scratch, "w").write(body)
    try:
        out = subprocess.run([wolf, "test", "--json", "--deny-warnings", scratch], cwd=root, env=env,
                             capture_output=True, text=True, timeout=3600)
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
            print(f"percase: {f} {r.get('name')} {st} {det}")
        elif r.get("event") == "summary":
            print(f"percase: {f} summary {r}")
    if not out.stdout:
        print(out.stderr[-3000:])
    print(f"percase: {f} totals checked-pass={n['pass']} fail={n['fail']} unsupported={n['unsupported']} other={n['other']}", flush=True)
