#!/bin/bash
# yw05 (lane): the job stream's lost frame, timed (inside ctr, CPUs 0-3):
# js-probe2.sh N BYTES INJECT_NS KEYS — per run: ok or the key, and the wall ms.
t=/home/mfwolffe/lanes/yw05/yew; cd $t; tree=$t/target/oracle/sagitta; h=$tree/build/perf_jobstream
out=$t/target/js-probe2; mkdir -p $out/home/config; export HOME=$out/home XDG_CONFIG_HOME=$out/home/config
n=$1; bytes=$2; inj=$3; keys=$4
for who in c port; do
  b=$t/target/release/yew; [ $who = c ] && b=$tree/build/yew
  line="$who bytes=$bytes inject=$inj keys=$keys:"
  for i in $(seq 1 $n); do
    s=$(date +%s%N)
    (cd $tree && YEW_JOBSTREAM_BYTES=$bytes YEW_JOBSTREAM_INJECT_NS=$inj YEW_JOBSTREAM_KEYS=$keys YEW_RUNTIME_DIR=$tree/runtime YEW_PERF_ADVISORY=1 taskset -c 0-3 $h --yew $b \
      --baseline tests/perf/baselines/latency-x86_64-linux-gnu.txt) > $out/$who-$bytes-$inj-$i.txt 2>&1
    e=$(( ($(date +%s%N) - s) / 1000000 ))
    if grep -q '^jobstream ' $out/$who-$bytes-$inj-$i.txt; then line="$line ok@${e}"; else line="$line K$(grep -o 'key [0-9]* never' $out/$who-$bytes-$inj-$i.txt | cut -d' ' -f2)@${e}"; fi
  done
  echo "$line"
done
