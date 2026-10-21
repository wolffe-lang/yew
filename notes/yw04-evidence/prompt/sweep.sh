#!/bin/bash
# yw04-prompt: PTY goldens by name, inside the container (RULES §5);
# binaries built on the host beforehand. Usage: sweep.sh CASEFILE TIER... ;
# writes target/verify/sweep-<casefile>-<tier>.log, one verdict line a case.
cd "$(dirname "$0")/../../.." || exit 2
list=$1; shift
v=target/verify
mkdir -p $v
tag=$(basename "$list" .txt)
for tier in "$@"; do
  out=$v/sweep-$tag-$tier.log
  echo "sweep: $tag $tier yew $(sha256sum target/$tier/yew | cut -c1-12) demo $(sha256sum target/tools/demo_paint 2>/dev/null | cut -c1-12)" > $out
  ok=0; red=0
  for c in $(cat "$list"); do
    tools/goldens --yew target/$tier/yew --demo target/tools/demo_paint --suite pty --case "$c" > /dev/null 2>&1
    if grep -q "^pty: $c: ok\$" target/oracle/goldens/pty.log; then
      echo "$c ok" >> $out; ok=$((ok + 1))
    else
      echo "$c RED" >> $out; red=$((red + 1))
      cp target/oracle/goldens/pty.log "$v/red-$tier-$c.log"
    fi
  done
  echo "sweep: $tag $tier: $ok ok, $red red" >> $out
  tail -1 $out
done
