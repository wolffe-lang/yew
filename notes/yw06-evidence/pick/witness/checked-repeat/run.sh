#!/bin/bash
# run.sh — checked-repeat's scaling, run in the ctr from the clone root:
# each (maker, N) under `conform-run --checked --json`, bounded at 120 s
# by timeout(1), its wall time and verdict printed.
set -u
export YEW_ROOT=$PWD YEW_LOG=/dev/null
. tools/lib-toolchain.sh
d=notes/yw06-evidence/pick/witness/checked-repeat
for how in repeat push; do
    for n in 65536 262144 1048576; do
        t0=$(date +%s%N)
        out=$(PROBE_HOW=$how PROBE_N=$n timeout 120 "$WOLF" conform-run --checked --json "$d/main.lu" 2>&1)
        rc=$?
        t1=$(date +%s%N)
        v=$(printf '%s' "$out" | grep -o -E '"(verdict|x-unsupported-construct)":"[^"]*"' | tr '\n' ' ')
        echo "$how n=$n rc=$rc wall=$(((t1 - t0) / 1000000)) ms $v"
    done
done
