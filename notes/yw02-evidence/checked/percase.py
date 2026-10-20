#!/usr/bin/env python3
# yw02-percase — run each case of a test file on the checked machine by itself:
# a scratch copy with `fn t_x()` renamed `fn test_x()` and `main` dropped, so
# `wolf test` runs every case in a fresh checked machine (no native fallback
# for the file as a whole). Prints one row per case. Scratch files removed.
import json, os, re, subprocess, sys
root = os.path.expanduser("~/lanes/yw02/yew")
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
                             capture_output=True, text=True, timeout=3600).stdout
    finally:
        os.remove(scratch)
    n = {"pass": 0, "fail": 0, "unsupported": 0, "other": 0}
    for line in out.splitlines():
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
    print(f"percase: {f} totals checked-pass={n['pass']} fail={n['fail']} unsupported={n['unsupported']} other={n['other']}", flush=True)
