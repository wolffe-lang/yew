#!/bin/bash
# The bytes-view probe on the native and release tiers and the checked
# machine; run in the ctr from the clone root.
set -u
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
d=notes/yw06-evidence/pick/witness/bytes-view
mkdir -p target/pick
"$WOLF" build --deny-warnings $d/main.lu -o target/pick/bytes-view && echo "== native" && target/pick/bytes-view
"$WOLF" build --release --deny-warnings $d/main.lu -o target/pick/bytes-view-r && echo "== release" && target/pick/bytes-view-r
echo "== checked"
"$WOLF" conform-run --deny-warnings --checked --json $d/main.lu | grep -o '"stdout":"[^"]*"'
