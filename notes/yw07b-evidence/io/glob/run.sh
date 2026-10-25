#!/bin/bash
# One binary (YEW=...) answers cases.fl over setup.sh's tree; inside ctr.sh.
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
d=$TMPDIR/yew-io-glob
"$here/setup.sh" "$d" >/dev/null
export IOW="$d"
"${YEW:?the binary under test}" fl "$here/cases.fl" < /dev/null
echo "exit=$?"
chmod 755 "$d/locked"; rm -rf "$d"
