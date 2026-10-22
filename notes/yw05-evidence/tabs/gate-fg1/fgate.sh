#!/bin/bash
# yw05-tabs (in ctr, CPUs 8-11): the fork's final gate at one head.
# fgate.sh TAG -> target/verify/fgate-TAG/ (every step's output) and one
# "step NAME rc N" line a step on stdout, each exit read directly.
t=/home/mfwolffe/lanes/yw05-tabs/yew; b=/home/mfwolffe/lanes/yw05/bin; tag=$1
cd $t; export YEW_ROOT=$PWD
out=target/verify/fgate-$tag; rm -rf $out; mkdir -p $out
step() { local name=$1; shift; local s=$(date +%s); "$@" > $out/$name.log 2>&1; local rc=$?; echo "step $name rc $rc ($(( $(date +%s) - s )) s)"; return 0; }
date -u +%FT%TZ
step check-fmt tools/check-fmt
step build-native tools/build --native
step build-release tools/build --release
step build-demo tools/build-demo
for tier in native release; do
  for cf in c05-tabs-cases c05-s22-cases c03-cases c04-cases; do
    $b/sweep.sh $t target/$tier/yew $b/$cf.txt $tag-$cf-$tier > /dev/null 2>&1
    cp target/verify/sweep-$tag-$cf-$tier.txt $out/
    echo "sweep $cf $tier: $(tail -n 1 target/verify/sweep-$tag-$cf-$tier.txt) red: $(grep ' RED$' target/verify/sweep-$tag-$cf-$tier.txt | cut -d' ' -f1 | tr '\n' ' ')"
  done
done
step renditions-release python3 notes/yw05-evidence/tabs/renditions.py target/release/yew chrome_tabs chrome_tabs_colors_16 chrome_tabs_nocolor chrome_tabs_ascii s57_29_prompt_select_colors_16 s57_29_prompt_select_nocolor s57_29_prompt_select_ascii s41_theme_nocolor_empty s41_theme_nocolor_set s41_theme_term_dumb s41_c_dark_colors_256 s41_c_dark_colors_16 s41_c_light_colors_256
step fuzz-tabs-native tools/run-fuzz-tabs --native --campaign --against-oracle
step fuzz-tabs-release tools/run-fuzz-tabs --campaign --against-oracle
step check-test-native tools/check-test --native
step percase bash -c "XDG_STATE_HOME=$t/target/test-state python3 notes/yw05-evidence/panes/percase.py src/edit_strip_test.lu src/edit_tabs_test.lu"
step check-test-checked tools/check-test
date -u +%FT%TZ
