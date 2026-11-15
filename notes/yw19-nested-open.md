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
