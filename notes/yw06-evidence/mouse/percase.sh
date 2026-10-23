#!/bin/bash
# percase.sh FILE VAR N — the checked machine per case (G29): FILE's
# cases 0..N-1 one at a time through the selector VAR, each verdict read
# from conform-run's JSON (never a pipe's status). Run in the ctr from
# the clone root.
set -u
export YEW_ROOT=$PWD YEW_LOG=/dev/null
mkdir -p "$YEW_ROOT/target/test-state"
export XDG_STATE_HOME="$YEW_ROOT/target/test-state"
. tools/lib-toolchain.sh
file=$1; var=$2; n=$3
ok=0; bad=0
for i in $(seq 0 $((n - 1))); do
    out=$(env "$var=$i" "$WOLF" conform-run --deny-warnings --checked --json "$file" 2>&1)
    verdict=$(printf '%s' "$out" | grep -o '"verdict":"[^"]*"' | head -1)
    name=$(printf '%s' "$out" | grep -o -E '(RED [a-z_0-9]+|[a-z_0-9]+: PASS)' | head -1)
    msg=$(printf '%s' "$out" | grep -o '"trap_message":"[^"]*"' | head -1)
    echo "case $i ${name:-?} $verdict $msg"
    if [ "$verdict" = '"verdict":"exit(0)"' ]; then ok=$((ok + 1)); else bad=$((bad + 1)); fi
done
echo "percase $file: $ok exit(0), $bad other"
