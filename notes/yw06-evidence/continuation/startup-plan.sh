#!/bin/bash
# yw06 deliverable 3 check, inside ctr from the repository root.
set -u
export CARGO_INCREMENTAL=0 YEW_LOG=/dev/null
YEW_ROOT=$PWD; export YEW_ROOT
. tools/lib-toolchain.sh
git rev-parse HEAD
fail=0
"$WOLF" fmt src/edit/driver.lu src/edit/workspace.lu src/edit/ed.lu src/edit/grouppicker.lu src/edit_startup_test.lu src/ws/state_lit.lu src/ws_state_lit_test.lu src/edit_state_fuzz.lu src/edit_ws_save_test.lu
git diff > target/fmt.patch; echo "fmt patch lines: $(wc -l < target/fmt.patch)"
mkdir -p target/d3
"$WOLF" build --deny-warnings src/edit_startup_test.lu -o target/d3/startup && target/d3/startup; rc=$?; echo "NATIVE startup rc=$rc"; [ $rc = 0 ] || fail=1
"$WOLF" conform-run --deny-warnings --checked --json src/edit_startup_test.lu; echo
tools/build --native; rc=$?; echo "NATIVE-BUILD yew rc=$rc"; [ $rc = 0 ] || fail=1
for c in ${CASES:-s23_three_tabs}; do
  tools/goldens --yew target/oracle/sagitta/build/yew --suite pty --case "$c" > /dev/null 2>&1
  echo "C $c: $(grep -m1 "^pty: $c:" target/oracle/goldens/pty.log)"
done
for c in ${PCASES:-startup_explicit_workspace s25_resume_exact s25_resume_survives_resize startup_multiple_files}; do
  tools/goldens --yew target/native/yew --suite pty --case "$c" > target/d3/$c.out 2>&1
  echo "PORT $c: $(grep -m1 "^pty: $c:" target/oracle/goldens/pty.log)"
  cp target/oracle/goldens/pty.log target/d3/$c.pty.log
done
echo "d3 fail=$fail"
exit $fail
