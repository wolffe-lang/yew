#!/bin/bash
# Independent continuation after the completed 287 goldens and RSS baseline.
# A fresh cold-open observation remains red; this is NOT a combined green gate.
set -euo pipefail
export WOLF_STD="$PWD/.wolf-bin/std"
printf 'remaining head=%s\n' "$(git rev-parse HEAD)"
git diff --exit-code
# The executable and all application source are exactly the measured 35e21b9.
git diff --exit-code 35e21b9 -- src runtime wolf-toolchain.toml tools/demo-paint tools/yew-torture
echo '8e3c3c57849d9c254254c441bb02b7c9f45a0208191ea676f7e4e298f76a6b6d  target/release/yew' | sha256sum -c -
stage() {
    echo "BEGIN $* $(date -u +%FT%TZ)"
    "$@"
    echo "END $* $(date -u +%FT%TZ)"
    used=$(du -sk .. | cut -f1)
    echo "lane KiB=$used"
    [ "$used" -lt 20971520 ] || { echo 'lane exceeds 20 GiB'; return 1; }
}
stage python3 -I tools/perf-editor-verdict --selftest
stage tools/run-perf-text --taskset 8-11 --rounds 1
stage tools/run-perf-panes-tabs --cpus 8-11
stage tools/check-test
stage tools/check-test --native
stage python3 -I tools/check-test-cases
printf 'REMAINING CHECKS COMPLETE; cold-open follow-up, #40, plants and toy VM remain\n'
