# yw13 — FUSS: the git layer and F mode (sagitta s51, s52)

Footprint: cross-cutting

Contract: `wolf/sprints/yew/13-fuss-git/yw13-fuss-and-git.md`. Launched on trunk `f1b68316` (wolf 0.2.35), rebased once onto `1218169e` (r41q's pin, wolf 0.2.36 / lupin 0.1.58) after the PAX window; `sagitta.pin` `9ace98c2`. s53 (hunks, blame, the diff view) is yw13b's. Its code is ported only where s52 calls it (R-yw13-3). Do not merge before the detached final-head gauntlet (below) and CI are green.

## 1. Forbidden, kept

- No golden, C test, runtime asset or pin changed. `tests/fixtures/git/mkrepo.sh` and `hashes.txt` are sagitta's, verbatim (`bc3838e`). `mkxy.sh` is new (`f82b942`).
- git's source never read; its manual pages only. sagitta read and cited.
- No label, merge, tag, release, issue, planning-repo or `~/.claude` edit. No attribution trailers.
- Every PTY run used a fresh root. Every run set its own `HOME`, `XDG_*`, `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM`. kasumi work ran on CPUs 12–15 under the cores lock (`/mnt/steamlib/lanes/yw13` before the PAX window, `/home/mfwolffe/lanes/yw13` after), Mac builds under the Mac lock. One exception: a parse-only `wolf build` of a test file on the Mac ran without the lock (seconds; reported). The work stopped for the PAX window on the coordinator's word (2026-10-30T01:22Z, `v1` stopped by its container) and resumed after kasumi rejoined (2026-11-02).

## 2. Inputs, verified; the inventory (item 1)

The registry, not the contract's count (R-yw13-1). The two `#if YEW_WITH_FUSS` blocks of `tests/pty/registry.c` and `tutor_ch07` hold **60 cases: 36 yw13, 23 yw13b, 1 yw16**. Every case ran on the C oracle twice: once with the shipped runtime, once with `runtime/syntax/` emptied (`notes/yw13-evidence/inventory/`). **30 depend on highlighting** (26 yw13, 4 yw13b). Each of the 30 has an identical text grid, and its style differences sit only on highlighted source cells (`classify.txt`).

| case | sprint | owner | C without highlighting | port |
|---|---|---|---|---|
| startup_directory_workspace | s56.5 | yw13 | green | **gated, ok** |
| fuss_drawer_startup_dot, _startup_directory, _enter_tab, _split_h, _split_v, _escape_exact | s56.5/s57.5–7 | yw13 | green | **gated, ok** (6) |
| fuss_tree_light_tabs_80, fuss_memory_reentry, fuss_nonrepo | s52 | yw13 | green | **gated, ok** (3) |
| fuss_tree_unicode_80/_120, fuss_tree_compact_40/_64/_240, fuss_tree_ascii, fuss_nav_next/_prev/_row_next/_parent/_enter, fuss_tree_toggle, fuss_jump_hint, fuss_jump_clears, fuss_group_picker, fuss_group_close, fuss_actions_palette, fuss_diff_viewer_restores_layout, fuss_loading_first_frame, fuss_discard_confirmation, fuss_leave_q, fuss_leave_esc | s52 | yw13 | waits on yw10 | recorded; port frames == C without highlighting (22) |
| s57_13_fuss_file_menu, s57_13_fuss_dir_menu | s57.13 | yw13 | waits on yw10 | recorded; == C without highlighting (2) |
| fuss_status_conflict_ignored_incoming, _ascii | s52 | yw13 | waits on yw10 | recorded; also need s53's `▎` sign column (yw13b) |
| git_editor_* (23: blame 3, diff 2, sign 7, status 11) | s53 | yw13b | 4 wait on yw10 | yw13b's |
| tutor_ch07 | s58 | yw16 | green | yw16's |

Totals: yw13's 10 passable cases pass byte for byte. Of the 26 that wait on yw10, 24 match C with highlighting off, cell for cell, and the two conflict cases also wait on yw13b (`notes/yw13-evidence/nosyn-match/`: the 26 C logs, `cmpgot.py`, `g4-result.txt`). `--version`'s modules line is C's already (`modules: lsp ai fuss plugins`), so no change.

## 3. Prediction: hits and misses (`notes/yw13-evidence/prediction.txt`, written before the first change)

- **Miss.** "45 of 59 carry highlight attributes." Measured: 30 of 60. The registry also has 60 cases, not 59 (`tutor_ch07`).
- **Hit.** Three porcelain classes the pin's fixtures never exercise: 64-hex names, non-UTF-8 path bytes, and submodule fields beyond `N...`/`S.M.`. All three are now unit rows (`edde538`). `mkxy.sh` builds the last two from real git, and the differential below covers them.
- **Hit.** The first golden to disagree was `startup_directory_workspace`, on the timing of its one-frame wait. The port painted the opening frame twice (`sync_pairs=2`, kasumi `jobs/g1.log`). Cause: C's `0 + 16` stamp is measured against a boot-relative clock (G61, R-yw13-6, `ed7b5d5`).

## 4. What yw13 measured

**The git layer (s51).** `edit.git` holds the availability probe, the verb table as the only argv path, the pinned environment, detection, the wall-clock cache, the taxonomy and `ed.git.info`. The pure `git` module holds the porcelain v2 grammar and the fuss tree. **Porcelain differential** (`notes/yw13-evidence/porcelain-diff/`): sagitta's own `porcelain.o` (`cdump.c`) and the port (`git_status_dump.lu`) dump the same `status --porcelain=v2 --branch -z` bytes. The bytes come from eight real repositories (mkrepo's fixture and its four variants; mkxy's every-XY merge, its mix and its submodule), each under five status variants: **40 of 40 dumps equal**. Every prefix of the two richest streams was also dumped: **2,461 of 2,461 equal**. Units: `test_porcelain` 8 and three port rows (`edde538`), `test_gitcache` 30 (its seven s53 cases are yw13b's), and `git_layer.c` ported over real git (`edit_gitlayer_test`, 8: C's six checks, every unmerged XY, and the mix records compared as bytes).

**F mode (s52).** Entry and exit, the tree and items, glyphs, depth navigation, type-to-jump (cleared as C's W4), the verb keymap, the drawer, typed confirmations, the commit editor, pickers, the actions palette, the diff viewer over the pulled-forward panel (R-yw13-5), and the three FUSS context-menu builders. R-yw06-11 is closed: the `test_ctxrows` walk SKIPs nothing by name. Refresh keeps the toggled state and the selection (`edit_fussrefresh_test`, 2). Units: `test_fussdrawer` 27, `test_fussjump` 13, `test_fusstree` 12 (with `fuss_marker_order_and_conflict_override`), `test_fussnav` 8, `test_fussexpand` 7, `test_fusscommit` 12, `test_fusstheme` 1, `test_panel` 18 (LSP's emphasis and mark SKIP, yw11's), `fuss_commands.c` 24 over real git, `test_job_handover` (its pty legs SKIP, G60), and the symwalk notice's three rows.

**Found and fixed by the ports.**
- `0b86a7d`: F mode called a directory a file. `fuss_target_lookup` read word 2 of the lstat record (`modified_ms`) as the mode. `fuss_commands.c`'s guard case was red ("select a file to diff").
- `ed7b5d5` (with `cf6d957` reverting `32c8c45`/`0c1b2a6`): the opening frame before the loop's first turn.

**Checked machine** (`tools/check-test-cases`, 202 cases over the 10 lane files). Five cases were red on the first run; all were fixed or allowed:
- `test_gitcache` case 13: the verb's 5 s deadline fired before the case's own kill. The deadlines now read the cycle's start; alone, the case is then past the step budget (`allow … 13 budget`).
- Three `test_fussdrawer` cases: the walk's 2 ms step lists the fixture in one tick natively, but not on the checked machine. `walk_done` now ticks until the walk ends.
- The filename matrix exceeds the budget alone: `allow … 2 budget`.

**Plants** (item 5): `yw13-plant-porcelain`, `yw13-plant-argv-join` and `yw13-plant-collapse`, each the final head plus one deliberate break, each a draft PR. `notes/yw13-evidence/red-first/` holds `red.sh` (the gauntlet's `red-first` step), which builds every plant and five red-first mutations from a copy of `src/` and runs the row that must catch it, every one RED by name (`red2`, kasumi 12–15, head `f468b9c`, wolf 0.2.36; `notes/yw13-evidence/red-first/result.txt`, `COUNTS red-first not-caught=0`, `END red2 exit=0`). A first run (`8bcacaf`) left both patch plants unapplied (the container has no `patch(1)`) and did not count that; `f468b9c` applies with `git apply` and counts a failed apply.

| variant | the break | row, red by name |
|---|---|---|
| `yw13-plant-porcelain` | a `2` record read as a `1` (the rename's source path lost) | `git_porcelain_test` traps in its first case, `porcelain_status_all_records_headers_and_sort`; `edit_gitlayer_test` 0 `rename-new.txt is an entry`, 7 `the non-UTF-8 rename is an entry, its path the exact bytes` |
| `yw13-plant-argv-join` | a path verb's argv built by string join | `edit_fusscommands_test` 2 `stage a b` |
| `yw13-plant-collapse` | the rebuild skips the open memories | `edit_fussrefresh_test` 0 `the refresh keeps docs/ toggled` |
| mut-literal-env | no `GIT_LITERAL_PATHSPECS` for a verb | `edit_gitlayer_test` 5 `literal pathspecs` |
| mut-lstat-kind | `0b86a7d` undone (the lstat mode word) | `edit_fusscommands_test` 23 `ed.git.diff dir` |
| mut-symwalk | the discovery test inverted | `edit_symwalk_test` 0 ("the notice": none posted), 1 ("no notice": C's notice posted with `git` on `PATH`) |
| mut-fence | no Markdown fence dropped | `edit_panel_test` 15 `four rows (5)` |
| mut-selection | the rebuild always selects row 0 | `edit_fussrefresh_test` 1 ("the selection stays on z.txt": it moved to docs/) |

**CI.** A new gate step, `goldens, campaign 11's FUSS drawer and F mode by name (yw13's gate)`, runs the ten cases by name. The campaign-05 recorded step drops the seven now gated. A campaign-11 recorded step announces the 24 that wait on yw10 (`fa87cba`).

**Fix round (yew#102's run 41500851220 at `54ebe37`).** Every failing job read:
- E0301 `there is no module named git`: five harnesses stage their own source tree (`tools/build-demo`, `build-fuzz-cmdparse`, `build-fuzz-search`, `build-perf-search`, `run-perf-cmdcomp`) and their lists lacked yw13's `git` module. This failed both oracle jobs' demo build, `fuzz (port-2)` and `fuzz (against-c-1)` on linux and macOS. `tools/check-staged-modules` (a CI step and the gauntlet's `staged` step) follows each list's `use` closure. It was committed red first, naming all five (`6594087`), and goes green with the lists fixed (`ce71e59`: `ok (10 staged lists, every import closed)`).
- Cascades of the demo build, not defects of their own: campaign 01's and 03's goldens (`cannot resolve target/tools/demo_paint`). Also the fault-shim step's `Permission denied`: the skipped clipboard step normally makes `target/tests` as the runner, so the torture-live container made it as root. That step now makes the directory first (`4ea1203`).
- Advisories red at trunk too: macOS `notepad_restore_segv` (recorded) and the hosted jobstream 2× gate (trunk run 41361984681: ratio 3.37; here 4.15).
- The two timeouts, `port (ubuntu-latest)` at its 60 minutes and `unit (shard 2/6)` at its 120, were yw13's (G62). The native tier loads all of `Ed` for a field read through `mut ed`. The builder's LIFO delete is quadratic in a function's size. `Ed` carrying `GitCtx` and `FussMode` inline grew from 1,107 leaves to 1,355, and every function that reads `ed` grew with it. Measured on `edit_block_test`, native, `--no-cache`, kasumi 12–15:
  - the build took 160.7 s at trunk and 238.4 s with the two structs inline;
  - the WIR grew from 185 MB to 247 MB;
  - under perf, `truncate_to_mark` went from 21 % to 25 % of samples.

  `ed.git` and `ed.fuss` are now one-element lists (`ed.git[0]` is `ed->git`), and the build takes 171.0 s (codegen 80.6 s, against trunk's 80.4 s). CI's per-file builds had gone from about 85 s to 220 s.

**Gauntlet**: yw09b's wrapper (fail-fast, a `COUNTS` and an `END <step> exit=N` line per step) with yw13's paths and four steps of its own: `staged` (`tools/check-staged-modules`), `fuss36` (the ten gated cases ok, the 26 matched against `nosyn-match/c-nosyn/`: 24 SAME and only the two conflict cases DIFF), `porcelain-diff` (`run.sh`) and `red-first` (`red.sh`). Its reachable PTY inventory is 310 (yw09b's 300 and yw13's ten). The run at `54ebe37` (`gauntlet-54ebe37`) went red at `demo` with the same E0301 as CI (`END demo exit=2`, after fmt, harness, registry, oracle, native-all 217/217, checked-lane, tools-build, release and runtime-explicit green). It runs detached at this note's head, launched after the push; its pid, log and marker are in the PR body.

## 5. Rulings asked, issues, corrections

Ruling entries R-yw13-1..9 are in `docs/MAP.md` §6, each implemented as A:
1. The registry's 60.
2. The 26 that wait on yw10 are recorded and matched without highlighting.
3. s53 code only where s52 calls it.
4. The symwalk notice is pulled forward.
5. The panel is pulled forward.
6. The opening frame before the loop (G61).
7. A non-UTF-8 path in F mode is refused with C's message; the parser, tree and commit keep its bytes (G59).
8. The handover's pty legs SKIP (G60).
9. `git_layer.c`'s fake git keeps its first dump (`set -C`).

Gaps G59 (no byte argv), G60 (no pty opener), G61 (process-relative clock) and G62 (a field read loads the whole root aggregate; the builder's LIFO delete is quadratic) are listed for the orchestrator to file.
G59 and G60 still stand at wolf 0.2.36: its std has no byte argv for a spawn and no pty opener.

Not done, plainly:
- The 26 yw13 goldens that wait on yw10's highlighting claim no pass. 24 match C cell for cell with highlighting off; the two conflict cases also wait on yw13b's sign column.
- A path that is not UTF-8 cannot be staged, diffed or blamed from F mode (G59).
- `test_job_handover`'s two terminal legs SKIP (G60).
- s53 is yw13b's.

Test targets:
- [x] unit, native, on kasumi: every lane file green (listed in §4); after the rebase onto wolf 0.2.36, gitcache, fussdrawer and fussrefresh re-run green (`v1b`), the whole suite in the gauntlet's `native-all`
- [x] checked machine, case by case: 202 cases over the ten lane files; the five first-run reds fixed or allowed, re-run alone at `50b1f88` on wolf 0.2.36 (fussdrawer 15, 21, 22 and fussrefresh 0, 1 `exit(0)`; gitcache 13 now past the budget, allowed in `8bcacaf`)
- [x] porcelain differential: 40/40 streams, 2,461/2,461 prefixes
- [x] staged harness trees close over their imports (`tools/check-staged-modules`, red first at `6594087` naming the five lists, green at `ce71e59`)
- [x] compile time back to trunk's: `edit_block_test` native 238.4 s with `Ed`'s git and F-mode state inline, 171.0 s boxed, trunk 160.7 s (kasumi 12–15, G62)
- [x] yw13 goldens: 10/10 gated ok; 24/26 equal to C without highlighting
- [x] plants and red-first mutations: 3 plants and 5 mutations, 11 rows, every one RED by name (`red2`, `COUNTS red-first not-caught=0`); the plants are draft PRs
- [x] macOS F-mode PTY rows (nomad, macOS 26.4.1 arm64, the Mac lock, a worktree pinned to `b7fb08d`, wolf 0.2.36): `fuss_drawer_startup_dot`, `startup_directory_workspace`, `fuss_tree_light_tabs_80`, `fuss_nonrepo` ok by name against the release editor (sha256 `19d171aa…51e6`; `notes/yw13-evidence/macos/`)
- [ ] final-head gauntlet (detached, kasumi 12–15): launched after the PR; see the PR body
- [ ] CI at the final head: the run id read once, in the PR body
