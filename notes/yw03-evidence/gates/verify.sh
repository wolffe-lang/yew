#!/bin/bash
# yw03: the whole local gate at one head, inside the container (RULES §5).
# Writes target/verify/*.log and prints one line per step.
cd "$(dirname "$0")"/../yew 2>/dev/null || cd ~/lanes/yw03/yew
mkdir -p target/verify
v=target/verify
step() { local name=$1; shift; "$@" > "$v/$name.log" 2>&1; echo "verify: $name: exit $?"; }
echo "verify: head $(cat target/verify/HEAD 2>/dev/null)"
step fmt tools/check-fmt
step tables tools/check-tables
step cmdtab tools/check-cmdtab
step runtime tools/check-runtime
step build-all tools/build --all
step build-demo tools/build-demo
for tier in release native; do
  for f in notepad_ s15_ s16_ s17_; do
    tools/goldens --yew target/$tier/yew --demo target/tools/demo_paint --suite pty --filter $f > "$v/goldens-$tier-$f.log" 2>&1
    echo "verify: goldens $tier $f: exit $? $(grep -c ': ok$' target/oracle/goldens/pty.log) ok; $(grep -E '^pty: ' target/oracle/goldens/pty.log | grep -vcE ': ok$|xfailed=|global budget') not ok"
    cp target/oracle/goldens/pty.log "$v/pty-$tier-$f.log"
  done
done
step check-native tools/check-test --native
step check-checked tools/check-test
tail -1 "$v/check-checked.log"
grep -c "\[native\] ok" "$v/check-native.log" | sed 's/^/verify: native files ok: /'
