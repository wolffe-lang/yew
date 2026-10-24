#!/bin/bash
# The retained runner outputs identify allnl, not piece, as the killed phase.
set -euo pipefail
lane=$(dirname "$PWD")
out="$lane/evidence/piece-attribution"
cap=$(cat /sys/fs/cgroup/memory.max)
echo "allnl-attribution cap_bytes=$cap $(date -u +%FT%TZ)"
for cell in a c; do
    binary="$PWD/target/perf-text/perf-text"
    [ "$cell" != a ] || binary="$lane/perf-attribution/a/target/perf-text/perf-text"
    echo "BEGIN allnl cell=$cell $(date -u +%FT%TZ)"
    if /usr/bin/time -v -o "$out/allnl-time-$cap-$cell.txt" "$binary" open "$PWD/target/perf-fixtures" 100m-allnl > "$out/allnl-$cap-$cell.txt" 2>&1; then rc=0; else rc=$?; fi
    echo "$rc" > "$out/allnl-exit-$cap-$cell.txt"
    cat "$out/allnl-$cap-$cell.txt" "$out/allnl-time-$cap-$cell.txt"
    echo "END allnl cell=$cell exit=$rc $(date -u +%FT%TZ)"
    [ "$rc" = 0 ] || [ "$rc" = 137 ] || exit "$rc"
done
cat /sys/fs/cgroup/memory.events
echo 'ALLNL ATTRIBUTION OBSERVED; OOM is not a passing performance gate'
