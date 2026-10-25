#!/bin/bash
# fmt-diff.sh: the port's probe and C yew over notes/yw07b-evidence/fmt/cases.txt.
set -u
cd /home/mfwolffe/lanes/yw07b/fmt
ev=notes/yw07b-evidence/fmt; out=target/fmt-diff; mkdir -p $out
stage=target/fmt-probe
rm -rf $stage; mkdir -p $stage
cp $ev/probe/main.lu $stage/main.lu
for d in src/*/; do m=$(basename $d); mkdir -p $stage/$m; cp src/$m/*.lu $stage/$m/; find $stage/$m -name '*_test.lu' -delete; done
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
$W build --deny-warnings $stage/main.lu -o target/fmt-probe.bin > target/fmt-probe.build.log 2>&1 || { echo BUILD-FAIL; tail -30 target/fmt-probe.build.log; exit 1; }
target/fmt-probe.bin $ev/cases.txt > $out/port.hex; echo "port exit=$?"
python3 -I $ev/c-cases.py /home/mfwolffe/lanes/yw07b/fmt-oracle/sagitta/build/yew $ev/cases.txt > $out/c.hex; echo "c exit=$?"
python3 -I $ev/compare.py $ev/cases.txt $out/port.hex $out/c.hex > $out/compare.log; echo "compare exit=$?"
tail -1 $out/compare.log
