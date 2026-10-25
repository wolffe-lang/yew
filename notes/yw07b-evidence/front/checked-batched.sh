#!/bin/bash
# Detached tier runs over a frozen tree: for each test entry, the native and
# release tiers plain and stressed in one container session, then strict
# checked per case in batches of BATCH cases per container session, plain
# then YEW_FL_GC_STRESS=1, so the cores lock is held a few minutes at a time.
#   setsid -f bash checked-batched.sh TREE OUTDIR BATCH FILE...
# Writes OUTDIR/pid, OUTDIR/log (verdict lines), OUTDIR/exit (when done).
set -u
tree=$1; out=$2; batch=$3; shift 3
files=("$@")
phases=${PHASES:-tiers plain stress}
mkdir -p "$out"; echo $$ > "$out/pid"; : > "$out/log"; rm -f "$out/exit"
cd "$tree"
ctr=/home/mfwolffe/lanes/yw07b/front/notes/yw07b-evidence/lane/ctr.sh
tfiles=("${files[@]}")
case " $phases " in *" tiers "*) ;; *) tfiles=() ;; esac
for file in "${tfiles[@]}"; do
  "$ctr" . bash -c "notes/yw07b-evidence/front/tiers.sh $file native release native-stress release-stress" 2>&1 \
    | grep -E '^(native|release)' | sed "s|^|$file |" >> "$out/log"
done
modes=()
case " $phases " in *" plain "*) modes+=("") ;; esac
case " $phases " in *" stress "*) modes+=(--stress) ;; esac
for mode in "${modes[@]}"; do
  for file in "${files[@]}"; do
    names=$(python3 - "$file" <<'P'
import re, sys
s = open(sys.argv[1]).read()
p, m = s[:s.index('fn main()')], s[s.index('fn main()'):]
d = re.findall(r'^fn (\w+)\(\)', p, re.M)
print(' '.join(sorted((n for n in d if re.search(r'\b' + n + r'\(\)', m)),
                      key=lambda n: re.search(r'\b' + n + r'\(\)', m).start())))
P
)
    set -- $names
    while [ $# -gt 0 ]; do
      chunk=""
      for _ in $(seq 1 "$batch"); do [ $# -gt 0 ] && { chunk="$chunk $1"; shift; }; done
      "$ctr" . python3 notes/yw07b-evidence/front/cases.py "$file" $mode --only $chunk 2>&1 \
        | grep -E ' (PASS|FAIL|UNSUPPORTED) -?[0-9]+$' >> "$out/log"
    done
  done
done
echo done > "$out/exit"
