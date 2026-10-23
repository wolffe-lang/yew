#!/bin/sh
# Run from the repository root inside the lane's container:
#   YEW_ROOT=$PWD . tools/lib-toolchain.sh; sh notes/yw06-evidence/ctx/witness/read-param-store/run.sh
W=notes/yw06-evidence/ctx/witness/read-param-store
for v in plain copied rebuilt; do
    echo "== $v"
    "$WOLF" build --deny-warnings "$W/$v/main.lu" -o "target/ctx/witness-$v" 2>&1
    echo "build exit=$?"
    [ -x "target/ctx/witness-$v" ] && "target/ctx/witness-$v"
    rm -f "target/ctx/witness-$v"
done
