#!/bin/bash
# yw04: one live-editor save under the fault shim with no fault (YEW_FAULT_AT unset),
# printing the shim log: live-one.sh TREE BIN TAG [AT]
t=$1; bin=$2; tag=$3; at=$4
b=$t/target/oracle/sagitta/build
r=$(mktemp -d /tmp/live-one-XXXXXX); mkdir -p $r/state
cp $t/target/verify/troot/*/atomic-0.old $r/f.txt; cp $r/f.txt $r/f.old; cp $t/target/verify/troot/*/atomic-0.new $r/f.new
cd $r
env XDG_STATE_HOME=$r/state YEW_TORTURE_YEW=$bin YEW_RUNTIME_DIR=$t/target/oracle/sagitta/runtime LD_PRELOAD=$b/tests/torture/faultshim.so   YEW_FAULT_ENABLE=0 YEW_FAULT_SHORT=1 YEW_FAULT_LOG=$r/f.log YEW_FAULT_SEED=1 ${at:+YEW_FAULT_AT=$at}   $b/yew-live-torture --save $r/f.txt $r/f.new; echo "$tag: save exit $?"
XDG_STATE_HOME=$r/state $b/yew-torture --check $r/f.txt $r/f.old $r/f.new; echo "$tag: check $?"
echo "$tag: shim log:"; cat $r/f.log | tr "\n" ";"; echo
ls -la $r $r/state/yew/journal 2>/dev/null | grep -v total
