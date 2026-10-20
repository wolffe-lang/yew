#!/bin/bash
# yw04: forksetup NAME  -> ~/lanes/yw04-NAME/yew, a clone of yew at origin/yw04
# (branch yw04-NAME), commit.gpgsign false (local), the pinned toolchain and the
# built oracle copied from the lane tree (~/lanes/yw04/yew).
set -e
n=$1; d=~/lanes/yw04-$n
mkdir -p $d && cd $d
[ -d yew ] || git clone -q https://github.com/wolffe-lang/yew.git yew
cd yew && git fetch -q origin && git checkout -q -B yw04-$n origin/yw04 && git config commit.gpgsign false
[ -d .wolf-bin ] || cp -a ~/lanes/yw04/yew/.wolf-bin .wolf-bin
mkdir -p target && [ -d target/oracle ] || cp -a ~/lanes/yw04/yew/target/oracle target/oracle
echo forksetup: $d/yew at $(git log --oneline -1)
