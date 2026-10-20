#!/bin/bash
# yw04: PTY goldens by name inside the container. sweep.sh TREE BIN CASEFILE TAG
# writes TREE/target/verify/sweep-TAG.txt (one line a case: ok / RED) and keeps
# each red case's pty.log beside it.
t=$1; bin=$2; cases=$3; tag=$4
cd "$t"; mkdir -p target/verify; out=target/verify/sweep-$tag.txt
echo "sweep $tag: bin $(sha256sum $bin | cut -c1-12) demo $(sha256sum target/tools/demo_paint 2>/dev/null | cut -c1-12)" > $out
n=0; okn=0
for c in $(cat $cases); do
  n=$((n+1))
  tools/goldens --yew $bin --demo target/tools/demo_paint --suite pty --case $c > /dev/null 2>&1
  if grep -q "^pty: $c: ok\$" target/oracle/goldens/pty.log; then
    echo "$c ok" >> $out; okn=$((okn+1))
  else
    echo "$c RED" >> $out; cp target/oracle/goldens/pty.log target/verify/sweep-$tag-$c.log
  fi
done
echo "sweep $tag: $okn/$n ok" >> $out
