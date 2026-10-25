#!/bin/bash
# One binary (YEW=...) answers the editor API cases headless; inside ctr.sh.
# stdout then stderr per run, as the conformance runner reads them (two
# pipes, tests/fletch/run.c:599-642): C's stdout is a stdio stream flushed
# at exit, the port's is unbuffered, so only a merged sink could tell them apart.
here=$(cd "$(dirname "$0")" && pwd)
run() {
    "$YEW" fl "$@" < /dev/null 2> "$TMPDIR/api-stderr"; local rc=$?
    echo "--- stderr"; cat "$TMPDIR/api-stderr"; echo "exit=$rc"
}
: "${YEW:?the binary under test}"
run "$here/cases.fl"
run --caps none "$here/caps-none.fl"
run /home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/tests/fletch/34-editor.fl
run /home/mfwolffe/lanes/yw07b/scratch-front/oracle/sagitta/tests/fletch/errors/kind_handle.fl
