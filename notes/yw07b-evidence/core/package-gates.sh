#!/bin/bash
set -euo pipefail
export WOLF_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
export LUPIN_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/lupin
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
E=notes/yw07b-evidence/core
"$WOLF_BIN" fmt src/fl_compile_test.lu src/fl_vm_test.lu tools/fl-core/main.lu tools/fl-headless/main.lu
python3 -I tools/test-check-test-cases > "$E/selector-selftest.log" 2>&1
for mode in normal stress; do
  unset YEW_FL_GC_STRESS FL_GC_STRESS
  [ "$mode" = normal ] || export YEW_FL_GC_STRESS=1
  python3 -I tools/check-test-cases src/fl_compile_test.lu src/fl_vm_test.lu > "$E/selector-$mode.log" 2>&1
  tail -1 "$E/selector-$mode.log"
done
unset YEW_FL_GC_STRESS FL_GC_STRESS
tools/check-fl-trace /home/mfwolffe/lanes/yw07b/yew/target/oracle/sagitta > "$E/trace-tool.log" 2>&1
cat "$E/trace-tool.log"
