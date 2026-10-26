#!/bin/bash
# yw05 ctr pattern, with yw07's lock and no host /usr overlay (yew#60).
set -euo pipefail
lane="$HOME/lanes/yw08"
d=$(cd "$1" && pwd); shift
case "$d" in "$lane"/*) ;; *) echo 'ctr: not a yw08 directory' >&2; exit 2;; esac
s="$lane/scratch-$(basename "$d")"
mkdir -p "$s/home" "$s/config" "$s/state" "$s/cache" "$s/tmp"
exec flock "$HOME/lanes/kasumi-cores-12-15.lock" podman run --rm --network none \
  --userns=keep-id --init --pids-limit 4096 --ulimit core=0 --memory 8g \
  -v "$lane:$lane" -w "$d" \
  -e HOME="$s/home" -e XDG_CONFIG_HOME="$s/config" \
  -e XDG_STATE_HOME="$s/state" -e XDG_CACHE_HOME="$s/cache" \
  -e TMPDIR="$s/tmp" -e YEW_RUNTIME_DIR="$d/runtime" \
  -e TERM=xterm-256color -e CARGO_INCREMENTAL=0 \
  ${YEW_FL_GC_STRESS:+-e YEW_FL_GC_STRESS="$YEW_FL_GC_STRESS"} \
  localhost/px13-ubuntu taskset -c 12-15 bash -c 'ulimit -c 0; exec "$@"' bash "$@"
