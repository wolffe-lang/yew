#!/bin/bash
# yw04: yw03's ptymem.py (I-mode typing and line moves into a 10,000-line file)
# over yw03's editor (9bd219c, native) and yw04's (native), in the container.
cd /home/mfwolffe/lanes/yw04/yew
f=/tmp/mem-10k.txt
python3 -c "
with open('$f','w') as o:
    for i in range(10000): o.write('line %05d of the memory fixture, some words to type over\n' % i)
"
for b in ${BINS:-target/yw03ref/yew-yw03-native target/native/yew target/release/yew}; do
  for ph in type arrows; do
    cp $f /tmp/mem-run.txt
    echo "== $(basename $b) $(sha256sum $b | cut -c1-12) $ph: $(python3 notes/yw03-evidence/gates/ptymem.py $b /tmp/mem-run.txt 4000 $ph 2>&1 | tail -1)"
  done
done
cp $f /tmp/mem-run.txt
echo "== C $(sha256sum target/oracle/sagitta/build/yew | cut -c1-12) type: $(python3 notes/yw03-evidence/gates/ptymem.py target/oracle/sagitta/build/yew /tmp/mem-run.txt 4000 type 2>&1 | tail -1)"
cp $f /tmp/mem-run.txt
echo "== C arrows: $(python3 notes/yw03-evidence/gates/ptymem.py target/oracle/sagitta/build/yew /tmp/mem-run.txt 4000 arrows 2>&1 | tail -1)"
