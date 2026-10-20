# yw03 — The modal core

**Opus 5.5 (#89 R4). Crawl 54+. Drafted by yw02 from `docs/MAP.md` §7
and sagitta campaign 03.** Ruling #89 (`sprints/yew/index.md`); the
track's seven standing rules; `docs/MAP.md` (the idiom §1 as yw02
extended it, the gaps §5, the rulings §6); `sprints/RULES.md`. Ports
sagitta campaign 03 (`s13-keymap-engine.md`, `s14-modes-L-I.md`,
`s15-viewport-statusline.md`, `s16-modes-W-B.md`,
`s17-mode-H-multicursor.md` at `sagitta.pin`): `src/edit/` `cmd.c`,
`keymap.c`, `keys_default.c`, `mode.c`, `dispatch.c`, `motion.c`,
`select.c`, `sel_actions.c`, `multicursor.c` (the editor half: the
cursor set's core is `text.cset` since yw02), `ed.c`, `loop.c`,
`word.c`, `block.c`, `edit_cmds.c`, `file_cmds.c` (14,334 C lines);
`src/ui/` `viewport.c`, `statusline.c`, `gutter.c`, `message.c`,
`draw.c`, `win.c` (4,186; `docs/MAP.md` §2 gives these to yw05, but
s15 is campaign 03's — the map is corrected by this contract); and
`src/unicode/wordbreak.c` with the generated `tables_wb.c`. The port
inherits the idiom yw00–yw02 set (regions/`List`/`Map`, `str` tables,
`(s, at, end)` byte conventions, `copy` on lent getters and on a list
element of struct type, `distinct` coordinates at function boundaries
only, node pools of indices for every tree, the one `unsafe` module var
per `[mem.static.2]`, no bound `.bytes()` in a hot loop, the environment
and every process-wide registry as a threaded VALUE, never module state
of a run-time value (E1010), never a function value across a module
boundary (wolf-lang#806, G19/G20)).

## Deliverables

1. **`edit.cmd` and `edit.keymap`** (s13): the named-command registry —
   one descriptor table, one invoke choke point that keys, E mode
   (yw04), Fletch (yw09) and the recorder (yw09) all reach — and the key
   trie with stacked mode/user/plugin layers, the chord/ambiguity timeout
   state machine (milliseconds suffice: G8 is a perf gap, not a chord
   one) and count prefixes; the binding tables as DATA (`BindRow` rows
   now, Fletch `bind()` rows in s36, the same builder). C's `CmdDesc` and
   `UnitOps` are tables of function pointers (`cmd.h:137-160`,
   `motion.h:25-32`); wolf refuses a function value across a module
   boundary on the release tier (G19/G20, wolf-lang#806), so the port's
   registry is a table of names and flags with a command id and ONE
   `invoke` that matches on the id, and the unit engines a `match` on a
   unit kind — the shape is ruled before the first command lands (§
   Rulings). `test_keymap` (3), `test_cmdreg` (5) ported.
2. **`Ed`, `Win` and the loop** (s14, the notepad milestone): the event
   loop over the tty and the signal set with the timer heap and
   typeahead coalescing (at 0.2.33 `os_signal_wait_fd` with the `VTIME`
   interim, #93 R2; `os_signal_wait_fds` when 0.2.34 is pinned, G2),
   `mode.c` with the Esc law, the L-mode command keys, I mode over
   `text.TextBuf` with grapheme arrows, argv open with the
   journal-recovery prompt (`text.journal_probe`/`journal_replay_edit`,
   yw02), save through `text.edit_save` (the atomic path, G3 as the pin
   has it), quit with the dirty-check prompt. **The ownership seam**:
   yw02's `text.EditCtx` OWNS the buffer, marks, cursor set, journal and
   undo tree (C's holds pointers), while sagitta puts the cursor set on
   the WINDOW ("multi-cursor lives on the window, not the buffer",
   `01-architecture.md`) and the journal owner list is process-wide; the
   port's `Ed` holds the buffers (each an `EditCtx` without its cursor
   set) and the `JournalSet`, a `Win` holds its `CursorSet`, and an edit
   moves the window's set into the context and back (`take`), measured
   per keystroke. The 25 `notepad_*` PTY goldens. `test_modes` (11),
   `test_loop` (7) ported.
3. **The viewport, gutter, statusline and message line** (s15): the
   follow-cursor viewport with scrolloff, horizontal scroll for `nowrap`
   and grapheme-aware `wrap`, the gutter (absolute / relative / hybrid,
   the reserved sign column), the statusline spec with the mode chip,
   the timed message line, `SIGWINCH` → relayout → full damage; the
   `FileMeta` fields (`eol`, `had_bom`, `binary`, `had_invalid_utf8`,
   `missing_final_nl`, yw02) reach the user here. The 15 `s15_*`
   goldens. `test_viewport` (14), `test_statusline` (8), `test_message`
   (6), `test_gutter_sign` (4) ported.
4. **The W and B unit engines** (s16): the unit-engine interface (a
   `match` on the kind, deliverable 1's ruling) with the line, word,
   block and char instances; UAX #29 word boundaries with WORD and
   subword variants from the generator's new `--word-break` mode
   (`tables_wb`, data-only, checked against sagitta's arrays as
   `tools/check-tables` does the grapheme tables); B's structural units
   (bracket scope with string/comment heuristics, indentation block,
   paragraph) chained by containment, the syntax provider slot inert
   until yw10. The 6 `s16_*` goldens. `test_word` (3), `test_wordbreak`
   (1), `test_block` (14) ported.
5. **H mode and multi-cursor** (s17, modal complete): H over every unit
   engine with the mode-memory rule (`H·W`), char / line / rectangular
   selections (rectangular `CCol`-based, the wide-glyph and tab edges),
   the selection actions through the registry (yank, delete, change,
   case, indent, shift, join; yank and paste through yw02's
   `text.register` and `text.clipboard`, OSC 52 in a terminal; the
   subprocess backends are yw02's named gap and a golden that reaches
   one is a STOP), the three selection→multi-cursor lifts, simultaneous
   multi-cursor editing as ONE undo transaction (`text.cset` +
   `TXN_MULTI`, yw02) with the overlap/merge rules, selection and
   secondary-cursor rendering. The 16 `s17_*` goldens. `test_select`
   (8), `test_hmode` (13), `test_multicursor` (31), `test_edit_cmds`
   (28) ported; `test_multicursor_replay` is the recorder's (yw09).
6. **The gates**: `tools/check-test` and `--native` green, with the
   per-case checked-machine run for every file `wolf test` falls back to
   native (yw02's note §3 shows how: a file's `main` past the checked
   machine's 20M-step budget runs NATIVELY under `wolf test`, by
   `detail: [native]`); campaign 03's 62 PTY goldens (`notepad_*`,
   `s15_*`, `s16_*`, `s17_*`) against `target/release/yew` gated BY NAME
   in CI, the editor's recorded step narrowing to what is still red by
   design; the 2× gate moving from `demo_paint` to the editor (sagitta's
   own `perf_startup` and `perf_latency` against both binaries) on
   kasumi under `taskset -c 0-3`; **M-YW3**. The live-editor kill9 lane
   (`yew-live-torture.c`) types `Ndd`, a bracketed paste, `s` and
   `:ed.quit_force` (`yew-live-torture.c:181-219`): the last needs E
   mode (s18, yw04), so the lane is yw04's unless the ruling below says
   yw03 carries a minimal `:` (yw02 asked it; the batch lane is yw09's).
7. **The note and the map**: `notes/yw03-the-modal-core.md` with the
   five sections, the measurements, the `unsafe` census delta, the
   registry's shape and why; `docs/MAP.md` §2 (the `ui` files campaign
   03 owns), §5 and §6 updated; yw04's contract drafted in full from §7.

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. Read sagitta's
`src/edit/*.c`, `src/ui/*.c` and `src/unicode/wordbreak.c` freely and
cite `file:line`; **no other editor's keymap, modal engine, viewport or
multi-cursor source, ever**. No dependency but wolf-std. No golden
edited; a disagreeing golden is a STOP with the diff. The command
registry's shape is ruled before it is written; a function value across
a module boundary is never the answer (it builds natively and is
refused on the release tier, yw01's G19/G20). Toolchains: the pin at
yw02's merge (wolf 0.2.33 / lupin 0.1.54 / wolf-std `cceda63`) unless
0.2.34 (s247 + s248) has been released, in which case the bump is
yw03's first commit with its prediction and it ADOPTS what yw02 met as
gaps: `fs_sync`/`fs_sync_dir` at `text.file`'s two named sync sites
(`no_sync_g3`, `no_sync_dir_g3`, G3) and the journal's, `fs_realpath`
for `text.file_realpath`'s walk (G4), `os_signal_wait_fds` for the loop
(G2) and the clipboard reader, `os_fork` for the clipboard writer's
double fork — each with the yw02 test that is KNOWN-RED or SKIP today
turned green (`save_fault_shim_contract`, the replica's determinism
order, the clipboard subprocess cases).

## Inputs (re-derive)

sagitta at the pin: `s13`–`s17`, the files above with their headers,
`tests/unit/test_{keymap,cmdreg,modes,loop,viewport,statusline,message,
gutter_sign,word,wordbreak,block,select,hmode,multicursor,edit_cmds}.c`,
`tests/pty/registry.c` (the 62 campaign-03 cases) and their goldens,
`tests/torture/yew-live-torture.c`, `tests/perf/perf_startup.c`,
`perf_latency.c`, `budgets.txt`, `scripts/gen-unicode-tables.c` (the
`--word-break` mode), `ucd/16.0.0/WordBreakProperty.txt`; the yew repo
at yw02's merge (`src/text`, the idiom and gaps in `docs/MAP.md`,
`notes/yw02-the-text-engine.md`); wolf-std `std/term`, `std/signal`,
`std/process`, `std/time`; the spec `[os.signal.*]`, `[os.term.*]`.

## Prediction (write before the first change)

The registry ports as data plus one `match` with no function value
crossing a module boundary, and the release tier builds it; the
ownership seam costs one move of the cursor set per edit, invisible in
the 2× gate; the notepad, `s15`, `s16` and `s17` goldens go green
without a golden edited, `tables_wb` regenerates byte-identical to
sagitta's arrays; the editor's cold start → first paint within 2× of C
yew's (the demo's was 1.51× at yw01) and keypress → paint within 2×;
the only campaign-03 rows red at the end are the ones that reach a
named gap (a subprocess clipboard, if any golden does) or E mode.

## Done-when

Every deliverable with its tests; `tools/check-test` and `--native`
green and the per-case checked run recorded; campaign 03's PTY goldens
green by name against the wolf binary (M-YW3); the 2× gate on the
editor recorded on kasumi under `taskset -c 0-3`; `docs/MAP.md`
updated; yw04's contract drafted; CI green; PR open with the five
sections, shas as bullets, a test checklist; `bash
wolf/tools/lane-audit.sh yew yw03 <PR>` passing but for the final run's
green; hand back per RULES.md §6.
