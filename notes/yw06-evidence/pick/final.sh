#!/bin/bash
# final.sh — the pick fork's release-tier verdicts at one head, run in
# yw06's kasumi ctr from the clone root: the release editor and the ten
# picker PTY cases against it, the finder perf beside C's
# (tools/run-perf-finder, taskset 8-11), then fuzz_gitignore's campaign
# against C's driver with both wall times, and the checked machine's
# reason for each case it refuses alone. Each step's rc is printed;
# nothing is piped.
set -u
echo "head=$(git rev-parse HEAD) dirty=$(git status --porcelain | wc -l)"
tools/build --release
echo "release-build rc=$?"
notes/yw06-evidence/pick/pty.sh target/release/yew s26_finder_chrome s26_finder_chrome_wide \
    s26_finder_cjk_highlight s26_buffer_switcher s26_undo_branches startup_multiple_files \
    chrome_picker chrome_picker_nocolor chrome_picker_colors_16 chrome_picker_ascii
tools/run-perf-finder --cpus 8-11
echo "perf-finder rc=$?"
PERF_PREBUILT=1 tools/run-perf-finder --cpus 8-11
echo "perf-finder (again) rc=$?"
tools/run-fuzz-gitignore --campaign --against-oracle
echo "fuzz-gitignore rc=$?"
for c in 0 4 5; do
    notes/yw06-evidence/pick/case-alone.sh src/edit_narrow_test.lu "$c" 600
done
notes/yw06-evidence/pick/case-alone.sh src/edit_picker_test.lu 9 600
