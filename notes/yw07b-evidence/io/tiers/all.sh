#!/bin/bash
# Inside ctr.sh from the io mirror: the io fork's remaining tier runs in one
# lock hold. Args: "build" rows "FILE TIERS" via env ROWS; then the per-case
# checked machine over CASES, normal and stressed.
W=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf
export WOLF_STD=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/std
out=target/lead/all; mkdir -p $out
while read -r t tiers; do
  [ -z "$t" ] && continue
  name=$(basename "$t" .lu)
  for tier in $tiers; do
    case $tier in
    checked)
      for s in "" 1; do sfx=${s:+.stress}
        env ${s:+YEW_FL_GC_STRESS=1} $W test --deny-warnings --nocapture --no-native-fallback "$t" > $out/$name.checked$sfx.log 2>&1
        echo "$name checked$sfx exit=$? $(grep -E '^wolf test:' $out/$name.checked$sfx.log | tail -1)"
      done ;;
    native|release)
      flag=; [ $tier = release ] && flag=--release
      $W build --deny-warnings $flag "$t" -o $out/$name.$tier > $out/$name.$tier.build.log 2>&1 || { echo "$name $tier BUILD exit=$?"; continue; }
      for s in "" 1; do sfx=${s:+.stress}
        env ${s:+YEW_FL_GC_STRESS=1} $out/$name.$tier > $out/$name.$tier$sfx.log 2>&1
        echo "$name $tier$sfx exit=$? pass-lines=$(grep -c ': PASS\|^PASS' $out/$name.$tier$sfx.log) $(grep -E 'cases run|^PASS' $out/$name.$tier$sfx.log | tail -1)"
      done ;;
    esac
  done
done <<< "$ROWS"
if [ -n "$CASES" ]; then
  export WOLF_BIN=$W LUPIN_BIN=/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/lupin
  python3 -I tools/check-test-cases $CASES > $out/cases.log 2>&1; echo "check-test-cases rc=$? $(tail -1 $out/cases.log)"
  YEW_FL_GC_STRESS=1 python3 -I tools/check-test-cases $CASES > $out/cases.stress.log 2>&1; echo "check-test-cases stress rc=$? $(tail -1 $out/cases.stress.log)"
fi
echo ALL-DONE
