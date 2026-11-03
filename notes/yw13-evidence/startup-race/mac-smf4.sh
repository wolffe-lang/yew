#!/bin/bash
# mac-smf4.sh SHA N: the throttled port run, each editor behind ptyrelay.py
# (a timestamped log of every byte both ways); the logs of failing runs kept.
set -u
sha=$1; n=${2:-10}
lane=/Users/mfwolffe/lanes/yw13
wt=$lane/build-$sha
cd "$wt" || exit 4
out=$lane/jobs/smf4-$sha
rm -rf "$out"; mkdir -p "$out/logs"
w=$out/yew-relay
printf '#!/bin/sh\nexec /usr/bin/python3 %s %s/logs/relay.$$ /usr/sbin/taskpolicy -b %s "$@"\n' "$lane/tools-local/ptyrelay.py" "$out" "$wt/target/release/yew" > "$w"; chmod +x "$w"
ok=0; bad=0
for i in $(seq 1 "$n"); do
    rm -f "$out"/logs/relay.*
    YEW_PTY_DIFF=full tools/goldens --yew "$w" --suite pty --case startup_multiple_files > "$out/run-$i.out" 2>&1
    if grep -qx "pty: startup_multiple_files: ok" target/oracle/goldens/pty.log; then ok=$((ok + 1)); v=ok; mkdir -p "$out/ok-$i"; mv "$out"/logs/relay.* "$out/ok-$i/" 2>/dev/null
    else bad=$((bad + 1)); v=FAIL; mkdir -p "$out/fail-$i"; mv "$out"/logs/relay.* "$out/fail-$i/" 2>/dev/null; cp target/oracle/goldens/pty.log "$out/fail-$i/pty.log"; fi
    echo "RUN $i $v $(date -u +%T)"
done
rm -rf target/oracle/sagitta/build/pty-startup_multiple_files-*
echo "COUNTS smf4 ok=$ok fail=$bad of $n"
