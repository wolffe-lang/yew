#!/bin/bash
# mac-gates.sh FIX: yw06's 81 gated goldens and yw13's ten against FIX's
# release editor on macOS, each by name, as ci.yml runs them (unthrottled).
set -u
fix=$1
lane=/Users/mfwolffe/lanes/yw13
cd "$lane/build-$fix" || exit 4
cases="$(cat tools/goldens-yw06-cases.txt) startup_directory_workspace fuss_drawer_startup_dot fuss_drawer_startup_directory fuss_drawer_enter_tab fuss_drawer_split_h fuss_drawer_split_v fuss_drawer_escape_exact"
cases="$cases $(grep -A 20 "goldens, campaign 11's FUSS drawer and F mode by name" .github/workflows/ci.yml | grep -o 'cases="\$cases [^"]*"' | sed 's/cases="\$cases //; s/"$//' | tr '\n' ' ')"
ok=0; bad=0; n=0
for c in $cases; do
    n=$((n + 1))
    tools/goldens --yew target/release/yew --suite pty --case "$c" > /dev/null 2>&1
    if grep -qx "pty: $c: ok" target/oracle/goldens/pty.log; then ok=$((ok + 1)); else bad=$((bad + 1)); echo "RED $c: $(head -1 target/oracle/goldens/pty.log)"; fi
done
rm -rf target/oracle/sagitta/build/pty-*
echo "COUNTS mac-gates ok=$ok fail=$bad of $n"
