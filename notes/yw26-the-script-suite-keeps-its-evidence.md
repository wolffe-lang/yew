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

## What the probe found

The probe ran on a hosted macOS runner (macOS 26.7.2, arm64; run
44588221629), from its own branch, which is not part of this change.

### The bare sequence

Four copies at once for 150 seconds, each repeating the runner's steps
from `pipe` to `execv` of `/usr/bin/true`:

| the parent also calls `setpgid(child, child)` | children | failures |
|---|---|---|
| yes, as `runner.c:1228` does | 99,724 | 137 |
| no | 99,579 | 0 |

Every failure was `setpgid` refused with `EPERM`, in the child's
`setpgid(0, 0)` or in the parent's `setpgid(child, child)`, never both
for one child. No `dup2`, `realpath`, `setenv`, `chdir` or `execv`
failed in either mode. So it's a race between the two calls for the
same new process group, about once in 700 children with four copies
running, and it needs both calls.

### What each side's refusal looks like in the suite

- **The child's**: `_exit(126)` at `runner.c:991`, before the
  descriptors are redirected and with no message: `FAIL <case> (exit
  126)`. This is the red the hosted run showed.
- **The parent's**: `runner.c:1228-1238` accepts only `EACCES` and
  `ESRCH`, so it kills the child and reports `FAIL <case> (runner setup
  failed)`.

In both, the editor was never executed, and the case that takes the
blame is whichever one the runner happened to be starting.

### The suite itself

The same job then looped the script suite through `tools/goldens`, as
the gate runs it, against the oracle's own editor:

| loop | runs | red | the red cases |
|---|---|---|---|
| quiet, 15 minutes | 88 | 2 | `39_skip_protocol`, `plug_examples_notes`, both `(runner setup failed)` |
| four busy loops beside it | 7 | 1 | `07_functions (runner setup failed)` |

The loaded loop stopped at its first red (a mistake in the probe's
script, not a finding). Three reds in 95 runs of 93 cases is about one
child in 2,900.

The prediction held on the cause (the parent and child racing to create
one group) and was wrong on the rate: I expected the suite loop to stay
green, and it went red three times.

## The change

The race is in sagitta's script runner, which this repository builds
and runs and never changes. Two things change here, both in
`tools/goldens`:

1. **A red script case shows its evidence.** The first five red cases
   are printed with the block the runner wrote under each.
2. **A case the runner never started is run once more, by name.** Only
   the two shapes above qualify: `(runner setup failed)`, and `(exit
   126)` with no output from the child at all. A 126 that says anything
   (`cannot prepare sandbox` included) stays red. At most three cases in
   one suite run, once each; more than three is left red as it is. Each
   is reported as a `RERUN` line, and as a warning on a hosted run, so a
   rerun is never silent. A case red on its second run is red.

The rerun is narrower than a retry of a flaky test: it can't turn an
assertion failure, a wrong byte, a timeout, a signal or any exit status
other than a wordless 126 green, since none of those is run again.

`tools/goldens-selftest` holds both: its `version-only` plant must show
the plant's stderr, a plant that exits 126 once for one case must come
out green with its `RERUN` line, and a plant that does so every time
must stay red.

The cure at the source is two lines in the runner: the child and the
parent each treat `EPERM` as success when the child's group is already
its own pid. With that in the pinned oracle the rerun has nothing left
to do and can go.

## After

The probe's second run (44595044151, the same runner image) looped the
suite through `tools/goldens` at the head of this change:

| loop | runs | red | runs with a rerun |
|---|---|---|---|
| quiet, 25 minutes | 157 | 0 | 7 |
| four busy loops beside it, 15 minutes | 71 | 0 | 6 |

228 runs, none red. Thirteen runs had one case the runner never started
(some `(exit 126)`, some `(runner setup failed)`), each was run once
more and passed, and each is named in the output. Before the change
those thirteen runs would have been red; the first probe's loops were
red in 3 of 95.

The selftest on the same runner was green, and it met the race itself:
under the `version-only` plant one case came back `(exit 126)` with no
output, was run again, failed again as every case of that plant does,
and stayed red.
