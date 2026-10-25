#!/bin/bash
# Diagnostic only: no change to tools/build or default release flags.
set -euo pipefail
root=/home/mfwolffe/lanes/yw07b/core
cd "$root"
export WOLF_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
export LUPIN_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/lupin
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
E=notes/yw07b-evidence/core/pgo
mkdir -p "$E" target/perf-pgo/profiles
unset YEW_FL_GC_STRESS FL_GC_STRESS
tools/build-fl-core --release > "$E/stage.log" 2>&1
entry=target/fl-core-release/main.lu
"$WOLF_BIN" build --release --deny-warnings --codegen-report "$entry" -o target/perf-pgo/plain > "$E/plain-build.log" 2>&1
"$WOLF_BIN" build --release --deny-warnings --profile-gen="$root/target/perf-pgo/profiles" "$entry" -o target/perf-pgo/generate > "$E/generate-build.log" 2>&1
target/perf-pgo/generate --train > "$E/training.log" 2>&1
find target/perf-pgo/profiles -type f -name '*.wprof' -print > "$E/profile-paths.txt"
mapfile -t profiles < "$E/profile-paths.txt"
[ "${#profiles[@]}" -eq 1 ] || { echo "expected one training profile, got ${#profiles[@]}"; exit 2; }
"$WOLF_BIN" build --release --deny-warnings --codegen-report --profile="${profiles[0]}" "$entry" -o target/perf-pgo/profiled > "$E/profiled-build.log" 2>&1
for run in 1 2 3; do
  echo "run=$run C"
  /home/mfwolffe/lanes/yw07b/yew/target/oracle/sagitta/build/fl_smoke --perf 3
  echo "run=$run plain"
  target/perf-pgo/plain --perf 3
  echo "run=$run PGO"
  target/perf-pgo/profiled --perf 3
done > "$E/timings.txt"
target/perf-pgo/profiled --trace > "$E/profiled-trace.txt"
sed '/^# dispatch:/d' "$E/profiled-trace.txt" > target/perf-pgo/profiled-clean.txt
sed '/^# dispatch:/d' notes/yw07b-evidence/core/oracle-trace1.txt > target/perf-pgo/c-clean.txt
diff -u target/perf-pgo/c-clean.txt target/perf-pgo/profiled-clean.txt > "$E/trace.diff"
cat "$E/timings.txt"
