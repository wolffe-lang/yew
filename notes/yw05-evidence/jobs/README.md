# yw05 — the `jobs` fork's evidence (yw04's job half, R-yw05-2 = A)

kasumi, wolf 0.2.34 / lupin 0.1.55 / wolf-std `e036bec`, in `ctr`'s
container on CPUs 0-3, the fork tree `~/lanes/yw05-jobs/yew`.

What the fork ports, over the `wait` fork's `os_signal_wait_fds` turn
(merged at `85b9a61`): `job.c`'s table (`9ae6f7e`: spawn, pump, reap,
settle, the deadlines, the owners as KINDS matched in one place — no
function value crosses a module boundary, G19/G20), `shell.c`'s three modes
with the region filter's restricted loop and the `*jobs*` table
(`b0d784a`), the persistent session of s57.27 over a framed job
(`461c84f`, `d66567f`'s `--yew-env0`), `:!`, `:!bg`, `:r !`, the filter and
the job commands through the job layer (`8f43b8e`), the generator, `--help`
and fish jobs as callback owners (`c50698e`), the loop's job turn — one wait
over the jobs' descriptors, the reap on `SIGCHLD`, the job deadline
(`dddbc94`) —, the teardown's kill-and-reap of every live group
(`cc97bc1`), the running-job badge (`a7bec3e`), the stream sink, and a
focused job output retired by Escape and `:q` (`47e6391`). The filter's
WRITE side (R-yw04-3, wolf-lang#818) is a forked writer child feeding the
filter's stdin (`job_fork_writer`, `os_fork`, G30's fork half), so no
non-blocking pipe write is needed at this pin.

## The goldens (`g1`, the fork merged with `yw05` at `35db18c`)

Built 2026-10-22T12:51Z-13:09Z (release `1737c5d099c7`, native
`506448c3be4a`, demo `f1679d1e7733`): yw04's 21 red campaign-04 rows
**21/21 green natively** (`sweep-g1-jobs21-native.txt`), then campaign 01
18/18, campaign 03 62/62 and **campaign 04 104/104 on both tiers**
(`sweep-g1-*`, `gate-g1.log`). No golden edited. CI gates the 104 by name since
`b77f12c`.

## The unit suites

yw04's SKIP-by-name cases of the job suites run (yw04's note §4.3 table):
`test_job` 29 (`817dc95`), `test_shsession` 17 (`fd3a98a`), `test_compgen`'s
nine generator cases (`22d36a9`), `test_comphelp`'s thirteen help-job cases
(`ad57505`), `test_compfish`'s oracle cases through the prompt, real fish
included where the host has one (`a43bccd`), `test_cdaware`'s generator and
session cases (`e94411c`), `test_shell_term`'s KNOWN-RED row retired —
`:!true` is one user job (`a9a3310`) — and `test_cmdcomp_shell`'s
spawns-nothing case counting the job table as C does (`0a405c2`). At the
fork's head (`e578d6f`'s sources) `tools/check-test --native` exits 0
with 89 files ok and **51 SKIP lines** (the wait fork's head had 254, the
sync fork's 216: yw04's job-suite SKIPs all run now; what remains SKIPs
by name for yw09, yw10, yw11, yw13 and — the tab jumps and the
peer-window half — this lane's tabs and panes forks), and the checked lane
"89 passed; 0 failed" (`check-native-ck1.log`, `check-checked-ck1.log`).
Those two runs shared the tree with `g1`'s own check-test lanes (a slip:
`g1`'s were void — a plant ran on the tree mid-run — and the harness
refused stopping `ck1`'s container when the overlap was found), so the
lane gate on `yw05` at the merge is the clean record (`../lane/`).

## Seen red (`red-*.txt`)

Each new or turned-green suite under one planted break in the code it
covers, restored after the run (`/Users/mfwolffe/lanes/yw05/bin-jobs/
plant.sh`): `test_job`, `test_comphelp`, `test_compfish`, `test_cdaware`,
`test_shell_term`, `test_shsession`, `test_compgen` and
`test_cmdcomp_shell` (a spawn planted in the completion path: "the job
table is empty" traps). Each file holds the plant's diff and the run's
tail.
