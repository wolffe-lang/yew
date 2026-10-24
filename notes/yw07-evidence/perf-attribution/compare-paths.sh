#!/bin/bash
# Approved same-bits comparison, five per path, alternating pair order.
# C's harness has no cold-only flag: preserve its whole unchanged output,
# extracting just its single cold-open observation from each invocation.
set -euo pipefail
root=$PWD
lane=$(dirname "$root")
orig="$root/target/release/yew"
copy="$lane/perf-attribution/c/target/release/yew"
cmp "$orig" "$copy"
sha256sum "$orig" "$copy"
out="$lane/evidence/cold-paths-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$out/home" "$out/config" "$out/state"
export HOME="$out/home" XDG_CONFIG_HOME="$out/config" XDG_STATE_HOME="$out/state"
export YEW_RUNTIME_DIR="$root/target/oracle/sagitta/runtime" YEW_PERF_ADVISORY=1
h="$root/target/oracle/sagitta/build/perf_latency"
base="$root/target/oracle/sagitta/tests/perf/baselines/latency-x86_64-linux-gnu.txt"
printf 'trial\tpath\tcold_ns\n' > "$out/rows.tsv"
echo "cold-path output=$out"
for trial in 1 2 3 4 5; do
    order='original copy'; [ $((trial % 2)) != 0 ] || order='copy original'
    for label in $order; do
        bin=$orig; [ "$label" != copy ] || bin=$copy
        if (cd "$root/target/oracle/sagitta" && "$h" --yew "$bin" --baseline "$base") > "$out/$trial-$label.log" 2>&1; then rc=0; else rc=$?; fi
        [ "$rc" -le 1 ] || { cat "$out/$trial-$label.log"; exit "$rc"; }
        row=$(grep '^cold_open_to_first_paint ' "$out/$trial-$label.log")
        value=$(printf '%s\n' "$row" | awk '{print $2}')
        [[ "$value" =~ ^[0-9]+$ ]] || exit 2
        printf '%s\t%s\t%s\n' "$trial" "$label" "$value" >> "$out/rows.tsv"
        echo "trial=$trial path=$label $row"
    done
done
python3 -I - "$out/rows.tsv" <<'PY'
import csv, statistics, sys
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
for label in ('original', 'copy'):
    values = [int(r['cold_ns']) for r in rows if r['path'] == label]
    assert len(values) == 5
    print(label, 'raw_ns='+str(values), 'min_ns='+str(min(values)),
          'median_ns='+str(statistics.median(values)), 'max_ns='+str(max(values)))
PY
echo 'SAME-BITS PATH COMPARISON COMPLETE'
