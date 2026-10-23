#!/bin/bash
# case-alone.sh FILE CASE SECONDS — one case of FILE alone on the checked
# machine (YEW_PICK_CASE), bounded by timeout(1), its wall time and the
# machine's words printed. Run in the ctr from the clone root.
set -u
export YEW_ROOT=$PWD YEW_LOG=/dev/null
. tools/lib-toolchain.sh
mkdir -p target/pick
t0=$(date +%s)
YEW_PICK_CASE=$2 timeout "$3" "$WOLF" conform-run --deny-warnings --checked --json "$1" > target/pick/case-alone.json 2>&1
rc=$?
echo "case-alone $1 case $2: rc=$rc wall=$(($(date +%s) - t0)) s"
grep -o -E '"(verdict|x-unsupported-construct|trap_message)":"[^"]*"' target/pick/case-alone.json
