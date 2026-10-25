#!/bin/bash
set -euo pipefail
root=/home/mfwolffe/lanes/yw07b/core
oracle=/home/mfwolffe/lanes/yw07b/yew/target/oracle/sagitta
[ "$(git -C "$oracle" rev-parse HEAD)" = 9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a ]
objects=$(make --no-print-directory -s -C "$oracle" --eval 'core-objects:;@echo $(PERF_CORE_OBJ)' core-objects)
cd "$oracle"
cc -std=c11 -O2 -Wall -Wextra -Werror -I src \
  -DPERF_SOURCE='"'"$oracle/tests/perf/perf_fletch.c"'"' \
  "$root/notes/yw07b-evidence/core/headless/oracle-headless.c" $objects -lm \
  -o "$root/target/oracle-headless"
