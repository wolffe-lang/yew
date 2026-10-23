#!/bin/bash
# fmt.sh — `wolf fmt` over src/ and every tools/*/ program (twice: G22,
# not a fixed point on some files), the change left as target/fmt.patch
# for the Mac side to apply; then tools/check-fmt's verdict. Run in the
# ctr from a clean clone root; `git checkout -- .` after.
set -u
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
"$WOLF" fmt src
"$WOLF" fmt src
for d in tools/*/; do
    [ -f "$d/main.lu" ] && "$WOLF" fmt "$d" && "$WOLF" fmt "$d"
done
"$WOLF" fmt notes/yw06-evidence/pick/witness/bytes-view
mkdir -p target
git diff > target/fmt.patch
echo "fmt: $(git diff --stat | tail -1)"
tools/check-fmt
echo "check-fmt rc=$?"
