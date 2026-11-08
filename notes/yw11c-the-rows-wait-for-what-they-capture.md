# yw11c — the LSP rows wait for what they capture

_A fix to the LSP oracle rows' harness, not to the editor: on hosted
macOS runners `lsp-rows` went red on `c lspw_open_diag.3-list: unstable
between runs`, twice in a row (trunk's push run at `3a9983e`, run
42438330768; this PR's run at `c8443c7`, run 42438402076)._

## Prediction

Written before the first change (2026-11-08, base `c8443c7`, the head of
this branch over trunk `3a9983e`; wolf 0.2.36 / lupin 0.1.58 / std
`78b9d3cb`, `sagitta.pin` `9ace98c2`).

### What the step waits on now

`case_lspw_open_diag` types `:ed.lsp.diagnostics` (`lsprow_command`),
then `lsprow_wait(c, "1/1", …)`: the list's count, in the picker's footer
row, at a frame boundary (`ptc_wait_until` samples only between DECSET
2026 pairs, `harness.c:397-423`); then 300 ms with no output
(`LSPROW_QUIET_MS`); then the screen is kept as `3-list`.

### What the red screens are

Both red runs differ in rows 22 and 23 only. Rows 2 to 21, the picker's
box (its title row under the command line's hint, its filter line, the
one diagnostic and the `1/1` footer), are the same in both captures, so
the list had been drawn in both. What differs is the editor's footer:

| | row 22 | row 23 |
|---|---|---|
| first frame | blank | ` L E ✗ [wolf] this is \`str\`, …` (the hint under the cursor) |
| repainted | `ed.lsp.diagnostics → lsp.diagnostics` | `:` |

On trunk's run, C's run 1 kept the repainted screen and run 2 the first
frame; on this PR's run it was the other way round. The port's two runs
kept the first frame both times.

### Why the list's screen has two forms

- **C draws the footer before the picker.** `yew_ed_render` draws the
  footer when it is damaged (`ed.c:2728-2729`) and then the modal overlays
  (`ed.c:2741-2748`). The picker opens its filter line, which is the
  editor's one command line, inside its own draw (`picker.c:963-965`,
  `ensure_filter` at `picker.c:204-210`). So the frame that opens the list
  draws the footer while the command line is still closed: the message row
  with the cursor's hint. From then on the command line is open, and the
  next frame that redraws the footer draws it there too
  (`draw.c:1071-1072`), with the stale hint the line kept from the typed
  command (`cmdline.c:810-857`). The port draws in the same order
  (`draw.lu:1299-1313`, `picker.lu:1292-1298`, `draw.lu:889-891`).
- **Something redraws C's footer with no key pressed: its repository
  discovery.** At its first idle turn C yew runs `git --version`
  (`git.c:1481-1483`) and then `git rev-parse …` (`git.c:1572-1576`) as jobs,
  from the loop's idle refresh (`loop.c:651-654`, `git.c:1952-1975`). A
  job's start and its exit mark the jobs table dirty (`job.c:1142`,
  `:1321`, `:1566`, `:1820`), and the loop redraws the footer for that
  (`loop.c:615-621`). The port has no git module yet (`src/mod/git/` is
  yw13's, `docs/MAP.md`), so it never repaints here.
- **On a hosted macOS runner the two calls can end after the list opens.**
  There `git` is `/usr/bin/git`, the developer-tools shim. If the
  discovery's last job ends in the step's window, that run keeps the
  repainted screen; otherwise the first frame. That is the red: C's two
  runs disagree, the port's agree. Linux (a plain `git`) and the local
  Macs (about 10 ms a call) finish the discovery long before the list.

So the brief's reading, a frame taken before the list was drawn, does not
fit the screens: the list is in both. The step's wait (`1/1` and 300 ms of
quiet) ends on the list's first frame, which neither editor shows once
anything has repainted, and whether a repaint lands in the window is C's
git's timing.

**Witness** (Apple M2, macOS 15.5, C yew built at the pin with clang, the
port's native build at `c8443c7`), each a row written for the probe and
never pushed:

- the real git: 20 of 20 C captures and 10 of 10 of the port's keep the
  first frame, and the screen 3 s later is the same, with no frame between;
- a `git` first on the rows' PATH that waits 2 s and then runs the real
  one: C's screen 3 s after the list opened is the red screen (row 22 the
  hint, row 23 `:`), one more frame than the list's (6 to 7); the port's
  stays the first frame and no call reaches the shim from the port;
- splitting the typed command from its Enter (the text drawn first) keeps
  the first frame in both editors: the input's timing is not the cause.

### The fix

The step waits for the frame any repaint draws. After the list's frame,
HOME: on the list's one row it moves nothing and repaints the whole screen
in both editors (`picker.c:790-793`, `picker.lu:1081-1085`). Then the row
waits for the footer's command line (`:` at row 23, column 0) at a frame
boundary, then the quiet. Every later repaint, C's discovery's included,
draws the same frame again. The condition is observable, so no longer
delay is needed.

Probe (the same Mac): with the step so, C's screen with the real git, C's
with the 2 s git, and the port's are the same cell for cell
(`compare.py`), and so is each screen 3 s later.

The kept `3-list` changes in both editors from the first frame (the
message row in the footer) to the repainted one (the filter's command
line in the footer). `compare.py` holds them to each other as before; no
golden is involved.

### The red row

`lspw_open_diag_lategit`: `lspw_open_diag`'s steps over a `git` that holds
C's discovery until the row says so. `tools/lsp-rows/lategit/git`, first
on the row's PATH, waits for a gate file in the case's state directory
(`$XDG_STATE_HOME`, which the harness gives the editor and the editor its
jobs), then runs the next `git` on PATH and appends a receipt line. Run 1
opens the gate as soon as the list is seen and, in C, waits for the
receipt of `rev-parse`, the discovery's last call; run 2 opens it only
after the list's screen is kept, and waits for the receipt before it
quits. The port runs no git, so its half waits for no receipt.

- **At `c8443c7`'s step** run 1 keeps the repainted screen and run 2 the
  first frame: `lsp-rows: c lspw_open_diag_lategit.3-list: unstable
  between runs`, the CI red by name, on any host; and C's run 1 against
  the port's, `lspw_open_diag_lategit.3-list: DIFFERS`.
- **At the fix** both runs, in both editors, keep the repainted screen.

The slow part is C's git, not the server (R-yw11c-1). The server's
diagnostic is already waited for (`E:1`); a fake server slow to publish
delays the badge and nothing after it, so it cannot redden this step.

Expected red at the row's commit, on the Mac and on Linux; green at the
fix on both.

### The audit

Every `lspw_`, `lspf_` and `lspg_` step that waits on time rather than on
what it keeps or checks, and what it waits on instead:

- `lspw_references.1-picker`, `lspw_symbols.1-picker`: pickers opened from
  the command line, so the same first-frame footer. The same step (HOME,
  the footer's command line). Their selection starts on row 0, so HOME
  moves nothing.
- `lspf_hang`: `ptc_settle(c, 2000)` before checking that the initialize
  deadline (1000 ms) ended the server. Wait for the checked state itself:
  the badge without its ellipsis and no job badge.
- `lspf_slow`: `ptc_settle(c, 2000)` "past the 1.5 s reply" before the
  save. Wait for the server to be ready (`lsprow_wait_ready`, whose ESC
  nudge repaints the lagging badge).
- `lspf_deaf_quit`: `ptc_settle(c, 500)` before the save. The same.
- `lsprow_after_trigger` (`lspf_crash`, `lspf_malformed`):
  `ptc_settle(c, 600)` for the restart's 250 ms delay (`client.c:768`),
  then one ESC for the turn that restarts it. Nudge with ESC until the
  restarted server's diagnostic shows, as `lsprow_wait_ready` nudges.
- `lspw_keys_help`, C's half: `ptc_settle(c, 500)` before checking that
  ESC ? opened nothing. Check it once `:ed.keys`'s answer is on the screen
  instead: the editor reads its input in order, so ESC ? has been handled
  by then.

Kept as they are: `lspf_deadline`'s wait on the clock (the request's own
10 s deadline is the condition, `d71abca`, `7ec10b5`);
`lsprow_wait_ready`'s nudge loop (its bound is not a wait); the settles
between keystrokes in `lspf_mirror_sync`, `lspw_multicursor` and
`lsprow_command` (the editor reads keys in order, and nothing is kept
there); the `lspg_*` rows (C's own `s47_*` helpers in `registry.c`, which
wait on markers and screen text).

### Rows expected

- `lspw_open_diag_lategit`: red at its commit, green at the fix (Mac and
  Linux).
- Every other row green at the fix, its two runs stable and C's screens
  the port's, on the Mac and on Linux, with the plant restoring
  `lspw_open_diag`'s time-based wait red by name at the late-git row.
- This PR's labelled run: the macOS oracle job's `lsp-rows` green with no
  `unstable` line.
