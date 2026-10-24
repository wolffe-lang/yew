set -euo pipefail
ulimit -c 0
export YEW_ROOT="$PWD"
python3 -I tools/check-test-cases-selftest
