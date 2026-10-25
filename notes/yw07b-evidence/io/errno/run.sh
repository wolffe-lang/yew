#!/bin/bash
# One binary (YEW=...) answers cases.fl; run inside ctr.sh from the io worktree.
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
d=$TMPDIR/yew-io-errno
"$here/setup.sh" "$d" >/dev/null
export IOW="$d" IOW_LONG=$(printf 'a%.0s' $(seq 1 300))
"${YEW:?the binary under test}" fl "$here/cases.fl" < /dev/null
echo "exit=$?"
chmod 755 "$d/ro"; rm -rf "$d"
