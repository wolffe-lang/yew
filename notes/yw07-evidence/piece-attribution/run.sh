#!/bin/bash
# Attribute the 1M-insert workload at the same 8 GiB cap; no source changes.
set -euo pipefail
lane=$(dirname "$PWD")
a="$lane/perf-attribution/a"
out="$lane/evidence/piece-attribution"
mkdir -p "$out" "$a/target/perf-text/src"
echo "piece-attribution cap_bytes=$(cat /sys/fs/cgroup/memory.max)"
echo "a=$(git -C "$a" rev-parse HEAD) c=$(git rev-parse HEAD)"
cat /proc/loadavg
# Build only the old tree's original harness; c is the binary just OOM-killed.
cp "$a/tools/perf-text/main.lu" "$a/target/perf-text/src/main.lu"
for m in util unicode term text; do
    cp -a "$a/src/$m" "$a/target/perf-text/src/$m"
    rm -f "$a/target/perf-text/src/$m/"*_test.lu
done
WOLF_STD="$a/.wolf-bin/std" "$a/.wolf-bin/wolf" build --release --deny-warnings \
    "$a/target/perf-text/src/main.lu" -o "$a/target/perf-text/perf-text"
sha256sum "$a/target/perf-text/perf-text" "$PWD/target/perf-text/perf-text"
for cell in a c; do
    binary="$PWD/target/perf-text/perf-text"
    [ "$cell" != a ] || binary="$a/target/perf-text/perf-text"
    echo "BEGIN piece cell=$cell $(date -u +%FT%TZ)"
    if /usr/bin/time -v -o "$out/time-$cell.txt" "$binary" piece > "$out/piece-$cell.txt" 2>&1; then rc=0; else rc=$?; fi
    echo "$rc" > "$out/exit-$cell.txt"
    cat "$out/piece-$cell.txt" "$out/time-$cell.txt"
    echo "END piece cell=$cell exit=$rc $(date -u +%FT%TZ)"
    [ "$rc" = 0 ] || [ "$rc" = 137 ] || exit "$rc"
done
# C's unmodified driver supplies the memory/latency scale beside both ports.
if YEW_PERF_ADVISORY=1 /usr/bin/time -v -o "$out/time-oracle.txt" \
    target/oracle/sagitta/build/perf_piece > "$out/piece-oracle.txt" 2>&1; then rc=0; else rc=$?; fi
echo "$rc" > "$out/exit-oracle.txt"
cat "$out/piece-oracle.txt" "$out/time-oracle.txt"
cat /sys/fs/cgroup/memory.events
[ "$rc" -le 1 ]
echo 'PIECE ATTRIBUTION OBSERVED; OOM is recorded, not a passing performance gate'
