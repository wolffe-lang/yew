#!/bin/bash
# yw13 item 1, second pass: every case that failed with highlighting off
# is rerun with YEW_PTY_DIFF=full so the whole want/got pair is kept, then
# classified cell by cell (inv-classify.py): a case whose text grid is
# identical and whose style differences all sit on cells the golden draws
# in a syntax colour depends on highlighting, nothing else.
set -uo pipefail
lane=/mnt/steamlib/lanes/yw13
root=$lane/yew
out=$lane/inv
tree=$root/target/oracle/sagitta
cd "$root"
mkdir -p "$out/full"
for c in $(grep ' nosyn=[^0]' "$lane/jobs/inv1.log" | awk '{print $2}'); do
    YEW_PTY_DIFF=full YEW_PTY_RUNTIME_DIR="$out/runtime-nosyn" \
        tools/goldens --yew "$tree/build/yew" --suite pty --case "$c" > "$out/full/$c.log" 2>&1
    rc=$?
    cp target/oracle/goldens/pty.log "$out/full/$c.pty.log"
    printf 'FULL %s rc=%s\n' "$c" "$rc"
done
python3 -I "$lane/inv-classify.py" "$out/full" "$tree/tests/pty/goldens" > "$out/classify.txt"
cat "$out/classify.txt"
