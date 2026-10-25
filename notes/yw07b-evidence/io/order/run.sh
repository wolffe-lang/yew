#!/bin/bash
# Build native and release, run each into one file, both streams.
cd "$(dirname "$0")"
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
for t in native release; do
  f=; [ $t = release ] && f=--release
  $W build --deny-warnings $f main.lu -o $TMPDIR/order-$t > /dev/null 2>&1 || { echo "$t build failed"; continue; }
  $TMPDIR/order-$t > $TMPDIR/order-$t.out 2>&1
  echo "== $t file"; cat $TMPDIR/order-$t.out
  $TMPDIR/order-$t 2>&1 | cat > $TMPDIR/order-$t.pipe
  echo "== $t pipe"; cat $TMPDIR/order-$t.pipe
done
