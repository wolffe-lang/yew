#!/bin/bash
base=/home/mfwolffe/lanes/yw07b/core
E="$base/notes/yw07b-evidence/core"
echo $$ > "$E/registry.pid"
/home/mfwolffe/lanes/yw07b/yew/notes/yw07b-evidence/lane/ctr.sh "$base" bash "$E/validate-registry.sh" > "$E/registry-run.log" 2>&1
rc=$?
printf '%s\n' "$rc" > "$E/registry.exit"
exit "$rc"
