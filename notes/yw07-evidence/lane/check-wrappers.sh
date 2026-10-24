#!/bin/bash
# Run inside yw07's ctr, from the yew root. Exit statuses are never piped.
set -euo pipefail
export WOLF_STD="$PWD/.wolf-bin/std"
mkdir -p target/yw07
.wolf-bin/wolf fmt src/term_wait_storage_test.lu
for f in src/term_tty_test.lu src/term_wait_storage_test.lu src/edit_cmdparse_test.lu; do
    date -u
    echo "CHECKED $f"
    .wolf-bin/wolf test --deny-warnings --nocapture --no-native-fallback "$f"
    echo "NATIVE $f"
    .wolf-bin/wolf build --deny-warnings "$f" -o target/yw07/test
    target/yw07/test
    echo "RELEASE $f"
    .wolf-bin/wolf build --release --deny-warnings "$f" -o target/yw07/test
    target/yw07/test
done
tools/oracle --cc gcc --build-only --jobs 4
tools/build-demo
tools/goldens --yew target/release/yew --suite version,help
for c in probe_modern probe_dumb paint_basic paint_wide paint_colors_truecolor paint_colors_256 paint_colors_16 paint_damage paint_resize restore_quit restore_crash restore_bus restore_abrt restore_suspend input_keys_modern input_keys_legacy osc52_reply osc52_frame; do
    tools/goldens --yew target/release/yew --demo target/tools/demo_paint --suite pty --case "$c"
    grep -q "^pty: $c: ok$" target/oracle/goldens/pty.log
    cp target/oracle/goldens/pty.log "target/yw07/$c.log"
done
echo 'WRAPPER GATES GREEN: three suites, checked/native/release; version/help; 18 PTY cases'
