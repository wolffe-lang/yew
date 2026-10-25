#!/bin/bash
# The parse_only row, C and the port in the same run (inside ctr.sh, from
# the repo root): core's headless harness over THIS tree, release tier,
# runtime/init.fl at the pin, ROUNDS alternations (default 3).
set -euo pipefail
I=/home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/runtime/init.fl
notes/yw07b-evidence/front/perf/build.sh port --release > /dev/null
for r in $(seq 1 "${ROUNDS:-3}"); do
  target/perf-front/oracle-headless parse_only "$I" | sed 's/^/C    /' | cut -c1-60
  target/perf-front/port--release parse_only "$I" | sed 's/^/port /' | cut -c1-60
done
