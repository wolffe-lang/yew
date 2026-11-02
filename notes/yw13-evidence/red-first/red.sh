#!/bin/bash
# red.sh: yw13's plants and red-first mutations, in yw13's container.
# Each variant is the clone's src/ copied under $lane/var/<name>/src with
# one fault applied (a plant's patch, or a one-line python edit); the named
# test is built from that copy and run from the clone's root (its
# fixtures). A variant is RED when its test exits nonzero; every line the
# test prints with RED, SKIP or a trap is kept. Prints END lines.
set -u
here=$(cd "$(dirname "$0")" && pwd)
lane=/home/mfwolffe/lanes/yw13
root=$lane/yew
cd "$root"
export WOLF_STD=$root/.wolf-bin/std YEW_LOG=/dev/null
mkdir -p "$lane/var" "$lane/red"
red=0
variant() {
    local name=$1 kind=$2 arg=$3
    rm -rf "$lane/var/$name"
    mkdir -p "$lane/var/$name"
    cp -r "$root/src" "$lane/var/$name/src"
    if [ "$kind" = patch ]; then
        # The container has git, not patch(1); `git apply` works outside a repository.
        (cd "$lane/var/$name" && git apply -p1 "$here/$arg") || { echo "END variant $name apply=FAIL"; red=$((red + 1)); return 1; }
    else
        python3 -I -c "$arg" "$lane/var/$name/src" || { echo "END variant $name apply=FAIL"; red=$((red + 1)); return 1; }
    fi
    echo "APPLIED $name"
}
probe() {
    local name=$1 test=$2 case=$3
    local bin=$lane/var/$name/$test
    if ! .wolf-bin/wolf build --deny-warnings "$lane/var/$name/src/$test.lu" -o "$bin" > "$lane/red/$name-$test.build.log" 2>&1; then
        echo "END variant $name test $test build=FAIL (a plant must compile)"; tail -5 "$lane/red/$name-$test.build.log"; red=$((red + 1)); return
    fi
    if [ -n "$case" ]; then YEW_PICK_CASE=$case "$bin" > "$lane/red/$name-$test.log" 2>&1; else "$bin" > "$lane/red/$name-$test.log" 2>&1; fi
    local rc=$?
    grep -E "RED|SKIP|wolf-trap|^  at " "$lane/red/$name-$test.log" | sort -u | head -8
    if [ $rc -ne 0 ]; then
        echo "END variant $name test $test case=${case:-all} exit=$rc verdict=RED"
    else
        echo "END variant $name test $test case=${case:-all} exit=0 verdict=GREEN (the fault was not caught)"; red=$((red + 1))
    fi
}
# The three plants (contract item 5).
variant plant-porcelain patch plant-porcelain.patch && {
    probe plant-porcelain git_porcelain_test ""
    probe plant-porcelain edit_gitlayer_test 0
    probe plant-porcelain edit_gitlayer_test 7
}
variant plant-argv-join patch plant-argv-join.patch && probe plant-argv-join edit_fusscommands_test 2
variant plant-collapse py '
import sys
p = sys.argv[1] + "/edit/fussmode.lu"
s = open(p).read()
old = "    let _ = fuss_open_files_refresh(mut ed)\n    fuss_apply_effective(mut ed)\n    if fuss_row(ed) < 0"
assert old in s
s = s.replace(old, "    let _ = fuss_open_files_refresh(mut ed)\n    // yw13-plant-collapse: the rebuild drops the open memories.\n    if fuss_row(ed) < 0")
open(p, "w").write(s)
' && probe plant-collapse edit_fussrefresh_test 0
# Red-first mutations of the code yw13's new rows cover.
variant mut-literal-env py '
import sys
p = sys.argv[1] + "/edit/git.lu"
s = open(p).read()
old = "        (mut rows).push(\"GIT_LITERAL_PATHSPECS=1\")\n"
assert old in s
open(p, "w").write(s.replace(old, ""))
' && probe mut-literal-env edit_gitlayer_test 5
variant mut-lstat-kind py '
import sys
p = sys.argv[1] + "/edit/fusscmds.lu"
s = open(p).read()
old = "dir = st[0] == 1"
assert old in s
open(p, "w").write(s.replace(old, "dir = st[2] & 61440 == 16384"))
' && probe mut-lstat-kind edit_fusscommands_test 23
variant mut-symwalk py '
import sys
p = sys.argv[1] + "/edit/symwalk.lu"
s = open(p).read()
old = "if !sw_executable_in_path(\"git\") {"
assert old in s
open(p, "w").write(s.replace(old, "if sw_executable_in_path(\"git\") {"))
' && { probe mut-symwalk edit_symwalk_test 0; probe mut-symwalk edit_symwalk_test 1; }
variant mut-fence py '
import sys
p = sys.argv[1] + "/edit/panel.lu"
s = open(p).read()
old = "    len == 3 && b[lo] as int == 96 && b[lo + 1] as int == 96 && b[lo + 2] as int == 96\n"
assert old in s
open(p, "w").write(s.replace(old, "    len < 0\n"))
' && probe mut-fence edit_panel_test 15
variant mut-selection py '
import sys
p = sys.argv[1] + "/edit/fussmode.lu"
s = open(p).read()
old = "    if fuss_row(ed) < 0 && ed.fuss.tree.items.len != 0 {\n        fuss_select_row(mut ed, 0)\n    }\n    ed.fuss.scroll = 0\n    fuss_damage(mut ed)\n}"
assert old in s
open(p, "w").write(s.replace(old, "    if ed.fuss.tree.items.len != 0 {\n        fuss_select_row(mut ed, 0)\n    }\n    ed.fuss.scroll = 0\n    fuss_damage(mut ed)\n}"))
' && probe mut-selection edit_fussrefresh_test 1
rm -rf "$lane/var"
echo "COUNTS red-first not-caught=$red"
[ $red -eq 0 ]
