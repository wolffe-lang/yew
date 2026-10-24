#!/bin/bash
# R-yw07-11 A: one container and core lock for both builds and all nine runs.
set -euo pipefail
lane=$(dirname "$PWD")
control="$lane/perf-attribution"
out="$control/results"
mkdir -p "$out"
unset WOLF_BIN LUPIN_BIN WOLF_STD
printf 'instrument head=%s\n' "$(git rev-parse HEAD)"
[ "$(git rev-parse HEAD)" = 35e21b90ca658c2bffd64275eb7a6921305ea708 ]
git diff --exit-code
for cell in a b c; do
    echo "CELL $cell head=$(git -C "$control/$cell" rev-parse HEAD)"
    "$control/$cell/.wolf-bin/wolf" --version
    "$control/$cell/.wolf-bin/lupin" --version
    cat "$control/$cell/.wolf-bin/std/STD-REV"
done
# Retain the literal b failure, then the missing-field-only failure, before b-prime.
if (cd "$control/b" && tools/build --release) > "$out/b-literal-build.log" 2>&1; then rc=0; else rc=$?; fi
echo "literal b build=$rc (BUILD-RED required)"
[ "$rc" = 2 ] && grep -q 'E0408' "$out/b-literal-build.log"
git -C "$control/b" apply --include=src/term/tty.lu "$control/compile-compat.patch"
if (cd "$control/b" && tools/build --release) > "$out/b-mode-only-build.log" 2>&1; then rc=0; else rc=$?; fi
echo "b with missing Mode fields only build=$rc (E1004 required)"
[ "$rc" = 2 ] && grep -q 'E1004' "$out/b-mode-only-build.log"
git -C "$control/b" apply --include=src/edit/cmdparse.lu "$control/compile-compat.patch"
git -C "$control/b" diff > "$out/b-prime-source.patch"
for cell in a b; do
    echo "BUILD $cell $(date -u +%FT%TZ)"
    (cd "$control/$cell" && tools/build --release) > "$out/build-$cell.log" 2>&1
    cat "$out/build-$cell.log"
    echo "BUILT $cell $(date -u +%FT%TZ)"
done
# c uses the exact binary of the failed run, copied without rebuilding.
echo '8e3c3c57849d9c254254c441bb02b7c9f45a0208191ea676f7e4e298f76a6b6d  target/release/yew' | sha256sum -c -
cp target/release/yew "$control/c/target/release/yew"
for cell in a b c; do sha256sum "$control/$cell/target/release/yew"; done > "$out/binary-digests.txt"
cat "$out/binary-digests.txt"
for trial in 1 2 3; do
    for cell in a b c; do
        label=$cell; [ "$cell" != b ] || label=b-prime
        echo "MEASURE trial=$trial cell=$label $(date -u +%FT%TZ)"
        # Exit 1 records a ratio MISS. Exit 2 is an instrument fault, not data.
        if tools/run-perf-editor --cpus 8-11 --yew "$control/$cell/target/release/yew" > "$out/trial-$trial-$label.log" 2>&1; then rc=0; else rc=$?; fi
        echo "trial=$trial cell=$label perf_exit=$rc"
        [ "$rc" -le 1 ] || { cat "$out/trial-$trial-$label.log"; exit "$rc"; }
        cp -a target/perf-editor "$out/raw-$trial-$label"
        grep -E '^ratio\.(cold_open_to_first_paint|wolf_kitty_first_backspace_to_paint) ' "$out/trial-$trial-$label.log"
    done
done
python3 -I "$control/summarize.py" "$out" > "$out/summary.tsv"
cat "$out/summary.tsv"
echo 'ATTRIBUTION MEASUREMENTS COMPLETE; causal verdict pending review'
