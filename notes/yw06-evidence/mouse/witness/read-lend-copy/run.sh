#!/bin/bash
# Run from the repository root inside the lane's container:
#   bash notes/yw06-evidence/mouse/witness/read-lend-copy/run.sh
# Builds the witness on both tiers, runs each, and prints each caller's
# stack frame (`sub $N,%rsp`) from the binary.
set -u
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
W=notes/yw06-evidence/mouse/witness/read-lend-copy
mkdir -p target/mouse-witness
for tier in native release; do
    flag=""
    [ "$tier" = release ] && flag=--release
    # shellcheck disable=SC2086
    "$WOLF" build $flag --deny-warnings "$W/main.lu" -o "target/mouse-witness/rlc-$tier" 2>&1
    echo "build $tier exit=$?"
    [ -x "target/mouse-witness/rlc-$tier" ] || continue
    taskset -c 8-11 "target/mouse-witness/rlc-$tier" | sed "s/^/$tier: /"
    for f in step_read step_mut step_field; do
        fr=$(objdump -d --no-show-raw-insn "target/mouse-witness/rlc-$tier" | awk "/<[^>]*$f[^>]*>:/,/^\$/" | grep -o 'sub \+\$0x[0-9a-f]*,%rsp' | head -1)
        echo "$tier: $f frame: ${fr:-none}"
    done
done
rm -rf target/mouse-witness
