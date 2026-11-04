#!/usr/bin/env bash
# yew#99's row: yw09b's runtime-skew PTY row twice in ONE --root.
#
#   runtime-pty-twice.sh YEW RUNTIME ROOT
#
# The first run starts from whatever ROOT holds; the second reuses the
# first's root, so its workspace state (keyed to the work folder's path)
# is there. Both must pass `runtime_locked_mode`. Prints
# `FAIL runtime_pty_second_run_same_root` when a run is red.
set -u
here=$(cd "$(dirname "$0")/../../.." && pwd)
yew=$1
runtime=$2
root=$3
for n in 1 2; do
    if python3 -I "$here/notes/yw09b-evidence/runtime-pty.py" --yew "$yew" --root "$root" --runtime "$runtime" >"$root.run$n.log" 2>&1; then
        echo "runtime-pty run $n: $(grep -m1 '^runtime_locked_mode' "$root.run$n.log")"
    else
        echo "runtime-pty run $n: red"
        sed 's/^/  | /' "$root.run$n.log" | tail -8
        echo "FAIL runtime_pty_second_run_same_root (run $n of 2 in one root)"
        exit 1
    fi
done
echo "runtime_pty_second_run_same_root: ok"
