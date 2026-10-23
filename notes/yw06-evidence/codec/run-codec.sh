#!/usr/bin/env bash
# Run only inside the lane's ctr (scratch HOME, taskset 8-11, capped memory).
set -euo pipefail
export CARGO_INCREMENTAL=0
mkdir -p target/codec notes/yw06-evidence/codec/logs
exec > >(tee notes/yw06-evidence/codec/logs/verification-$(date -u +%Y%m%dT%H%M%SZ).log) 2>&1
date -u
.wolf-bin/wolf --version
sha256sum src/ws/{fllit,fl_parse,fl_emit,state_lit}.lu src/ws_{fl_lit_test,state_lit_test,state_corpus_test,fl_stress,fl_roundtrip}.lu
printf "affinity: "; taskset -pc $$
printf "oracle pin: "; git -C target/oracle/sagitta rev-parse HEAD
for f in src/ws/fllit.lu src/ws/fl_parse.lu src/ws/fl_emit.lu src/ws/state_lit.lu src/ws_fl_lit_test.lu src/ws_state_lit_test.lu src/ws_state_corpus_test.lu src/ws_fl_stress.lu src/ws_fl_roundtrip.lu; do .wolf-bin/wolf fmt --check "$f"; done
for f in ws_fl_lit_test ws_state_lit_test ws_state_corpus_test; do
  .wolf-bin/wolf build --deny-warnings "src/$f.lu" -o "target/codec/$f"
  "target/codec/$f"
done
for f in ws_fl_lit_test ws_state_lit_test; do
  .wolf-bin/wolf conform-run --deny-warnings --checked --json "src/$f.lu"
done
# Observe each checked corpus case independently; refusals are NOT successes.
checked_ok=0; checked_refused=0
while IFS= read -r fixture; do
  echo "CHECKED fixture $fixture"
  YEW_CODEC_FIXTURE="$fixture" .wolf-bin/wolf conform-run --deny-warnings --checked --json src/ws_state_corpus_test.lu > target/codec/checked.json 2>target/codec/checked.err
  cat target/codec/checked.err target/codec/checked.json
  if grep -q '"verdict":"exit(0)"' target/codec/checked.json; then checked_ok=$((checked_ok+1));
  elif grep -q '"verdict":"unsupported"' target/codec/checked.json; then checked_refused=$((checked_refused+1));
  else exit 1; fi
done < <(find tests/unit/fixtures/wsstate/v1 -name '*.fl' -printf '%P\n' | sort)
echo "CHECKED corpus accepted=$checked_ok refused=$checked_refused"
.wolf-bin/wolf build --deny-warnings src/ws_fl_stress.lu -o target/codec/stress
target/codec/stress --caps
for seed in 1 25 7301 3735928559; do target/codec/stress --fuzz "$seed" 100000; done
.wolf-bin/wolf build --release --deny-warnings src/ws_fl_roundtrip.lu -o target/codec/roundtrip
oracle=target/oracle/sagitta
mapfile -t objects < <(find "$oracle/build-gcc/src" -name '*.o' ! -path '*/main.o' | sort)
gcc -std=c11 -O2 -Wall -Wextra -Werror -I"$oracle/src" -I"$oracle/build-gcc" notes/yw06-evidence/codec/codec_oracle.c "${objects[@]}" -lm -o target/codec/oracle
python3 notes/yw06-evidence/codec/differential.py
python3 notes/yw06-evidence/codec/large_map.py
date -u
