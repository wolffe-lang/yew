#!/usr/bin/env bash
# Execute inside the lane's container. No local macOS compilation.
set -euo pipefail
export YEW_ROOT=$PWD YEW_RUNTIME_DIR=$PWD/runtime
. tools/lib-toolchain.sh
. tools/lib-test-env.sh
test_env_begin
out=target/floats
mkdir -p "$out/driver"
cp notes/yw07b-evidence/floats/driver/main.lu "$out/driver/main.lu"
mkdir -p "$out/driver/fl"
cp src/fl/float.lu "$out/driver/fl/float.lu"
"$WOLF" fmt --check src/fl/float.lu src/fl_float_test.lu notes/yw07b-evidence/floats/driver/main.lu
"$WOLF" test --nocapture --no-native-fallback src/fl_float_test.lu
"$WOLF" build --release --deny-warnings src/fl_float_test.lu -o "$out/test-release"
"$out/test-release"
"$WOLF" build --release --deny-warnings "$out/driver/main.lu" -o "$out/port"
cc -std=c11 -pedantic -Wall -Wextra -Werror -O2 notes/yw07b-evidence/floats/oracle.c -o "$out/oracle"
python3 -I notes/yw07b-evidence/floats/corpus.py "$out/corpus.txt"
sha256sum src/fl/float.lu "$out/corpus.txt" "$out/port" "$out/oracle"
python3 -I notes/yw07b-evidence/floats/compare.py "$out/corpus.txt" "$out/oracle" "$out/port" "$out/full.json"
# The tool records every mismatch, not an overall PASS while G51 is open.
echo 'R4 corpus measured; read named NaN differences and host-C verdict before adoption'
