#!/bin/bash
# C yew at the pin and the port's yew (target/lead/yew-io) over the API cases.
# The port side ran at 735ab4a with host-wiring.diff applied to flcli (the
# lead's to land): `yew fl` handing edit's registry to ed.commands.
here=notes/yw07b-evidence/io/api
YEW=/home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/build/yew $here/run.sh > $here/c.log 2>&1
YEW=$PWD/target/lead/yew-io $here/run.sh > $here/port.log 2>&1
diff $here/c.log $here/port.log > $here/diff.log; echo "diff=$?" >> $here/diff.log; cat $here/diff.log
