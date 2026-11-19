# yw26 — the script suite keeps its evidence

_A fix to the goldens harness, not to the editor. On a hosted macOS
runner `tools/goldens-selftest` once went red on the oracle itself:
`script: pass=92 fail=1`, `FAIL 07_functions (exit 126)` (trunk's push
run at `5d8e6ea`, run 44441894655). The same commit passed 93 of 93 in
run 44322145309._

## Prediction

Written before the first change (2026-11-19, base trunk `feef667`;
`sagitta.pin` `9ace98c2`).

### What exit 126 is

The case is a 20-line Fletch file of closures and recursion. It execs
nothing itself. The binary under test in that row was the oracle's own
`build/yew`, built hours earlier in the same job and already run by 3
suites in that step, so it wasn't a file still being written or not yet
executable.

The status is the script runner's, from its child between `fork` and
`execv` (`tests/script/runner.c:977-1013`). A failed `execv` leaves 127
and names the binary. 126 is left from three earlier places:

| place | what failed | what the child prints |
|---|---|---|
| `runner.c:990-991` | `setpgid(0, 0)` | nothing |
| `runner.c:998-1001` | one of three `dup2` calls | nothing |
| `runner.c:1005-1010` | the sandbox environment: `setenv`, `realpath("runtime")`, `chdir` into the sandbox | `script: cannot prepare sandbox: <errno text>` |

The editor's only own 126 is a clipboard helper's child
(`src/text/clipboard.c:520`, `:939`), whose status the editor never
passes on.

### Why the run can't say which

The runner prints the failing child's stdout and stderr under its `FAIL`
line, and names the sandbox it kept. `tools/goldens` writes all of that
to `target/oracle/goldens/script.log` and prints only the `FAIL` lines.
On a hosted runner the log is gone with the job. So the one red run
holds the status and nothing else: whether the child printed `cannot
prepare sandbox`, and with which errno, was written and thrown away.

### What I expect

- **The harness row, red first.** `tools/goldens-selftest`'s
  `version-only` plant fails every script case with `exit 1` and
  `version-only: not an editor` on stderr. At trunk the selftest's output
  has the `FAIL` lines without that text; a new check for it fails. With
  `tools/goldens` printing each failing case's block, it passes, and the
  two plants stay red and the oracle green.
- **The cause.** A probe on its own branch repeats the runner's
  fork-to-exec sequence on a hosted macOS runner, alone and four at once,
  with the parent's own `setpgid(child, child)` on and off, and reports
  the step and errno of any failure. It then loops the script suite as
  the gate runs it, quiet and under load, the second time with the two
  silent exits made to print. I expect the failure to be rare enough
  that the suite loop stays green, and the bare sequence, at thousands of
  forks a second, to be the one place it may show. If it shows only with
  the parent's `setpgid` on, it's the parent and child racing to create
  the same process group. If nothing shows, the cause stays unknown and
  this note says so.
- **No golden moves, and the oracle tree is never written** outside the
  probe's own throwaway job.
