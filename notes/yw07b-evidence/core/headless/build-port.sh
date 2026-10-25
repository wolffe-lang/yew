#!/bin/bash
set -euo pipefail
root=/home/mfwolffe/lanes/yw07b/core
stage="$root/target/headless-driver"
mkdir -p "$stage"
cp -R "$root/src/." "$stage/"
find "$stage" -maxdepth 1 -type f -name '*.lu' -delete
find "$stage" -type f -name '*_test.lu' -delete
cp "$root/notes/yw07b-evidence/core/headless/main.lu" "$stage/main.lu"
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
case ${1:---release} in --release) tier=--release ;; --native) tier= ;; *) exit 2 ;; esac
/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf build $tier --deny-warnings "$stage/main.lu" -o "$root/target/headless-driver-bin"
