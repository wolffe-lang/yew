#!/bin/bash
# fuzz-std.sh ITERS [--native]: build the port's fuzz_fl_std and run it at seed 1.
set -u
cd /home/mfwolffe/lanes/yw07b/fmt
export LUPIN_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/lupin WOLF_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
tools/build-fuzz-fl-std ${2:-} > /home/mfwolffe/lanes/yw07b/fmt-runs/fuzz-std-build.log 2>&1 || { echo BUILD-FAIL; tail -40 /home/mfwolffe/lanes/yw07b/fmt-runs/fuzz-std-build.log; exit 1; }
start=$(date +%s)
target/tools/fuzz-fl-std --iters=$1 --seed=1
echo "exit=$? seconds=$(( $(date +%s) - start ))"
