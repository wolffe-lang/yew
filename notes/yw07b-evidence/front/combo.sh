#!/bin/bash
# Stage a TEST-ONLY tree on kasumi: this worktree plus a fork branch's
# family files, never committed anywhere. Usage: combo.sh STAGE BRANCH FAMILY...
# e.g. combo.sh /tmp/combo yw07b-fmt fmt  (takes src/fl/std<family>.lu and
# drops that family's pending rows from native_pending.lu).
set -euo pipefail
stage=$1; branch=$2; shift 2
repo=$(cd "$(dirname "$0")/../../.." && pwd)
mkdir -p "$stage"
rsync -a --delete --exclude /target/ --exclude /.git "$repo/" "$stage/"
for fam in "$@"; do
  git -C "$repo" show "$branch:src/fl/std$fam.lu" > "$stage/src/fl/std$fam.lu"
  python3 - "$stage/src/fl/native_pending.lu" "$fam" <<'P'
import sys, re
p, fam = sys.argv[1], sys.argv[2]
s = open(p).read()
a = s.find('/// Pinned %s_DEFS rows' % fam.upper())
if a >= 0:
    b = s.index('/// Pinned', a + 10)
    s = s[:a] + s[b:]
open(p, 'w').write(s)
P
done
