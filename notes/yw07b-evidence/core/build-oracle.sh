#!/bin/bash
set -euo pipefail
root=/home/mfwolffe/lanes/yw07b/core
oracle=/home/mfwolffe/lanes/yw07b/yew/target/oracle/sagitta
build="$root/target/oracle-trace"
[ "$(git -C "$oracle" rev-parse HEAD)" = 9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a ]
make --no-print-directory -s -j4 -C "$oracle" BUILD="$build" FL_CGOTO=0 CFLAGS_FL_TRACE=1 "$build/fl_smoke"
objects=$(make --no-print-directory -s -C "$oracle" --eval 'core-objects:;@echo $(PERF_CORE_OBJ)' core-objects)
cd "$oracle"
cc -std=c11 -O2 -Wall -Wextra -Werror -I src "$root/notes/yw07b-evidence/core/oracle-core.c" $objects -lm -o "$root/target/oracle-core"
"$build/fl_smoke" --trace > "$root/notes/yw07b-evidence/core/oracle-trace1.txt"
"$build/fl_smoke" --trace > "$root/notes/yw07b-evidence/core/oracle-trace2.txt"
cmp "$root/notes/yw07b-evidence/core/oracle-trace1.txt" "$root/notes/yw07b-evidence/core/oracle-trace2.txt"
