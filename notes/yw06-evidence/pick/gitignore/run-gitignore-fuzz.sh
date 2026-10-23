#!/bin/bash
# The pick fork's fuzz_gitignore evidence, run in yw06's kasumi ctr from
# the clone root: C's own driver built at the pin, the port's campaign
# against it (the report lines byte for byte), then the answer fold of
# the port against gi_answers.c's over C's matcher at the same
# arguments. No C source or golden is modified.
#   run-gitignore-fuzz.sh [ITERS] [SEED]   (default 200000 1: C's campaign)
set -euo pipefail
iters=${1:-200000}
seed=${2:-1}
root=$PWD
oracle=target/oracle/sagitta
out=target/pick-witness
mkdir -p "$out"
head=$(git -C "$oracle" rev-parse HEAD)
test "$head" = 9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a
printf 'oracle=%s\n' "$head"
printf 'affinity='; taskset -pc $$
make -C "$oracle" --no-print-directory -j2 CC=gcc BUILD=build-gcc build-gcc/fuzz_gitignore >/dev/null
echo "== the campaign: the port's report against C's driver"
tools/run-fuzz-gitignore --campaign --against-oracle --seeds="$seed" --iters="$iters"
echo "== the answer fold: the port's matcher against C's"
mapfile -t objects < <(find "$oracle/build-gcc/src" -name '*.o' ! -path '*/main.o' | sort)
gcc -std=c11 -O2 -Wall -Wextra -Werror -I"$oracle/src" -I"$oracle/tests/fuzz" -I"$oracle/build-gcc" \
    notes/yw06-evidence/pick/gitignore/gi_answers.c "$oracle/build-gcc/tests/fuzz/fuzzlib.o" \
    "${objects[@]}" -lm -o "$out/gi-answers"
c_lines=$(cd "$oracle" && "$root/$out/gi-answers" --iters="$iters" --seed="$seed")
port_lines=$(FUZZ_PREBUILT=1 tools/run-fuzz-gitignore --iters="$iters" --seed="$seed" --answers)
printf 'C:    %s\n' "$c_lines" | sed '2,$s/^/      /'
printf 'port: %s\n' "$port_lines" | sed '2,$s/^/      /'
if [ "$c_lines" != "$port_lines" ]; then
    echo "gitignore-fuzz: the port's answers differ from C's" >&2
    exit 1
fi
echo "gitignore-fuzz: equal"
