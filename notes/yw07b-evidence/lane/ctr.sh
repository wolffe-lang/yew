#!/bin/bash
# yw05 ctr pattern, with yw07's lock and no host /usr overlay (yew#60).
set -euo pipefail
lane="$HOME/lanes/yw07b"
d=$(cd "$1" && pwd); shift
case "$d" in "$lane"/*) ;; *) echo 'ctr: not a yw07b directory' >&2; exit 2;; esac
s="$lane/scratch-$(basename "$d")"
mkdir -p "$s/home" "$s/config" "$s/state" "$s/cache" "$s/tmp"
exec flock "$HOME/lanes/kasumi-cores-8-11.lock" podman run --rm --network none \
  --userns=keep-id --init --pids-limit 4096 --ulimit core=0 --memory 8g \
  -v "$lane:$lane" -w "$d" \
  -e HOME="$s/home" -e XDG_CONFIG_HOME="$s/config" \
  -e XDG_STATE_HOME="$s/state" -e XDG_CACHE_HOME="$s/cache" \
  -e TMPDIR="$s/tmp" -e YEW_RUNTIME_DIR="$d/runtime" \
  -e TERM=xterm-256color -e CARGO_INCREMENTAL=0 \
  localhost/px13-ubuntu taskset -c 8-11 bash -c 'ulimit -c 0; exec "$@"' bash "$@"
