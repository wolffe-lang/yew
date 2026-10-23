#!/bin/bash
# yw05 (lane): the job stream's lost frame, probed (inside ctr, CPUs 0-3):
# perf_jobstream over C and the port, N runs each at a stream size. js-probe.sh N BYTES...
t=/home/mfwolffe/lanes/yw05/yew; cd $t; tree=$t/target/oracle/sagitta; h=$tree/build/perf_jobstream
out=$t/target/js-probe; rm -rf $out; mkdir -p $out/home/config; export HOME=$out/home XDG_CONFIG_HOME=$out/home/config
n=$1; shift
for bytes in "$@"; do for who in c port; do
  b=$t/target/release/yew; [ $who = c ] && b=$tree/build/yew
  ok=0; fails=""
  for i in $(seq 1 $n); do
    s=$(date +%s%N)
    (cd $tree && YEW_JOBSTREAM_BYTES=$bytes YEW_RUNTIME_DIR=$tree/runtime YEW_PERF_ADVISORY=1 taskset -c 0-3 $h --yew $b \
      --baseline tests/perf/baselines/latency-x86_64-linux-gnu.txt) > $out/$who-$bytes-$i.txt 2>&1
    e=$(( ($(date +%s%N) - s) / 1000000 ))
    if grep -q '^jobstream ' $out/$who-$bytes-$i.txt; then ok=$((ok+1)); else fails="$fails $(grep -o 'key [0-9]* never' $out/$who-$bytes-$i.txt | cut -d' ' -f2)@${e}ms"; fi
  done
  echo "$who bytes=$bytes: $ok/$n ok;$fails"
done; done
