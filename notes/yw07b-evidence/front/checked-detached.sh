#!/bin/bash
# Per-case strict checked runs of one test entry, one container per case so
# the cores lock is released between cases. Detached use:
#   setsid -f bash checked-detached.sh FILE OUTDIR [--stress]
# Writes OUTDIR/pid, OUTDIR/log (one verdict line per case), OUTDIR/exit.
set -u
repo=${REPO:-/home/mfwolffe/lanes/yw07b/front}
file=$1; out=$2; mode=${3:-}
mkdir -p "$out"; echo $$ > "$out/pid"; : > "$out/log"; rm -f "$out/exit"
cd "$repo"
names=$(python3 - "$file" <<'P'
import re, sys
s = open(sys.argv[1]).read()
p, m = s[:s.index('fn main()')], s[s.index('fn main()'):]
d = re.findall(r'^fn (\w+)\(\)', p, re.M)
print(' '.join(sorted((n for n in d if re.search(r'\b' + n + r'\(\)', m)),
                      key=lambda n: re.search(r'\b' + n + r'\(\)', m).start())))
P
)
for n in $names; do
  notes/yw07b-evidence/lane/ctr.sh . python3 notes/yw07b-evidence/front/cases.py "$file" $mode --only "$n" 2>&1 | grep -v ' PASS, ' >> "$out/log"
done
grep -c ' PASS ' "$out/log" > /dev/null
echo done > "$out/exit"
