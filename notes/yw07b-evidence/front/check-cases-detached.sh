#!/bin/bash
# tools/check-test-cases over a frozen tree, one container session per file
# so the cores lock turns over between files. Detached use:
#   setsid -f bash check-cases-detached.sh TREE OUTDIR FILE...
set -u
tree=$1; out=$2; shift 2
mkdir -p "$out"; echo $$ > "$out/pid"; : > "$out/log"; rm -f "$out/exit"
cd "$tree"
B=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin
for f in "$@"; do
  /home/mfwolffe/lanes/yw07b/front/notes/yw07b-evidence/lane/ctr.sh . \
    env WOLF_BIN=$B/wolf LUPIN_BIN=$B/lupin WOLF_STD=$B/std python3 -I tools/check-test-cases "$f" >> "$out/log" 2>&1
done
echo done > "$out/exit"
