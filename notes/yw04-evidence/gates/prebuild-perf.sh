#!/bin/bash
# yw04: build the perf drivers on kasumi's HOST (the release tier needs
# clang), off the gate's CPUs, so the 2x gates run them in the container.
cd /home/mfwolffe/lanes/yw04/yew
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
s=target/perf-re; rm -rf $s; mkdir -p $s target/tools
cp tools/perf-re/main.lu $s/main.lu
for m in util unicode term text search; do cp -R src/$m $s/$m; rm -f $s/$m/*_test.lu; done
taskset -c 4-15 "$WOLF" build --release --deny-warnings $s/main.lu -o target/tools/perf-re; echo "perf-re $?"
taskset -c 4-15 tools/build-perf-search; echo "perf-search $?"
s=target/perf-cmdcomp; rm -rf $s; mkdir -p $s
cp tools/perf-cmdcomp/main.lu $s/main.lu
for m in util unicode term text search ws edit; do cp -R src/$m $s/$m; rm -f $s/$m/*_test.lu; done
taskset -c 4-15 "$WOLF" build --release --deny-warnings $s/main.lu -o $s/perf-cmdcomp; echo "perf-cmdcomp $?"
echo END
