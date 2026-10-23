#!/bin/bash
# unit.sh FILE [VAR N] — one of the mouse fork's unit files, run in yw06's
# kasumi ctr from the clone root: built on the native tier with warnings
# denied and run whole (its exit read directly, its peak RSS and wall
# time from /usr/bin/time), then, given the file's selector VAR and its
# case count N, each case alone on the checked machine (percase.sh, G29).
# Exit 0 only when the build, the native run and (given) every checked
# case held.
set -u
export YEW_ROOT=$PWD YEW_LOG=/dev/null
mkdir -p "$YEW_ROOT/target/test-state"
export XDG_STATE_HOME="$YEW_ROOT/target/test-state"
. tools/lib-toolchain.sh
file=$1
name=$(basename "$file" .lu)
mkdir -p target/mouse
status=0
"$WOLF" build --deny-warnings "$file" -o "target/mouse/$name"
rc=$?
echo "build $file rc=$rc"
if [ "$rc" = 0 ]; then
    /usr/bin/time -f "time: %e s wall, %M KB max RSS" "target/mouse/$name"
    rc=$?
    echo "native $file rc=$rc"
    rm -f "target/mouse/$name"
fi
[ "$rc" = 0 ] || status=1
if [ -n "${3:-}" ]; then
    notes/yw06-evidence/mouse/percase.sh "$file" "$2" "$3" || status=1
fi
exit $status
