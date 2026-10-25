#!/bin/bash
cd /home/mfwolffe/lanes/yw07b/fmt-oracle/sagitta
start=$(date +%s)
build/fuzz_fl_std --iters=200000 --seed=1 > ../c-fuzz-std.out 2> ../c-fuzz-std.err
echo "exit=$? seconds=$(( $(date +%s) - start ))" >> ../c-fuzz-std.out
cat ../c-fuzz-std.out
