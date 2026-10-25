set -u
o=$1; full=${2:-0}
step() { n=$1; shift; s=$(date +%s); "$@" > $o/$n.log 2>&1; rc=$?; echo "$n exit=$rc secs=$(( $(date +%s) - s )) :: $(tail -1 $o/$n.log)" >> $o/summary.txt; }
: > $o/summary.txt
step fmt tools/check-fmt
step build tools/build --release
step goldens tools/check-fletch-goldens target/release/yew
step dump tools/check-fl-dump target/release/yew
step trace tools/check-fl-trace
step smoke-c tools/smoke-fl target/oracle/sagitta/build/yew
step smoke tools/smoke-fl target/release/yew
step cases-selftest python3 -I tools/check-fl-cases --selftest
step cases python3 -I tools/check-fl-cases
step ctc-selftest python3 -I tools/check-test-cases-selftest
step ctc-controls python3 -I tools/test-check-test-cases
if [ "$full" = 1 ]; then
  [ -x target/oracle/sagitta/build/fuzz_fl_std ] || step oracle-fuzz-std make -C target/oracle/sagitta --no-print-directory -j4 build/fuzz_fl_std
  step fuzz-lex tools/run-fuzz-fl-front lex --against-oracle --iters=200000 --seed=1
  step fuzz-parse env FUZZ_PREBUILT=1 tools/run-fuzz-fl-front parse --against-oracle --iters=200000 --seed=1
  step fuzz-std tools/run-fuzz-fl-std --against-oracle --iters=200000 --seed=1
  step ctc-io python3 -I tools/check-test-cases src/fl_std_io_test.lu src/fl_api_headless_test.lu
fi
echo done >> $o/summary.txt
