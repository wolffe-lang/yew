#!/bin/bash
# frames.sh BIN NAME... — each edit function's stack frame (`sub $N,%rsp`)
# and its code size, read from a release binary; "inlined" when the
# symbol is not in the binary. Run in the ctr from the clone root.
set -u
bin=$1; shift
objdump -d --no-show-raw-insn "$bin" > target/frames.s
for f in "$@"; do
    fr=$(awk -v f="$f" 'index($0, "<_Wedit." f "$") && /:$/ {on=1; next} on && /^$/ {exit} on && /sub +\$0x[0-9a-f]+,%rsp/ {print $NF; exit}' target/frames.s)
    sz=$(nm -S "$bin" | awk -v f="$f" 'index($4, "_Wedit." f "$") == 1 {print $2}')
    echo "frame $f: ${fr:-none} size: ${sz:-inlined}"
done
rm -f target/frames.s
