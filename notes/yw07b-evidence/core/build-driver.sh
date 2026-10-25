#!/bin/bash
set -euo pipefail
root=/home/mfwolffe/lanes/yw07b/core
stage="$root/target/core-driver"
mkdir -p "$stage"
cp "$root/notes/yw07b-evidence/core/driver/main.lu" "$stage/main.lu"
for m in fl util unicode; do mkdir -p "$stage/$m"; cp "$root/src/$m/"*.lu "$stage/$m/"; done
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf build --release --deny-warnings "$stage/main.lu" -o "$root/target/core-driver-bin"
