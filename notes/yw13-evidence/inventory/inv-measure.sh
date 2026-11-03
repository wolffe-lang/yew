#!/bin/bash
# yw13 item 1: each FUSS-block case on the C oracle, twice: with the
# shipped runtime (control) and with a runtime whose syntax/ is empty
# (highlighting off). A case green on both does not depend on highlighting;
# a case green on the control and red without syntax does, and its diff
# is kept to say on which cells.
set -uo pipefail
lane=/mnt/steamlib/lanes/yw13
root=$lane/yew
out=$lane/inv
tree=$root/target/oracle/sagitta
cd "$root"
mkdir -p "$out"
rm -rf "$out/runtime-nosyn" "$out/control" "$out/nosyn"
mkdir -p "$out/control" "$out/nosyn"
cp -R "$tree/runtime" "$out/runtime-nosyn"
rm -rf "$out/runtime-nosyn/syntax"
mkdir -p "$out/runtime-nosyn/syntax"
ls "$tree/runtime/syntax" | wc -l | sed 's/^/syntax files removed: /'
# The registry's case table holds two #if YEW_WITH_FUSS blocks: the
# startup one (startup_directory_workspace) and the FUSS block.
python3 -I - "$tree/tests/pty/registry.c" > "$out/cases.txt" <<'PY'
import re, sys
src = open(sys.argv[1]).read()
table = src[src.index("const PtyCase yew_pty_cases[] = {"):]
table = table[:table.index("\n};")]
names, stack = [], []
for line in table.splitlines():
    s = line.strip()
    if s.startswith("#if"):
        stack.append("YEW_WITH_FUSS" in s)
    elif s.startswith("#else"):
        stack[-1] = False
    elif s.startswith("#endif"):
        stack.pop()
    else:
        m = re.match(r"C\(([a-z0-9_]+),", s)
        if m and stack and stack[-1]:
            names.append(m.group(1))
print("\n".join(names))
PY
wc -l < "$out/cases.txt" | sed 's/^/cases: /'
for c in $(cat "$out/cases.txt"); do
    tools/goldens --yew "$tree/build/yew" --suite pty --case "$c" > "$out/control/$c.log" 2>&1
    rc1=$?
    cp target/oracle/goldens/pty.log "$out/control/$c.pty.log"
    YEW_PTY_RUNTIME_DIR="$out/runtime-nosyn" tools/goldens --yew "$tree/build/yew" --suite pty --case "$c" > "$out/nosyn/$c.log" 2>&1
    rc2=$?
    cp target/oracle/goldens/pty.log "$out/nosyn/$c.pty.log"
    printf 'INV %s control=%s nosyn=%s\n' "$c" "$rc1" "$rc2"
done
echo "COUNTS inventory cases=$(wc -l < "$out/cases.txt")"
