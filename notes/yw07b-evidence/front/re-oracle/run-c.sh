#!/bin/bash
# Run every case-NNN.fl under the pinned C yew; stdout to case-NNN.out.
cd "$(dirname "$0")/cases"; rm -f ../c-exit.txt
for f in case-*.fl; do
  timeout 60 /home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/build/yew fl "$f" > "${f%.fl}.out" 2> "${f%.fl}.err"
  echo "${f%.fl} $?" >> ../c-exit.txt
done
