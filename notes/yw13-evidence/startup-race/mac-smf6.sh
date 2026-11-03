#!/bin/bash
# mac-smf6.sh SHA N: port and C, each throttled behind ptyrelay.py with PATH
# naming a git wrapper that stamps every git child's start and end, so the
# editor's git chain can be placed against the keys and the frames.
set -u
sha=$1; n=${2:-8}
lane=/Users/mfwolffe/lanes/yw13
wt=$lane/build-$sha
cd "$wt" || exit 4
out=$lane/jobs/smf6-$sha
rm -rf "$out"; mkdir -p "$out/logs"
for who in port c; do
    if [ $who = port ]; then bin=$wt/target/release/yew; else bin=$wt/target/oracle/sagitta/build/yew; fi
    w=$out/yew-$who
    printf '#!/bin/sh\nPATH=%s:/usr/bin:/bin YW13_GITLOG=%s/logs/git.$$ exec /usr/bin/python3 %s %s/logs/relay.$$ /usr/sbin/taskpolicy -b %s "$@"\n' "$lane/tools-local/fakebin" "$out" "$lane/tools-local/ptyrelay.py" "$out" "$bin" > "$w"; chmod +x "$w"
    for i in $(seq 1 "$n"); do
        rm -f "$out"/logs/*
        tools/goldens --yew "$w" --suite pty --case startup_multiple_files > /dev/null 2>&1
        v=$(grep -qx "pty: startup_multiple_files: ok" target/oracle/goldens/pty.log && echo ok || echo FAIL)
        mkdir -p "$out/$who-$v-$i"; mv "$out"/logs/* "$out/$who-$v-$i/" 2>/dev/null
        echo "RUN $who $i $v"
    done
done
rm -rf target/oracle/sagitta/build/pty-startup_multiple_files-*
