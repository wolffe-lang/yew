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
