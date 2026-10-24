#!/bin/bash
# Same R11 cells and unchanged pane instrument, three paired trials each.
set -euo pipefail
lane=$(dirname "$PWD")
out="$lane/evidence/pane-attribution"
mkdir -p "$out"
for trial in 1 2 3; do
    for cell in a b c; do
        label=$cell; [ "$cell" != b ] || label=b-prime
        binary="$lane/perf-attribution/$cell/target/release/yew"
        echo "BEGIN trial=$trial cell=$label $(date -u +%FT%TZ)"
        sha256sum "$binary"
        if tools/run-perf-panes-tabs --cpus 8-11 --rows 'many tabswitch' --yew "$binary" > "$out/$trial-$label.log" 2>&1; then rc=0; else rc=$?; fi
        cat "$out/$trial-$label.log"
        echo "END trial=$trial cell=$label exit=$rc"
        [ "$rc" -le 1 ] || exit "$rc"
        cp -a target/perf-panes-tabs "$out/raw-$trial-$label"
    done
done
echo 'PANE ATTRIBUTION COMPLETE; b-prime is pin + compile compatibility'
