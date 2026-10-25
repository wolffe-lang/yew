#!/bin/bash
# Build core's headless perf_fletch harness (yw07b core, notes/yw07b-evidence/
# core/headless/, copied unchanged) over THIS tree, and the C side from the
# pinned oracle build. Run inside ctr.sh from the repo root.
#   build.sh port [--release|--native] | build.sh oracle
set -euo pipefail
root=$(pwd)
here=$root/notes/yw07b-evidence/front/perf
case $1 in
port)
  stage=$root/target/perf-front/driver
  rm -rf "$stage"; mkdir -p "$stage"
  cp -R "$root/src/." "$stage/"
  find "$stage" -maxdepth 1 -type f -name '*.lu' -delete
  find "$stage" -type f -name '*_test.lu' -delete
  cp "$here/${MAIN:-main}.lu" "$stage/main.lu"
  export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
  tier=--release; [ "${2:---release}" = --native ] && tier=
  /home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf build $tier --deny-warnings "$stage/main.lu" -o "$root/target/perf-front/${MAIN:-port}${2:---release}"
  ;;
oracle)
  oracle=/home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta
  [ "$(git -C "$oracle" rev-parse HEAD)" = 9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a ]
  objects=$(make --no-print-directory -s -C "$oracle" --eval 'core-objects:;@echo $(PERF_CORE_OBJ)' core-objects)
  (cd "$oracle" && make -s -j4 $objects)
  mkdir -p "$root/target/perf-front"
  cd "$oracle"
  cc -std=c11 -O2 -Wall -Wextra -Werror -I src \
    -DPERF_SOURCE='"'"$oracle/tests/perf/perf_fletch.c"'"' \
    "$here/oracle-headless.c" $objects -lm -o "$root/target/perf-front/oracle-headless"
  ;;
esac
