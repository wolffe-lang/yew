#!/usr/bin/env bash
# yw05-tail regression gate. Run inside ctr, taskset 8-11, 8g, core=0.
# C: tests/perf/perf_cmdcomp.c:247-304; tests/perf/perf_latency.c:21-22.
set -eu
export CARGO_INCREMENTAL=0
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
v=$YEW_ROOT/target/yw06-tail-verify
mkdir -p "$v"
date -u +%FT%TZ
git rev-parse HEAD
sha256sum tools/perf-cmdcomp/main.lu tools/run-perf-panes-tabs notes/yw06-evidence/tail/verify.sh notes/yw06-evidence/tail/keys-test.py
printf 'affinity='; taskset -pc $$
printf 'core_limit='; ulimit -c
printf 'HOME=%s\nXDG_STATE_HOME=%s\n' "$HOME" "$XDG_STATE_HOME"
python3 -I notes/yw06-evidence/tail/keys-test.py "$YEW_ROOT" "$v/keys"
for kind in plant fixed; do
  d=$v/$kind
  rm -rf "$d"
  mkdir -p "$d"
  cp tools/perf-cmdcomp/main.lu "$d/main.lu"
  for m in util unicode term text search ws edit; do
    cp -R "src/$m" "$d/$m"
    rm -f "$d/$m/"*_test.lu
  done
  if [ "$kind" = plant ]; then
    python3 -I - "$d/main.lu" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1]); text = p.read_text()
old = 'mut menu, mut ed.dbuf, edit.rect(0, 0, 100, 23), style)'
assert text.count(old) == 1
p.write_text(text.replace(old, 'mut menu, edit.rect(0, 0, 100, 23), style)'))
PY
  fi
  set +e
  "$WOLF" build --release --deny-warnings "$d/main.lu" -o "$d/perf-cmdcomp" > "$v/build-$kind.log" 2>&1
  rc=$?
  set -e
  echo "perf-cmdcomp $kind: build exit=$rc"
  if [ "$kind" = plant ]; then
    test "$rc" -eq 2
    grep -m1 'error\[' "$v/build-$kind.log"
    grep -Fq 'takes 6 arguments, but this call passes 5' "$v/build-$kind.log"
  else
    test "$rc" -eq 0
  fi
done
python3 -I - "$v/fixture" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1]); p.mkdir(exist_ok=True)
for i in range(10000): (p / f'entry{i:05d}').touch()
PY
"$v/fixed/perf-cmdcomp" "$v/fixture" --trials 3 > "$v/smoke.log" 2>&1
cat "$v/smoke.log"
grep -q 'entries=10000 keys=18 trials=3.*opendirs=1 rows=500' "$v/smoke.log"
echo 'yw05-tail local module gate: GREEN; 2 plants seen red, 2 fixes green; 0 SKIP'
date -u +%FT%TZ
