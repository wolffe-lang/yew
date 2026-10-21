#!/bin/bash
# yw04: the 104 campaign-04 cases against C yew itself (the oracle), one by name.
cd /home/mfwolffe/lanes/yw04/yew
mkdir -p target/verify
out=target/verify/c04-oracle.txt; : > $out
for c in $(cat /home/mfwolffe/lanes/yw04/bin/c04-cases.txt); do
  tools/goldens --yew target/oracle/sagitta/build/yew --suite pty --case $c > /dev/null 2>&1
  if grep -q "^pty: $c: ok\$" target/oracle/goldens/pty.log; then echo "$c ok" >> $out; else echo "$c RED" >> $out; cp target/oracle/goldens/pty.log target/verify/c04-oracle-$c.log; fi
done
echo done >> $out
