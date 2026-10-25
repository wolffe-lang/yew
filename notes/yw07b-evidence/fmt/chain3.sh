#!/bin/bash
# chain.sh: after fmtcases, math's whole file checked, then fl_data_test's
# fixture batches checked (data-batches2.txt: LABEL NAMES), each normal and stressed.
set -u
cd /home/mfwolffe/lanes/yw07b/fmt-runs
while [ ! -f mathcases.done ]; do sleep 20; done

root=/home/mfwolffe/lanes/yw07b/fmt
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
C=/home/mfwolffe/lanes/yw07b/yew/notes/yw07b-evidence/lane/ctr.sh
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
out=/home/mfwolffe/lanes/yw07b/fmt-runs/databatch2; mkdir -p $out; : > $out.summary
while read -r label names; do
  for s in "" 1; do
    sfx=${s:+.stress}
    log=$out/$label$sfx.log
    (cd $root && env ${s:+YEW_FL_GC_STRESS=1} timeout 3000 $C . env YEW_DATA_FIXTURE="$names" $W test --deny-warnings --nocapture --no-native-fallback src/fl_data_test.lu > $log 2>&1)
    echo "$label$sfx exit=$? $(grep -E '^wolf test:' $log | tail -1) | $(grep -c ': PASS' $log) case lines" >> $out.summary
  done
done < data-batches2.txt
echo done > databatch2.done
