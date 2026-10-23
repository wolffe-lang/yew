#!/bin/bash
# yw06 deliverable 6 check (and the full fmt check), inside ctr from the root.
set -u
export CARGO_INCREMENTAL=0 YEW_LOG=/dev/null
YEW_ROOT=$PWD; export YEW_ROOT
. tools/lib-toolchain.sh
git rev-parse HEAD
fail=0
if [ "${RUNNER:-0}" = 1 ]; then make -C target/oracle/sagitta -B -j2 CC=gcc BUILD=build-gcc build-gcc/pty_runner > target/runner-build.log 2>&1; echo "RUNNER rc=$?"; fi
"$WOLF" fmt src/edit/shell.lu src/edit/state_emit.lu src/edit_state_corpus_test.lu src/edit_shell_self_test.lu
git diff > target/fmt.patch; echo "fmt patch lines: $(wc -l < target/fmt.patch)"
tools/check-fmt; rc=$?; echo "CHECK-FMT rc=$rc"; [ $rc = 0 ] || fail=1
mkdir -p target/d6
for t in edit_shell_self_test edit_shell_quote_test edit_shell_term_test edit_shsession_test edit_startup_test; do
  "$WOLF" build --deny-warnings src/$t.lu -o target/d6/$t && target/d6/$t > target/d6/$t.out 2>&1; rc=$?
  echo "NATIVE $t rc=$rc $(grep -c PASS target/d6/$t.out) PASS $(grep -c SKIP target/d6/$t.out) SKIP"; [ $rc = 0 ] || { tail -5 target/d6/$t.out; fail=1; }
done
for i in 0 1 2 3; do
  YEW_SELF_CASE=$i "$WOLF" conform-run --deny-warnings --checked --json src/edit_shell_self_test.lu > target/d6/self.$i.json
  echo "CHECKED shell_self case $i: $(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["verdict"], d.get("x-unsupported-construct",""), (d.get("stdout_inline") or "").strip())' target/d6/self.$i.json)"
done
tools/build --native; rc=$?; echo "NATIVE-BUILD yew rc=$rc"; [ $rc = 0 ] || fail=1
for c in ${PCASES:-s57_11_shell_self_open s57_12_shift_arrow_highlight s57_12_clipboard_cut_paste s57_12_job_output_quit_returns startup_explicit_workspace s25_resume_exact s25_resume_survives_resize}; do
  tools/goldens --yew target/native/yew --suite pty --case "$c" > target/d6/$c.out 2>&1
  echo "PORT $c: $(grep -m1 "^pty: $c:" target/oracle/goldens/pty.log)"
  cp target/oracle/goldens/pty.log target/d6/$c.pty.log
done
echo "d6 fail=$fail"
exit $fail
