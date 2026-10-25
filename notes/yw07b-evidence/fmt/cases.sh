#!/bin/bash
# cases.sh TAG TESTFILE VAR CASE...: each case alone on the checked machine,
# normal then YEW_FL_GC_STRESS=1, one container (one lock hold) per run.
# Logs in fmt-runs/TAG/; summary in TAG.summary; marker TAG.done.
set -u
tag=$1; t=$2; var=$3; shift 3
root=/home/mfwolffe/lanes/yw07b/fmt
out=/home/mfwolffe/lanes/yw07b/fmt-runs/$tag; mkdir -p $out
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
C=/home/mfwolffe/lanes/yw07b/yew/notes/yw07b-evidence/lane/ctr.sh
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
cd $root
: > $out.summary
for c in "$@"; do
  for s in "" 1; do
    sfx=${s:+.stress}
    log=$out/$c$sfx.log
    env $var=$c ${s:+YEW_FL_GC_STRESS=1} timeout 3000 $C . env $var=$c $W test --deny-warnings --nocapture --no-native-fallback "$t" > $log 2>&1
    rc=$?
    echo "$c$sfx exit=$rc $(grep -E '^wolf test:' $log | tail -1) | $(grep -E 'case [0-9]+: PASS|PASS fl_data' $log | tail -1)" >> $out.summary
  done
done
echo done > $out.done
