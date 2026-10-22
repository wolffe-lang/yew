#!/bin/bash
# yw05-hot: the PTY memory matrix, inside the container from the tree root.
# run-ptymem.sh OUT N LABEL=BIN... -> target/hot/ptymem-OUT.txt. Every phase
# runs every binary in turn (C yew, the oracle's build, first when given),
# so each row's C and port figures come from the same run. Each run gets a
# fresh copy of its file and an empty yew state (a killed editor's journal
# would ask the recovery question of the next run). Files: R = README.md
# (yw04's prompt file, 3,470 B, two non-ASCII lines), K = yw03's 10,000-line
# ASCII fixture (`mem-compare.sh`'s). Phases: yw04's two prompt rows, yw03's
# typing and line moves, `lines40` (40 down, 40 up: README's 71 lines keep
# every move a move; yw03's 500 would park on the last line), and the
# two-pane session (`ctrl+w s` first). Then yw04's driver unchanged (window
# 0x0) over its worst row, to tie to its 210 KB.
set -u
out=target/hot/ptymem-$1.txt; n=$2; shift 2
h=notes/yw05-evidence/hot
mkdir -p target/hot/run
python3 -c "
with open('target/hot/run/k10.txt','w') as o:
    for i in range(10000): o.write('line %05d of the memory fixture, some words to type over\n' % i)
"
{
echo "# ptymem-hot.py, N=$n, 24x80, $(date -u +%FT%TZ), cpus $(taskset -pc $$ | sed 's/.*: //'), load $(cut -d' ' -f1-3 /proc/loadavg)"
for lb in "$@"; do echo "# ${lb%%=*} ${lb#*=} $(sha256sum ${lb#*=} | cut -c1-12)"; done
for spec in prompt-menu:R prompt-type:R type:R type:K arrows:K lines40:R pane-lines40:R pane-arrows:K pane-type:R pane-prompt-menu:R; do
  ph=${spec%%:*}; f=${spec##*:}
  src=README.md; [ $f = K ] && src=target/hot/run/k10.txt
  for lb in "$@"; do
    cp $src target/hot/run/m.txt; rm -rf "$XDG_STATE_HOME/yew"
    echo "${lb%%=*} $f $(python3 $h/ptymem-hot.py ${lb#*=} target/hot/run/m.txt $n $ph 2>&1 | tr '\n' ' ')"
  done
done
for lb in "$@"; do
  cp README.md target/hot/run/m.txt; rm -rf "$XDG_STATE_HOME/yew"
  echo "${lb%%=*} R yw04-driver $(python3 $h/ptymem-prompt-yw04.py ${lb#*=} target/hot/run/m.txt $n menu 2>&1 | tr '\n' ' ')"
done
echo "# done $(date -u +%FT%TZ)"
} > $out 2>&1
