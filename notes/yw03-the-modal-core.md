# yw03 — the modal core

**Opus 5.5, crawl 54, 2026-10-20.** Contract: planning repo
`sprints/yew/03-the-modal-core/yw03-the-modal-core.md` at `e0d646c`
(drafted by yw02 as this repo's `notes/contracts/yw03-the-modal-core.md`).
Ports sagitta campaign 03 (`s13`–`s17` at `sagitta.pin`): the
named-command registry and the key trie, `Ed`/`Win` and the event loop,
modes L/W/B/H/I, the viewport, gutter, statusline and message line, the
W and B unit engines with UAX #29 word boundaries, H mode and
multi-cursor.

## The toolchain at the lane's start

`gh release list -R wolffe-lang/wolf-lang` at 2026-10-20T17:27Z: the
latest release is **v0.2.33** (2026-10-19T18:37Z); r39 (0.2.34) is in
flight and unreleased. The pin yw02 left stands — wolf 0.2.33
`85dab5d7`, lupin 0.1.54, wolf-std `cceda63` — so the loop's wait is
`os_signal_wait_fd` with the `VTIME` interim (#93 R2, `term.tty_wait`),
and G2/G3/G4/G30 stay met, not adopted. If 0.2.34 lands mid-lane the
lane finishes at 0.2.33 and the bump is yw04's.

## Rulings taken at launch (the orchestrator's, recorded)

- **R-yw02-1 = A, R-yw02-2 = A, R-yw02-3 = A.** The live-editor torture
  lane (`yew-live-torture.c`, which types `:ed.quit_force`) is yw04's;
  the batch lane is yw09's.
- **The registry's shape** (contract deliverable 1): a table of names,
  flags and command ids plus ONE `invoke` that matches on the id; the
  unit engines a `match` on a unit kind. No function value crosses a
  module boundary (wolf-lang#806, G19/G20) — forced by the language. A
  cleaner shape the release tier accepts would be recorded as a
  proposal, not switched to mid-lane.
- **The pin**: 0.2.33 (above).

## Prediction (written 2026-10-20, before the first port line)

The contract's, kept: the registry ports as data plus one `match` with
no function value crossing a module boundary, and the release tier
builds it; the ownership seam (the window's `CursorSet` moved into the
buffer's `EditCtx` for an edit and back) costs one move per edit,
invisible in the 2× gate; the notepad, `s15`, `s16` and `s17` goldens go
green without a golden edited; `tables_wb` regenerates byte-identical to
sagitta's arrays; the editor's cold start → first paint within 2× of C
yew's (the demo's was 1.51× at yw01) and keypress → paint within 2×; the
only campaign-03 rows red at the end are the ones that reach a named gap
(a subprocess clipboard, if any golden does) or E mode.

The lane's own, from reading sagitta's PTY registry and runtime before
any code:

1. **Every one of the 62 cases tears down through the command line.**
   `quit_editor_cleanly` and `force_quit` (`tests/pty/registry.c:679-
   700`) type `esc`, `:`, `ed.quit` (or `ed.quit_force`) and `enter`,
   then `ptc_expect_exit(c, 0)`; the dirty-prompt cases snapshot AFTER
   `:ed.quit enter` (`registry.c:908-952`) and `notepad_restore_suspend`
   reaches `:ed.suspend` (`harness.c:1508-1675`). The case's verdict is
   the snapshot AND the exit, so with no `:` every campaign-03 case is
   red at its teardown, the snapshot green or not. Predicted: M-YW3
   needs the narrowest `:` — E mode entered by `:`, the typed name
   collected, `enter` invoking it through the registry (C's
   `ed.cmdline.accept`), `esc` cancelling — and nothing else of sprint
   18 (no editing keys beyond insert/backspace, no history, no
   completion, no ranges). That collides with the launch decision "yw03
   carries no `:` line" (taken for R-yw02-1's torture lane); the lane
   implements the narrow `:` and asks **R-yw03-1** (§5).
2. **The goldens are C yew at the pin, not at sprint 14.** Every editor
   frame paints row 0 as the tab strip (`ui/tabs.c`, campaign 05's), in
   the default theme's colours (`runtime/themes/quiver-dark.fl`, a
   Fletch data file, campaign 08's), with the keymap and options that
   `runtime/init.fl` sets (381 `bind` rows and one `set({...})`, run by
   the Fletch VM before the first paint, campaign 07's). Predicted: the
   port copies both runtime files verbatim (`runtime/`, as the map
   says the first lane to need them does), embeds them as generated
   string constants with a drift check, and reads them at startup with
   a reader for exactly their flat shape (a `set` of literals, `bind`
   calls, a theme data literal) — the binding rows going through the
   same `BindRow` builder Fletch's `bind()` will feed in s36 — and
   paints the single-tab strip only (tabs, groups and the strip's
   overflow are yw05's). Asked as **R-yw03-2** and **R-yw03-3**.
3. **Twelve of the fifteen `s15_*` cases are `demo_paint` scenes**
   (`spawn_scene`, `registry.c:47-55`; `demo_paint.c:392-500`): the
   port's demo grows the `s15_*` scenes over the editor's real draw
   path; `s15_resize_roundtrip`, `s15_mode_l` and `s15_mode_i` drive
   the editor.
4. **The live-restore cases need nothing new**: `notepad_restore_term`
   and `_segv` signal the editor (listen + re-raise, and the guard),
   `_kill` SIGKILLs it (the guard), `_suspend` types `:ed.suspend`;
   predicted green through yw01's interim B once the editor exists.
5. **Typeahead coalescing**: `notepad_burst_keys` and `_burst_paste`
   require 4,096 keys (or a 4 KiB paste) to paint exactly ONE
   synchronized frame (`registry.c:1135-1205`); predicted green by
   draining the tty before dispatch as `loop_read_input` does.
6. **Module shape**: every campaign-03 `ui` file takes the `Ed` and `ed`
   calls every one of them, a cycle wolf refuses (E0303), so the port's
   `viewport`, `gutter`, `statusline`, `message`, `draw` and `win` live
   in `edit` (`src/edit/*.lu`, sagitta's file names kept) — yw02's
   answer for `coords`.

Hits and misses are recorded in §3 as they were measured.

## The plan

The contract is the directive; this is the order the lane works in.

1. **The registry and the keymap** (s13): `edit.cmd` — the descriptor
   table of every command C registers (names, arity, flags, help,
   recorder word), each a stable id; one `invoke` matching the id, an
   unported id answering C's deferred shape naming its sprint and lane;
   `edit.keymap` — key specs, the sorted-row lookup with stacked layers,
   the chord state machine and counts; `runtime/init.fl` embedded and
   read into `BindRow`s. `test_keymap`, `test_cmdreg`.
2. **The notepad** (s14): `Ed`, `Buffer` (an `EditCtx` without its
   cursor set), `Win` (its `CursorSet`), the loop over `term.tty_wait`,
   the timer heap, typeahead coalescing, modes and the Esc law, I mode,
   open with the recovery prompt, save, the dirty-quit prompt, the
   narrow `:`; the tab strip for one tab; the theme. `test_modes`,
   `test_loop`; the 25 `notepad_*` goldens.
3. **The view** (s15): viewport, gutter, statusline, message line,
   resize; the demo's `s15_*` scenes. `test_viewport`,
   `test_statusline`, `test_message`, `test_gutter_sign`; 15 goldens.
4. **W and B** (s16): the generator's `--word-break` mode and
   `unicode.wordbreak`, the word and block engines. `test_wordbreak`,
   `test_word`, `test_block`; 6 goldens.
5. **H and multi-cursor** (s17): selections, the actions, the lifts,
   one-transaction editing. `test_select`, `test_hmode`,
   `test_multicursor`, `test_edit_cmds`; 16 goldens.
6. **The gates**: `tools/check-test` both lanes with the per-case
   checked run for every `[native]` fallback; the 62 goldens by name in
   CI; the 2× gate on the editor on kasumi; the note, the map, yw04's
   contract, the PR.

Leaf units that need only the text engine and the unit-engine
interface (the word-break tables and the W engine, the B engine) run as
forks of the lane on their own branches once the interface is landed;
the editor core is the lane's own.

## 1. Forbidden

The seven standing rules and `sprints/RULES.md`, as the brief gave them,
and what the lane did under each. sagitta at `9ace98c2` read and cited
`file:line` (`~/lanes/yw03/sagitta`, cloned at the pin on both hosts,
read-only); no other editor's keymap, modal engine, viewport or
multi-cursor source, ever. wolf-lang's own runtime source was read once,
at the `v0.2.33` tag, to find how `os_signal_wait_fd` and
`os_term_set_mode` wait (`crates/wolf_rt/src/signal.rs:703-860`,
`term.rs:160-164`: `poll(2)`, and `tcsetattr(TCSADRAIN)`). No golden
edited: no golden disagreed. No dependency but wolf-std. The registry's
shape was ruled at launch and no function value crosses a module
boundary. No attribution trailer in any commit or PR body, whatever a
harness reminder said. No build or test on nomad-1: every build, test,
golden and measurement ran on kasumi (`bash -c`; `commit.gpgsign` was
never touched — commits are made on nomad-1). Every run of C yew and the
port, the oracle's tools included, had a scratch `HOME`,
`XDG_STATE_HOME`, `XDG_CONFIG_HOME` and `YEW_LOG`. No merge, no tag, no
issue filed or closed (§5 lists them). `~/.claude` untouched.

**Two RULES §5 slips, reported.** Signals go only to processes the test
started, inside a container. (1) At 2026-10-20T18:42–18:43Z the lane ran
`tools/goldens --filter notepad_` against the port on kasumi's host
process table once — the four `notepad_restore_*` cases signal their
own child (`SIGTERM`, `SIGSEGV`, `SIGKILL`, `SIGTSTP`) — before moving
every PTY run into a throwaway `archlinux:base-devel` podman container
(`--network none --userns=keep-id`, the lane directory at its own path,
under `taskset -c 0-3`) and re-running the 25 there (25/25). (2) At
2026-10-20T19:05Z the lane ran sagitta's `perf_latency` against the
port on the host; the port did not quit (G34, below) and the harness's
`yew_live_pty_close` SIGKILLed its own child (`live_pty.c:489-501`).
Every later perf run, memory probe and `tools/check-test` ran in the
container. Neither touched another process.

## 2. Inputs, verified

- The contract at the planning repo's `e0d646c` (read from
  `origin/trunk`, never the shared checkout's working tree); the track
  index's rulings #89/#93 and R-yw0N; `sprints/RULES.md`; `docs/MAP.md`
  and `notes/yw02-the-text-engine.md` at yew trunk `ab8bab0`, the
  lane's base (yw03 is a fast-forward of `origin/trunk`).
- **The toolchain**: `gh release list -R wolffe-lang/wolf-lang` read at
  2026-10-20T17:27Z, 19:43Z and 19:52Z: the latest is **v0.2.33**
  (2026-10-19T18:37:53Z) every time; the pin stands (wolf 0.2.33
  `85dab5d7`, lupin 0.1.54, wolf-std `cceda63`, by digest through
  `tools/fetch-toolchain`). wolf-lang#802 (G34's widening) is CLOSED,
  merged at `808ce11a` and unreleased.
- **sagitta** `9ace98c2` (`sagitta.pin`); the oracle tree yw02 built
  (`target/oracle/sagitta`, gcc, `build -> build-gcc`), plus the three
  editor perf harnesses this lane adds to `tools/oracle`
  (`perf_startup_s56`, `perf_latency`, `perf_nullexec`).
- **The goldens**: 62 campaign-03 PTY cases from `tests/pty/registry.c`
  by name (25 `notepad_`, 15 `s15_`, 6 `s16_`, 16 `s17_`); twelve
  `s15_` cases are `demo_paint --scene` (`registry.c:47-55`); the PTY
  harness writes a user `init.fl` (`let lsp = {servers: {}}`) into
  every case's `XDG_CONFIG_HOME` — read, not predicted (§3).
- **The unit suites**: `test_keymap` (3), `test_cmdreg` (5),
  `test_modes` (11), `test_loop` (7), `test_viewport` (14),
  `test_statusline` (8), `test_message` (6), `test_gutter_sign` (4),
  `test_word` (3), `test_wordbreak` (1), `test_block` (14),
  `test_select` (8), `test_hmode` (13), `test_multicursor` (31),
  `test_edit_cmds` (28): 156 cases, each counted in
  `tests/unit/registry.c`.

## 3. Prediction — the hits and misses

**The contract's.**

- *The registry ports as data plus one `match`, no function value
  crossing a module boundary, and the release tier builds it* — **HIT.**
  `edit.cmdtab` (408 rows generated from `cmd.c`), `edit.cmd` (the
  registry as a value), `edit.impl.run_impl` (one `match` on 119
  implementation ids); both tiers build with warnings denied. One
  surprise on the way: a `match` arm on a const NAME is a binding
  (W0801), so the arms are literal ids with the name in a comment.
- *The ownership seam costs one move of the cursor set per edit,
  invisible in the 2× gate* — **HIT, and cheaper than predicted**: a
  swap through a local, no allocation at all. Measured on the region
  ledger at three points of one edit loop (20 and 20,020 edits apart):
  224 / 224 / 224 bytes with the swap against 224 / 1,184 / 961,184
  with a placeholder `List` left in the window — 48 B an edit, G33's
  shape, which is why the seam swaps.
- *The notepad, `s15`, `s16` and `s17` goldens go green without a golden
  edited* — **HIT**: 62/62 by name on both tiers (§4), no golden
  touched.
- *`tables_wb` regenerates byte-identical to sagitta's arrays* —
  **HIT** (`tools/check-tables`, the word fork's evidence).
- *Cold start → first paint and keypress → paint within 2× of C yew's*
  — measured in §4.
- *The only campaign-03 rows red at the end reach a named gap or E
  mode* — **HIT, differently shaped**: no campaign-03 row is red; the
  editor's recorded step keeps the five `startup_`/`fuss_drawer_startup`
  rows, which need several startup files (yw05), the workspace resume
  (yw06) or a directory argument (yw13). No golden reached a subprocess
  clipboard.

**The lane's own six** (written before the first port line):

1. *Every case tears down through `:` — M-YW3 needs a narrow `:`* —
   **HIT**; implemented (`edit.cmdline`) and asked as R-yw03-1 (§5).
2. *The goldens are C yew at the pin: the tab strip, `quiver-dark`,
   `init.fl`'s keys* — **HIT**, with one row missed: the harness also
   writes a USER `init.fl` (`let lsp = {servers: {}}`) into each case's
   config directory. The first port read every user `init.fl` as "needs
   Fletch" and put a message on the footer — `notepad_open`'s first
   diff, row 28. The reader now takes `let NAME = <literal>` (a binding
   later campaigns read, `Config.globals`); R-yw03-2's wording carries
   it.
3. *Twelve of the fifteen `s15_` cases are `demo_paint` scenes* —
   **HIT**: the view fork ported them over the editor's real
   layout and draw (`tools/demo-paint`), proved by a plant that moved
   the gutter's floor and turned all four gutter scenes red.
4. *The live-restore cases need nothing new* — **HIT**: the four
   `notepad_restore_*` cases were green on the first run.
5. *Typeahead coalescing by a drain* — **HIT**: `notepad_burst_keys`
   and `_burst_paste` paint one synchronized frame through
   `term.tty_drain_begin/end`.
6. *The `ui` files live in `edit`* — **HIT** (E0303 otherwise).

**Not predicted.**

- **Enter (G34).** The 62 goldens press Enter as kitty's `CSI 13 u`;
  sagitta's `perf_latency` and `perf_startup` quit with a raw `:q!\r`.
  At 0.2.33 the port's raw mode cannot clear `ICRNL` (yw01's W1), the
  kernel hands the editor LF for that CR, and LF decodes as `C-j`,
  bound nowhere — the port sat at `:q!` and the harness SIGKILLed it
  (§1). Kitty does not save a real terminal: C pushes `\x1b[>21u`
  (`input.c:58`), which leaves Enter legacy. Ruling R-yw03-4, interim
  implemented: a legacy LF reads as Enter while the raw mode is in
  force (`bcf2163`).
- **Keywords**: `impl`, `take` and `use` cannot name a field or local.
- **G35**: a `take` parameter stored into a field of a `mut`
  parameter's list element is E1004 (the lifts store in the caller).

## 4. The sections, and what yw03 measured

All on kasumi (16 cpus, Linux 7.2.8), wolf 0.2.33, in the container
under `taskset -c 0-3` unless said; the loads quoted are `uptime`'s
one-minute figure, which other lanes' builds drove between 13 and 51
through the lane. The port's `src/edit/` is 37 files, 17,618 lines (422
generated in `cmdtab.lu`, 835 in `runtime_blob.lu`) against sagitta's
19,245 in the campaign-03 files it ports from; the tests are 19 new
files, 6,794 lines.

### 4.1 The registry and the key trie (s13, deliverable 1)

- **`edit.cmdtab`** — every command C registers at the pin, 408 rows
  (name, C handler, arity, flags, help, recorder word, the E-mode
  grammar, the handler's file), generated by `tools/gen-cmdtab` from
  `cmd.c`'s descriptor tables and checked by `tools/check-cmdtab` (CI).
- **`edit.cmd`** — the registry as a value (`CmdReg`): ids in C's order,
  names and words to ids, the alias pairs sharing C's handler,
  re-registration taking the old id back, C's validation as one
  function (`cmd_register_problem`) that registration `bug()`s on and
  the tests read. **The shape, and why** (ruled at launch): a handler
  KIND per row — a built-in implementation id, a plugin, a test probe —
  and ONE `match` on literal implementation ids (`edit.impl.run_impl`,
  119 implementations covering 129 commands). No function value crosses
  a module boundary: wolf 0.2.33 builds one natively and refuses it on
  the release tier (G19/G20, wolf-lang#806). The other 279 commands
  answer C's deferred status with "not yet ported: NAME: sagitta Sprint
  N (LANE)" on the message line and in the log, the owner read from the
  handler's C file (`cmd_owner`); `edit_cmdreg_test` invokes every one
  and asserts its message, so no stub is silent (invariant 3). **A
  cleaner shape, as a proposal only**: when closures cross modules on
  the release tier (s251, in flight), a row can carry its handler as
  C's does and `impl.lu` goes away; until then the table plus the match
  is the only shape both tiers build.
- **`edit.keymap`** — key ids, `key_parse_seq`/`key_format_seq`, the
  sorted-edge trie built from `BindRow`s with C's six diagnostics, the
  layered lookup; **`edit.keys`** — the panic floors and H's motion
  tables C builds in code. One million lookups over 300 one-key rows:
  **36 ms** natively (C's budget 150 ms, `test_keymap.c:119-120`).
- Suites: `test_keymap` 3/3, `test_cmdreg` 5/5 (with the unported
  sweep: 279 refuse by name), both lanes.

### 4.2 The notepad (s14, deliverable 2)

- **`edit.ed`** — `Ed`, `Buffer` (an `EditCtx` without its cursor set),
  `Tab`, the window's `CursorSet` lent to the edit context through the
  swap seam (`edit_take`/`edit_give`, §3), undo transactions by the I
  mode law (`edit.invoke`, `yew_ed_invoke`'s), damage and its batch,
  the recovery, overwrite and dirty-quit prompts, save.
- **`edit.loop`** — the timer heap (a kind and a payload, popped one due
  timer at a time), `loop_deadline` saturating at `INT64_MAX` as C's,
  the wait (`term.tty_wait`, #93 R2's `VTIME` interim), the read and
  the typeahead drain (`term.tty_drain_begin/end`), one frame a turn.
- **`edit.dispatch`**, **`edit.mode`**, **`edit.input`** — chords,
  counts, timeouts, the keystack; enter/escape and the Esc law; keys,
  pastes and resizes into the editor.
- **`edit.driver`** — C's startup order (`ed_driver_inner`): the
  workspace, the terminal, the bootstrap tab, the grid and renderer,
  the configuration — `runtime/init.fl` then the user's `init.fl` into
  one option store and one bind ledger (`edit.config` over
  `edit.fldata`, R-yw03-2) — the theme, the startup file, the loop.
  One startup file: several are yw05's, a directory yw13's, none (the
  resume) yw06's, each refused by name.
- **`edit.cmdline`** — the narrow `:` (R-yw03-1); **`edit.tabs`** — the
  one-tab strip (R-yw03-3); **`edit.pairs`** — auto-pairing
  (`init.fl` sets `autopair`).
- Goldens: **`notepad_` 25/25** on both tiers. Suites: `test_modes`
  11 run, 4 SKIP by name (F mode's halves, yw13 — `f` asserted to refuse
  naming yw13; the tab jumps, yw05 — `alt+1` asserted to refuse naming
  yw05); `test_loop` 7 run, 2 SKIP by name (the background work, yw11/
  yw09; the completion tick, yw04), both lanes.

### 4.3 The view (s15, deliverable 3) — the view fork

`edit.viewport` (follow, scrolloff, nowrap's horizontal scroll, wrap by
grapheme), `edit.gutter` (absolute / relative / hybrid, the sign
column, and the sign table with its warn-once mask), `edit.statusline`
(segments by priority, the mode chip), `edit.message` (timed messages,
the prompt chip, the bell), `edit.draw` (document rows, overlays, the
cursor, the footer, `draw_win`, layout and render; a headless editor
renders and flips but writes no frame), the twelve `s15_*` scenes in
the port's `tools/demo-paint` over those same modules. Goldens: **`s15_`
15/15** on both tiers with the port's demo (a plant that raised the
gutter's digit floor turned all four gutter scenes red,
`notes/yw03-evidence/view/plant-gutter-digits.log`). Suites:
`test_viewport` 14/14, `test_statusline` 8 run (2 SKIP by name: the
recorder, yw09; the git badge, yw13), `test_message` 6 run (1 SKIP: the
recorder's REC tail, yw09; on the checked machine one more, the bell's
child, G23), `test_gutter_sign` 4/4.

### 4.4 W and B (s16, deliverable 4) — the word and block forks

The generator's `--word-break` mode and `unicode.tables_wb`
(byte-identical to sagitta's arrays, `tools/check-tables`),
`unicode.wordbreak` (UAX #29), `edit.word` (word, WORD, subword),
`edit.block` and `edit.indent` (bracket scope with the string/comment
heuristics, indentation blocks, paragraphs, chained by containment; the
syntax provider a kind that answers nothing until yw10). Goldens:
**`s16_` 6/6** on both tiers. Suites: `test_word` 3/3,
`test_wordbreak` 1 (all 1,826 rows of `WordBreakTest.txt`), `test_block`
14 run (natively 4 SKIP by name — the syntax engine's fixtures, yw10:
three whole cases and one case's engine half; on the checked machine
the scan budget too, as C skips it instrumented).

### 4.5 H and multi-cursor (s17, deliverable 5) — the hmode fork

`edit.select` (char / line / rectangle spans by `CCol`),
`edit.sel_actions` (yank, delete, change, case, indent, shift, join,
the prompt seeding — every action one edit plan), `edit.multicursor`'s
editor half (`mc_run`: one batch, one `TXN_MULTI` transaction, the
overlap and merge rules, the skip plan, the literal-lift, completion
and LSP-edit guards), the three lifts (`edit_cmds`), secondary cursors
drawn. The case commands needed Unicode case mapping first: the
generator's `--case` mode, `unicode.tables_case` (checked against
sagitta's arrays) and `unicode.case`. Goldens: **`s17_` 16/16** on both
tiers. Suites: `test_select` 8/8, `test_hmode` 13/13,
`test_edit_cmds` 28/28, `test_multicursor` 31 run (28 pass, 1 SKIP by
name — the symbol-index and syntax-splice half of
`multicursor_batches_symbol_rebuild_and_damage`, yw11/yw10 — and 2
KNOWN-RED by name, G3: `multicursor_200_insert_is_one_undo_and_one_
journal_sync` and `multicursor_1000_failure_at_700_rolls_back_and_
syncs_once` run their bodies green in process, but the fault shim's
one `fsync-file` per transaction is unobservable at 0.2.33 —
R-yw02-2's shape), and `test_sel_actions` 30 run (27 pass, 3 SKIP by
name: the subprocess clipboard reader, yw02's R-yw02-3 STOP) — a suite
the contract's list omits and the fork ported. Two bugs the suites
found and fixed: `text.cset`'s stamp exhaustion overflowed instead of
reseeding at the stamp space's top (yw02's, `9a0730c`), and a
multi-cursor undo damaged the whole window where C damages each
replayed op's row (`e9771aa`).

### 4.6 The gates (deliverable 6)

- **The 62 goldens**, by name, at `cbec636` in the container: 62/62 on
  `target/release/yew` and 62/62 on `target/native/yew`, the s15 demo
  scenes through the port's `target/tools/demo_paint`
  (`notes/yw03-evidence/gates/goldens-summary.txt`, the binaries'
  sha256 prefixes in its first line; `pty-<tier>-<prefix>.log`). In CI
  (run 39490908160, at `efa5407`): ubuntu 62/62 ("campaign 03: 62
  goldens green by name"); macOS lost `notepad_restore_segv`'s
  reap-time check — the guard restores after a death the harness
  caused from outside, the race campaign 01's `restore_bus` and
  `restore_abrt` lose there (G1, R-yw01-1, wolf-lang#794) — so on
  macOS that case and `notepad_restore_kill` (the same mechanism) are
  recorded in an announced advisory step and the gate counts 60
  (`65190eb`).
- **`tools/check-test`**, both lanes, at `cbec636` in the container:
  checked "wolf test: 57 passed; 0 failed; 0 rejected; 0 unsupported";
  natively 57 files `[native] ok`
  (`notes/yw03-evidence/gates/check-{checked,native}.log`). **The
  fallbacks** (`wolf test --json src`, `gates/suites.json`): 20 of the
  57 files ran their `main` natively under `wolf test` (G29) — the six
  campaign-03 files that build an editor per case (`edit_keymap`,
  `edit_modes`, `edit_hmode`, `edit_edit_cmds`, `edit_sel_actions`,
  `edit_multicursor`: the registry, the keymaps and `init.fl` cost
  steps), `edit_wordbreak` (1,826 rows), `term_input`, and yw02's ten
  `text_*` files and two yw00 files. The per-case checked run
  (`notes/yw03-evidence/checked/percase.py`: one `test_` wrapper per
  call `main` makes, main's prologue first, every case on its own
  checked machine) over every root-level fallback file:
  **233 cases pass on the checked machine, 0 fail, 30 `unsupported`**
  (the step budget; each then rests on the native run, which runs them
  all): the six campaign-03 files 112 pass (`edit_hmode` 13/13,
  `edit_edit_cmds` 28/28, `edit_sel_actions` 30/30, `edit_multicursor`
  29, `edit_modes` 10, `edit_keymap` 2) and 4 unsupported (the million
  lookups, the eight-step mode walk, the 1,000-cursor rollback, the
  edit/motion fuzz); `term_input` 12 and 7 (the 131 legacy vectors and
  the other stream cases); the ten `text_*` files 109 and 19 — the same
  cases yw02 found unsupported, plus `coords`' port-only storage-reuse
  case — and `text_textbuf_props`' twelve properties pass at
  `YEW_PROP_N=5` as yw02 ran them (`notes/yw03-evidence/checked/
  percase.log`, `percase-term-input.log`, `percase-props5.log`).
  `edit_wordbreak` is one case of 1,826 rows: the word fork ran it
  checked in 19 slices (`notes/yw03-evidence/word/wordbreak-slices.log`;
  `edit.word`, `unicode.wordbreak` and the tables are unchanged since).
  `unicode/utf8_test` and `util/base64_test` are module-internal files
  (a per-case copy would be a second member of the module, and `wolf
  test` discovers `test_*` in a package's first file only, G10); their
  modules' sources are unchanged since yw00 and they fell back at
  yw02's head too.
- **The drift checks** (`tools/check-cmdtab`, `tools/check-runtime`) and
  `tools/check-tables` with the word-break and case arrays: green on
  kasumi's host at `cbec636` and in CI.
- **Plants** (RULES §7, draft PRs closed unmerged, each seen red in its
  PR run): #13 at `f4105e2` — one help string in `cmdtab.lu` — run
  39486863234, oracle on all three legs / "the registry table and the
  runtime copy are the pin's" (`check-cmdtab: src/edit/cmdtab.lu
  DIFFERS`); #14 at `31c6627` — one byte of the embedded light theme —
  run 39486867503, the same step on all three legs (`check-runtime:
  src/edit/runtime_blob.lu DIFFERS`); #15 at `41127f2` — the mode chip
  padded on one side — run 39486874148, oracle (ubuntu, macOS) /
  "goldens, campaign 03 (yw03's gate, M-YW3)" (`notepad_open: golden
  mismatch`), and the port job's `wolf test` caught it first
  (`edit_statusline_test`). The view fork's local plant on the s15
  scenes is above (§4.3); the word fork's on WB5
  (`notes/yw03-evidence/word/suites.txt`).
- **The 2× gate on the editor** (`tools/run-perf-editor --cpus 0-3`:
  sagitta's own `perf_startup_s56` and `perf_latency` over C yew and the
  port from the same run, C again after; in the container on kasumi at
  load 0.7–2.1, five runs; `notes/yw03-evidence/gates/
  perf-editor-{1..5}.log`, `perf-editor-medians.txt`). Medians of the
  port/C ratio: first paint **default 0.48**, **`--clean` 1.51**,
  **`TERM=dumb` 0.16**; **cold open 1.22**; **keypress → paint p99
  0.96**; **arrow p99 1.37**, **paced arrow p99 1.11**; the kitty
  Backspace pair **1.11** and **1.08**. Every median within 2×; three
  single rows over it, each named: run 1's `--clean` first paint (4.31,
  the series' first port start, 7.0 ms against 2.4–2.6 ms in the next
  four) and its first Backspace (5.53 — C's own first value was 115 µs
  and its second 623 µs, drift 5.42), and run 5's arrow p99 (5.13: C's
  p99 halved that run, 51 µs against ~92 µs, while the port's doubled,
  264 µs against ~120 µs). The arrow p99 is the port's one noisy row
  (the hosted runner saw 3.49 in run 39490908160's advisory step,
  every other row within 2×); in-process an arrow costs 9.9 µs, 9.5 of
  them the frame (126 bytes) — the tail is the I/O path's, a yw15 row
  to chase. **Read the default and dumb rows with care**: C's default
  start runs `init.fl` in the Fletch VM (22.5 ms against its `--clean`
  1.8 ms) and the port reads it with the literal reader (7.3 ms against
  2.4 ms), so 0.48 is the cost of a reader, not of the editor; the
  like-for-like start is `--clean`'s 1.51. The contract's prediction
  (cold start within 2×, the demo's was 1.51×; keypress within 2×):
  **HIT** on every median.
- **Memory per keystroke** (resident, C yew and the port under the same
  PTY driver typing 4,000 keys into a 10,000-line file in I mode, then
  4,000 line moves, `notes/yw03-evidence/gates/ptymem.py`, in the
  container): C +688 KB over the typing (176 B a key) and flat after
  the first quarter, then −1.8 MB over the moves (a peak of 28 MB in
  the first quarter returned); the port +1.3 MB over the typing (337 B
  a key: 11.9 / 11.4 / 12.0 / 12.6 MB at the quarters), and +2.5 MB over the moves (631 B a key, LINEAR: 12.2 / 12.8 /
  13.5 / 14.1 MB) — where C returns memory, the port keeps every turn's
  temporaries (the frame's interpolated strings, the theme lookups'
  copies, the gutter's numbers) to the session's end: a function
  allocates in its caller's region and the loop's is the session's,
  and a per-turn `region` around the work is E1010 because the work
  mutates the session's value (G18's shape at the editor's scale,
  `notes/yw03-evidence/witness/turn-region/`). At 631 B a key a
  100,000-key session holds ~63 MB. Asked as R-yw03-7 (§5).
  G33's shape (a `List` replaced inside the session-long `Ed` is held
  to the session's end) is the suspect for the port's growth; the
  seam itself allocates nothing (§3).
- **CI**: the first PR run, 39490908160 at `efa5407`: every port job
  green (fmt, both tiers, check-tables, both check-test lanes, the
  fuzzers), the oracle on ubuntu green with the 62 by name, the
  editor's 2× advisory as above, and macOS red at
  `notepad_restore_segv` (the race above, `65190eb`). The PR run at the
  final head is the merge run (yew is not tiered); the hand-back names
  it.

### 4.7 The `unsafe` census

**Delta: +1 module var** — `edit.gutter`'s warn-once mask for the ASCII
sign fallback (C's process-wide `static` mask; two blocks,
`gutter.lu:144-151`, invariant 8 as `unicode.width`'s). The census:
`unicode.width`'s `ambiguous_wide`, `text.file`'s `temp_counter`,
`text.undo`'s `text_hash_calls`, `edit.gutter`'s mask. The editor's
state is the `Ed` value; nothing else is module state.

## 5. Rulings asked, issues, and what to correct

**Rulings asked** (each with the lane's recommendation, implemented;
the text is `docs/MAP.md` §6):

- **R-yw03-1 — a narrow `:` in yw03** (every campaign-03 case tears
  down through `:`). **Recommend A**: the narrowest `:` — E mode by
  `:`, `e` and `!`, typed and pasted text sanitized as C's prompt does,
  `<cr>` resolving a name or abbreviation through the registry, `<esc>`
  cancelling; ranges, `:!`, history, completion and the editing keys
  refuse naming yw04 (`edit.cmdline`).
- **R-yw03-2 — the runtime files before Fletch.** **Recommend A**: the
  files copied verbatim and embedded, read by a literal-subset reader
  (calls, `let NAME = literal`, literals) that refuses anything else by
  line and column naming the VM's lane (`edit.fldata`, `edit.config`).
- **R-yw03-3 — the one-tab strip.** **Recommend A** (`edit.tabs`).
- **R-yw03-4 — Enter while `ICRNL` cannot be cleared (G34).**
  **Recommend A**: a legacy LF reads as Enter while the port's raw mode
  is in force, until the pin carries wolf-lang#802's widening.
- **R-yw03-5 — the two sync-count cases of `test_multicursor`.**
  `multicursor_200_insert_is_one_undo_and_one_journal_sync` and
  `multicursor_1000_failure_at_700_rolls_back_and_syncs_once` assert
  ONE `fsync-file` per transaction through sagitta's fault shim; at
  0.2.33 the port syncs nothing (G3). (A) KNOWN-RED by name, the bodies
  run and must be green, the sync count printed as not observable —
  R-yw02-2's shape (recommended, implemented); (B) SKIP.
- **R-yw03-6 — the paste key reaches R-yw02-3's STOP.** `ed.clip.paste`
  reads the system clipboard; where a subprocess reader is detected
  (`wl-paste`, `xclip`, `pbpaste`), yw02's reader exits 4 by name
  (G30). In yw03 a user reaches that with the paste key and loses the
  session (the journal keeps the edits). (A) keep the STOP as R-yw02-3
  ruled (implemented: no golden reaches it); (B) in the editor, refuse
  the paste with C's deferred status and a message naming G30, the
  registers and OSC 52 still serving. **Recommend B** for yw04 (it
  touches yw02's reader; not done here).

- **R-yw03-7 — a turn's temporaries** (§4.6: the port keeps ~630 B a
  line move, ~340 B a typed key, to the session's end). (A) the port's
  hot paths stop allocating — the statusline, gutter and theme lookups
  write into storage the `Ed` already owns, digits formatted in place,
  no interpolated `str` per frame — a lane of its own before M-YW5's
  daily driver (yw05) or yw15's budgets; (B) wolf: a per-turn region
  whose allocations the mutated value may not keep but whose pushes
  into storage the value already owns are allowed (E1010's precision,
  G18), after which the loop wraps each turn; (C) accept it until
  yw15. **Recommend A, scheduled into yw05** (B filed beside it); not
  done here — no campaign-03 gate measures it and the fix touches
  every draw path.

**Issues to file** (listed, not filed; the orchestrator files):

- **wolf-lang — G35**: E1004 refuses a `take` parameter stored into a
  field of a `mut` parameter's list element while the store of the
  whole element builds (`notes/yw03-evidence/witness/take-region/`).
- **wolf-lang — G18 at the editor's scale**: a `region` around one
  turn of a loop that mutates a session-long value is E1010 even when
  the turn only pushes into the value's existing storage
  (`notes/yw03-evidence/witness/turn-region/`).
- **wolf-lang — the keyword list**: `impl`, `take`, `use` and `scope`
  as field names are parse errors whose messages (E0202/E0201/E0207)
  never say "keyword"; a diagnostic naming the reserved word would
  have saved a build each.
- **yew — the prompt's and paste's bytes are a `str`.** `CmdCtx.sarg`
  is a `str`, so a paste of invalid UTF-8 inserts nothing where C
  inserts the bytes (`cmdline.c:262-311`, `ed.c:2435-2476`); a
  `List[byte]` argument is yw04's when it ports the full prompt.
- **yew — R-yw03-6**, if ruled B.

Already filed and still open or unreleased: wolf-lang#806 (closures
across modules; the registry's shape), #802 (G34, closed, unreleased),
#796 (G3), #795 (G2), G29's silent `[native]` fallback.

**Corrections, for the orchestrator** (the lane edits no memory file):

- **The lane's container has no `clang`**: `archlinux:base-devel` runs
  the checked machine and the native tier, but wolf's release tier
  needs `clang >= 15` (D33), so `tools/build --release`, the demo and
  `tools/check-tables` (its generator builds `--release`) must run on
  kasumi's host — no signal is involved — and only the runs go in the
  container. yw03 learned this from a verify script that built native
  in the container and tested a stale release binary (caught, rebuilt
  on the host, re-run: §4.6).
- `docs/MAP.md` §7/§2 corrections from the yw04 draft are made in the
  map (s57.21 has no sprint file; `menu` and `fuzzy` are yw04's;
  `complmenu` is yw11's; `test_job_handover` is yw13's); §8 gains the
  index's "(s18–s22)" and M-YW3's "script goldens".
- The contract lists 15 unit suites; sagitta also has `test_sel_actions`
  (30 cases) for `sel_actions.c`, which the lane ported.

## Evidence index

- `notes/yw03-evidence/gates/` — the lane's gate at `cbec636`:
  `goldens-summary.txt` and `pty-{release,native}-{notepad_,s15_,s16_,
  s17_}.log` (62/62 on both tiers), `check-checked.log`,
  `check-native.log`, `check-tables-host.log`, `suites.json` (`wolf test
  --json src`), `perf-editor-{1..5}.log` and `perf-editor-medians.txt`
  (the 2× gate), `verify-container.txt` (the container run, with the
  stale-release note), `verify.sh`, `verify-goldens.sh`, `ptymem.py`.
- `notes/yw03-evidence/checked/` — `percase.py` and its logs (the
  per-case checked runs).
- `notes/yw03-evidence/hmode/` — the H fork's suites, both check-test
  lanes, s17 on both tiers by name, the case tables' fixture tool.
- `notes/yw03-evidence/view/` — the view fork's suites, goldens, the
  per-case run of `edit_viewport_test`, the gutter plant.
- `notes/yw03-evidence/word/` — the word-break tables, the 19 checked
  slices of `edit_wordbreak_test`, the WB5 plant.
- `notes/yw03-evidence/witness/take-region/` — G35.
- CI: the PR run (§4.6); the plants' runs 39486863234, 39486867503,
  39486874148.

## Done-when

- [x] Every deliverable with its tests (§4.1–4.5); the registry's shape
  and why (§4.1); the `unsafe` census delta (§4.7).
- [x] `tools/check-test` and `--native` green; the per-case checked run
  recorded for every root-level `[native]` fallback (§4.6).
- [x] Campaign 03's 62 PTY goldens green by name against the wolf
  binary on both tiers (M-YW3), gated by name in CI.
- [x] The 2× gate on the editor recorded on kasumi under `taskset -c
  0-3` (§4.6).
- [x] `docs/MAP.md` §1, §2, §3, §5, §6, §7, §8 updated; yw04's contract
  drafted in full (`notes/contracts/yw04-execute-and-search.md`).
- [x] Plants seen red and closed unmerged (#13, #14, #15).
- [ ] CI green at the final head; the PR with the five sections; the
  lane audit — the hand-back carries them.
