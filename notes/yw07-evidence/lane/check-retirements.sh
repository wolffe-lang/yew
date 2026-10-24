#!/bin/bash
# Full pre-#40 baseline and regression pass. Every command's status is read.
set -euo pipefail
export WOLF_STD="$PWD/.wolf-bin/std"
mkdir -p target/yw07
printf 'retirements head=%s\n' "$(git rev-parse HEAD)"
git diff --exit-code
stage() {
    echo "BEGIN $* $(date -u +%FT%TZ)"
    "$@"
    echo "END $* $(date -u +%FT%TZ)"
    used=$(du -sk .. | cut -f1)
    echo "lane KiB=$used"
    [ "$used" -lt 20971520 ] || { echo 'lane exceeds 20 GiB: prune before continuing'; return 1; }
}
stage python3 -I notes/yw07-evidence/lane/retirement-goldens.py --list-only
stage tools/check-fmt
stage python3 -I tools/check-test-cases-selftest
stage tools/build --all
stage tools/oracle --cc gcc --build-only --jobs 4
stage tools/build-demo
stage tools/build-torture
stage python3 -I notes/yw07-evidence/lane/retirement-goldens.py
stage python3 -I notes/yw07-evidence/lane/memory-before.py
stage tools/run-perf-editor --cpus 8-11
stage tools/run-perf-text --taskset 8-11 --rounds 1
stage tools/run-perf-panes-tabs --cpus 8-11
stage tools/check-test
stage tools/check-test --native
stage python3 -I tools/check-test-cases
printf 'RETIREMENT BASELINE GREEN; #40 changes, plants and toy VM still owed\n'
