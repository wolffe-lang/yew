#!/bin/bash
cd /home/mfwolffe/lanes/yw04/yew
seq -f 'line %05g of the memory fixture, some words to type over' 0 9999 > /tmp/k.txt
for b in target/yw03ref/yew-yw03-native target/native/yew; do
  cp /tmp/k.txt /tmp/k1.txt; rm -rf "$XDG_STATE_HOME/yew"
  python3 /home/mfwolffe/lanes/yw04/bin/keydiag.py $b /tmp/k1.txt ${N:-200}
done
