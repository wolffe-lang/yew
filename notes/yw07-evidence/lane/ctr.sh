#!/bin/bash
# yw05's ctr pattern, restricted to yw07 and cores 8-11.
# Call from kasumi; the lock covers the entire container lifetime.
set -euo pipefail
lane="$HOME/lanes/yw07"
d=$(cd "$1" && pwd); shift
case "$d" in "$lane"/*) ;; *) echo "ctr: not a yw07 directory" >&2; exit 2;; esac
mem=${CTR_MEM:-8g}
case "$mem" in 8g|16g) ;; *) echo "ctr: cap must be 8g or the approved 16g measurement cap" >&2; exit 2;; esac
s="$lane/scratch-$(basename "$d")"
mkdir -p "$s/home" "$s/config" "$s/state" "$s/cache" "$s/tmp"
exec flock "$HOME/lanes/kasumi-cores-8-11.lock" podman run --rm --network none \
    --userns=keep-id --init --pids-limit 4096 --ulimit core=0 --memory "$mem" \
    -v /usr:/usr:ro -v /var/lib/pacman:/var/lib/pacman:ro \
    -v "$lane:$lane" -w "$d" \
    -e HOME="$s/home" -e XDG_CONFIG_HOME="$s/config" \
    -e XDG_STATE_HOME="$s/state" -e XDG_CACHE_HOME="$s/cache" \
    -e TMPDIR="$s/tmp" -e YEW_RUNTIME_DIR="$d/runtime" \
    -e TERM=xterm-256color -e CARGO_INCREMENTAL=0 \
    docker.io/library/archlinux:base-devel taskset -c 8-11 bash -c 'ulimit -c 0; exec "$@"' bash "$@"
