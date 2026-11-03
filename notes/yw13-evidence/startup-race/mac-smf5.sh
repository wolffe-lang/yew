#!/bin/bash
# mac-smf5.sh SHA N: C's editor at the pin behind ptyrelay.py, throttled as
# mac-smf4.sh runs the port, so the two byte streams can be compared.
set -u
sha=$1; n=${2:-6}
lane=/Users/mfwolffe/lanes/yw13
wt=$lane/build-$sha
cd "$wt" || exit 4
out=$lane/jobs/smf5-$sha
rm -rf "$out"; mkdir -p "$out/logs"
w=$out/yew-relay
printf '#!/bin/sh\nexec /usr/bin/python3 %s %s/logs/relay.$$ /usr/sbin/taskpolicy -b %s "$@"\n' "$lane/tools-local/ptyrelay.py" "$out" "$wt/target/oracle/sagitta/build/yew" > "$w"; chmod +x "$w"
for i in $(seq 1 "$n"); do
    rm -f "$out"/logs/relay.*
    tools/goldens --yew "$w" --suite pty --case startup_multiple_files > "$out/run-$i.out" 2>&1
    v=$(grep -qx "pty: startup_multiple_files: ok" target/oracle/goldens/pty.log && echo ok || echo FAIL)
    mkdir -p "$out/$v-$i"; mv "$out"/logs/relay.* "$out/$v-$i/" 2>/dev/null
    echo "RUN $i $v"
done
rm -rf target/oracle/sagitta/build/pty-startup_multiple_files-*
