#!/bin/bash
cd /home/mfwolffe/lanes/yw07b/fmt-oracle/sagitta
make --no-print-directory -j4 build/fuzz_fl_std build/fuzz_fl_parse > ../make.log 2>&1
echo "make=$?"
grep -n -i "error\|no rule" ../make.log | head
tail -3 ../make.log
ls -la build/fuzz_fl_std build/fuzz_fl_parse
