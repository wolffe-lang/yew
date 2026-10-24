#!/bin/bash
# Candidate validation on kasumi, inside ctr. This is not the full yw07 gate.
set -euo pipefail
export WOLF_STD="$PWD/.wolf-bin/std"
mkdir -p target/yw07
printf 'head=%s\n' "$(git rev-parse HEAD)"
date -u
files=(src/term/tty.lu src/edit/cmdparse.lu src/ws/state_lit.lu
    src/edit_state_fuzz.lu tools/fuzz-state/main.lu src/text/clipboard.lu
    tools/yew-torture/main.lu src/term_wait_storage_test.lu
    src/ws_state_sort_test.lu src/text_clipboard_host_test.lu src/edit_cmdparse_test.lu)
.wolf-bin/wolf fmt --check "${files[@]}"
git diff --stat
for f in src/term_wait_storage_test.lu src/ws_state_sort_test.lu src/text_clipboard_host_test.lu src/term_tty_test.lu; do
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
# The large corpus is deliberately case-sliced on the checked machine (G29).
python3 -I tools/check-test-cases src/edit_cmdparse_test.lu src/ws_state_corpus_test.lu
for tier in native release; do
    flags=()
    [ "$tier" = native ] || flags+=(--release)
    for f in src/edit_cmdparse_test.lu src/ws_state_corpus_test.lu; do
        .wolf-bin/wolf build "${flags[@]}" --deny-warnings "$f" -o target/yw07/corpus
        target/yw07/corpus
    done
done
# HOME is scratch; the control lives beside this clone.
old="$(dirname "$PWD")/archives/wolf-0.2.34/wolf-0.2.34-x86_64-unknown-linux-gnu/wolf"
bash notes/yw06-evidence/g20-closure/run.sh "$old" "$PWD/.wolf-bin/wolf" > target/yw07/g20-control.log
cat target/yw07/g20-control.log
grep -q 'twin release build=4 run=\[\].*vtable slot' target/yw07/g20-control.log
grep -q 'twin release build=0 run=\[1 2 3 3 11 22\]' target/yw07/g20-control.log
tools/build --all
tools/oracle --cc gcc --build-only --jobs 4
tools/build-demo
tools/goldens --yew target/release/yew --suite version,help
for c in probe_modern probe_dumb paint_basic paint_wide paint_colors_truecolor paint_colors_256 paint_colors_16 paint_damage paint_resize restore_quit restore_crash restore_bus restore_abrt restore_suspend input_keys_modern input_keys_legacy osc52_reply osc52_frame; do
    tools/goldens --yew target/release/yew --demo target/tools/demo_paint --suite pty --case "$c"
    grep -q "^pty: $c: ok$" target/oracle/goldens/pty.log
    cp target/oracle/goldens/pty.log "target/yw07/$c.log"
done
tools/run-fuzz-state --campaign --against-oracle --seeds=1 --sessions=200000
tools/run-perf-state --cpus 8-11
echo 'ADOPTION CANDIDATE GREEN (not the complete yw07 gate)'
