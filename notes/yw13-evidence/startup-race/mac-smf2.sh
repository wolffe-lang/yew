#!/bin/bash
# mac-smf2.sh SHA N: startup_multiple_files N times with the editor under
# `taskpolicy -b` (background QoS: the efficiency cores, throttled), the
# port's release editor and then C's at the pin as the control, from the
# worktree mac-smf.sh built. Failing runs keep their pty.log.
set -u
sha=$1; n=${2:-40}
lane=/Users/mfwolffe/lanes/yw13
wt=$lane/build-$sha
cd "$wt" || exit 4
out=$lane/jobs/smf2-$sha
mkdir -p "$out"
for who in port c; do
    if [ $who = port ]; then bin=$wt/target/release/yew; else bin=$wt/target/oracle/sagitta/build/yew; fi
    w=$out/yew-$who-bg
    printf '#!/bin/sh\nexec /usr/sbin/taskpolicy -b %s "$@"\n' "$bin" > "$w"; chmod +x "$w"
    ok=0; bad=0
    for i in $(seq 1 "$n"); do
        tools/goldens --yew "$w" --suite pty --case startup_multiple_files > "$out/$who-run-$i.out" 2>&1
        if grep -qx "pty: startup_multiple_files: ok" target/oracle/goldens/pty.log; then ok=$((ok + 1)); v=ok; rm -f "$out/$who-run-$i.out"
        else bad=$((bad + 1)); v=FAIL; cp target/oracle/goldens/pty.log "$out/$who-fail-$i.pty.log"; fi
        echo "RUN $who $i $v $(date -u +%T)"
    done
    echo "COUNTS smf2 $who ok=$ok fail=$bad of $n"
done
echo "DONE smf2 $(date -u +%FT%TZ)"
