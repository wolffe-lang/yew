#!/bin/bash
# unit.sh FILE [NCASES] — one of the pick fork's unit files, run in yw06's
# kasumi ctr from the clone root: built on the native tier with warnings
# denied and run whole (its exit read directly, its peak RSS and wall
# time from /usr/bin/time), then, given NCASES, each case alone on the
# checked machine (percase.sh, G29).
set -u
export YEW_ROOT=$PWD YEW_LOG=/dev/null
. tools/lib-toolchain.sh
file=$1
name=$(basename "$file" .lu)
mkdir -p target/pick
"$WOLF" build --deny-warnings "$file" -o "target/pick/$name"
rc=$?
echo "build $file rc=$rc"
if [ "$rc" = 0 ]; then
    /usr/bin/time -f "time: %e s wall, %M KB max RSS" "target/pick/$name"
    echo "native $file rc=$?"
fi
if [ -n "${2:-}" ]; then
    notes/yw06-evidence/pick/percase.sh "$file" "$2"
fi
