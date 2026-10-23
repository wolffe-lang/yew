#!/bin/bash
# The pick fork's C witnesses (W1-W5), run in yw06's kasumi ctr against
# the pinned oracle: no C source or golden is modified.
set -euo pipefail
oracle=target/oracle/sagitta
out=target/pick-witness
mkdir -p "$out"
head=$(git -C "$oracle" rev-parse HEAD)
test "$head" = 9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a
printf 'oracle=%s\n' "$head"
printf 'affinity='; taskset -pc $$
printf 'HOME=%s\nXDG_STATE_HOME=%s\n' "$HOME" "$XDG_STATE_HOME"
mapfile -t objects < <(find "$oracle/build-gcc/src" -name '*.o' ! -path '*/main.o' | sort)
gcc -std=c11 -O2 -Wall -Wextra -Werror -I"$oracle/src" -I"$oracle/build-gcc" \
    -Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=reallocarray \
    notes/yw06-evidence/pick/witness/picker_oracle.c "${objects[@]}" -lm -o "$out/picker-oracle"
echo "== W3: which keys reach the filter line (picker.c:759-870)"
"$out/picker-oracle" keys
echo "== W1: the file host (pickers.c:243-319)"
"$out/picker-oracle" files 5000
"$out/picker-oracle" files 200001
echo "== W5: allocation calls with the finder drawn (picker.c:944-1093, pickers.c:166-227)"
"$out/picker-oracle" alloc
echo "== W4: who calls yew_typejump_key at the pin"
git -C "$oracle" grep -n 'yew_typejump_key\|yew_typejump_active\|yew_typejump_clear' -- src tests || true
echo "== W2: C's finder gates, its own run"
make -C "$oracle" --no-print-directory -j2 CC=gcc BUILD=build-gcc build-gcc/perf_finder >/dev/null
"$oracle/build-gcc/perf_finder" --selftest-policy
"$oracle/build-gcc/perf_finder"
echo "witness: done"
