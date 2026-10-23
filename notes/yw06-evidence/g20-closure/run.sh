#!/bin/bash
# G20 reduction: each variant built native and --release with a given wolf;
# the exit status and the first stderr line recorded.
set -u
here=$(cd "$(dirname "$0")" && pwd)
for wolf in "$@"; do
    export WOLF_STD=$(dirname "$wolf")/std
    "$wolf" --version | head -1
    echo "std $(cat "$WOLF_STD/STD-REV")"
    for v in one two named; do
        for tier in native release; do
            flag=""; [ "$tier" = release ] && flag=--release
            out=$(mktemp -d)
            ( cd "$here/$v" && "$wolf" build --deny-warnings $flag main.lu -o "$out/p" ) > "$out/log" 2>&1
            rc=$?
            run=""
            [ "$rc" = 0 ] && run=$("$out/p")
            echo "$v $tier build=$rc run=[$run] $(head -1 "$out/log")"
            rm -rf "$out"
        done
    done
done
