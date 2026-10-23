#!/usr/bin/env bash
# run-router-goldens.sh BIN [OUTDIR] — the router's 68 PTY cases (R-yw06-2 = A):
# tools/goldens-yw06-cases.txt from `chrome_tabs` to its end, each run alone
# with `tools/goldens --suite pty --case`, its runner log kept, one verdict
# line a case, then the count. Run from the repository root, inside the
# lane's container. No golden is touched (tools/goldens never updates one).
set -u
bin=${1:?usage: run-router-goldens.sh BIN [OUTDIR]}
out=${2:-target/mouse-goldens}
mkdir -p "$out"
cases=$(sed -n '/^chrome_tabs$/,$p' tools/goldens-yw06-cases.txt)
n=$(echo "$cases" | wc -l)
[ "$n" -eq 68 ] || { echo "router-goldens: expected 68 cases, got $n"; exit 2; }
pass=0
fail=0
for c in $cases; do
    tools/goldens --yew "$bin" --suite pty --case "$c" >"$out/$c.out" 2>&1
    cp target/oracle/goldens/pty.log "$out/$c.log"
    if grep -qx "pty: $c: ok" "$out/$c.log"; then
        echo "router-golden: $c: ok"
        pass=$((pass + 1))
    else
        why=$(grep -E '^pty: ' "$out/$c.log" | grep -v ': ok$' | head -1)
        echo "router-golden: $c: RED ${why:-no verdict line}"
        fail=$((fail + 1))
    fi
done
echo "router-goldens: pass=$pass fail=$fail of 68"
[ "$fail" -eq 0 ]
