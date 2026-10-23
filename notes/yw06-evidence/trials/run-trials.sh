#!/bin/bash
# Build trials.c against the oracle's PTY harness objects (the pty_runner's
# own link line with registry.o swapped for trials.o) and run its four
# cases over C yew and the port, in the lane's container (RULES §5).
#   notes/yw06-evidence/trials/run-trials.sh PORT_BIN
set -eu
root=$(cd "$(dirname "$0")/../../.." && pwd)
tree=$root/target/oracle/sagitta
port=$1
case "$port" in /*) ;; *) port=$root/$port ;; esac
cd "$tree"
make -C "$tree" -j2 CC=gcc BUILD=build-gcc build-gcc/pty_runner >/dev/null
cc_line=$(make -n -B CC=gcc BUILD=build-gcc build-gcc/tests/pty/registry.o | grep -E '(^| )-o build-gcc/tests/pty/registry.o' | tail -1)
ld_line=$(make -n -B CC=gcc BUILD=build-gcc build-gcc/pty_runner | grep -E -- '-o build-gcc/pty_runner' | tail -1)
[ -n "$cc_line" ] && [ -n "$ld_line" ] || { echo "run-trials: cannot read the oracle's build lines" >&2; exit 2; }
cp "$root/notes/yw06-evidence/trials/trials.c" build-gcc/trials.c
eval "$(echo "$cc_line" | sed 's#-o build-gcc/tests/pty/registry.o#-o build-gcc/trials.o#; s#tests/pty/registry.c#build-gcc/trials.c#; s# -MMD -MP##')" -Itests/pty
eval "$(echo "$ld_line" | sed 's#build-gcc/tests/pty/registry.o#build-gcc/trials.o#; s#-o build-gcc/pty_runner#-o build-gcc/trials_runner#')"
for bin in "$tree/build-gcc/yew" "$port"; do
    echo "== trials over $bin ($(sha256sum "$bin" | cut -c1-12))"
    ulimit -c 0
    set +e
    YEW_PTY_BUDGET_MS=1350000 YEW_PTY_CASE_BUDGET_MS=300000 \
        build-gcc/trials_runner --demo build-gcc/demo_paint --yew "$bin"
    echo "trials exit=$?"
    set -e
done
