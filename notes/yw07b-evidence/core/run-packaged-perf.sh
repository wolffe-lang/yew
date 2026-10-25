#!/bin/bash
set -u
export WOLF_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
export LUPIN_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/lupin
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
unset YEW_FL_GC_STRESS FL_GC_STRESS
failed=0
for tier in release native; do
  tools/run-perf-fletch --"$tier" --advisory --oracle-tree /home/mfwolffe/lanes/yw07b/yew/target/oracle/sagitta > notes/yw07b-evidence/core/perf-$tier-tool.log 2>&1
  rc=$?
  [ "$rc" -eq 0 ] || failed=1
  printf '%s\n' "$rc" > notes/yw07b-evidence/core/perf-$tier-tool.exit
  printf 'perf %s exit=%s\n' "$tier" "$rc"
done
exit "$failed"
