#!/bin/bash
# wtest.sh FILE... — tools/check-test's checked lane (`wolf test
# --deny-warnings`) on the given test files one at a time, with
# check-test's environment, each bounded at 1800 s by timeout(1), its
# rows, rc and wall time printed. Run in the ctr from the clone root.
set -u
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
export YEW_LOG=/dev/null
mkdir -p target/test-state
export XDG_STATE_HOME=$PWD/target/test-state
for f in "$@"; do
    t0=$(date +%s)
    timeout 1800 "$WOLF" test --deny-warnings "$f" > target/pick/wtest.out 2>&1
    rc=$?
    t1=$(date +%s)
    echo "== $f rc=$rc wall=$((t1 - t0)) s"
    tail -6 target/pick/wtest.out | cut -c1-300
done
