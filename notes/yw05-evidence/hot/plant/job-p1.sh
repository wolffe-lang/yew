# yw05-hot plant P1: one per-frame allocation put back (draw_span's cluster
# bytes replaced by a fresh list each cluster: the G33 shape), in a worktree
# at the head; the ledger test must go red and the PTY B/key must move.
set -u
echo "plant start $(date -u +%FT%TZ) head $(git rev-parse --short HEAD)"
pt=target/hot/plantsrc
[ -d $pt ] || git worktree add -q --detach $pt HEAD
(cd $pt && git checkout -q --detach HEAD && git log --oneline -1)
python3 - <<'PY'
p='target/hot/plantsrc/src/edit/draw.lu'
s=open(p).read()
old='        clear_bytes(mut ed.dbuf.cluster)\n        var k = pos\n'
assert s.count(old)==1
s=s.replace(old,'        ed.dbuf.cluster = List[byte]()\n        var k = pos\n')
open(p,'w').write(s)
PY
(cd $pt && git diff | tee ../plant-p1.diff)
mkdir -p target/hot/plant
(cd $pt && ../../../.wolf-bin/wolf build --deny-warnings src/yew.lu -o ../plant/yew-native > ../plant/build.log 2>&1; echo "plant yew build rc=$?"; ../../../.wolf-bin/wolf build --deny-warnings src/edit_drawbufs_test.lu -o ../plant/dbt > ../plant/build-t.log 2>&1; echo "plant test build rc=$?")
(cd $pt && YEW_LOG=/dev/null ../plant/dbt > ../plant/dbt.run 2>&1; echo "plant edit_drawbufs_test rc=$?"; cat ../plant/dbt.run)
h=notes/yw05-evidence/hot
python3 -c "
with open('target/hot/run/k10.txt','w') as o:
    for i in range(10000): o.write('line %05d of the memory fixture, some words to type over\n' % i)
"
for spec in lines40:R prompt-menu:R; do
  ph=${spec%%:*}
  for lb in C=target/oracle/sagitta/build/yew hot-native=target/hot/final/yew-native plant-native=target/hot/plant/yew-native; do
    cp README.md target/hot/run/m.txt; rm -rf "$XDG_STATE_HOME/yew"
    echo "${lb%%=*} R $(python3 $h/ptymem-hot.py ${lb#*=} target/hot/run/m.txt 1000 $ph 2>&1 | tr '\n' ' ')"
  done
done
(cd $pt && git checkout -q -- src/edit/draw.lu && git status --short | head -3; echo "plant restored")
echo "plant done $(date -u +%FT%TZ)"
