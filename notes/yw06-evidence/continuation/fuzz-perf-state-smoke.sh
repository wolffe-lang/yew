#!/bin/bash
# yw06 fuzz_state smoke: fmt, the port's driver and C's, one small campaign compared.
set -u
export CARGO_INCREMENTAL=0 YEW_LOG=/dev/null
YEW_ROOT=$PWD; export YEW_ROOT
. tools/lib-toolchain.sh
git rev-parse HEAD
"$WOLF" fmt tools/fuzz-state/main.lu tools/fuzzgen/fuzzgen.lu tools/perf-state/main.lu; git diff > target/fmt.patch; echo "fmt patch lines: $(wc -l < target/fmt.patch)"
make -C target/oracle/sagitta -j2 CC=gcc BUILD=build-gcc build-gcc/fuzz_state build-gcc/perf_state > target/c-drivers.log 2>&1; echo "C-DRIVERS rc=$?"
/usr/bin/time -f "build wall=%e rss=%M" tools/build-fuzz-state; echo "BUILD rc=$?"
for s in ${SEEDS:-1}; do
  /usr/bin/time -f "port wall=%e rss=%M" target/tools/fuzz-state --iters=${ITERS:-200} --seed=$s; echo "PORT rc=$?"
  (cd target/oracle/sagitta && /usr/bin/time -f "c wall=%e rss=%M" build/fuzz_state --iters=${ITERS:-200} --seed=$s); echo "C rc=$?"
done
tools/run-perf-state --cpus 8-11; echo "PERF-STATE rc=$?"
