#!/bin/bash
# R-yw06-10's gate on the port: the port's lister (src/ws_walk_lister.lu)
# run by the C witness's own witness.py on the same two fixture trees,
# its JSON compared with C's from notes/yw06-evidence/finder-inputs/
# c-witness.log. Run in yw06's kasumi ctr from the clone root.
set -euo pipefail
export YEW_ROOT=$PWD YEW_LOG=/dev/null
. tools/lib-toolchain.sh
out=target/finder-inputs-port
rm -rf "$out"
mkdir -p "$out"
printf 'affinity='; taskset -pc $$
"$WOLF" build --deny-warnings src/ws_walk_lister.lu -o "$out/walk-lister"
python3 -I notes/yw06-evidence/finder-inputs/witness.py "$out/walk-lister" "$out/fixtures" > "$out/port.json"
sed -n '/^{/,/^}/p' notes/yw06-evidence/finder-inputs/c-witness.log > "$out/c.json"
echo "== the port's listings"
cat "$out/port.json"
if cmp -s "$out/c.json" "$out/port.json"; then
    echo "finder-inputs: the port's listings are IDENTICAL to C's"
else
    diff -u "$out/c.json" "$out/port.json" || true
    echo "finder-inputs: the port's listings DIFFER from C's" >&2
    exit 1
fi
