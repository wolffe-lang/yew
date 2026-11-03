#!/bin/bash
# mac-fix.sh RED FIX N: the loop row red at RED and green at FIX (native
# edit_loop_test), then FIX's release editor through the throttled golden
# N times (startup_multiple_files, the editor under taskpolicy -b), from
# worktrees pinned to each sha; the oracle tree copied from build-7196d95.
set -u
red=$1; fix=$2; n=${3:-40}
lane=/Users/mfwolffe/lanes/yw13
export PATH="$HOME/.cargo/bin:$PATH"
free=$(df -g ~ | tail -1 | awk '{print $4}')
[ "$free" -ge 15 ] || { echo "STOP: ${free} GB free, under 15"; exit 3; }
for sha in "$red" "$fix"; do
    wt=$lane/build-$sha
    [ -d "$wt" ] || git -C $lane/yew worktree add -q --detach "$wt" "$sha" || exit 4
    cd "$wt"; [ -x .wolf-bin/wolf ] || tools/fetch-toolchain > /dev/null 2>&1 || exit 5
    export WOLF_STD=$PWD/.wolf-bin/std
    mkdir -p target/yw13
    .wolf-bin/wolf build --deny-warnings src/edit_loop_test.lu -o target/yw13/edit_loop_test > target/yw13/loop.build.log 2>&1
    echo "END build loop_test $sha exit=$?"
    YEW_LOG=/dev/null target/yw13/edit_loop_test > target/yw13/loop.run.log 2>&1
    echo "END run loop_test $sha exit=$? :: $(grep -E 'RED|cases run' target/yw13/loop.run.log | tr '\n' ' ')"
done
wt=$lane/build-$fix; cd "$wt"
mkdir -p target/oracle; [ -d target/oracle/sagitta ] || cp -R $lane/build-7196d95b019f228ba63506771c2420de4ec89856/target/oracle/sagitta target/oracle/sagitta
tools/oracle --cc clang --build-only --jobs 4 | tail -1
tools/build --release; echo "END release $fix exit=$? $(date -u +%FT%TZ)"
shasum -a 256 target/release/yew
out=$lane/jobs/fix-$fix; rm -rf "$out"; mkdir -p "$out"
w=$out/yew-port-bg
printf '#!/bin/sh\nexec /usr/sbin/taskpolicy -b %s "$@"\n' "$wt/target/release/yew" > "$w"; chmod +x "$w"
ok=0; bad=0
for i in $(seq 1 "$n"); do
    tools/goldens --yew "$w" --suite pty --case startup_multiple_files > "$out/run-$i.out" 2>&1
    if grep -qx "pty: startup_multiple_files: ok" target/oracle/goldens/pty.log; then ok=$((ok + 1)); rm -f "$out/run-$i.out"
    else bad=$((bad + 1)); cp target/oracle/goldens/pty.log "$out/fail-$i.pty.log"; fi
done
rm -rf target/oracle/sagitta/build/pty-startup_multiple_files-*
echo "COUNTS throttled startup_multiple_files $fix ok=$ok fail=$bad of $n"
echo "DONE mac-fix $(date -u +%FT%TZ)"
