#!/bin/bash
# Run inside yw09's locked container. A JSON "unsupported" is never a pass.
set -euo pipefail
root=$1
case "$root" in /home/mfwolffe/lanes/yw09/*) ;; *) exit 2;; esac
cd "$root"
export WOLF_STD="$root/.wolf-bin/std"
out="$root/notes/yw09-evidence/checkpoint"
mkdir -p "$out" target/yw09
for suite in fl_handle_table_test fl_host_test; do
    for tier in native release; do
        flags=()
        if test "$tier" = release; then flags=(--release); fi
        .wolf-bin/wolf build --deny-warnings "${flags[@]}" "src/$suite.lu" -o "target/yw09/$suite-$tier"
        "target/yw09/$suite-$tier"
        YEW_FL_GC_STRESS=1 "target/yw09/$suite-$tier"
    done
    .wolf-bin/wolf conform-run --checked --json "src/$suite.lu" > "$out/$suite.json"
    python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["verdict"]=="exit(0)", d; print(sys.argv[1], d["verdict"])' "$out/$suite.json"
done
for variant in main control; do
    for tier in native release; do
        flags=()
        if test "$tier" = release; then flags=(--release); fi
        .wolf-bin/wolf build --deny-warnings "${flags[@]}" "notes/yw09-evidence/host-seam/$variant.lu" -o "target/yw09/g58-$variant-$tier"
        "target/yw09/g58-$variant-$tier"
    done
    .wolf-bin/wolf conform-run --checked --json "notes/yw09-evidence/host-seam/$variant.lu" > "$out/g58-$variant.json"
done
python3 -I -c 'import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); assert a["verdict"]=="unsupported" and a["x-unsupported-construct"]=="trait dispatch on a non-nominal receiver",a; assert b["verdict"]=="exit(0)",b; print("G58: nested argument refused, bound control passes")' "$out/g58-main.json" "$out/g58-control.json"
