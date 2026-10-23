#!/bin/bash
# run.sh — checked-bytes over (N, ITERS), run in the ctr from the clone
# root: each under `conform-run --checked --json`, bounded at 120 s by
# timeout(1), its wall time and verdict printed.
set -u
export YEW_ROOT=$PWD YEW_LOG=/dev/null
. tools/lib-toolchain.sh
d=notes/yw06-evidence/pick/witness/checked-bytes
for n in 1024 1048576; do
    for iters in 1000 10000; do
        t0=$(date +%s%N)
        out=$(PROBE_N=$n PROBE_ITERS=$iters timeout 120 "$WOLF" conform-run --checked --json "$d/main.lu" 2>&1)
        rc=$?
        t1=$(date +%s%N)
        v=$(printf '%s' "$out" | grep -o -E '"(verdict|x-unsupported-construct|stdout_inline)":"[^"]*"' | tr '\n' ' ')
        echo "n=$n iters=$iters rc=$rc wall=$(((t1 - t0) / 1000000)) ms $v"
    done
done
