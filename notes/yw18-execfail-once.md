# yw18 — a language server that fails to start is reported once

_A fix to the LSP client (yew#127): with a `.sh` file open and no
`bash-language-server` on PATH, yew reported the failure again on every
pass of its main loop and redrew its footer each time. On a real PAX
machine this coincided with the mouse lagging and then stopping, and both
recovered when the `.sh` tab was closed._

## Prediction

Written before the first change (2026-11-15, base trunk `727b605`, wolf
0.2.36 / lupin 0.1.58 / std `78b9d3cb`, `sagitta.pin` `9ace98c2`). Read from source; nothing run yet.

### What the code does at `727b605`

- `job_turn` (`src/edit/job.lu:2328-2345`) calls `lsp_pump` on **every**
  turn of the loop, and `lsp_pump` ends with `lsp_client_pump`
  (`src/edit/lsp.lu:458-477`).
- `spawn_server` (`src/edit/lsp_client.lu:696-738`) gets a job back from
  `job_spawn` even when the program is not on PATH: the spawn's own row
  makes the job "born an exec failure" (`JOB_EXECFAIL`, reaped, every
  descriptor closed, `src/edit/job.lu:1398-1408`). The server is left
  `LSP_INITIALIZING`.
- On the next turn `lsp_client_pump` (`:1042-1054`) finds the job in
  `JOB_EXECFAIL`, marks the server dead and given up, and calls
  `ed_msg(MSG_ERROR, "bashls: No such file or directory — install
  bash-language-server or set lsp.servers.sh.cmd")`. It neither releases
  the job nor records that it reported, so every later turn finds the
  same job in the same state and reports again. The only `job_release`
  in the pump is in the respawn branch, which `gave_up` skips.
- `ed_msg_at` (`src/edit/message.lu:161-189`) clears and sets the
  message (and rings the bell under `errorbells`), and marks the footer
  damaged; `ed_render` then redraws the footer into the grid every turn.
  The renderer diffs the grid against the last frame
  (`src/term/render.lu:903-990`), so an unchanged footer writes no bytes.
- C yew has the same branch at the pin (`client.c:1268-1360`, the
  `YEW_JOB_EXECFAIL` case): the re-report is sagitta's too.

### Does the loop spin without input?

**No, predicted.** A job that is not `JOB_RUNNING` adds no deadline
(`job_deadline`, `src/edit/job.lu:2206-2258`: only a running job's
framed, stream, kill and timeout deadlines count, and a rekill only while
the job is pending), and an exec failure has no descriptor for the wait
(`job_fds_refresh`). An error message has no expiry timer. So once the
start-up deadlines pass (the probe, git's first poll, `ed.idle`'s 500 ms
clock), the wait blocks: the re-report costs one footer redraw per turn
that something else caused, and nothing while idle.

### What each row should show at `727b605`

1. **The pty row** (`tools/execfail-row`, new): yew in a pty with a
   scratch HOME, `SHELL=/bin/sh` and a PATH without
   `bash-language-server`, one session with a `.sh` file and one with a
   `.txt` file, measuring the bytes yew writes and its CPU time
   (`/proc/<pid>/stat`) over 5 s idle and over 200 SGR mouse-motion
   reports.
   - Idle: `.sh` and `.txt` equal within noise, in bytes and CPU (no
     spin).
   - 200 motions: one footer redraw per turn for `.sh`; equal bytes
     (unchanged cells write nothing); CPU higher for `.sh` by the cost of
     the redraws, which may be inside the noise on Linux.
   - With `errorbells` set, every re-report rings the bell: about one BEL
     per turn for `.sh` against none for `.txt`. This is the row's
     reliable red.
   - A message the user raises (here `:lsp.info`'s answer) is replaced by
     the error at the next turn: red.
2. **The unit row** (`src/edit_lsp_execfail_test.lu`, new), the client
   pumped in-process:
   - after the failure is reported and the message cleared, further pumps
     set it again: red;
   - the failed job is still in the job table: red;
   - `:lsp.info` does not say why the server is off: red;
   - **`:lsp.restart` cannot retry.** `lsp_client_restart` resets the
     server's life and asks the old job to stop, but the old
     `JOB_EXECFAIL` job stays, so the next pump takes the exec-failure
     branch again before the respawn branch: a server installed after the
     failure is never started until yew restarts. Red.
   - The five-crash give-up (`lsp_life_crashed`, `src/lsp/client.lu:
     700-722`) is **not** re-reported: the crash branch runs only while
     the server is neither dead nor shutting down, and the give-up leaves
     it dead. Green at trunk; the row holds it.

### The change

- The exec-failure branch reports once, records the reason on the
  server's life (`LspLife.off_why`), and releases the failed job, so the
  server has no job and later pumps pass it by.
- `:lsp.restart` clears the reason with the rest of the life
  (`lsp_life_restart_reset`), so the respawn branch runs and a failure
  is reported once more.
- `:lsp.info` names the reason while the server is off.
- The five-crash give-up records its reason too; its job is kept, since
  its message points at `:lsp.log`, which reads that job's stderr.

### PAX under QEMU

The same row on a PAX image under QEMU, watching `/proc/pax-boot`'s
serial `dropped` count while idle with the `.sh` buffer open: flat at
trunk and after the fix (the prediction says the idle loop does not
spin); the motion phase is where trunk and the fix should differ.

## What the rows showed at trunk

Every take ran on Linux x86-64 in yew CI's image (ubuntu 24.04), on two
CPUs of the lane host's light slots, from fresh worktrees at commits of
this branch; the PAX takes ran image 3's live ISO under QEMU with KVM.
"Trunk code" is commit `7a862a0`: the rows and the tools on trunk's
`src/`, which the branch first changes at `68e1678`.

### The unit row, at `7a862a0`

`src/edit_lsp_execfail_test.lu`, each case alone, native tier: five of
six red by name, one green, as predicted.

| case | trunk code | why |
|---|---|---|
| execfail_reported_once | red | `not reported again: bashls: No such file or directory — install yw18-no-such-language-server or set lsp.servers.sh.cmd` |
| execfail_job_released | red | `the server has no job` |
| execfail_info_says_why | red | the line ends at `stale drops 0` |
| execfail_restart_tries_again | red | `started again: 1 jobs`: the old exec failure, no new job |
| crash_giveup_reported_once | green | the give-up is reported once |
| crash_giveup_info_says_why | red | the line ends at `stale drops 0` |

### The pty row, at trunk code

`tools/execfail-row` over a native build of `7a862a0` (TERM
xterm-256color; 5 s idle, 200 motion reports and 200 keys 5 ms apart):

| phase | `.txt` bytes / CPU | `.sh` bytes / CPU | `.sh`, errorbells: bytes / bells / CPU |
|---|---|---|---|
| idle 5 s | 0 / 0.5 ms | 0 / 0.5 ms | 0 / 0 / 0.0 ms |
| 200 motions | 0 / 59 ms | 0 / 113 ms | 200 / 200 / 124 ms |
| 200 keys | 59 / 73 ms | 176 / 116 ms | 376 / 200 / 110 ms |
| `:lsp.info`, one motion | 0 | 252, the failure drawn again | 2 / 2 |

A second take of trunk code, with the row as of `d24d2a0`, under TERM
xterm-256color and then `linux` (the PAX console's), gave the same bells
(200 for 200 motion reports and 200 for 200 keys, under both), the same
bytes, and 113 and 139 ms of CPU for the 200 motions against the
control's 62 and 65 ms. Under `linux` its message phase caught the
failure drawn again over `:lsp.info`'s answer (258 bytes); under xterm
the redraw came during the settle before the phase began, so the row
now measures that phase from the command itself (`f1ac43b`). Under
`linux` the errorbells session also rang 3 times while "idle": turns
that the command line's own idle work caused after `:set`, each a
re-report.

- **The loop does not spin.** Idle, the `.sh` session writes nothing and
  burns what the control burns, and the wait blocks: a job that is not
  running adds no deadline and an exec failure has no descriptor.
- **Every turn re-reports.** With `errorbells` on, 200 motion reports
  rang the bell 200 times, and 200 keys 200 times: one report a turn.
  Without it the re-report writes no bytes while the message's cells are
  unchanged (the renderer diffs), but it doubles the CPU a motion report
  costs (59 to 113 ms for 200), and it draws the failure over anything
  else: after `:lsp.info` answered, one motion report put the failure
  back on the message row. A key clears an error message, and the next
  turn without a key sets it again, so the message cannot be dismissed:
  the owner's "the status message about it stayed up".
- **Every turn keeps what it builds.** The message's strings are made in
  the loop's ambient region, which frees nothing; on Linux the resident
  set is too noisy to show it (the control's own phases moved it by
  megabytes either way), but on PAX it is plain (below).

### PAX under QEMU, image 3 as delivered (yew at `727b605`)

`tools/execfail-pax`'s first form over `pax-dev-5e95dec8.iso` (UEFI,
COM1 a 115200 baud UART; the console's TERM is `linux`), the resident
set read from the `/proc/<yew>/stat` lines its sampler printed (the
sampler as committed at `7a862a0`, whose verdict adds it):

| window | `.txt`: dropped / COM1 bytes / resident | `.sh`: dropped / COM1 bytes / resident |
|---|---|---|
| idle, 8 s to 13 s | +0 / 0 / +0 KiB | +0 / 0 / +0 KiB |
| 200 motions, 13 s to 19 s | +0 / 0 / +0 KiB | +0 / 0 / +356 KiB |

- `/proc/pax-boot` read `serial present tty mirrored dropped 0` from
  boot to the end of both sessions: yew wrote nothing while idle, and
  nothing for the motion reports (unchanged cells), so the serial line
  dropped nothing. The idle row is green at trunk, as predicted.
- PAX gives no CPU time per process yet (`utime` and `stime` in
  `/proc/<pid>/stat` are 0), so the PAX row cannot see the CPU.
- **The resident set grew 89 pages (356 KiB) over 200 motion reports in
  the `.sh` session, and not at all in the control:** about 1.8 KiB a
  turn, never freed. On a machine left with the `.sh` tab open, every key
  and every mouse report the editor reads adds to it.

### What this says about the PAX report

The rows do not reproduce the owner's lag, and they say what the
re-report does and does not do. It cannot make the loop spin, and it
writes nothing to the console while the message is unchanged. It does
cost every turn CPU and memory, and it holds the message up. The
`dropped 399856` the owner saw is not the re-report's: with nothing
changed on the screen the re-report writes no byte. Image 3's console
mirrors every byte a program draws to COM1 and drops what the line's
11.5 KB a second cannot carry, so ordinary drawing (a scroll, a
repaint at the machine's screen size) counts there. On PAX the console reports the mouse only with a button held
(kernel/console's header), so a pointer moved with no button pressed
does not wake yew at all. Why the pointer lagged and stopped, and why it
came back when the tab closed, is not shown here; by the source, closing
the tab at trunk keeps the failed server and its job (the buffer's
document is dropped, the server is not), so the re-report goes on.

## Hits and misses

- Hit: the loop does not spin; idle costs nothing in either session, on
  Linux and on PAX.
- Hit: the re-report writes no bytes while the message's cells are
  unchanged; with `errorbells` it rings once a turn.
- Hit: a message raised after the failure is replaced by it at the next
  turn.
- Hit: `:lsp.restart` cannot start a server after an exec failure at
  trunk (`started again: 1 jobs`).
- Hit: the five-crash give-up is reported once.
- Partly: the CPU a turn costs nearly doubled under motion reports (59
  to 113 ms for 200), more than "inside the noise".
- Miss: memory. The prediction did not say that every re-report keeps
  the strings it builds. PAX shows it plainly (+356 KiB over 200
  turns, the control +0); Linux's resident set is too noisy to judge it,
  so the Linux row prints it and the PAX row judges it.

## Decisions (each implemented as recommended)

- **R-yw18-1, the release.** A (recommended): report the first time
  only (the reason recorded on the server's life is the mark) and
  release the failed job once the job layer has settled it, the turn
  after its spawn, as every finished job is settled. B: keep the job and
  a "reported" flag (the dead job stays in the table, and `:lsp.restart`
  would have to release it to respawn). C: release it at once, in the
  turn of its spawn (it skips the settle, whose repository refresh C
  runs for every job a user can see: a second divergence for no gain).
- **R-yw18-2, where the reason shows.** A (recommended): `:lsp.info`
  ends with `; off until :lsp.restart: <why>` for a server that gave up
  with a reason, and is C's line otherwise. B: the status badge (it
  would move frames the LSP rows hold to C's, the crash rows'). C: a new
  command.
- **R-yw18-3, the five-crash give-up.** A (recommended): its report
  stays as it is (it was never repeated), its reason is recorded for
  `:lsp.info`, and its job is kept, because its message sends the user
  to `:lsp.log`, which reads that job's stderr.
- **R-yw18-4, sagitta.** C yew has the same re-report at the pin
  (`client.c:1287-1295`). Recommended: the owner hears of it (a yew lane
  never changes sagitta); the port's divergence is named in
  docs/MAP.md §9.
- **R-yw18-5, CI.** The unit row runs in CI as it is (`tools/check-test`
  finds every `*_test.lu`; `tools/check-test-cases.txt` has its
  per-case row). The pty and PAX rows are tools the gauntlet runs;
  wiring them into `.github/` would make this change cross-cutting.
  Recommended: a follow-up adds `tools/execfail-row` to the port job.
- **R-yw18-6, PAX's CPU time.** `/proc/<pid>/stat` on PAX reads 0 for
  `utime` and `stime`, so no row can see a program's CPU there.
  Recommended: an issue on pax.
- **R-yw18-7, the other give-ups.** A server that answers `initialize`
  with an error, or has no document synchronization, gives up with no
  reason recorded, as before. Recommended: a follow-up records those
  too.

## The fix, as written

- `lsp_client_pump`'s exec-failure branch (`src/edit/lsp_client.lu`)
  reports the failure the first time it sees it, and records the reason
  on the server's life (`LspLife.off_why`, `src/lsp/client.lu`), which
  is the mark that it was reported. Once the job layer has settled the
  failed job (the turn after its spawn), the branch releases it and the
  server keeps no job, so later pumps pass the server by: it is dead,
  given up, and has no job to look at.
- `:lsp.restart` resets the server's life (`lsp_life_restart_reset`),
  which now clears the reason too; the respawn branch then starts the
  server again, and a second failure is reported once more.
- The five-crash give-up records "crashed 5 times in 5 minutes" as its
  reason. Its job is kept.
- `:lsp.info` (`src/edit/lsp.lu`) ends with `; off until :lsp.restart:
  <why>` for a server that gave up with a reason.

At `b9c784d` (the first form of the fix: the job released in the turn
it was seen), the unit row is six of six green. At `d24d2a0` the pty row
is green under both terminals: the `.sh` session costs what the control
costs (200 motions: 72 and 54 ms against 58 and 59 ms; 200 keys: 84 and
73 ms against 81 and 74 ms), rings no bell, and after `:lsp.info` draws
nothing. The settle-first
release (`1fa887b`) and the reorder that lets the plant be one hunk
(`7558c64`) followed; the record at the pull request's head holds the
unit, pty and PAX rows there, with the LSP rows against C and the gated
PTY goldens, and the plant beside it.

## Evidence index

- The prediction: `85b4d85`, before the first change.
- The rows: `src/edit_lsp_execfail_test.lu` (`b7bd0fa`, `85c429c`),
  `tools/execfail-row` (`3f9753c`, `a176590`, `7c8983f`) and
  `tools/execfail-pax` (`7a862a0`), committed before the fix;
  `tools/execfail-pax-image` (`96144e0`), and the row's two corrections
  after it, the resident set printed and not judged (`d24d2a0`) and the
  message phase measured from the command (`f1ac43b`).
- The fix: `68e1678`, `f2f5b17`, `b9c784d`, `1fa887b`, `7558c64`.
- The trunk takes above: the unit row and the pty row at `7a862a0`, the
  PAX row over image 3's ISO (sha256 `32fe1a14…`, from the image's build
  directory) with the tool as committed at `7a862a0`.
- The records at the head and the plant's: in the pull request.

## What this lane did not do

- It did not reproduce the pointer's lag on the owner's machine (never
  touched): the rows measure what the re-report costs and show it is not
  a spin and writes nothing while the screen is unchanged.
- It did not change sagitta, which has the same branch at the pin.
- It did not wire the pty and PAX rows into CI (R-yw18-5).
