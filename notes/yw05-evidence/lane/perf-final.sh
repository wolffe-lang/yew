#!/bin/bash
# yw05 (lane): the 2x gates at the final sources (inside ctr, CPUs 0-3):
# the editor, campaign 05's panes and tabs, the job stream, the completion
# menu (yw04's, its path touched by the hot merge). perf-final.sh TAG
t=/home/mfwolffe/lanes/yw05/yew; cd $t; export YEW_ROOT=$PWD; v=target/verify; mkdir -p $v; tag=$1
date -u +%FT%TZ
sha256sum target/release/yew target/native/yew | cut -c1-12
for p in editor panes-tabs jobstream cmdcomp; do
  tools/run-perf-$p --cpus 0-3 > $v/perf-$p-$tag.txt 2>&1; rc=$?
  echo "run-perf-$p: exit $rc"
  grep -E 'ratio=|^row: |^jobstream: |GATED|RED' $v/perf-$p-$tag.txt | head -40
  date -u +%FT%TZ
done
