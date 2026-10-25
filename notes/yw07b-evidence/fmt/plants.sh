#!/bin/bash
# plants.sh: each gate seen red. A scratch copy of the fmt mirror gets one
# planted break per gate; the gate must fail, then the copy is discarded.
set -u
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
export WOLF_BIN=$W LUPIN_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/lupin
base=/home/mfwolffe/lanes/yw07b/fmt-runs/plant
run_plant() {  # name file sed-expr test-cmd...
  name=$1; file=$2; expr=$3; shift 3
  rm -rf $base; mkdir -p $base
  tar -C /home/mfwolffe/lanes/yw07b/fmt --exclude=./target -cf - . | tar -C $base -xf -
  cd $base
  before=$(md5sum $file | cut -c1-32)
  sed -i "$expr" $file
  after=$(md5sum $file | cut -c1-32)
  [ "$before" != "$after" ] || { echo "PLANT $name: the sed changed nothing"; return; }
  "$@" > $base.log 2>&1
  rc=$?
  echo "PLANT $name: exit=$rc $(grep -E 'FL_EQ|FAIL|wolf-trap|assert|differs|PASS' $base.log | head -3 | tr '\n' ' ')"
  cd /home/mfwolffe/lanes/yw07b/fmt-runs
}
mkdir -p $base
run_plant fmt-cycle-text src/fl/stdfmt.lu 's/fmt.repr: cycle at /fmt.repr: cycle near /' \
  bash -c "$W build --deny-warnings src/fl_std_fmt_test.lu -o t.bin && ./t.bin"
run_plant fmt-zero-pad src/fl/stdfmt.lu 's/let skip = if first == 45 || first == 43 || first == 32 then 1 else 0/let skip = 0/' \
  bash -c "$W build --deny-warnings src/fl_std_fmt_test.lu -o t.bin && ./t.bin"
run_plant math-round src/fl/stdmath.lu 's/7 => fl_float(mf.round(x)),/7 => fl_float(mf.floor(x)),/' \
  bash -c "$W build --deny-warnings src/fl_std_math_test.lu -o t.bin && ./t.bin"
run_plant data-bare-key src/fl/data.lu 's/c >= 97 \&\& c <= 122 || c >= 48 \&\& c <= 57 || c == 95)/c >= 97 \&\& c <= 122 || c >= 48 \&\& c <= 57 || c == 95 || c == 46)/' \
  bash -c "$W build --deny-warnings src/fl_data_test.lu -o t.bin && ./t.bin"
run_plant data-depth src/fl/data.lu 's/if depth > FL_DATA_MAX_DEPTH {/if depth > FL_DATA_MAX_DEPTH + 1 {/' \
  bash -c "$W build --deny-warnings src/fl_data_test.lu -o t.bin && ./t.bin"
run_plant fuzz-kind src/fl/stdfmt.lu '/^fn fmt_bad_directive/,/^}/ s/"type"/"bogus"/' \
  bash -c "tools/build-fuzz-fl-std --native > /dev/null && target/tools/fuzz-fl-std --iters=20000 --seed=1"
echo PLANTS-DONE
