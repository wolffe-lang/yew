#!/bin/bash
# yw05-tabs (in ctr): P5, edit_modes_test's tab-jump case: the digit window
# arms in Insert too (tabs.c:1820-1840's rule dropped). Seen red, restored.
cd /home/mfwolffe/lanes/yw05-tabs/yew; export YEW_LOG=/dev/null XDG_STATE_HOME=$PWD/target/test-state
mkdir -p target/plants target/tests
cp src/edit/tabs.lu target/plants/tabs.lu.orig
L=$(grep -n "ed.mode != MODE_I && ed.mode != MODE_F" src/edit/tabs.lu | cut -d: -f1)
sed -i "${L}s/ed.mode != MODE_I \&\& ed.mode != MODE_F/ed.mode != MODE_F/" src/edit/tabs.lu; diff target/plants/tabs.lu.orig src/edit/tabs.lu
.wolf-bin/wolf build --deny-warnings src/edit_modes_test.lu -o target/tests/plant-p5 > target/plants/p5.build 2>&1 || { echo "plant p5: BUILD FAIL"; cat target/plants/p5.build; }
target/tests/plant-p5 > target/plants/p5-modes.out 2>&1; echo "plant p5-modes: exit $?"; tail -3 target/plants/p5-modes.out
cp target/plants/tabs.lu.orig src/edit/tabs.lu; cmp target/plants/tabs.lu.orig src/edit/tabs.lu && echo "plant p5: restored"
