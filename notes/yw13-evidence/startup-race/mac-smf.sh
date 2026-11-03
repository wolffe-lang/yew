#!/bin/bash
# mac-smf.sh SHA [N]: startup_multiple_files N times on macOS (nomad) against
# the release editor built from a worktree pinned to SHA, run under heavy.sh
# (the Mac lock, the 8 GiB floor, yw13's HOME/XDG/git isolation). Every
# failing run's pty.log (the runner's two-capture diff) is kept under
# jobs/smf-SHA/. The worktree and its build stay for the fix's comparison.
set -u
sha=$1; n=${2:-30}
lane=/Users/mfwolffe/lanes/yw13
wt=$lane/build-$sha
out=$lane/jobs/smf-$sha
export PATH="$HOME/.cargo/bin:$PATH"
free=$(df -g ~ | tail -1 | awk '{print $4}')
[ "$free" -ge 15 ] || { echo "STOP: ${free} GB free, under 15"; exit 3; }
if [ ! -d "$wt" ]; then git -C $lane/yew worktree add -q --detach "$wt" "$sha" || exit 4; fi
cd "$wt"
[ "$(git rev-parse HEAD)" = "$(git -C $lane/yew rev-parse "$sha")" ] || { echo "STOP: worktree not at $sha"; exit 4; }
echo "START smf head=$(git rev-parse HEAD) $(date -u +%FT%TZ)"
if [ ! -x .wolf-bin/wolf ]; then tools/fetch-toolchain > "$lane/jobs/smf-fetch-$sha.log" 2>&1 || exit 5; fi
echo "wolf $(.wolf-bin/wolf --version | head -1)"
tools/oracle --cc clang --build-only --jobs 4; rc=$?; echo "END oracle exit=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] || exit $rc
if [ ! -x target/release/yew ] || [ "${SMF_REBUILD:-0}" = 1 ]; then tools/build --release; rc=$?; echo "END release exit=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] || exit $rc; fi
shasum -a 256 target/release/yew
mkdir -p "$out"
ok=0; bad=0
for i in $(seq 1 "$n"); do
    tools/goldens --yew target/release/yew --suite pty --case startup_multiple_files > "$out/run-$i.out" 2>&1
    if grep -qx "pty: startup_multiple_files: ok" target/oracle/goldens/pty.log; then ok=$((ok + 1)); v=ok; rm -f "$out/run-$i.out"
    else bad=$((bad + 1)); v=FAIL; cp target/oracle/goldens/pty.log "$out/fail-$i.pty.log"; fi
    echo "RUN $i $v $(date -u +%T)"
done
echo "COUNTS smf ok=$ok fail=$bad of $n"
echo "DONE smf $(date -u +%FT%TZ)"
