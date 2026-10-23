#!/bin/bash
# yw05 (lane): build every tools/*/main.lu harness against the tree's modules
# (inside ctr), warnings denied; one line a harness. harness-build.sh TAG
t=/home/mfwolffe/lanes/yw05/yew; cd $t; export YEW_ROOT=$PWD; . tools/lib-toolchain.sh
st=$t/target/yw05-harness; rm -rf $st; mkdir -p $st
for h in tools/*/main.lu; do n=$(basename $(dirname $h)); d=$st/$n/src; mkdir -p $d
  cp $h $d/main.lu; for m in src/*/; do cp -R $m $d/; done; rm -f $d/*/*_test.lu
  "$WOLF" build --release --deny-warnings $d/main.lu -o $st/$n/bin > $st/$n.log 2>&1; rc=$?
  echo "$n: exit $rc $(grep -m1 'error\[' $st/$n.log)"
done
