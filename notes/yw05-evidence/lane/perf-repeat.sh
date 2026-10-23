#!/bin/bash
# yw05 (lane): the repeat runs behind the 2x medians (inside ctr, CPUs 0-3):
# run-perf-editor five times (yw03's method), campaign 05's rows and the job
# stream three times each. perf-repeat.sh TAG
t=/home/mfwolffe/lanes/yw05/yew; cd $t; export YEW_ROOT=$PWD; v=target/verify; mkdir -p $v; tag=$1
echo "$(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg)"
for r in 1 2 3 4 5; do tools/run-perf-editor --cpus 0-3 > $v/perf-editor-$tag-$r.txt 2>&1
  echo "editor $r: exit $? load $(cut -d' ' -f1-3 /proc/loadavg) $(grep -c 'verdict=FAIL' $v/perf-editor-$tag-$r.txt) FAIL"; done
for r in 1 2 3; do tools/run-perf-panes-tabs --cpus 0-3 > $v/perf-panes-tabs-$tag-$r.txt 2>&1
  echo "panes-tabs $r: exit $? $(grep GATED $v/perf-panes-tabs-$tag-$r.txt | awk '{print $1, $5}' | tr '\n' ' ')"; done
for r in 1 2 3; do tools/run-perf-jobstream --cpus 0-3 > $v/perf-jobstream-$tag-$r.txt 2>&1
  echo "jobstream $r: exit $? $(grep '^jobstream: p99' $v/perf-jobstream-$tag-$r.txt)"; done
echo "$(date -u +%FT%TZ) END"
