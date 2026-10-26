#!/bin/bash
# profile.sh ROW...: the headless Fletch harness built as build-fl-core
# --headless stages it, with `--release --profile-gen`, one run per row, then
# `wolf profile show` (function counts; no generated code is read).
set -uo pipefail
L=/home/mfwolffe/lanes/yw08
sha=$(git -C $L/yew rev-parse --short HEAD)
root=$L/prof-$sha; out=$L/o55/prof-$sha
rm -rf "$root"; mkdir -p "$root" "$out"
git -C $L/yew archive HEAD | tar -x -C "$root" || exit 2
cp -a $L/yew/.wolf-bin "$root/.wolf-bin"
cd "$root"; export YEW_ROOT=$root; . tools/lib-toolchain.sh
stage=$root/target/fl-headless-prof
mkdir -p "$stage" target/tools
cp -R src/. "$stage/"
find "$stage" -maxdepth 1 -type f -name '*.lu' -delete
find "$stage" -type f -name '*_test.lu' -delete
cp tools/fl-headless/main.lu "$stage/main.lu"
"$WOLF" build --release --deny-warnings --profile-gen="$out/raw" "$stage/main.lu" -o target/tools/fl-headless-prof > "$out/build.log" 2>&1 || { cat "$out/build.log"; exit 2; }
echo "built $(date -u +%FT%TZ)"
for row in "$@"; do
  rm -rf "$out/raw"; mkdir -p "$out/raw"
  target/tools/fl-headless-prof "$row" $L/yew/target/oracle/sagitta/runtime/init.fl > "$out/$row.run" 2>&1
  echo "row $row exit=$? $(head -c 160 "$out/$row.run")"
  /bin/ls "$out/raw" | head -3
  f=$(find "$out/raw" -name '*.wprof' | head -1)
  [ -n "$f" ] && "$WOLF" profile show "$f" > "$out/$row.show" 2>&1
  head -40 "$out/$row.show"
done
rm -rf "$root"
