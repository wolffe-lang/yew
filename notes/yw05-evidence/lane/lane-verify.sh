#!/bin/bash
# yw05: the lane tree's gate at its head (run inside ctr): campaigns 01/03/04
# by name on both tiers, check-test both lanes, version/help. lane-verify.sh TAG
b=/home/mfwolffe/lanes/yw05/bin; t=/home/mfwolffe/lanes/yw05/yew
cd $t
tools/goldens --yew target/release/yew --suite version,help | tail -n 3
$b/verify.sh $t $1 $b/c01-cases.txt $b/c03-cases.txt $b/c04-cases.txt
