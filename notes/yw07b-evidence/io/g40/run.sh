#!/bin/bash
# One binary (YEW=...) over the G40 cases; inside ctr.sh.
here=$(cd "$(dirname "$0")" && pwd)
d=$TMPDIR/yew-io-g40; rm -rf "$d"; mkdir -p "$d"
export IOW="$d" IOW_BAD=$'v\xffw'
"${YEW:?the binary under test}" fl "$here/cases.fl" < /dev/null; echo "exit=$?"
rm -rf "$d"
