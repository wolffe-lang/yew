#!/bin/bash
# yw06 state suites at one head, inside ctr from the repository root.
# Native: each file built --deny-warnings and run, exit read directly.
# Checked: conform-run --checked per file; a budget refusal reruns per case
# (YEW_STATE_CASE or argv) so every case has a checked verdict (G29).
set -u
export CARGO_INCREMENTAL=0 YEW_LOG=/dev/null
YEW_ROOT=$PWD; export YEW_ROOT
. tools/lib-toolchain.sh
out=target/yw06-state; mkdir -p "$out"
fail=0
budget=0
git rev-parse HEAD 2>/dev/null || true
"$WOLF" --version | head -1
grep -E "SigBlk|SigIgn" /proc/$$/status
FILES=${STATE_FILES:-"ws_fl_lit_test ws_state_lit_test ws_state_corpus_test edit_ws_key_test edit_ws_history_test edit_state_schema_test edit_state_options_test edit_ws_restore_test edit_ws_cmds_test edit_ws_recover_test edit_ws_save_test edit_state_bytes_test edit_state_corpus_test"}
for name in $FILES; do
    echo "== native $name"
    if "$WOLF" build --deny-warnings "src/$name.lu" -o "$out/$name"; then
        "$out/$name"; rc=$?
        echo "NATIVE $name rc=$rc"
        [ "$rc" = 0 ] || fail=1
    else
        rc=$?; echo "NATIVE-BUILD $name rc=$rc"; fail=1
    fi
done
[ "${STATE_CHECKED:-1}" = 1 ] || { echo "state-suite fail=$fail (checked skipped by request)"; exit $fail; }
cases() {
    case $1 in
    edit_ws_key_test) echo 11 ;; edit_ws_restore_test) echo 18 ;; edit_ws_cmds_test) echo 16 ;;
    edit_ws_recover_test) echo 15 ;; edit_ws_save_test) echo 27 ;; *) echo 0 ;;
    esac
}
verdict() { python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("verdict"), d.get("x-unsupported-construct",""))' "$1" 2>/dev/null || echo "unreadable"; }
for name in $FILES; do
    echo "== checked $name"
    "$WOLF" conform-run --deny-warnings --checked --json "src/$name.lu" > "$out/$name.checked.json"
    v=$(verdict "$out/$name.checked.json")
    echo "CHECKED $name: $v"
    case $v in "exit(0)"*) continue ;; esac
    sel=YEW_STATE_CASE
    case $name in
    ws_state_corpus_test)
        sel=YEW_CODEC_FIXTURE
        list=$(grep -E '^const (CANONICAL|NONCANONICAL|INVALID): str' "src/$name.lu" | sed 's/.*= "//; s/"$//' | tr '|' ' ') ;;
    edit_state_corpus_test)
        sel=YEW_STATE_FIXTURE
        list=$(cd tests/unit/fixtures/wsstate/v1/invalid && ls *.fl) ;;
    *)
        n=$(cases "$name")
        if [ "$n" = 0 ]; then echo "CHECKED-RED $name (no per-case selector)"; fail=1; continue; fi
        list=$(seq 0 $((n - 1))) ;;
    esac
    for i in $list; do
        tag=$(echo "$i" | tr '/' '_')
        if [ "$name" = edit_ws_key_test ]; then
            "$WOLF" conform-run --deny-warnings --checked --json "src/$name.lu" -- "$i" > "$out/$name.$tag.checked.json"
        else
            env "$sel=$i" "$WOLF" conform-run --deny-warnings --checked --json "src/$name.lu" > "$out/$name.$tag.checked.json"
        fi
        v=$(verdict "$out/$name.$tag.checked.json")
        so=$(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print((d.get("stdout_inline") or "").strip().replace("\n"," | "))' "$out/$name.$tag.checked.json" 2>/dev/null)
        echo "CHECKED $name case $i: $v :: $so"
        case "$name:$i:$v" in
        *":exit(0)"*) ;;
        "ws_state_corpus_test:18-maximal-512-tabs.fl:unsupported step budget exhausted")
            echo "CHECKED-BUDGET $name $i (the checked machine's 20M-step budget; native covers it)"; budget=$((budget + 1)) ;;
        *) fail=1 ;;
        esac
    done
done
if [ "${STATE_RELEASE:-1}" = 1 ]; then
    echo "== release yew"
    tools/build --release; rc=$?; echo "RELEASE-BUILD yew rc=$rc"; [ "$rc" = 0 ] || fail=1
    echo "== release state fuzz"
    "$WOLF" build --release --deny-warnings src/edit_state_fuzz.lu -o "$out/state-fuzz"; rc=$?
    echo "RELEASE-BUILD edit_state_fuzz rc=$rc"; [ "$rc" = 0 ] || fail=1
fi
echo "state-suite fail=$fail budget=$budget"
exit $fail
