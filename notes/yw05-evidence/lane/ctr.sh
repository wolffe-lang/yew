#!/bin/bash
# yw05: ctr DIR CMD...  run CMD (bash -c) in a throwaway archlinux:base-devel
# podman container (RULES 5), DIR mounted at its own path, under taskset
# (CTR_CPUS, default 0-3), ulimit -c 0, a memory cap (CTR_MEM, default 8g),
# no network unless CTR_NET=1, the host's /usr and pacman db read-only
# (the host's clang/LLVM for the release tier; nothing installed), with a
# scratch HOME/XDG_* under DIR/../scratch-<basename> (yew#11); no YEW_LOG:
# it moves the log the PTY harness and C's unit suite read (osc52_reply,
# plug_trust_every_truncation), and XDG_STATE_HOME already keeps it here.
# yw04's ctr with the yw05 paths, the /usr mount and the knobs.
d=$(cd "$1" && pwd); shift
s=$(dirname "$d")/scratch-$(basename "$d")
mkdir -p "$s/home" "$s/state" "$s/config" "$s/cache" "$s/tmp"
net="--network none"; [ "${CTR_NET:-0}" = 1 ] && net=""
exec podman run --rm $net --userns=keep-id --init --pids-limit 4096 --ulimit core=0 --memory ${CTR_MEM:-8g} \
  -v /usr:/usr:ro -v /var/lib/pacman:/var/lib/pacman:ro \
  -v "$d:$d" -v "$s:$s" -v $HOME/lanes/yw05/bin:$HOME/lanes/yw05/bin:ro -w "$d" \
  -e HOME="$s/home" -e XDG_STATE_HOME="$s/state" -e XDG_CONFIG_HOME="$s/config" \
  -e XDG_CACHE_HOME="$s/cache" -e TMPDIR="$s/tmp" -e TERM=xterm-256color \
  docker.io/library/archlinux:base-devel taskset -c ${CTR_CPUS:-0-3} bash -c "ulimit -c 0; $*"
