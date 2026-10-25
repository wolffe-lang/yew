#!/bin/bash
# chain2.sh: after chain.sh, math's six cases alone on the checked machine
# (the whole stressed file is past the budget), normal and stressed.
set -u
cd /home/mfwolffe/lanes/yw07b/fmt-runs
while [ ! -f databatch.done ]; do sleep 20; done
./cases.sh mathcases src/fl_std_math_test.lu YEW_MATH_CASE 0 1 2 3 4 5 6
