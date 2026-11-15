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
