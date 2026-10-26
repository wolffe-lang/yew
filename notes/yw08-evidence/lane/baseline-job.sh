#!/bin/bash
lane=/home/mfwolffe/lanes/yw08
printf '%s\n' "$$" > "$lane/baseline.pid"
echo "LAUNCH $(date -u +%FT%TZ) pid=$$"
"$lane/yew/notes/yw08-evidence/lane/ctr.sh" "$lane/yew" bash "$lane/baseline-inner.sh"
rc=$?
printf '%s\n' "$rc" > "$lane/baseline.exit"
echo "FINISH $(date -u +%FT%TZ) exit=$rc"
exit "$rc"
