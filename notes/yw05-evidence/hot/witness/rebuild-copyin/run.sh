#!/bin/bash
# yw05-hot: the witness's two programs, native, in the container, from the
# tree root -> notes/yw05-evidence/hot/witness/rebuild-copyin/run.txt.
d=notes/yw05-evidence/hot/witness/rebuild-copyin; o=target/hot/witness; mkdir -p $o
{
echo "# $(date -u +%FT%TZ), $(.wolf-bin/wolf --version 2>&1 | head -1)"
for p in replace copyin; do
  mkdir -p $o/$p; cp $d/$p.lu $o/$p/main.lu
  echo "== $p.lu: wolf build"
  .wolf-bin/wolf build $o/$p/main.lu -o $o/$p/a 2>&1 | sed "s#$PWD/##g"
  rc=${PIPESTATUS[0]}
  echo "build exit=$rc"
  if [ $rc = 0 ]; then $o/$p/a; echo "run exit=$?"; fi
done
} > $d/run.txt 2>&1
