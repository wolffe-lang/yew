#!/bin/bash
# Build the witness on both compiled tiers, with the release codegen report,
# and run each three times (yw08, kasumi CPUs 12-15 in the lane container).
set -u
cd "$(dirname "$0")"
W=${WOLF:?WOLF names the pinned wolf}
out=${OUT:-.}
"$W" --version | head -1
"$W" build --release --deny-warnings --codegen-report main.lu -o "$out/witness-release" > "$out/codegen-report.txt" 2>&1 || { tail -20 "$out/codegen-report.txt"; exit 2; }
"$W" build --deny-warnings main.lu -o "$out/witness-native" || exit 2
grep -E '^fn [a-z_.]*(read8|run_calls|run_inline) ' "$out/codegen-report.txt"
for tier in release native; do
  for n in 1 2 3; do echo "$tier run $n: $("$out/witness-$tier")"; done
done
