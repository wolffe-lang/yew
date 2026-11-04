#!/usr/bin/env bash
# yew#98's row: the G50 witness under the pinned wolf and under a wolf past
# wolf-lang#998 (a246580b, the fix for #948), which refuses a plain push of
# a list-holding value into an outer list from inside a region (E1010).
#
#   g50-newer-wolf.sh PINNED_WOLF NEWER_WOLF
#
# Run from the repository root. The witness is yw07b's
# notes/yw07b-evidence/stdlib/scratch-once/main.lu: `fl_str_new` and
# `fl_list_new` inside `region native_scratch { }` with the VM outside,
# which reaches `fl_gc_alloc`'s pushes of a fresh slot. It is staged as the
# fuzz tools stage their drivers (the entry beside src's modules) in two
# forms: this tree's (`push(copy fl_empty_slot())`) and trunk's before
# yew#98 (the copy taken out). Each form is built native with each wolf and
# run. The row holds when the newer wolf refuses trunk's form with E1010
# naming src's fl/gc.lu and builds this tree's, and this tree's form runs
# green under both; the pinned wolf's verdict on trunk's form is reported
# (native read a freed arena there: #948's exit 139). Prints
# `FAIL g50_witness_accepted_past_948` otherwise.
set -u
pinned=$1
new=$2
root=$(pwd)
scratch=${TMPDIR:-/tmp}/yw14-g50-$$
rm -rf "$scratch"
mkdir -p "$scratch"
want="native scratch constructors survive outside region and collection"
echo "g50: pinned: $("$pinned" --version | head -1)"
echo "g50: newer:  $("$new" --version | head -1)"
ok=1
for form in fixed trunk; do
    st=$scratch/$form
    mkdir -p "$st"
    cp "$root/notes/yw07b-evidence/stdlib/scratch-once/main.lu" "$st/main.lu"
    for d in "$root"/src/*/; do
        m=$(basename "$d")
        cp -R "$d" "$st/$m"
        find "$st/$m" -maxdepth 1 -name '*_test.lu' -exec rm -f {} +
    done
    if [ "$form" = trunk ]; then
        sed -i.orig 's/push(copy fl_empty_slot())/push(fl_empty_slot())/' "$st/fl/gc.lu"
        rm -f "$st/fl/gc.lu.orig"
    fi
    echo "g50: $form: $(grep -c 'push(copy fl_empty_slot())' "$st/fl/gc.lu") copied push(es) in fl/gc.lu"
    for which in pinned newer; do
        w=$pinned
        [ "$which" = newer ] && w=$new
        "$w" build --deny-warnings "$st/main.lu" -o "$scratch/$form-$which" >"$scratch/$form-$which.log" 2>&1
        b=$?
        e=$(grep -c 'E1010' "$scratch/$form-$which.log" || true)
        r=-
        line=
        if [ "$b" = 0 ]; then
            "$scratch/$form-$which" >"$scratch/$form-$which.out" 2>&1
            r=$?
            line=$(head -1 "$scratch/$form-$which.out")
        fi
        echo "g50: $form under $which wolf: build exit=$b E1010 lines=$e run exit=$r ${line:+output=\"$line\"}"
        grep -m2 -A3 'E1010' "$scratch/$form-$which.log" | sed 's/^/g50:   /'
        case "$form-$which" in
        fixed-*)
            { [ "$b" = 0 ] && [ "$r" = 0 ] && [ "$line" = "$want" ]; } || ok=0 ;;
        trunk-newer)
            { [ "$b" != 0 ] && [ "$e" != 0 ] && grep -q 'fl/gc.lu' "$scratch/$form-$which.log"; } || ok=0 ;;
        esac
    done
done
rm -rf "$scratch"
if [ "$ok" != 1 ]; then
    echo "FAIL g50_witness_accepted_past_948"
    exit 1
fi
echo "g50_witness_accepted_past_948: ok (trunk's form refused with E1010 past #998; the copy builds and runs on both)"
