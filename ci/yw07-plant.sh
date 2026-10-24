set -euo pipefail
ulimit -c 0
export YEW_ROOT="$PWD"
. tools/lib-toolchain.sh
mkdir -p target/plant
"$WOLF" build --deny-warnings src/text_undo_clock_test.lu -o target/plant/test
. tools/lib-test-env.sh
test_env_begin
target/plant/test
