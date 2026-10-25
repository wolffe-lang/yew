#!/bin/bash
# Run one test entry on the three tiers, plain and under YEW_FL_GC_STRESS=1.
# Usage (inside ctr.sh, from the repo root): tiers.sh FILE [TIERS...]
# TIERS default: checked native release checked-stress native-stress release-stress
set -uo pipefail
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
wolf=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
file=$1; shift
tiers=${*:-checked native release checked-stress native-stress release-stress}
name=$(basename "$file" .lu)
out=target/front/tiers
mkdir -p "$out"
status=0
built_native=0
built_release=0
for t in $tiers; do
  stress=
  case $t in *-stress) stress=1;; esac
  base=${t%-stress}
  start=$(date +%s%N)
  case $base in
    checked)
      if [ -n "$stress" ]; then
        YEW_FL_GC_STRESS=1 "$wolf" test --deny-warnings --nocapture --no-native-fallback "$file" > "$out/$name.$t.log" 2>&1
      else
        "$wolf" test --deny-warnings --nocapture --no-native-fallback "$file" > "$out/$name.$t.log" 2>&1
      fi
      rc=$?
      if [ $rc -ne 0 ] && grep -q 'budget exhausted' "$out/$name.$t.log"; then rc=UNSUPPORTED; fi;;
    native|release)
      bin="$out/$name-$base"
      flag=
      [ "$base" = release ] && flag=--release
      if { [ "$base" = native ] && [ $built_native = 0 ]; } || { [ "$base" = release ] && [ $built_release = 0 ]; }; then
        if ! "$wolf" build $flag --deny-warnings "$file" -o "$bin" > "$out/$name.$base.build.log" 2>&1; then
          echo "$t BUILD-FAIL"; cat "$out/$name.$base.build.log" | head -40; status=1; continue
        fi
        [ "$base" = native ] && built_native=1
        [ "$base" = release ] && built_release=1
      fi
      if [ -n "$stress" ]; then
        YEW_FL_GC_STRESS=1 "$bin" > "$out/$name.$t.log" 2>&1
      else
        "$bin" > "$out/$name.$t.log" 2>&1
      fi
      rc=$?;;
  esac
  end=$(date +%s%N)
  ms=$(( (end - start) / 1000000 ))
  last=$(tail -1 "$out/$name.$t.log" | cut -c1-160)
  echo "$t exit=$rc ${ms}ms :: $last"
  if [ "$rc" != 0 ]; then status=1; tail -30 "$out/$name.$t.log"; fi
done
exit $status
