#!/bin/bash
# pty-plant.sh — the PTY gate seen red: the picker's count separator
# `/` (C `picker.c`'s "%u/%u") planted as `|` in the working tree, the
# native editor rebuilt, two picker cases run (expected: neither ok), the
# plant reverted with git and the editor rebuilt clean. Run in the ctr
# from the clone root.
set -u
f=src/edit/picker.lu
grep -q 'pk_line_str(mut ed, "/")' "$f" || { echo "plant site moved"; exit 2; }
sed -i 's|pk_line_str(mut ed, "/")|pk_line_str(mut ed, "\|")|' "$f"
git diff --stat
tools/build --native > /dev/null || { git checkout -- "$f"; exit 2; }
notes/yw06-evidence/pick/pty.sh target/native/yew s26_finder_chrome chrome_picker
for c in s26_finder_chrome chrome_picker; do
    if [ -f "target/pick-pty/$c.log" ]; then
        echo "--- $c (planted) ---"
        head -40 "target/pick-pty/$c.log"
    fi
done
git checkout -- "$f"
git diff --stat
tools/build --native > /dev/null && echo "rebuilt clean"
notes/yw06-evidence/pick/pty.sh target/native/yew s26_finder_chrome chrome_picker
