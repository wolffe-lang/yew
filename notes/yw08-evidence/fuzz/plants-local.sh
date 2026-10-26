#!/bin/bash
# Local seen-red for the fuzz gate: P1 skips the driver body (selftest on,
# then selftest off to reach the runner's tally floor), P2 leaks a stack
# slot in fl_vm_run. Each in its own scratch tree; the clone is not touched.
set -u
L=/home/mfwolffe/lanes/yw08
for p in p1 p1-noself p2; do
  t=$L/plant-$p
  rm -rf "$t"; mkdir -p "$t"
  (cd $L/yew && tar --exclude=./target --exclude=./.git -cf - .) | (cd "$t" && tar -xf -) || { echo "copy failed"; exit 2; }
  mkdir -p "$t/target/oracle"; ln -s $L/yew/target/oracle/sagitta "$t/target/oracle/sagitta"
  case $p in
  p1|p1-noself)
    sed -i 's/    if p.had_error || p.incomplete { return state_error(vm) }/    if p.had_error || p.incomplete || data.len >= 0 { return state_error(vm) }/' "$t/tools/fuzz-fl-vm/main.lu"
    [ "$(grep -c 'data.len >= 0' "$t/tools/fuzz-fl-vm/main.lu")" = 1 ] || { echo "p1 plant not applied"; exit 2; } ;;
  esac
  if [ $p = p1-noself ]; then
    sed -i '/^target\/tools\/fuzz-fl-vm --selftest$/d' "$t/tools/run-fuzz-fl-vm"
    ! grep -q 'fuzz-fl-vm --selftest' "$t/tools/run-fuzz-fl-vm" || { echo "selftest not removed"; exit 2; }
  fi
  if [ $p = p2 ]; then
    python3 - "$t/src/fl/vm.lu" <<'EOP' || exit 2
import sys
p=sys.argv[1]; s=open(p).read()
old="    vm.edit_depth = 0\n    vm.sp = 0\n    result\n}"
assert s.count(old)==1
open(p,'w').write(s.replace(old,"    vm.edit_depth = 0\n    result\n}"))
EOP
  fi
  echo "=== plant $p applied: $(cd $t && git -C $L/yew diff --no-index --stat $L/yew/tools/fuzz-fl-vm/main.lu tools/fuzz-fl-vm/main.lu | tail -1) $(diff $L/yew/src/fl/vm.lu $t/src/fl/vm.lu | head -2 | tr '\n' ' ')"
  (cd "$t" && YEW_ROOT=$t tools/run-fuzz-fl-vm --iters=200000 --seed=1 > $L/o55/plant-$p.out 2>&1); rc=$?
  echo "plant $p exit=$rc"; grep -v 'watchdog expired' $L/o55/plant-$p.out | tail -6
  rm -rf "$t"
done
