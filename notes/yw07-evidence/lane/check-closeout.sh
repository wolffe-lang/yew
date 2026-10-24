#!/bin/bash
# Frozen deliverable-1 source. Ratios are retained even when disposition is pending.
set -euo pipefail
export WOLF_STD="$PWD/.wolf-bin/std"
base="$(dirname "$PWD")/evidence/closeout-artifacts"
mkdir -p "$base"
printf 'closeout head=%s\n' "$(git rev-parse HEAD)"
git diff --exit-code
stage() { echo "BEGIN $* $(date -u +%FT%TZ)"; "$@"; echo "END $* $(date -u +%FT%TZ)"; }
stage tools/check-fmt
stage python3 -I tools/perf-editor-samples --selftest
stage python3 -I tools/perf-editor-verdict --selftest
stage python3 -I tools/check-test-cases-selftest
stage tools/build --all
stage tools/build-demo
stage tools/build-torture
stage python3 -I notes/yw07-evidence/lane/retirement-goldens.py
stage python3 -I notes/yw07-evidence/lane/memory-before.py after
if tools/run-perf-panes-tabs --cpus 8-11 > "$base/panes.log" 2>&1; then rc=0; else rc=$?; fi
cat "$base/panes.log"
echo "pane gate exit=$rc"
[ "$rc" -le 1 ] || exit "$rc"
cp -a target/perf-panes-tabs "$base/panes-raw"
if tools/run-perf-editor --cpus 8-11 > "$base/editor.log" 2>&1; then rc=0; else rc=$?; fi
cat "$base/editor.log"
echo "editor gate exit=$rc"
[ "$rc" -le 1 ] || exit "$rc"
cp -a target/perf-editor "$base/editor-raw"
stage tools/check-test
stage tools/check-test --native
stage python3 -I tools/check-test-cases
printf 'SKIP static-binary handoff: scope decision, belongs to the fresh Fletch PR\n'
printf 'CLOSEOUT CHECKS COMPLETE; ratio MISS accounting and CI plants still required\n'
