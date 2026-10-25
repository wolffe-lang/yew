#!/bin/bash
# Build the errno witness tree; prints the directory. Run inside ctr.sh.
set -euo pipefail
d=${1:?dir}
rm -rf "$d"; mkdir -p "$d"
cd "$d"
printf x > file
mkdir full; printf x > full/x
printf x > noperm; chmod 000 noperm
ln -s loop loop
mkdir ro; printf k > ro/k; mkdir ro/e; chmod 555 ro
echo "$d"
