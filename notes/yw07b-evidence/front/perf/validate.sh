#!/bin/bash
# Hold the front end's gates across a perf change (inside ctr.sh, from the
# repo root): the 178-file dump differential through `yew fl` against the
# pinned C yew, and the lex and parse cases on the checked and native tiers.
set -u
B=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin
export WOLF_BIN=$B/wolf LUPIN_BIN=$B/lupin WOLF_STD=$B/std
oracle=/home/mfwolffe/lanes/yw07b/scratch-front/oracle
[ -e target/oracle ] || ln -s "$oracle" target/oracle
tools/build --native > target/perf-front/build-native.log 2>&1 || { echo "build FAILED"; tail -20 target/perf-front/build-native.log; exit 1; }
tools/check-fl-dump target/native/yew "$oracle/sagitta/build/yew" 2>&1 | tail -4
for f in src/fl_lex_test.lu src/fl_parse_test.lu; do
  notes/yw07b-evidence/front/tiers.sh $f native release 2>&1 | sed "s|^|$f |"
done
python3 notes/yw07b-evidence/front/checked-cases.py 2>&1 | tail -3
