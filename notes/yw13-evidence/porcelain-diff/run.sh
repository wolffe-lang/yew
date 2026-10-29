#!/bin/bash
# run.sh [WORK]: yw13's porcelain differential. sagitta's parser (cdump.c,
# linked from the oracle build's porcelain.o and arena.o) and the port's
# (src/git_status_dump.lu) read the same `git status --porcelain=v2
# --branch -z` bytes from real repositories built per run under WORK
# (default: $TMPDIR/yw13-porcelain-diff): sagitta's mkrepo.sh fixture and
# its four variants, mkxy.sh's xy (every unmerged XY) and mix (copy,
# intent-to-add, deletions, typechange, a submodule's every state,
# ignored, non-UTF-8 paths), each under five status variants; then every
# prefix of the two richest streams. Every pair of dumps must be equal.
# Run from the yew checkout root inside yw13's container.
set -uo pipefail
root=$(pwd)
oracle=$root/target/oracle/sagitta
work=${1:-${TMPDIR:-/tmp}/yw13-porcelain-diff}
here=$root/notes/yw13-evidence/porcelain-diff
rm -rf "$work"
mkdir -p "$work/bin" "$work/repos" "$work/streams"

gcc -O1 -std=c11 -I "$oracle/src" "$here/cdump.c" \
    "$oracle/build/src/mod/git/porcelain.o" "$oracle/build/src/util/arena.o" \
    -o "$work/bin/cdump" || { echo "run.sh: cdump does not build"; exit 2; }
WOLF_STD=$root/.wolf-bin/std "$root/.wolf-bin/wolf" build --deny-warnings \
    src/git_status_dump.lu -o "$work/bin/pdump" >"$work/pdump.build.log" 2>&1 ||
    { cat "$work/pdump.build.log"; echo "run.sh: pdump does not build"; exit 2; }

sh tests/fixtures/git/mkrepo.sh "$work/repos/fixture" ||
    { echo "run.sh: mkrepo.sh failed"; exit 2; }
sh tests/fixtures/git/mkxy.sh "$work/repos/x" ||
    { echo "run.sh: mkxy.sh failed"; exit 2; }
v=$work/repos/fixture/.fixture-variants
repos="fixture=$work/repos/fixture detached=$v/detached unborn=$v/unborn upstream=$v/upstream seed=$v/upstream-seed xy=$work/repos/x/xy mix=$work/repos/x/mix sub=$work/repos/x/mix/sub"

variants() {
    case $1 in
    plain) echo "" ;;
    all) echo "--untracked-files=all" ;;
    ignored) echo "--untracked-files=all --ignored=matching" ;;
    copies) echo "--untracked-files=all --ignored=traditional" ;;
    none) echo "--untracked-files=no" ;;
    esac
}

compared=0
same=0
for pair in $repos; do
    name=${pair%%=*}
    dir=${pair#*=}
    for var in plain all ignored copies none; do
        renames=-c\ status.renames=true
        [ $var = copies ] && renames=-c\ status.renames=copies
        out=$work/streams/$name.$var
        # shellcheck disable=SC2086
        git -C "$dir" -c core.quotepath=false $renames status --porcelain=v2 \
            --branch -z $(variants $var) >"$out.raw" 2>/dev/null
        "$work/bin/cdump" <"$out.raw" >"$out.c"
        "$work/bin/pdump" <"$out.raw" >"$out.port"
        compared=$((compared + 1))
        if cmp -s "$out.c" "$out.port"; then
            same=$((same + 1))
        else
            echo "DIFF $name.$var"
            diff "$out.c" "$out.port" | head -8 | sed 's/^/    /'
        fi
        printf '%s.%s %s bytes %s entries\n' "$name" "$var" \
            "$(wc -c <"$out.raw" | tr -d ' ')" "$(grep -c '^entry ' "$out.c")" >>"$work/streams.txt"
    done
done
echo "streams: $same of $compared dumps equal"

# Every prefix of the two richest streams: truncation at each byte.
prefixes=0
psame=0
for s in xy.ignored mix.copies; do
    raw=$work/streams/$s.raw
    n=$(wc -c <"$raw" | tr -d ' ')
    i=0
    while [ $i -le "$n" ]; do
        head -c "$i" "$raw" >"$work/prefix.raw"
        "$work/bin/cdump" <"$work/prefix.raw" >"$work/prefix.c"
        "$work/bin/pdump" <"$work/prefix.raw" >"$work/prefix.port"
        prefixes=$((prefixes + 1))
        if cmp -s "$work/prefix.c" "$work/prefix.port"; then
            psame=$((psame + 1))
        else
            echo "DIFF $s prefix $i"
            diff "$work/prefix.c" "$work/prefix.port" | head -6 | sed 's/^/    /'
        fi
        i=$((i + 1))
    done
done
echo "prefixes: $psame of $prefixes dumps equal"
cat "$work/streams.txt"
[ $same = $compared ] && [ $psame = $prefixes ]
