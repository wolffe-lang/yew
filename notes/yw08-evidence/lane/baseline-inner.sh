#!/bin/bash
set -euo pipefail
root=/home/mfwolffe/lanes/yw08/yew
out=/home/mfwolffe/lanes/yw08/baseline
mkdir -p "$out"
cd "$root"
echo "BEGIN $(date -u +%FT%TZ) $(git rev-parse HEAD)"
.wolf-bin/wolf --version
.wolf-bin/lupin --version
grep -E 'Cpus_allowed_list|SigBlk|SigIgn' /proc/self/status
printf '\nBUILD RELEASE\n'
tools/build --release
printf '\nBUILD ORACLE\n'
tools/oracle --cc gcc --build-only --jobs 4
oracle="$root/target/oracle/sagitta"
cd "$oracle"
cc -std=c11 -O2 -Wall -Wextra -Werror -Isrc -Itests -o "$out/yewpaint" "$root/notes/yw08-evidence/lane/yewpaint.c" tests/support/live_pty.c
mkdir -p "$out/fixtures"
: > "$out/fixtures/empty.c"
printf 'x\n' > "$out/fixtures/fixture.c"
python3 -I -c 'import sys; open(sys.argv[1], "w").write("x\n" * 10000)' "$out/fixtures/fixture.c"
export YEW_RUNTIME_DIR="$oracle/runtime"
for round in 1 2 3; do
  for mode in cold clean; do
    fixture="$out/fixtures/fixture.c"
    [ "$mode" != clean ] || fixture="$out/fixtures/empty.c"
    state="$out/state-$mode-$round"
    mkdir -p "$state"
    echo "MEASURE $mode round=$round $(date -u +%FT%TZ)"
    cat /proc/loadavg
    "$out/yewpaint" "$mode" 50 "$fixture" "$state" "$out/$mode-$round.tsv" "c=$oracle/build/yew" "wolf=$root/target/release/yew"
    echo "MEASURED $mode round=$round $(date -u +%FT%TZ)"
  done
done
sha256sum "$root/target/release/yew" "$oracle/build/yew"
echo "END $(date -u +%FT%TZ)"
