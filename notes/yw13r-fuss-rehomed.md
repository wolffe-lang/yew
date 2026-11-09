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

- No golden, C test, runtime asset, sagitta file or pin changed. sagitta read
  at the pin and cited; git's source never read.
- No label, merge, tag, release or issue. No attribution trailers.
- Every take ran from a fresh clone at its head, pinned to its commit; every
  PTY run used a fresh root; every run set its own `HOME`, `XDG_*` and
  `TMPDIR`.
- yw13's six commit messages that cite a ruling id are its own, already
  public on its branch, and were replayed as written; this lane's commits
  cite none.

## Inputs, verified

- **Base:** trunk `3a9983ee` (yw15's note), wolf 0.2.36 / lupin 0.1.58,
  `sagitta.pin` `9ace98c2`; the pins are the same on both sides of the
  rebase. yw13's head `4912fe0` (111 commits on `1218169e`).
- **The rebase:** 109 of yw13's commits replayed onto this note's prediction
  (`595e8ba`): 78 as the same patch, 31 with a conflict or a moved context
  resolved, and 2 dropped (below). Each file that merged cleanly is
  identical to a plain three-way merge of the two heads; each of the 27 that
  conflicted is resolved by hand. The map from each yw13 sha to its rebased
  sha is in `notes/yw13r-evidence/sha-map.tsv`, so yw13's note, which cites
  its pre-rebase shas, can be followed on this branch.

### What the rebase changed

The rule: trunk's behaviour, except where yw13 is the change itself.

- **The floating panel is yw11b's.** yw13 had pulled C's `ui/panel.c`
  forward for F mode's viewer (R-yw13-5); yw11b then ported it whole, with
  hover's emphasis spans and the document mark. yw13's copy (`53063e9`) and
  its test (`a8c48ce`) are dropped, and the viewer opens trunk's panel with
  C's spec: the body copied at open, the title and the `git.ignored` role
  flagged as set (`03d9542`). The panel's key route, its draw as the last
  overlay, its close on a window release or retarget and its one command
  (`ed.ui.panel.move`, trunk's arm 1119) are trunk's; yw13's duplicates of
  each are gone. F mode's frame keeps yw13's guard before it reads the
  window (`draw.lu`).
- **Shared numbers.** LSP rename had taken input kind 2 for the command
  line's typed answers; F mode's prompt answers as kind 3 (`cmdline.lu`).
  The picker hosts were already distinct (FUSS 8).
- **Where both sides added a call, C's order.** A save is
  `yew_lsp_buffer_save`, then `yew_git_invalidate` (`ed.c:2061-2062`). A
  window release and a retarget clear the LSP highlight, then close the
  panel (`ed.c:1171-1172`, `:1192-1203`). The loop's job turn keeps
  trunk's guard (jobs or a child pending) with yw13's settle inside it,
  then `lsp_pump` (`loop.c:598-614`). The document menu shows the LSP
  section, then the git section (`ctxrows.c:405-426`), and
  `ctxrows_doc_optional_sections_are_absent_not_greyed` asserts both
  queries with no SKIP left.
- **Modules.** `mod_enabled` answers for LSP and FUSS; `--version`'s
  modules line is C's already (`modules: lsp ai fuss plugins`).
- **The keys help (yw15).** It read F mode and every git command as
  yw13's and unported. F mode is entered now, so `mode_unported_owner`
  answers no owner for F and its row carries no status. The git commands
  still refused are the twelve of `src/mod/git/editor.c`, all s53's (hunks,
  blame, the diff view, the conflict commands), so a refusal names
  `sagitta Sprint 53 (git in the editor) (yw13b)` in place of Sprint 51
  and yw13 (`ed04767`). `edit_keys_help_test` moved first (`3ec1663`): red
  at that commit on the hunk rows, which still named Sprint 51, and green at
  `ed04767`.
- **Lists both sides extended.** The five staged harness trees and the
  cmdcomp fixture copy `lsp` and `git`; `tools/check-test-cases.txt` keeps
  trunk's rows and yw13's (trunk's `edit_panel_test` row, by
  `YEW_PANEL_CASE`, in place of yw13's); `ctxrows_test` keeps every trunk
  case, and yw13's port case (the FUSS kinds' refusal) is gone with the
  refusal.
- **CI.** The oracle job keeps trunk's 270-minute cap on both legs, and
  yw13's `oracle-cmdcomp` job keeps the linux leg's perf_cmdcomp build and
  2x gate; the split tests and `nightly-red`'s `needs` name trunk's
  `macos-unit` and yw13's `oracle-cmdcomp` both.
- **Unchanged:** yw13's start-up turn for the git layer's first poll
  (`git_first_poll_deadline`, R-yw13-4) stays, since yw11b deferred the
  symbol index, which would give that turn, to yw10.

## Evidence index

## Rulings asked

## yw13b's contract, what moved (s53, at this lane's merge)

yw13b ports s53 (git in the editor: hunks, blame, the diff view, the
statusline's branch segment, `ed.group.from_dir`, the cat-file batch and
the editor runtime). Since yw13's contract named it:

- **Its refusals are its own now.** The twelve `editor.c` commands refuse
  naming `Sprint 53 (git in the editor) (yw13b)` (`cmd_owner`'s first row);
  yw13b retires that row as it ports them, and moves
  `edit_keys_help_test`'s two hunk assertions to a ported status. The
  three conflict commands hard-error with C's own words (`conflict
  resolution is not a 1.0 feature (F mode's diff and your editor are)`,
  `editor.c:1443`, `s53-editor-git.md:464-468`), a scope statement to
  port as C's message, not an unported refusal.
- **Its window state lands on trunk's `Win`,** which carries yw11b's panel,
  request records and highlight; C's `Win` adds `git_sign_gen`,
  `git_sign_buf`, `git_diff_rows` and `git_diff_intra` (`ed.c:1177-1180`).
  G62 still holds (a field read through `mut ed` loads the whole root
  aggregate): measure a native build of `edit_block_test` before and after,
  as yw13 did, and box what moves it.
- **Two of yw13's goldens are yw13b's to gate:**
  `fuss_status_conflict_ignored_incoming` and its `_ascii` twin differ from
  C only on s53's `▎` sign column (with highlighting off); with yw10's
  highlighting they join the gated set.
- **Its 23 `git_editor_*` goldens** (blame 3, diff 2, sign 7, status 11;
  4 wait on yw10), `test_gitcache`'s seven s53 cases, `test_blamecache`,
  `test_diffview`, `test_hunk`, `test_diff` and `test_git_editor`, as
  yw13's inventory lists them (`notes/yw13-evidence/inventory/`).
- **Hosts and the perf gate** as this note's rulings leave them; the
  start-up turn (`git_first_poll_deadline`) stays until the symbol index
  lands.

## Done-when
