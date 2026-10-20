#!/bin/bash
# yw03: the 62 campaign-03 goldens by name on both tiers, inside the
# container (RULES §5); binaries built on the host beforehand.
[ -x tools/goldens ] || exit 2
v=target/verify
mkdir -p $v
echo "verify-goldens: head $(cat $v/HEAD) release $(sha256sum target/release/yew | cut -c1-12) native $(sha256sum target/native/yew | cut -c1-12) demo $(sha256sum target/tools/demo_paint | cut -c1-12)"
for tier in release native; do
  for f in notepad_ s15_ s16_ s17_; do
    tools/goldens --yew target/$tier/yew --demo target/tools/demo_paint --suite pty --filter $f > "$v/goldens-$tier-$f.log" 2>&1
    rc=$?
    cp target/oracle/goldens/pty.log "$v/pty-$tier-$f.log"
    echo "verify-goldens: $tier $f: exit $rc, $(grep -c ': ok$' $v/pty-$tier-$f.log) ok, $(grep -E '^pty: ' $v/pty-$tier-$f.log | grep -vcE ': ok$|xfailed=|global budget') not ok"
  done
done
cat $v/pty-*-*.log | grep -E '^pty: .*: ok$' | sed 's/^pty: //; s/: ok$//' | sort | uniq -c | awk '{print $1}' | sort | uniq -c | sed 's/^/verify-goldens: cases seen N times: /'
