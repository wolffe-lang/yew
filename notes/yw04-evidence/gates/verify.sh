#!/bin/bash
# yw04: the lane's gate at one head, inside the container (RULES 5): campaign
# 03's 62 (and any extra case list) by name on both tiers, check-test --native
# and the checked lane. Binaries built on the host first. verify.sh TAG [CASEFILE...]
cd /home/mfwolffe/lanes/yw04/yew
tag=$1; shift
v=target/verify; mkdir -p $v
for cf in /home/mfwolffe/lanes/yw04/bin/c03-cases.txt "$@"; do
  n=$(basename $cf .txt)
  for tier in release native; do
    /home/mfwolffe/lanes/yw04/bin/sweep.sh $PWD target/$tier/yew $cf $tag-$n-$tier
    tail -1 $v/sweep-$tag-$n-$tier.txt
  done
done
tools/check-test --native > $v/check-native-$tag.log 2>&1; echo "check-test native: exit $? $(grep -c '\[native\] ok' $v/check-native-$tag.log) ok"
tools/check-test > $v/check-checked-$tag.log 2>&1; echo "check-test checked: exit $? $(tail -1 $v/check-checked-$tag.log)"
