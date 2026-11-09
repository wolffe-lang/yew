# yw13r — FUSS re-homed: yw13 on today's trunk, its perf baseline, its records

yw13 (the git layer and F mode, sagitta s51 and s52; `notes/yw13-fuss-and-git.md`)
was built on trunk `1218169e` and stalled for hosts, not code. This lane puts its
111 commits onto trunk `3a9983ee` (yw11b, yw11c, yw14 and yw15 landed since),
decides how the Fletch perf gate's baseline moves to a new host, and retakes the
records. yw13's note stands as written; this one says what the move changed.

## Prediction (written before the first change)

**The rebase.** A three-way merge of yw13's head onto trunk conflicts in 27 files.
Two are add/add: `src/edit/panel.lu` and `src/edit_panel_test.lu`, because yw13
pulled the floating panel forward for F mode's viewer and yw11b then ported it
whole (with hover's emphasis and the document mark that yw13 left out). The other
25 hold one to three hunks each, where LSP and FUSS each added a line in the same
place. Expected resolutions:

- The panel is trunk's. yw13's panel port and its test are dropped, and F mode's
  viewer is adapted to trunk's spec (`panel_spec_new(body, x, y, place)`, with
  `has_title` and `has_role` set). Expected: the viewer's frames do not move,
  and `fuss_diff_viewer_restores_layout` still equals C's frames with
  highlighting off.
- Both sides took prompt kind `2` in `cmdline.lu`, and both sides register
  `panel_cmd_move` in `impl.lu`. F mode's prompt takes the next free kind, and
  yw13's duplicate panel arm goes.
- `mod_enabled` answers for LSP and FUSS both; `--version`'s modules line is
  unchanged (C's `lsp ai fuss plugins` already).
- C's order where both sides added a call: the window release clears the LSP
  highlight, then closes the panel; a save is LSP's, then git's invalidate.
- yw15's keys help reads F mode and every git command as yw13's and unported.
  With yw13 in, its rows go red at the rebased head: F is entered, and the git
  commands still unported are s53's, owned by yw13b. The refusal's owner for
  those moves to Sprint 53 (yw13b), and the keys-help rows follow.
- Nothing else in trunk's behaviour moves. yw13's start-up turn
  (`git_first_poll_deadline`) stays, since trunk still has no symbol-index turn.

**Rows.** Every yw13 unit file green natively, and the whole unit set green,
with no new SKIP. The ten gated FUSS goldens green and 24 of the 26 that wait on
yw10 equal to C with highlighting off, as before. LSP's rows green beside F mode.
The first row I expect to go red at the rebased head is `edit_keys_help_test`'s
F-mode row, for the reason above.

**The perf gate on a new host.** The baseline in `tools/perf-fletch-baseline.txt`
was measured on a pool host that is no longer a lane host. Measured on the new one
(Linux x86-64, an Intel Core i7-12700KF, one block of three P-cores and their
hyperthreads, in yew CI's image):

- The same-run ratio half holds as it did on the old host: the sixteen named rows
  stay over 2x, the others under it, and `macrolib_scan_200` sits near the line.
- The new host runs every row faster than the old baseline. Against the old
  numbers, then, the regression half passes on every row by more than its own
  15/10 % bar, and it would not catch a regression of that size.
- A baseline measured on the new host, at trunk, three sessions under one block,
  puts every row back within the bar of its own number.

## Forbidden

## Inputs, verified

## Evidence index

## Rulings asked

## Done-when
