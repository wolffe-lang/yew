#!/bin/bash
# A/B the parse-only profiling driver: build THIS tree's prof as NAME, then
# alternate it with BASE (an earlier build) three times, same session.
#   ab.sh NAME BASE   (inside ctr.sh, from the repo root)
set -euo pipefail
name=$1; base=$2
P=/home/mfwolffe/lanes/yw07b/scratch-front/perf-prof
I=/home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/runtime/init.fl
MAIN=prof notes/yw07b-evidence/front/perf/build.sh port --release > /dev/null
cp target/perf-front/prof--release "$P/$name"
for r in 1 2 3; do
  printf '%-14s ' "$base"; "$P/$base" "$I" 400
  printf '%-14s ' "$name"; "$P/$name" "$I" 400
done
