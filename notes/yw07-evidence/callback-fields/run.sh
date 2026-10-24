#!/bin/bash
# Measure callback forms without claiming that a compiler refusal is a skip.
set -u
wolf=$(realpath "$1")
export WOLF_STD="$(dirname "$wolf")/std"
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$here/out"
"$wolf" --version
for variant in direct bound mut-vm; do
    echo "VARIANT=$variant"
    "$wolf" fmt "$here/$variant"
    "$wolf" conform-run --deny-warnings --checked --json "$here/$variant/main.lu"
    for tier in native release; do
        flags=()
        [ "$tier" = native ] || flags+=(--release)
        "$wolf" build --deny-warnings "${flags[@]}" "$here/$variant/main.lu" -o "$here/out/$variant-$tier"
        rc=$?
        echo "$variant $tier build=$rc"
        if [ "$rc" = 0 ]; then "$here/out/$variant-$tier"; echo "run=$?"; fi
    done
done
