#!/bin/bash
# The glob witness tree; run inside ctr.sh. Names include bytes that are not UTF-8.
set -euo pipefail
d=${1:?dir}
rm -rf "$d"; mkdir -p "$d"; cd "$d"
printf a > a.txt; printf b > b.md; printf h > .hidden; printf c > 'c]d'; printf s > '*star'
printf q > 'q[x'; printf z > zz.txt; printf u > a-b; printf u > a_b
mkdir -p sub/deep sub/.dot zz; printf x > sub/b.txt; printf x > sub/deep/c.txt; printf x > sub/.dot/h.txt
printf x > zz/q.txt
ln -s "$d" sub/loop
ln -s nowhere dangling
mkdir locked; printf x > locked/in.txt; chmod 000 locked
printf x > "$(printf 'bad\377.txt')"
mkdir "$(printf 'bad\376dir')"; printf x > "$(printf 'bad\376dir')/in.txt"
echo "$d"
