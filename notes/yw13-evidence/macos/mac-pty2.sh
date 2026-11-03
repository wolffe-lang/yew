#!/bin/bash
# mac-pty2.sh SHA: yw13's macOS F-mode PTY rows, from a worktree pinned to
# SHA (the lane rules: build from a commit), under heavy.sh. The C oracle
# with clang, the port's release editor, four FUSS goldens by name, then
# the worktree's build output pruned and the worktree removed by its path.
set -u
sha=$1
wt=/Users/mfwolffe/lanes/yw13/build-$sha
export PATH="$HOME/.cargo/bin:$PATH"
df -g ~ | tail -1
free=$(df -g ~ | tail -1 | awk '{print $4}')
[ "$free" -ge 15 ] || { echo "STOP: ${free} GB free, under 15"; exit 3; }
git -C /Users/mfwolffe/lanes/yw13/yew worktree add -q --detach "$wt" "$sha" || exit 4
cd "$wt"
echo "START mac-pty2 head=$(git rev-parse HEAD) $(date -u +%FT%TZ)"
tools/fetch-toolchain > /Users/mfwolffe/lanes/yw13/jobs/mac-pty2-fetch.log 2>&1
rc=$?; echo "END fetch-toolchain exit=$rc $(.wolf-bin/wolf --version 2>/dev/null | head -1)"; [ $rc -eq 0 ] || exit $rc
tools/oracle --cc clang --build-only --jobs 4
rc=$?; echo "END oracle exit=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] || exit $rc
tools/build --release
rc=$?; echo "END release exit=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] || exit $rc
shasum -a 256 target/release/yew
for c in fuss_drawer_startup_dot startup_directory_workspace fuss_tree_light_tabs_80 fuss_nonrepo; do
    tools/goldens --yew target/release/yew --suite pty --case "$c"
    rc=$?
    grep -x "pty: $c: ok" target/oracle/goldens/pty.log
    g=$?
    echo "END golden $c exit=$rc verdict=$([ $g -eq 0 ] && echo ok || echo FAIL) $(date -u +%FT%TZ)"
    cp target/oracle/goldens/pty.log "/Users/mfwolffe/lanes/yw13/jobs/mac-pty2-$c.log"
done
cd /Users/mfwolffe/lanes/yw13
rm -rf "$wt/target" "$wt/.wolf-bin"
git -C /Users/mfwolffe/lanes/yw13/yew worktree remove "$wt" && echo "pruned $wt"
echo "DONE mac-pty2 $(date -u +%FT%TZ)"
