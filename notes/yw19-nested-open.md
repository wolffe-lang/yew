# yw19 — `:!yew PATH` opens in the running editor

_A fix for yew#129: on a PAX machine, `:!yew identity.lu` in a workspace
of over twenty tabs left a workspace of three. `:!yew PATH` is meant to
open PATH in the running editor, and a second editor in a workspace must
never replace the first one's saved state._

## Prediction

Written before the first change (2026-11-15, base trunk `727b605`, wolf
0.2.36 / lupin 0.1.58 / std `78b9d3cb`, `sagitta.pin` `9ace98c2`). Read
from source; nothing run yet.

### Where `:!yew PATH` is decided

- **The handoff is the editor's, not the session's.** `shc_run`
  (`src/edit/shell_cmds.lu:118-127`) asks `shell_try_self_open`
  (`src/edit/shell.lu:1012-1063`, sagitta `shell.c:528-647`) before any
  shell runs. When it answers `SHELL_SELF_OPENED` the file is a tab of
  this editor and no job exists. The persistent session, `--yew-env0`,
  fd 9 and the frame carry only the shell's directory and exports back
  to the editor (`ss_put_tail`, `ss_adopt`); nothing in them hands a
  path over.
- **When the recognizer declines** (`SHELL_SELF_NOT_HANDLED`), the line
  runs in the session like any other: a first word that is not exactly
  `yew`; an operand the shell would expand (`$`, a backquote, `*?[]{}`,
  a leading `~` or `=`, `#`, `|&;<>()`, a newline); a second operand; an
  operand starting with `-` without `--`; a directory. A relative
  operand is resolved from the workspace root, never from the session's
  directory (`self_open_path`, `shell.lu:968-981`).
- **A declined line cannot start a second editor.** It runs inside the
  session with stdin `/dev/null` and stdout the session's pipe
  (`ss_send`'s `__yew_run </dev/null 9>&-`), so the nested yew stops at
  `tty_require_terminal` (`src/term/tty.lu:1004-1012`), before it reads
  or writes any workspace state, and its `*job:N*` buffer says it is not
  a terminal. A full second editor needs a terminal: `:!!yew PATH`
  (`shc_term_run`, the terminal handed over, in the session's
  directory), or another terminal.

Predicted for the contract's candidates, on Linux at `727b605`:

| case | prediction |
|---|---|
| a path in a directory made by an earlier `:!mkdir` | opens here (green) |
| a relative path after `:!cd sub` | opens the ROOT's file, a new empty buffer, not `sub/`'s (red: the wrong file, no second editor) |
| the session busy, ended, or `shell.session` fresh | opens here: the recognizer runs before the session is asked (green) |
| 25+ tabs | opens here: `TAB_MAX` is 512 (green) |
| `:!yew DIR`, `:!yew $X`, `:!yew -R x` | reach the shell; a job buffer with the not-a-terminal message (red against "refuses by name") |
| `:!!yew x` in the same workspace | a second editor that logs `owned by pid N` and saves nothing (green on Linux) |

So the owner's lines, as recorded, should not start a second editor at
trunk. If the PAX run starts one where Linux does not, the cause is on
PAX's side of the recognizer and is named before any fix.

### The ownership check

- `state_lock_claim` (`src/edit/state_save.lu:86-120`, sagitta
  `state_save.c:56-140`) reads the pid in the workspace's `lock`, tests
  it with `os_signal_send(pid, 0)` (`kill(pid, 0)`; `denied` counts as
  alive), and otherwise writes its own pid and reads it back.
- PAX answers `kill(pid, 0)` as Linux does: 0 for a live process that
  may be signalled, `ESRCH` for no process, `EPERM` across users (pax
  `kernel/signal/signal.lu:472-490`). Predicted: on PAX the second
  editor of `:!!yew` logs the ownership line too.
- **What trunk does not handle:** a reader never becomes the owner. When
  the owner quits it saves and removes its lock; the reader, still
  running with its own tabs, never saves; the next editor claims the
  lock, restores the old owner's save and later writes its own. The
  reader's tabs are then lost for good, whatever it held. Predicted red.

### `active_tab` and the dropped record

- `active_tab` is a tab **id** (`state_emit.lu:294-298`, sagitta
  `state_emit.c:808-813`), not an index, and tab ids are monotonic in one
  editor's life (`next_tab_id`). A state of three records with
  `active_tab: 21` is consistent when one record has id 21: the writer
  had opened 21 tabs in its life. Predicted: at trunk the saved
  `active_tab` always names a saved record (all tabs up to 512 are
  written); the row holds it.
- **The record dropped at every start is the untitled tab.** A resume
  (`yew` with no file) keeps the bootstrap untitled tab (`ed_run` closes
  it only when files are given, `src/edit/driver.lu:300-311`); `se_tab`
  writes it with `path: nil` (sagitta's choice, `state_emit.c:600-605`:
  the restore drops it rather than recreating a scratch buffer), and
  `sp_tabs` counts it among the dropped (`state_parse.lu:449-455`, `:486`). So
  every resume logs `1 tab record(s) dropped`. Predicted: a seeded resume
  logs exactly one.

### What each row should show at `727b605`

`tools/nested-open-row` (new): yew in a pty, a scratch HOME,
`SHELL=/bin/sh`, a workspace of 26 files plus `paths_test.lu`, resumed
so the first editor holds 28 tabs.

- `newdir` (the owner's four lines): green.
- `cd`: red (`cd_session_cwd`).
- `refuse` (`:!yew DIR`, `:!yew $HOME/x.lu`, `:!yew -R x.lu`): red
  (`refuse_*_named`, `refuse_*_no_job`).
- `passthru` (`:!yew --version` still runs in the session): green.
- `bangbang` (`:!!yew identity.lu`): green.
- `takeover` (a reader beside the first editor, the first quits): red
  (`takeover_reader_saves`, `takeover_third_is_reader`,
  `takeover_reader_last`).
- `dropped`: `active_saved` green; `no_drop_logged` red.

`tools/nested-open-pax` (new): `newdir`, `bangbang` and `refuse` on image
3's ISO under QEMU. Predicted as on Linux: `newdir` and `bangbang` green,
`refuse` red.

### The change, as planned

- The recognizer resolves a relative operand from the session's
  directory when the session reported one, as the shell would.
- A `:!yew` line that would start an editor and that the recognizer
  cannot open is refused by name on the message line, and never reaches
  a shell; lines that are not an editor start (`--version`, `--help`,
  `--batch`, `fl`) still run in the session.
- A reader takes the lock over at its next save point once the owner is
  gone, so the editor still running is the one whose tabs are saved.
- The untitled tab's record is not counted as dropped.

### Hits and misses

Measured after the prediction, on x86-64 Linux in yew CI's image (a pty,
`TERM=xterm-256color`) and on image 3's ISO under QEMU (KVM, the console
typed on COM1, `TERM=linux`, `SHELL=/bin/sh`, yew `727b6056`). The row's
files became `.txt` before its first full run: a `.lu` file starts `wolf
lsp`, which neither host has, and yew#127 reports that failure on every
pass of the loop, over the message line the row reads.

- **The owner's four lines open in the running editor, on both hosts, at
  trunk** (hit). Linux: one editor, 30 saved tab records (the untitled
  tab, 27 files, `identity/identity.txt`, `identity_test.txt`), no second
  start in the log. PAX: the same 30 records written by the first
  editor, one `:q!` to the prompt, no restore and no ownership line. So
  yew#129's two starts 51 s apart did not come from `:!yew` lines: a
  `yew` reached from `:!` has no terminal and stops at
  `tty_require_terminal` before it reads any state (seen: `not a terminal;
  use --batch SCRIPT for headless execution`, exit 1, in a `*job:N*`
  buffer). Both starts had a terminal. See "What yew#129's evidence needs".
- `cd`: red at trunk (hit): after `:!cd sub`, `:!yew x.txt` opened the
  root's `x.txt`, a new empty buffer.
- `refuse`: red at trunk (hit): each line ran as a job whose yew said it
  was not a terminal.
- `passthru` and `bangbang`: green at trunk (hit). The second editor of
  `:!!yew` logs `workspace state is owned by pid N; this session will
  not save it` on Linux and on PAX: **the ownership check works on PAX
  within one boot.** PAX answers `kill(pid, 0)` as Linux does
  (pax `kernel/signal/signal.lu`'s `kill`) and never reuses a pid within
  a boot (`kernel/sched/sched.lu`'s `take_pid`).
- **What the pid check misses, on PAX most of all** (a miss of the
  prediction, which looked at the reader that outlives its owner): pids
  start again at 1 on every boot, in boot order, so a lease left by an
  editor that never removed it (a power-off, `kill -9`) can name a pid
  the next boot gave to a program that stays up. Every later editor in
  the workspace is then a reader that saves nothing, for as long as that
  program lives, with one message on its first change. The `stale` rows
  plant exactly that, a lease naming pid 1: red at trunk on Linux and on
  PAX (`workspace state is owned by pid 1; this session will not save
  it`, the lease still `1` after the quit).
- `takeover` was replaced by `reader` before its first run: the planned
  takeover would have a reader replace its owner's saved state once the
  owner quits, which yew#129's own requirement forbids (a second editor
  never replaces the first one's saved state), so trunk's reader stays a
  reader and the row holds that: green at trunk.
- `dropped`: `active_saved` green (hit: every resume's `active_tab` names
  a written record); `no_drop_logged` red (hit).
- The unit file, red at trunk's code (`yw19-red`, `7d7bc7a`: this branch's
  rows and unit file on trunk's `src/`): the session directory, the
  refusals, the plain operands, the untitled record, `active_tab` past the
  record cap, a held owner lock, a stale lease naming a live pid; green:
  the lines left to the shell, and a pid-only lease of a live process
  still owning (C's lease kept).

### What yew#129's evidence needs

The rows do not reproduce a second editor from the owner's lines, on
Linux or on image 3. What fits the machine's evidence is the gap above:

1. the twenty-tab editor was itself a **reader** from its start: the
   lease named a pid that was alive then (the earlier `owned by pid N`
   line in the log would be that start's own), so none of its tabs ever
   reached the saved state;
2. the two starts 51 s apart found that pid gone, took the lease and
   saved their own small states, the last one with three records.

`active_tab: 21` is not past the list: `active_tab` is a tab **id**, and
ids grow through one editor's life, so the last writer had opened 21
tabs. Three things on the machine would settle it, read-only: the pid and
time of the earlier ownership line against the twenty-tab editor's start;
the three records' `id` fields (is one of them 21?); and how the two
starts at 01:27 were begun (a second console or session, or `:!!`).

### The change, as made

- `self_open_path` resolves a relative operand from the directory the
  persistent session last reported (`shsession.cwd`), as the shell
  would; from the workspace root while it has reported none, or under
  `shell.session fresh`, as C does.
- `shell_self_open_words` (`src/edit/shell.lu`), asked by `shc_run` once
  the recognizer has declined: a `:!yew` line whose words, read as
  `args_parse` reads them, start an editor never reaches a shell. Plain
  files open here (several as several tabs, the last active); a
  directory, a word the shell would expand and an editor option are
  refused on the message line by name (`:!LINE is not opened here:
  …`). A `yew` that starts no editor (`--version`, `--help`, `--batch`,
  `fl`, a usage error such as `-R`), a compound line (`|`, `;`, `>`, …),
  an unterminated quote and any other first word still run in the
  session, as before. The recognizer itself is C's, unchanged
  (`edit_shell_self_test.lu` holds it).
- The owner lock (`src/edit/state_save.lu`): beside the pid lease, a file
  `lock.owner` the owner opens once and takes an advisory lock on
  (`fs_lock`, `flock(2)`; PAX has it, pax `kernel/files/files.lu`'s
  `flock`), held for the session's life. A second
  session finds it held and is a reader, whatever the lease says; a lease
  naming the pid the owner record names, with the lock free, is stale
  however alive that pid is; a lease with no owner record behind it is a
  session from before the lock and owns by its pid, as in C. The lease
  keeps C's text, so an older yew still reads it. A host or filesystem
  with no `flock` keeps C's lease alone.
- `sp_tabs` skips a `path: nil` record (the untitled tab, written so by
  design, `state_emit.c:600-605`) without counting it dropped.
- `state_emit_at` never names a tab past the records it wrote (only
  reachable past the 512-record cap, which the tab cap keeps a live editor
  under).

## Forbidden

- No merge, label, tag or release, and no issue filed or closed. No
  attribution trailer.
- Clean room: sagitta at the pin was read and is cited `file:line`
  (`src/edit/shell.c`, `src/ws/state_save.c`, `src/ws/state_emit.c`,
  `src/ws/state_parse.c`, `tests/unit/test_shell_self.c`); PAX's own
  kernel was read where the ownership check meets it (`kernel/signal/
  signal.lu`'s `kill`, `kernel/sched/sched.lu`'s `take_pid`,
  `kernel/files/files.lu`'s `flock`, `kernel/procfs/procfs.lu`'s entries),
  PAX being this project's own; no other editor's source.
- No golden edited and no sagitta file changed. `sagitta.pin` and the wolf
  pin are unchanged. The port's ported tests (`edit_shell_self_test.lu`,
  `edit_ws_save_test.lu`) are unchanged.
- The real PAX machine and its owner's yew state were not touched: the
  evidence from it is yew#129's, as filed.

## Inputs verified

- **Base:** trunk `727b605`, still trunk's head. yw18 (yew#127) is open in
  parallel; it changes `src/edit/lsp_client.lu` and the LSP rows, none of
  this branch's files, and adds `tools/execfail-pax-image`, which
  `tools/nested-open-pax-image` copies by value (one of the two can go
  once both are in).
- **Toolchain:** wolf 0.2.36 (`5adf3d91`), lupin 0.1.58, std `78b9d3cb`,
  from the pinned archives (`tools/fetch-toolchain`).
- **C yew:** `sagitta.pin` (`9ace98c2`), read for the recognizer, the
  lease and the state's emit and parse; built by `tools/oracle` for the
  gated PTY goldens.
- **PAX:** image 3's ISO, `pax-dev-5e95dec8.iso`, sha256
  `32fe1a14834a530eb790d56c224bebbe3b697fa93c4587b22bf1c556b99f3836`, its
  yew `1.0.0-dev` at `727b6056` (trunk), booted by UEFI under QEMU with
  KVM. The fix's legs swap its `/bin/yew` for this branch's static build
  (`tools/nested-open-pax-image`) and keep every other member.

| host | role |
|---|---|
| x86-64 Linux, rootless podman, a block's two light CPUs | every build, the unit files, the pty row, the gated PTY goldens, QEMU for the PAX legs |
| Apple M-series Mac | edits and git only |

## Evidence index

The R-list (decisions taken as recommended):

- **R-yw19-1** — a relative `:!yew` operand: (A) the session's reported
  directory, the root without one — taken; (B) the root always, as C.
  A follows what the shell the line is typed into would open.
- **R-yw19-2** — a `:!yew` line the recognizer leaves: (A) open its plain
  files here, refuse the rest of the editor starts by name, leave every
  other `yew` to the shell — taken; (B) refuse every such line; (C) let
  the session expand the words and open what it answers (not built: an
  internal job type whose completion opens tabs; a follow-on if wanted).
- **R-yw19-3** — the owner check: (A) an advisory lock held for the
  session's life beside C's pid lease, the lease kept for messages and
  older yews — taken; (B) the lease's pid checked against
  `/proc/PID/exe` (PAX has only `/proc/self/exe`, so every live owner
  would read as stale there: refused); (C) C's pid lease alone.
- **R-yw19-4** — a reader whose owner quits: (A) stays a reader, as C —
  taken, by yew#129's own rule that a second editor never replaces the
  first one's saved state; (B) takes the owner lock at its next save
  point and saves its own tabs over the owner's.
- **R-yw19-5** — the untitled tab's record: (A) still written, skipped at
  restore without a "dropped" line — taken (the state stays C's byte for
  byte); (B) not written at all.
- **R-yw19-6** — `active_tab` past the record cap: (A) the last written
  record's id — taken; (B) 0, which restore reads as its first record.
