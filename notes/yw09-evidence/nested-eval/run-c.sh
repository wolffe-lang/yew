#!/bin/sh
# R-yw09-6's witness, C's half: build witness.c against the oracle's own
# objects (tools/oracle's build, MODULES=lsp ai fuss plugins as
# sagitta's Makefile:100 defaults them) and run it. Inside the lane's
# container, from the yew root, under the scratch HOME/XDG_* and
# TMPDIR the container sets.
#
#   sh notes/yw09-evidence/nested-eval/run-c.sh [SAGITTA_TREE]
set -eu
tree=${1:-target/oracle/sagitta}
build=
for d in "$tree"/build-*; do
    if [ -f "$d/src/main.o" ]; then build=$d; break; fi
done
if [ -z "$build" ]; then
    echo "run-c: no oracle build under $tree (run tools/oracle first)" >&2
    exit 2
fi
out=target/yw09/nested-eval
mkdir -p "$out"
objs=$(find "$build/src" -name '*.o' ! -path "$build/src/main.o" | sort)
gcc -std=c11 -O1 -g -I"$tree/src" \
    -DYEW_WITH_LSP=1 -DYEW_WITH_AI=1 -DYEW_WITH_FUSS=1 \
    -DYEW_WITH_PLUGINS=1 -DYEW_EMBED_RUNTIME=0 \
    -DYEW_RUNTIME_DIR_DEFAULT='"/usr/local/share/yew/runtime"' \
    notes/yw09-evidence/nested-eval/witness.c $objs -lm -o "$out/witness-c"
YEW_RUNTIME_DIR="$tree/runtime" "$out/witness-c"
