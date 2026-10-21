#!/bin/bash
# yw04: ctr DIR CMD...  run CMD (bash -c) in a throwaway archlinux:base-devel
# podman container (RULES 5: every signal-bearing run), DIR mounted at its own
# path, no network, under taskset -c 0-3, with a scratch HOME/XDG_*/YEW_LOG
# (yew#11) under DIR/../scratch-<basename>.
d=$(cd "$1" && pwd); shift
s=$(dirname "$d")/scratch-$(basename "$d")
mkdir -p "$s/home" "$s/state" "$s/config" "$s/cache"
exec podman run --rm --network none --userns=keep-id --pids-limit 4096 --ulimit core=0 --memory ${CTR_MEM:-6g}   -v "$d:$d" -v "$s:$s" -v $HOME/lanes/yw04/bin:$HOME/lanes/yw04/bin:ro -w "$d"   -e HOME="$s/home" -e XDG_STATE_HOME="$s/state" -e XDG_CONFIG_HOME="$s/config"   -e XDG_CACHE_HOME="$s/cache" -e YEW_LOG="$s/yew.log" -e TERM=xterm-256color   docker.io/library/archlinux:base-devel taskset -c ${CTR_CPUS:-0-3} bash -c "$*"
