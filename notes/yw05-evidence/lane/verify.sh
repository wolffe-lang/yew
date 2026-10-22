#!/bin/bash
# yw05 (yw04's verify): a tree's gate at one head, inside the container: each
# case file by name on both tiers, check-test --native and the checked lane.
# Binaries built first. verify.sh TREE TAG [CASEFILE...] (default c03 + c04).
t=$1; tag=$2; shift 2
cd "$t"; v=target/verify; mkdir -p $v
cfs="$*"; [ -n "$cfs" ] || cfs="/home/mfwolffe/lanes/yw05/bin/c03-cases.txt /home/mfwolffe/lanes/yw05/bin/c04-cases.txt"
for cf in $cfs; do
  n=$(basename $cf .txt)
  for tier in release native; do
    /home/mfwolffe/lanes/yw05/bin/sweep.sh $PWD target/$tier/yew $cf $tag-$n-$tier
    tail -n 1 $v/sweep-$tag-$n-$tier.txt
  done
done
tools/check-test --native > $v/check-native-$tag.log 2>&1; echo "check-test native: exit $? $(grep -c '\[native\] ok' $v/check-native-$tag.log) ok; SKIP lines $(grep -c SKIP $v/check-native-$tag.log)"
tools/check-test > $v/check-checked-$tag.log 2>&1; echo "check-test checked: exit $? $(tail -n 1 $v/check-checked-$tag.log)"
