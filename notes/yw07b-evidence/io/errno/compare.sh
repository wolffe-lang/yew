#!/bin/bash
YEW=/home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/build/yew notes/yw07b-evidence/io/errno/run.sh > notes/yw07b-evidence/io/errno/c.log 2>&1
YEW=$PWD/target/lead/yew-io notes/yw07b-evidence/io/errno/run.sh > notes/yw07b-evidence/io/errno/port.log 2>&1
sed "s#scratch-io#X#" notes/yw07b-evidence/io/errno/c.log > $TMPDIR/c; sed "s#scratch-io#X#" notes/yw07b-evidence/io/errno/port.log > $TMPDIR/p
diff $TMPDIR/c $TMPDIR/p > notes/yw07b-evidence/io/errno/diff.log; echo "diff=$?" >> notes/yw07b-evidence/io/errno/diff.log; cat notes/yw07b-evidence/io/errno/diff.log
