#!/bin/bash
# yw05-tabs (in ctr): one planted break per new test file and for the tab
# oracle, each run seen RED, then restored from a backup. plants.sh
cd /home/mfwolffe/lanes/yw05-tabs/yew; export YEW_ROOT=$PWD YEW_LOG=/dev/null XDG_STATE_HOME=$PWD/target/test-state
mkdir -p target/plants target/tests target/test-state
cp src/edit/strip.lu target/plants/strip.lu.orig; cp src/edit/tabs.lu target/plants/tabs.lu.orig
run_test() { # NAME FILE
  .wolf-bin/wolf build --deny-warnings $2 -o target/tests/plant-$1 > target/plants/$1.build 2>&1 || { echo "plant $1: BUILD FAIL"; cat target/plants/$1.build; return; }
  target/tests/plant-$1 > target/plants/$1.out 2>&1; echo "plant $1: exit $?"; tail -4 target/plants/$1.out
}
date -u +%FT%TZ
# P1 edit_strip_test: the follow walk scrolls two at a time (strip.c:76-100's minimality broken).
sed -i '144s/first += 1/first += 2/' src/edit/strip.lu; diff target/plants/strip.lu.orig src/edit/strip.lu
run_test p1-strip src/edit_strip_test.lu
cp target/plants/strip.lu.orig src/edit/strip.lu
# P2 edit_tabs_test: shifted_index's inequality backwards (tabs.c:486-493).
sed -i '469s/i > from \&\& i <= to/i > from \&\& i < to/' src/edit/tabs.lu; diff target/plants/tabs.lu.orig src/edit/tabs.lu
run_test p2-tabs src/edit_tabs_test.lu
cp target/plants/tabs.lu.orig src/edit/tabs.lu
# P3 edit_tabs_test's port row: a refused w closes the tab anyway (tabs.c:2146-2197).
sed -i '1564d' src/edit/tabs.lu; diff target/plants/tabs.lu.orig src/edit/tabs.lu
run_test p3-tabs-port src/edit_tabs_test.lu
cp target/plants/tabs.lu.orig src/edit/tabs.lu
# P4 fuzz-tabs: the close keeps the active INDEX instead of resolving the survivor's id.
sed -i '424s/ed.tab_active = tab_index_of_id(ed, survivor)/ed.tab_active = if ed.tab_active < ed.tabs.len then ed.tab_active else ed.tabs.len - 1/' src/edit/tabs.lu; diff target/plants/tabs.lu.orig src/edit/tabs.lu
tools/run-fuzz-tabs --native --iters=10000 --seed=1 > target/plants/p4-fuzz.out 2>&1; echo "plant p4-fuzz: exit $?"; cut -c1-300 target/plants/p4-fuzz.out | tail -4
cp target/plants/tabs.lu.orig src/edit/tabs.lu
cmp target/plants/tabs.lu.orig src/edit/tabs.lu && cmp target/plants/strip.lu.orig src/edit/strip.lu && echo "plants: restored"
date -u +%FT%TZ
