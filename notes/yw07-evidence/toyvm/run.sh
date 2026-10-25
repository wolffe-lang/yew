#!/usr/bin/env bash
# Run INSIDE the bounded lane container, from yew's root; no C/golden edits.
set -euo pipefail
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
. tools/lib-test-env.sh
test_env_begin
src=notes/yw07-evidence/toyvm/main.lu
out=target/toyvm
mkdir -p "$out"
date -u +%FT%TZ
sha256sum "$src" wolf-toolchain.toml
"$WOLF" fmt --check "$src"
"$WOLF" test --nocapture --no-native-fallback "$src"
for tier in native release; do
    flags=(); [ "$tier" = native ] || flags+=(--release)
    "$WOLF" build --deny-warnings "${flags[@]}" "$src" -o "$out/$tier"
    sha256sum "$out/$tier"
    "$out/$tier" layout
    for mode in compact nonmoving; do
        "$out/$tier" test "$mode"
        "$out/$tier" memory "$mode"
        set +e
        "$out/$tier" plant "$mode" >"$out/plant-$tier-$mode.log" 2>&1
        rc=$?
        set -e
        cat "$out/plant-$tier-$mode.log"
        echo "stale plant tier=$tier mode=$mode exit=$rc"
        test "$rc" = 134
        grep -q '^wolf-trap: assert$' "$out/plant-$tier-$mode.log"
    done
done
set +e
"$WOLF" build --deny-warnings notes/yw07-evidence/toyvm/shared-cycle/main.lu \
    -o "$out/shared" >"$out/shared.log" 2>&1
rc=$?
set -e
cat "$out/shared.log"
echo "shared-cycle exit=$rc"
test "$rc" = 2
grep -q 'error\[E1006\]' "$out/shared.log"
echo 'toyvm: checked/native/release, roots/cycle/reentry/memory/shared PASS'
