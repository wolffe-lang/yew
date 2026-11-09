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

### The dev-green run (no record is claimed from it)

At `5f60ccc` (the code of every later head), in yew CI's image on one
6-CPU block of the new host, from a fresh clone:

- the front end of `src/yew.lu` clean; `check-fmt` green (a first take
  went red there on `edit_keys_help_test.lu`, fixed by `5f60ccc`);
- **the whole unit set natively: 232 of 232 test files green** (two takes
  of 116), every SKIP by name (s53's diff rows for yw13b, G60's terminal
  legs, the image's missing fish, the torture shim, the symbol index for
  yw11 and yw10, the syntax engine for yw10, the profiler), none for want
  of C's fake clipboard tool or language server;
- **the checked machine** over the 23 test files the branch changes: 20
  green (per case where `tools/check-test-cases.txt` lists them), 3 past the
  step budget as whole files and green natively (`edit_draw_test`,
  `edit_job_test`, `edit_modes_test`);
- yw13's 36 FUSS goldens: the ten gated ok, 24 of the 26 that wait on yw10
  equal to C with highlighting off (`fuss_diff_viewer_restores_layout`
  among them, the viewer over trunk's panel), the two conflict cases on
  s53's sign column, as before;
- the porcelain differential: 40 of 40 streams and 2,461 of 2,461 prefixes
  equal;
- **CI's gated PTY cases: 320 of 320.** The take's own step went red on
  two, `lsp_feat_rename_diff` and `_refusal` ("fake LSP did not become
  ready"): C's rename cases find the fake server beside the editor binary
  (`tests/pty/registry.c:9857-9858`), which ci.yml's LSP features gate
  copies there and the take's step had not. With it copied, both pass, and
  the LSP rows are green beside them; the record's PTY step copies it.
- On macOS (arm64), natively: `edit_keys_help_test`, `edit_ctxrows_test`,
  `edit_modes_test`, `edit_panel_test` and `edit_fussdrawer_test` at
  `ed04767`; `red.sh` at `40cd36c`, three plants and five mutations red over
  11 rows (`notes/yw13r-evidence/red-first/macos-40cd36c.txt`). **Corrected:**
  three of those 11 rows were red for the wrong reason. The three
  `edit_gitlayer_test` probes (the porcelain plant's cases 0 and 7,
  `mut-literal-env`'s case 5) stopped at "mkxy.sh builds" before any case
  ran, because that fixture could not be built on APFS (below). Re-probed at
  `540bd26`, all three are red by their faults' own checks.

### The fifth name on APFS (the macOS take at `7ee9fe4`)

The macOS take at `7ee9fe4` went red in `edit_fusscommands_test`, case 2
(the filename matrix), on "the snapshot holds a\x80b". The two hostile-path
cases before it passed.

**The cause is the test, on a file system that refuses the name.** APFS
refuses a name that is not valid UTF-8: creating `a\x80b` fails with EILSEQ
("Illegal byte sequence"), so the fifth name is never written there. C's
case allows exactly this (`fuss_commands.c:591`: only the fifth name may
fail to materialize). It indexes the blob without a worktree file
(`index_blob_without_worktree_file`, `:334-364`), and it indexes it again
after each of its stages (`:604`, `:618`, `:624`). That is needed because,
with no file in the worktree, `git add -- <name>` stages the removal.

The port indexed the blob once, then staged the name with its own `git add`
(F mode refuses the name, G59) and never indexed it again. So the status
had no entry for it, and the snapshot could not hold it. On Linux the name
is written, so this path never ran there.

**The fix (`ab2b54b`, the test only)** indexes the blob again after that
add when the file system refused the name, as C does. It also prints that
it took this path ("the file system refused a\x80b: indexed without a
worktree file"), so a pass on such a file system names what it ran. It is
not a SKIP: on APFS the case now runs every check C's case runs there, and
C's own case passes on the same Mac.

The evidence is in `notes/yw13r-evidence/fusscmds-apfs/`:
- `red-7ee9fe4-macos.txt`: red on macOS before the fix;
- `green-ab2b54b-macos.txt`: green on macOS after it, 24 cases run, through
  the index-only path;
- `green-ab2b54b-linux.txt`: still green on Linux, 24 cases run, the name
  written, so the path is not taken;
- `c-fuss-commands-macos.txt`: C's `fuss_commands` at `sagitta.pin`, 544
  assertions ok on APFS.

### The non-UTF-8 records on APFS (the macOS take at `e0d6cb0`)

The macOS take at `e0d6cb0` went red in `edit_gitlayer_test` at "mkxy.sh
builds", before any case ran. The twelve test files before it were green,
the filename matrix's fix among them.

**The cause is the same refusal, in the port's own fixture.**
`tests/fixtures/git/mkxy.sh` (yw13's, not sagitta's) writes two names that
are not UTF-8 into its `mix` repository: `bad\376name.txt`, which it
commits and then renames to `bad\375renamed.txt` with `git mv`, and the untracked
`raw\377.txt`. Run by hand on the Mac, it stops at the first of them
(`line 120: ... Illegal byte sequence`, exit 1). C has no case to follow
here: its git-layer fixture (`mkrepo.sh`) has no such name, and C's
`git_layer` passes on the same Mac (15,371 assertions). The two records
cannot exist on APFS. An untracked record needs the file itself, and a
rename kept in the index only reads as `RD`, not `R.`.

**So the two checks SKIP by name where the name is refused, and nothing
else does:**
- `c3d4c50`: `mkxy.sh` probes the destination first. Where a non-UTF-8 name
  is refused, it leaves those two records out, builds every other record as
  on Linux, and writes the shell's reason to `DEST/raw-names-refused`.
- `f8a6e73`: the mix case then prints `SKIP port_gitlayer_mix_records: the
  non-UTF-8 rename and untracked records: the file system refuses a name
  that is not UTF-8 (Illegal byte sequence)`. It also checks that neither
  record exists, and runs its other checks.
- That first cut was still red on the Mac. The reason file quoted the
  refused name, so the test's text read of it failed and the SKIP never
  fired. `1cdb775` writes the reason alone, in ASCII; `540bd26` lets the
  file's presence decide.
- On Linux the name is written, no reason file exists, and every check runs
  as before.

**Every other fixture was checked before the retake.** `mkrepo.sh` and
`mkxy.sh` are the only fixture scripts under `tests/fixtures`. Both run
clean on the Mac at `540bd26`. None of the other test files the macOS take
runs writes a name that is not UTF-8: `edit_job_test` sends such bytes
through a job's stdin and stdout, and `git_porcelain_test` parses them from
memory, neither as a file name.

The evidence is in `notes/yw13r-evidence/gitlayer-apfs/`:
- `red-e0d6cb0-macos.txt` and `mkxy-by-hand-e0d6cb0-macos.txt`: the red,
  and the fixture's own refusal;
- `red-f8a6e73-macos.txt`: the first cut, still red;
- `green-540bd26-macos.txt`: the fixture scripts' dry run, the test green
  with the SKIP by name (8 cases run), and C's `git_layer`;
- `green-540bd26-linux.txt`: both changed test files green on Linux, with no
  SKIP;
- `red-first-540bd26-macos.txt`: the three re-probed rows.

The three re-probed rows are red by their faults:
- the porcelain plant's case 0, at "rename-new.txt is an entry";
- its case 7, at "a C. copy";
- `mut-literal-env`'s case 5, at "the child's GIT_LITERAL_PATHSPECS: want
  `1`, got absent".

## Rulings asked

### R-yw13r-1: the Fletch perf gate's baseline, on a new host (decided: A)

**The gate** (`tools/fl-headless/compare.py`) has two halves.

- **The ratio half** fails a row whose port/C median is over 2x, unless
  `tools/perf-fletch-misses.txt` names it for the host. The host string is
  `linux-x86_64`, which every Linux x86-64 host shares.
- **The regression half** fails a row whose median is over its baseline by
  15 % and whose minimum is over it by 10 % (`tools/perf-fletch-baseline.txt`).
  It is what holds a named row to the number it was named at.

Of the 17 rows the gate holds, 16 are named at this head
(`macrolib_scan_200` among them, R-yw13-11). So the ratio half by itself
gates one row (`parse_only`) and the concat-join ratio. The baseline was
measured on a pool host that is no longer a lane host: the VM rows at
yw08's head, the editor rows at yw09's. The tool can't hold the two halves
apart: `--advisory`, which hosted CI uses, relaxes both at once
(`compare.py:177`, `:186-191`), a missing baseline fails (`:183-187`), and
`--host` selects only the named-MISS rows (`:138`).

**Measured** on the new host: an Intel Core i7-12700KF, one block of three
P-cores and their hyperthreads, yew CI's image, the release tier, the
block's two locks and its light lock held (nothing else on the block),
host load 5 to 6 from the other blocks. Three sessions of `compare.py`
exactly as the gauntlet's perf steps run it, at trunk `3a9983e`
(`notes/yw13r-evidence/perf/`):

| row | old baseline median / min (ns) | trunk medians, % of it | trunk mins, % of it | spread of medians | port/C |
|---|---|---|---|---|---|
| `fib24` | 28,027,820 / 25,210,081 | 76 75 75 | 83 83 83 | 0.7 % | 4.25-4.27x |
| `map10k` | 4,722,112 / 4,118,359 | 77 78 77 | 87 88 87 | 1.0 % | 3.03-3.09x |
| `motion100k` | 47,251,312 / 41,272,080 | 76 75 74 | 86 85 84 | 3.4 % | 2.24-2.29x |
| `startup` | 116,695 / 108,904 | 93 97 92 | 97 99 97 | 4.9 % | 2.35-2.54x |
| `parse_only` | 261,712 / 226,421 | 92 83 82 | 103 94 92 | 13.1 % | 1.09-1.23x |
| `motion_dispatch` | 536,317,270 / 487,700,021 | 82 82 82 | 89 90 87 | 1.1 % | 2.63-2.70x |
| `fib27` | 117,187,698 / 112,993,264 | 80 80 81 | 82 83 83 | 0.9 % | 4.31-4.56x |
| `map_heavy` | 482,685,732 / 389,998,012 | 83 82 83 | 103 101 101 | 1.2 % | 7.27-7.44x |
| `strbuild_join` | 12,302,599 / 11,922,394 | 82 82 82 | 83 84 84 | 0.7 % | 3.93-4.05x |
| `strbuild_concat` | 192,663,813 / 181,508,787 | 87 87 86 | 92 92 92 | 1.0 % | 3.67-3.72x |
| `join5k` | 2,722,344 / 2,507,045 | 76 76 78 | 83 83 85 | 2.6 % | 3.27-3.33x |
| `list_sort` | 130,514,469 / 124,292,345 | 84 84 85 | 87 87 89 | 1.5 % | 4.04-4.13x |
| `config_load` | 2,299,722 / 2,263,908 | 107 103 105 | 102 104 106 | 3.5 % | 2.74-2.83x |
| `config_reload_500` | 6,414,120 / 6,333,094 | 113 111 110 | 111 110 109 | 3.1 % | 3.32-3.43x |
| `macrolib_scan_200` | 1,854,969 / 1,819,383 | 111 114 114 | 111 112 110 | 2.7 % | 2.01-2.06x |
| `motion_editor` | 1,074,012,631 / 1,060,999,975 | 101 101 100 | 101 102 101 | 0.7 % | 7.32-7.42x |
| `query_cur_pos` | 521,180,129 / 519,939,057 | 106 104 105 | 106 104 105 | 2.1 % | 35.20-36.19x |

- **The old baseline is stale both ways.** A row regresses only when its
  median and its minimum both cross their bars, so a row can hide a
  slowdown as large as the bigger of its two margins. The VM rows run at
  74-97 % of the old numbers, and could slow by 19-52 % unseen (`fib24`
  52 %, `startup` 19 %). The editor rows run at 100-114 %:
  `config_reload_500` and `macrolib_scan_200` have 2 % and 1 % of room
  left, `config_load` 7 %, `query_cur_pos` 8 %, `motion_editor` 14 %. The editor rows were measured at yw09's
  head, before the LSP client landed, so some of that is trunk's own drift.
  The old host can't separate the two now.
- **The sessions agree** in this set: every row's three medians are within
  3.5 % of each other, except the two shortest rows, `startup` (4.9 %)
  and `parse_only` (13 %, a 0.24 ms row whose first session ran slow).
  Later sets show this is not typical (R-yw13r-3).
- **The ratio half** reads as it did on the old host: the sixteen named
  rows are over 2x, and `parse_only` is under it. At trunk,
  `macrolib_scan_200` reads 2.01-2.06x and is not named there, so trunk
  itself is red on this host by the ratio half (`failures=1` in every
  session). yw13's head names it (R-yw13-11).

**The head against trunk**, three more trunk sessions interleaved with
three at this branch (`5f60ccc`), on the same block an hour later, host
load 5 to 6:

| row | head / trunk, paired sessions (%) | head against the old baseline | head against a baseline from trunk's first three sessions |
|---|---|---|---|
| `fib24` | 100 102 99 | ok,ok,ok | ok,ok,ok (100 102 100 %) |
| `map10k` | 100 104 100 | ok,ok,ok | ok,ok,ok (101 103 100 %) |
| `motion100k` | 98 100 98 | ok,ok,ok | ok,ok,ok (98 99 98 %) |
| `startup` | 37 98 102 | ok,ok,ok | ok,ok,ok (95 96 94 %) |
| `parse_only` | 102 102 97 | ok,ok,ok | ok,ok,ok (91 91 89 %) |
| `motion_dispatch` | 98 101 101 | ok,ok,ok | ok,ok,ok (100 99 100 %) |
| `fib27` | 98 98 99 | ok,ok,ok | ok,ok,ok (101 100 101 %) |
| `map_heavy` | 98 103 102 | ok,ok,ok | ok,ok,ok (101 103 104 %) |
| `strbuild_join` | 102 99 101 | ok,ok,ok | ok,ok,ok (103 101 101 %) |
| `strbuild_concat` | 100 101 101 | ok,ok,ok | ok,ok,ok (101 101 102 %) |
| `join5k` | 101 100 101 | ok,ok,ok | ok,ok,ok (102 98 99 %) |
| `list_sort` | 100 87 99 | ok,ok,ok | ok,ok,ok (99 97 98 %) |
| `config_load` | 105 103 97 | ok,ok,ok | ok,ok,ok (103 103 98 %) |
| `config_reload_500` | 104 98 102 | REGRESSION,ok,ok | ok,ok,ok (102 101 102 %) |
| `macrolib_scan_200` | 103 89 104 | REGRESSION,ok,REGRESSION | ok,ok,ok (101 99 103 %) |
| `motion_editor` | 101 103 104 | ok,ok,ok | ok,ok,ok (102 103 104 %) |
| `query_cur_pos` | 100 101 100 | ok,ok,ok | ok,ok,ok (101 102 101 %) |

- **yw13 costs the editor rows 0-3 % and the VM rows nothing measurable.**
  Paired by session, the means are `motion_editor` +2.7 %,
  `config_reload_500` +1.6 %, `config_load` +1.4 %, `query_cur_pos`
  +0.4 % and `macrolib_scan_200` -1.3 %. The editor's perf driver also
  takes 21 % longer to build (2,896 s, against trunk's 2,391 s: G62).
- **Against the old baseline the head goes red** in two of three sessions,
  on the two editor rows that trunk already crowds. **Against trunk's own
  numbers on this host it is green** in all three, every row within 4 %.
  Trunk's two sets of sessions, an hour apart, agree within 3 % by row.
- **Host blips are real here.** Two of the three later trunk sessions had
  rows run slow: `startup` at 2.8x its usual median in one, and
  `list_sort` and `macrolib_scan_200` at +14 % in the other. Of all nine
  sessions, those two had blips, and the head's three had none. Against
  a baseline from the first three sessions, the `startup` blip alone
  fails the regression half. So a
  record, whose three perf steps must each pass, can go red on a blip
  that is no regression, as yw13's first take did on the old host.

**Options.**

- **(A) Re-home the baseline.** Each row is the maximum of three quiet
  sessions at trunk on one P-core block of the new host, as yw08's and
  yw09's rows were the maximum of three; the why column names the host by
  its hardware and block. The bar is unchanged, and no source changes. The
  perf steps run on a P-core block, never on the block that mixes in
  E-cores. The cost: a host move means a re-measure again, and other
  blocks' load sits inside the bar (sessions agree within 3.5 % on all
  but the two shortest rows).
- **(B) The ratio half gates alone, the baseline advisory.** This needs a
  source change: a flag that relaxes the regression half only. It does not
  depend on the host. But the named rows skip the ratio half by design, so
  16 of the 17 rows would have no gate at all, and a VM slowed to twice its
  time would pass.

**Decided: (A)**, with the rule below committed with the numbers.

**Recommended: (A).** It keeps both halves, needs no source change, and
on this host it separates yw13's 0-3 % from the old baseline's 11-15 %
(the old numbers fail the head on rows where trunk itself has 1-2 % of
room, and pass slowdowns of up to half on the VM rows).
If ruled A:

- the committed numbers are re-measured at trunk before the record, three
  sessions under one P-core block's three locks, kept only if every row's
  medians agree within 5 % (the two shortest rows within 10 %); a set that
  doesn't is retaken (superseded by R-yw13r-3: rows, not sets, drop a
  blip);
- each of the record's perf steps waits, in a printing loop of at most an
  hour, for the host's one-minute load to fall to 3 or under (the
  other blocks' work) before it measures. A perf step that still goes red
  names its row, and the record says so; the head is then measured against
  trunk interleaved, as above, before any rerun.

### R-yw13r-3: the baseline's agreement rule, measured (decided: c)

**A correction to R-yw13r-1.** It claimed the sessions agree within 3.5 %
on every row but the two shortest. That was one set. Over the 18 quiet
trunk sessions taken on one block (load 1.5-3 for the twelve taken under
the rule):

- ten have no row more than 5 % (10 % for `startup` and `parse_only`)
  from that row's median;
- the other eight each have one or two rows slow by 5-15 %, on rows that
  change from session to session (`macrolib_scan_200` 4 times,
  `map_heavy` twice, and `startup`, `parse_only`, `fib27`,
  `strbuild_join`, `list_sort`, `config_load` and `config_reload_500`
  once each). One `startup` session ran at 2.7x its median.
- The VM-heavy rows `fib24`, `map10k`, `motion100k`, `motion_dispatch`,
  `strbuild_concat`, `motion_editor` and `query_cur_pos` never left 3.3 %.

So a set of three passes the ruled 5 % rule only 9 % of the time (72 of
the 816 sets of three these 18 sessions make). Four sets were taken under
the rule, and none was kept; one failed on a single row at 5.4 %. Against
a baseline from any three clean sessions, the regression half (+15 %
median and +10 % min, both) would have failed one of the 18 sessions: the
2.7x `startup` one. The gate's own bar absorbs this host's noise; the 5 %
keep rule does not.

- **(a) Keep the rule:** retake sets until one is kept. About one set in
  eleven passes; each set is three takes of the block, minutes each when
  it is free.
- **(b) Widen it to 10 % (15 % for the two shortest):** half the sets
  pass. A kept set can carry a blip of up to 10 % into a row's maximum,
  which loosens that row's gate by as much.
- **(c) Keep 5 %, but reject by row, not by set:** take five sessions;
  each row's baseline is the maximum over the sessions within 5 % (10 %)
  of that row's median of the five, and the set is kept only if every row
  has three such sessions. A blip costs one row of one session, not the
  set, and the numbers stay as tight as the rule meant.

Recommended: **(c)**. Under (a) a loop retook sets meanwhile.

**Decided (c)**, with one condition: no choosing among sessions already
taken. The loop under (a) was stopped in its first set and its files
voided. Tonight's earlier sessions stay as evidence only, since picking a
favourable group after the fact biases the gate. Five fresh consecutive
sessions came next, each its own take of the block's three locks, each
after the printing load wait, with at most three groups of five
(`notes/yw13r-evidence/perf/rule-c-group1.txt`, `basecheck_c.py`).
**Group 1 was kept.** Every row keeps three or more sessions:

- 14 rows keep all five;
- `config_reload_500` drops session 2 (+6.8 %);
- `config_load` drops sessions 1 and 2 (+11.1 %, +12.5 %);
- `macrolib_scan_200` drops sessions 1 and 2 (+16.1 %, +15.8 %).

Sessions 1 and 2 ran back to back while another lane's light step worked
on the same host, and only the file-system editor rows moved. Each row of
`tools/perf-fletch-baseline.txt` (`68e6a0c`) is now the maximum over its
kept sessions.

Against these numbers, this branch's three sessions from the A/B above
regress on no row; the closest is at 104 % of its baseline median
(`config_load`, `motion_editor`).

### R-yw13r-2: yew#115's CI caps under this branch's record (decided: A)

yew#115 (open, on the same trunk) raises the port job's Linux cap to 90
minutes and scales the goldens selftest's quiet windows by 4. This branch
makes each release build of the editor longer still (the perf driver's
build: +21 %), so its own PR run wants those caps. A merge reorders heads:
whichever of the two lands second is rebased, and a rebased head voids its
local record.

- **(A) Carry yew#115's three commits here, unchanged, before the record.**
  They apply cleanly onto this branch, and `ci/macos-split-test.py` and
  `ci/legs-test.py` pass with yw13's `oracle-cmdcomp` job beside them. If
  this branch merges first, yew#115 has nothing left to merge; if yew#115
  merges first, this branch's rebase drops the three as already applied,
  but the head moves.
- **(B) Merge yew#115 first, then rebase here before the record.** It is
  the cleaner history, but it waits on yew#115's own red macOS oracle job.

Recommended: **(A)**, so the record doesn't wait on yew#115, with this
branch merged before it. **Decided A:** the three are carried unchanged
(`09335f0`, `fe8edc7`, `7d6d2b7`, each the same patch as yew#115's
`c06fc57`, `03171fd`, `c8443c7`), and this branch merges first.

### R-yw13r-4: the refused fifth name, C's path or a SKIP (decided: A)

The filename matrix's fifth name cannot be written on APFS (above). There
were two ways to handle it.

- **(A) Do what C does.** C's case permits the refusal, keeps the name in
  the index only, and indexes it again after every stage. The port had
  dropped that re-add, and putting it back is the fix. The printed path line
  keeps a pass on APFS from reading as the pass on Linux.
- **(B) SKIP the case by name wherever the name is refused.** This was the
  first proposal. It assumed the snapshot could not hold the name on APFS,
  but it can: C's case holds it and passes on the same Mac (544 assertions).

**Decided A:** a SKIP would hide a case C runs and passes on APFS. The
fix is `ab2b54b`. The non-UTF-8 records of `mkxy.sh` are the opposite case.
C has no such records, and they cannot exist on APFS, so their two checks
SKIP by name with the measured reason (above).

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

- [x] yw13 on trunk `3a9983e`: 109 commits replayed, 2 dropped (the panel
  and its test, now trunk's), every clean-merged file equal to a plain
  three-way merge; what moved is listed above.
- [x] Prediction scored: the conflicts, the panel's resolution, the shared
  input kind and the duplicate command arm, `--version`, and the keys
  help's row as the first red, all as predicted. Missed: "the new host runs
  every row faster than the old baseline". The VM rows do; the editor rows
  run level or slower. Missed by omission: the fake LSP server beside the
  editor, which the rename goldens need and a gauntlet's PTY step must
  copy as CI does.
- [x] Dev-green: the whole unit set natively (232 of 232), the checked
  machine on every changed test file, yw13's FUSS goldens and porcelain
  differential, CI's 320 gated PTY cases and the LSP rows; macOS natively
  on the files the rebase touched by hand.
- [x] The keys help's rows red first (`3ec1663`) and green (`ed04767`).
- [x] `red.sh`: three plants and five mutations red by name on macOS. The
  three `edit_gitlayer_test` rows were red only at the fixture at
  `40cd36c`; they are red by their faults at `540bd26`.
- [x] The Fletch baseline re-homed: five quiet sessions at trunk, rows not
  sets dropping a blip, every row on three or more (`68e6a0c`).
- [x] yew#115's CI caps carried unchanged.
- [x] README read and refreshed (`1ea45d9`, README only): campaign 09 in
  the status line, the editor's Fletch rows and their re-measured baseline.
- [x] The filename matrix on APFS: red on macOS at `7ee9fe4`, green at
  `ab2b54b` on macOS and on Linux, as C's own case is on APFS.
- [x] The non-UTF-8 records on APFS: red on macOS at `e0d6cb0`, green at
  `540bd26` with their two checks SKIPped by name, and every check run on
  Linux. Every fixture script was dry-run on the Mac.
- [ ] The record at this branch's head, the three plants re-cut onto it and
  red by name, the macOS take, and CI: in the PR body, since a commit after
  them would move the head they were taken at.
