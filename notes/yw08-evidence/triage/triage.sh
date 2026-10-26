#!/bin/bash
# yew#78 / #76 triage: each file whole under conform-run --checked --json,
# three times, verdict and trap message; then wolf test once each. Frozen tree.
set -u
L=/home/mfwolffe/lanes/yw08
sha=$(git -C $L/yew rev-parse --short HEAD); root=$L/triage-$sha; out=$L/o55/triage-$sha
rm -rf "$root" "$out"; mkdir -p "$root" "$out"
git -C $L/yew archive HEAD | tar -x -C "$root"; cp -a $L/yew/.wolf-bin "$root/.wolf-bin"
cd "$root"; export YEW_ROOT=$root; . tools/lib-toolchain.sh
export YEW_LOG=/dev/null; mkdir -p target/test-state; export XDG_STATE_HOME=$root/target/test-state
echo "TREE $(git -C $L/yew rev-parse HEAD) load=$(cat /proc/loadavg)"
for f in src/edit_cmdcomp_shell_test.lu src/edit_ws_recover_test.lu; do
  n=$(basename $f .lu)
  for k in 1 2 3; do
    s=$(date +%s)
    "$WOLF" conform-run --deny-warnings --checked --json "$f" > "$out/$n-$k.json" 2> "$out/$n-$k.err"; rc=$?
    echo "$n run $k: conform-run rc=$rc secs=$(( $(date +%s) - s )) $(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("verdict"), "|", d.get("trap_message") or d.get("x-unsupported-construct") or "")' "$out/$n-$k.json" 2>&1 | head -c 300)"
  done
  "$WOLF" test --deny-warnings --nocapture "$f" > "$out/$n-wolftest.log" 2>&1; echo "$n wolf test rc=$? $(grep -E "^test |refused" "$out/$n-wolftest.log" | head -3 | tr '\n' '|')"
done
rm -rf "$root"
