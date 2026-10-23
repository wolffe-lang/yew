#!/bin/bash
# Run in yw06's kasumi ctr: no C source or golden modifications.
set -euo pipefail
oracle=target/oracle/sagitta
out=target/finder-inputs
mkdir -p "$out"
head=$(git -C "$oracle" rev-parse HEAD)
test "$head" = 9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a
printf 'oracle=%s\n' "$head"
printf 'affinity='; taskset -pc $$
printf 'HOME=%s\nXDG_STATE_HOME=%s\n' "$HOME" "$XDG_STATE_HOME"
mapfile -t objects < <(find "$oracle/build-gcc/src" -name '*.o' ! -path '*/main.o' | sort)
gcc -std=c11 -O2 -Wall -Wextra -Werror -I"$oracle/src" -I"$oracle/build-gcc" \
    notes/yw06-evidence/finder-inputs/walk_oracle.c "${objects[@]}" -lm -o "$out/walk-oracle"
python3 -I tools/walk-listings/witness.py "$out/walk-oracle" "$out/fixtures"
