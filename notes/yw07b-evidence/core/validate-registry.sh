#!/bin/bash
set -euo pipefail
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
E=notes/yw07b-evidence/core
"$W" fmt src/fl/vm.lu src/fl_compile_test.lu src/fl_vm_test.lu src/fl_gc_test.lu src/fl_motion_compile_test.lu
for tier in native release; do
  opt=; [ "$tier" = native ] || opt=--release
  for unit in compile vm gc motion_compile; do
    echo "build $tier $unit"
    "$W" build --deny-warnings $opt src/fl_${unit}_test.lu -o target/registry-$unit-$tier
    extra=; [ "$unit" != gc ] || extra=--residency
    for mode in normal stress; do
      unset YEW_FL_GC_STRESS FL_GC_STRESS
      [ "$mode" = normal ] || export YEW_FL_GC_STRESS=1
      echo "run $tier $unit $mode"
      target/registry-$unit-$tier $extra > "$E/registry-$unit-$tier-$mode.log" 2>&1
    done
  done
done
for mode in normal stress; do
  unset YEW_FL_GC_STRESS FL_GC_STRESS
  [ "$mode" = normal ] || export YEW_FL_GC_STRESS=1
  for unit in gc motion_compile; do
    echo "checked $unit $mode"
    "$W" test --deny-warnings --nocapture --no-native-fallback src/fl_${unit}_test.lu > "$E/registry-$unit-checked-$mode.log" 2>&1
  done
  echo "checked compiler cases $mode"
  CASE_TAG=registry-$mode python3 -I "$E/checked-cases.py"
done
unset YEW_FL_GC_STRESS FL_GC_STRESS
# Strict budget exhaustions remain nonzero; never translate them to PASS.
CASE_TAG=registry python3 -I "$E/vm-cases.py" checked
