#!/bin/bash
# pty.sh BIN CASE... — the pick fork's PTY goldens, run in yw06's kasumi
# ctr from the clone root: each case by name through tools/goldens
# against BIN, its verdict line read from target/oracle/goldens/pty.log.
# `--runner` first rebuilds C's pty_runner in this clone (the copied one
# embeds the original tree's paths, Makefile:853).
set -u
if [ "${1:-}" = --runner ]; then
    shift
    make -C target/oracle/sagitta --no-print-directory -B -j2 CC=gcc BUILD=build-gcc build-gcc/pty_runner > /dev/null
    echo "pty_runner rebuilt rc=$?"
fi
bin=$1
shift
ok=0
bad=0
for c in "$@"; do
    tools/goldens --yew "$bin" --suite pty --case "$c" > /dev/null 2>&1
    line=$(grep -a "pty: $c:" target/oracle/goldens/pty.log | tail -1)
    echo "${line:-pty: $c: (no verdict line)}"
    case "$line" in
    *": ok"*) ok=$((ok + 1)) ;;
    *)
        bad=$((bad + 1))
        mkdir -p target/pick-pty
        cp target/oracle/goldens/pty.log "target/pick-pty/$c.log"
        ;;
    esac
done
echo "pty: $ok ok, $bad other against $bin"
