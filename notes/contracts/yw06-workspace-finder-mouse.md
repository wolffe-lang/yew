# yw06 — workspace, finder and mouse

**Model per ruling #89 R4, chosen at launch. Crawl 54+. Drafted by yw05
from `docs/MAP.md` §7 and sagitta campaign 05's second half, with the
four sprints ruling R-yw05-1 = A moved here and the yw05 carry-overs.**
Ruling #89 (`sprints/yew/index.md`); the track's seven standing rules —
rule 7 binds from this lane (M-YW5: the static x86-64 binary and its
digest); `docs/MAP.md` (the idiom §1, the gaps §5, the rulings §6, as
yw05 left them); `sprints/RULES.md`. Ports sagitta campaign 05's
s25–s27 (`.docs/sprints/05-ui-workspace/`: `s25-workspace-state.md`
582, `s26-fuzzy-finder.md` 568, `s27-mouse-and-feel.md` 521: 1,671
lines at `sagitta.pin`); the four R-yw05-1 moved here, after s27
(`13-performance/`: `s57_13-mouse-overhaul-context-menus.md` 411,
`s57_14-tab-drag-feel.md` 463, `s57_15-strip-scrolling.md` 125,
`s57_22-drag-to-spawn-pane.md` 132: 1,131); s56.5's startup resolver
(§1 and §6 of `s56_5-workspace-interaction.md`, 318); and the two field
repairs of MAP §7's list that land on surfaces already ported,
`s57_11-shell-self-open.md` (240) and
`s57_12-selection-clipboard-job-return.md` (179). The rest of that list
is not this lane's C (R-yw06-4, **Decided**): s56.5 §2–§5 and §7, s57.5
(545), s57.6 (201) and s57.7 (236) are FUSS's and shadow's; s57.9 (189)
and s57.10 (96) sit in files yw03 and yw05 ported; s57.20 (141) has no
C at the pin. The C it ports: `src/ws/` `workspace.c` (247) + `.h`
(74), `state.h` (280), `state_emit.c` (820), `state_parse.c` (1,178),
`state_save.c` (325), `state_lit.c` (303), `fllit.h` (148), `fl_emit.c`
(237), `fl_parse.c` (592), `walk.c` (561) + `.h` (123), `gitignore.c`
(539) + `.h` (124); `src/edit/ws_cmds.c` (295) + `.h` (46); `src/ui/`
`picker.c` (1,093) + `.h` (193), `pickers.c` (655) + `.h` (50),
`filter.c` (398) + `.h` (138), `typejump.c` (105) + `.h` (63),
`mouse.c` (3,090) + `.h` (432), `ctxmenu.c` (671) + `.h` (183),
`ctxrows.c` (838) + `.h` (303) — 30 files, 14,104 lines — and two
ranges of files earlier lanes ported: the start plan
(`ed.c:2815-2917`, 103) and the `:!yew FILE` recognizer
(`shell.c:301-647`, 347; yw04 left it unrecognised, `edit.shell`'s
header): **14,554 C lines**. Not here: the state's Fletch path at the
pin (`state_fletch.c`, 234, over yw07's `fl/data.c`; R-yw06-1) and the
trust database (`trust.c` 1,099 + `.h` 152, `trust_prompt.c` 207 + `.h`
35; R-yw06-5). The port inherits the idiom yw00–yw05 set and yw03's
module rule: a file that reaches the `Ed` or an `edit` unit is
`src/edit/*.lu` with sagitta's name — every `ui` file here
(`picker.h:41-45` takes `edit/cmd.h` and `ui/layout.h`) and every
`state_*` file (`state.h:27` takes `edit/loop.h`); the six that reach
neither (`workspace.c`, `fllit.h`, `fl_emit.c`, `fl_parse.c`, `walk.c`,
`gitignore.c`) join `ws` beside yw04's `ws.fuzzy`.

## Deliverables

1. **The toolchain, first.** `gh release list -R wolffe-lang/wolf-lang`
   and `-R wolffe-lang/wolf-interp` read and quoted with their time at
   the lane's start. yw05 pinned wolf 0.2.34 / lupin 0.1.55 / wolf-std
   `e036bec`; at this drafting (2026-10-22T13:46:27Z) **v0.2.34 is the
   latest** (2026-10-21T12:58:10Z; lupin 0.1.55, 2026-10-20T22:11:27Z).
   The NEXT pin's (0.2.35): s251 (function values and closures across
   modules on the release tier: yew#17, yew#27), s255 (the per-turn
   region and `List.reset`/`reserve`, wolf-lang#859), sc69's std
   wrappers (wolf-std `3bacc5f`: `term.Mode`'s `raw_cr`, `raw_output`,
   `strip8`; `signal.wait_fds`; `term.restore_at_exit`: yew#24), s250
   (`os_exe()` under `wolf test` refused by name, `check-test
   --nocapture`/`--no-native-fallback`: yew#20), s253 (`fs_adopt`, G26;
   `os_name`/`os_arch`, G31: yew#22) and s254 (yew#23:
   `directory_writable`, the lstat before the open, the path stat after
   it, the `mkfifo` utility, the blocking clipboard write). If a release
   carrying them is out at launch, the bump (wolf, lupin, the std the
   archive bundles, digests read twice) is yw06's FIRST commit with its
   prediction, and it ADOPTS each issue's retirement with its test
   turned green or renamed: yew#20's `self_reexecutes` guards come off,
   and this lane's new child-role cases (deliverable 2's fork-and-kill
   children) are written to the new shape from the start; s255's
   `List.reserve`/`reset` is what s26 §7 asks of the refilter ("both
   vectors reserved to `n` at open", no per-candidate allocation; at
   0.2.34, MAP §1's `copy region` row); what yw05's deliverable 6 left
   to a per-turn region (R-yw03-7) is measured again with `ptymem.py`,
   C beside it. If none is out, the lane stays at yw05's pin and the six
   issues are named, not touched. `fs_realpath` (G4), which workspace
   identity needs, is 0.2.34's.
2. **Workspace identity and state** (s25). `ws.workspace`: the key
   (`fs_realpath`, then FNV-1a 64 over the BYTES, `%016lx`), the `path`
   record written atomically, the probe walk `1..15` then stateless, the
   `0700` directory, `--clean` stateless before any I/O. The v1 format
   through R-yw06-1's codec: six kinds and no floats (`ratio_permille`
   through `yew_permille_to_ratio`/`yew_ratio_to_permille`,
   `state_emit.c:358-379` — a binary32 division, then a double — held
   in yw05's `util.f32` bits, since the checked machine refuses `f32` at
   0.2.34), the pinned escapes and layout, `#` comments accepted and
   never emitted, unknown keys (and `options`) kept for re-emission. The
   schema's order: groups before tabs, every file id remapped through
   an id map (DoD 4's grep), `panes.win` a pre-order index assigned in
   ONE pass for `panes` and `wins` (s25 §4's pitfall), `goal: -1` for
   EOL, `deferred` an instruction; the undo reference names the `.yewu`
   sidecar (`state_emit.c:706-722`; the sprint's `.sagu` predates the
   rename) that yw02's `text.undo` writes. Saving: `mark_dirty` from
   s25 §5's events, the 2,000 ms debounce on the timer heap
   (`state.h:76`), a save on quit and on `TERMINATE`/`HANGUP`, never
   from a fatal path, through `text.file`'s atomic write with 0.2.34's
   `fs_sync`/`fs_sync_dir` (no second copy: DoD 8); the pid lock probed
   with `os_signal_send(pid, 0)` (v0.2.34 `spec/11-os.md:537-552`:
   `not_found` is `ESRCH`, `denied` is `EPERM`). Restore in s25 §6's
   nine steps — one hydration, counted by yw05's `text.file` read hook
   (R-yw05-4 = A); `vp_clamp`, never follow — the missing-file rows
   with one summary message, §7's corrupt rows (renamed aside with the
   UTC stamp, five kept, never deleted, never a prompt, exit 0).
   Per-workspace history (§8, `history.scope`, merged at load) retires
   `edit.cmdline_hist`'s global interim (its header) and with it
   `tools/torture-live`'s one KNOWN-RED by name (kill9's shared state
   home: the second determinism run lacks the first's history append,
   `05391c7`; still printed at yw05's lane gate L2): the branch and its
   acceptance are deleted, the shared run seen red first. Jump state follows
   the pin's literal emission/restoration path (`src/ws/state_emit.c:485-520`),
   not `yew_jumplist_serialize`'s separate `jumplist 1` tab-separated blob
   (`src/edit/jumplist.c:344-385`), which remains uncalled as in shipping C
   (R-yw06-8 = A, Decided). Share resolved-position logic where it is the
   same code; never put the unrelated blob into the frozen literal schema. The five `ed.ws.*` commands `cmd_owner` routes here
   (`save_state`, `restore_state`, `info`, `forget`, `migrate`) and the
   start with no file (`edit.driver`'s "starting with no file" refusal)
   restoring. Unit: `test_ws_key` (11), `test_ws_save` (27),
   `test_ws_restore` (18), `test_ws_recover` (15), `test_ws_history`
   (12), `test_ws_cmds` (16), `test_state_schema` (12),
   `test_state_corpus` (13), `test_state_options` (2) — **126**;
   `test_state_diff` (2: the data writer's quoting, a pure literal runs
   nothing) is the VM's, yw09's. The corpus
   `tests/unit/fixtures/wsstate/v1/` (22 canonical, 4 `noncanonical/`,
   20 `invalid/`) copied verbatim. `test_ws_save`'s kill-9 torture
   (`test_ws_save.c:1020-1100`: the fault shim's `YEW_FAULT_AT` walked
   across write, sync, rename and directory sync) and its gone-pid
   cases fork (`:143-160`, `:621-640`): child-role (G23) and
   `os_fork` is `unsupported` on the checked machine, so they run
   natively in the container, counted. PTY: `s25_resume_exact`,
   `s25_resume_survives_resize` (its golden is
   `s25_resume_after_resize.golden`). Fuzz: `fuzz_state` (s25: 100,000
   cases × 4 seeds; `Makefile:135-139`). Perf: `perf_state.c`'s three
   budgets (emit ≤ 5 ms on 512 tabs × 16 leaves, parse ≤ 10 ms, a 40-tab
   restore ≤ 20 ms, `perf_state.c:56-58`; in-process, so the port's own
   harness beside C's numbers); `startup.first_paint.workspace50` and
   `mem.workspace50` (`budgets.txt:35`, `:62`; `perf_startup.c:246-262`
   drives a binary with `--workspace` and 50 `buf-NN.c`: run over both).
3. **The startup plan** (s56.5 §1, §6): `start_canonical_dir`,
   `yew_start_plan_resolve` and `ed_apply_start_files`
   (`ed.c:2815-2917`) — `yew` (cwd, restore), `yew FILE...` (cwd,
   restore, then each file opened or focused, the last active),
   `--workspace DIR FILE...`, a directory beside another target refused
   before raw mode, never the first file's parent; restore BEFORE the
   files (`ed.c:3012-3015`). A directory launch (`yew DIR`, `yew .`)
   resolves and restores its workspace and its `enter_fuss` refuses by
   name on the message line naming yw13, leaving L mode — the shape
   s56.5 §1 gives `MODULES=""` (the port has no `MODULES=""` build,
   R4). Unit: `test_startup` (3). PTY: `startup_explicit_workspace`.
   `startup_directory_workspace` waits on the drawer and Git discovery
   (`registry.c:8621-8640`): yw13's; `startup_directory_workspace_no_fuss`
   is registered only where FUSS is compiled out (the `#else` of
   `registry.c:12599-12605`), never the port's build.
4. **The finder and the one picker** (s26). `ws.walk`: an explicit
   stack (never recursion, G41), each directory's entries read whole
   and sorted before descent as C's are (`walk.c:285-311`), the
   `(dev, ino)` loop guard from `fs_lstat`'s words 9–10 (v0.2.34
   `spec/11-os.md:3080-3105`), `.git` skipped first, `max_depth`,
   `max_entries` with its one message, budget slices on the idle timer.
   `ws.gitignore`: s26 §4's table, every supported row and every pinned
   divergence and nested sets. Disk loading follows measured pinned C,
   including its `.git/info/.gitignore` lookup instead of `exclude` and
   NULL-base nested rules (R-yw06-10); in-memory base-scoped compilation
   remains distinct. Gate both fixture-tree listings against C. Preserve
   the conservative prune and a directory-read counter (DoD 5: a pruned 5,000-file
   `node_modules/` costs one stat and no read). `edit.picker`: the
   filter line IS yw04's `CmdLine` (DoD 9), selection held by payload
   across refilters, the keymap layer, the centred box and the
   under-24-column refusal, `PICK_ROW` regions. `edit.filter`:
   narrowing on append, the sliced full rescan with ` scanning…`, the
   cached candidate set, a bounded top-k, never a sort of the set.
   `edit.pickers`: `ed.find.file` (the preview through `fs_read_at`,
   capped at 64 KiB, never a `Buffer`: DoD 11), `ed.find.buffer` (by
   `tab_id`, the deferred and orphan marks), `ed.undo.branches`
   (closing s10 §11, an injected `now`), `ed.find.command` (the
   palette, `pickers.c:494-543`: the registry alone). `edit.typejump`
   (500 ms, `typejump.h:36`, a timer-heap deadline). `PickerSpec`'s
   `items`/`preview`/`accept`/`search_part` function pointers
   (`picker.h`) become a host KIND matched in one place (G19/G20); a
   later lane's host (the symbol picker, yw11; plugins, yw14) is a kind
   that refuses by name. yw04's `ws.fuzzy` is the scorer. Unit:
   `test_walk` (20), `test_gitignore` (26), `test_picker` (13),
   `test_pickers` (10), `test_narrow` (11), `test_typejump` (11) —
   **91**. PTY: `s26_*` (5), and `startup_multiple_files` (yw05's
   R-yw05-5 = A: its tabs are yw05's and green, its snapshot is
   `:buffers` Enter, `ed.find.buffer`). Fuzz: `fuzz_gitignore` (`fuzz_fuzzy` is
   yw04's). Perf: `tests/perf/finder.c`'s gates (a walk slice ≤ 3 ms,
   the first key ≤ 5 ms in frame, each narrowing key ≤ 5 ms complete,
   open → first paint ≤ 16 ms, `finder.c:39-41`; in-process: the port's
   own harness over the same 100,000-path corpus shape, `finder.c:74`).
5. **The router, context menus and drag** (s27, s57.13, s57.14,
   s57.15, s57.22, in R-yw06-2's order). `edit.mouse`: the one entry
   from `edit.input`'s mouse route (s27 DoD 2: one loop branch), the
   phase machine (a press arms, leaving the cell drags, wheels are
   impulses, Esc and focus-out cancel to the entry state), the region
   and the identity (`tab_id`, `gid`, path) captured at the press,
   s27 §2's region → action table with every unlisted row inert, the
   wheel scrolling the pane under the pointer (3 rows, `clamp`, never
   `follow`: DoD 5), multi-click through yw03's unit engines into H
   with the unit borrowed (400 ms, `mouse.h:75`), drag-reorder with
   nothing in the tab array moved until the drop, the dwell read from
   the pre-drag slots (`yew_strip_pre_payload`) — **500 ms at the pin**
   (`mouse.h:57`; s27 §4's 400 and s57.14 §3's 250 were superseded by
   s57.14's second field repair, `s57_14-tab-drag-feel.md:331`) — the
   120 ms autoscroll on a timer, the float and gap and row 1 as the
   group exit (s57.14), the explicit strip scroll surviving the
   follow-the-active clamp and the chevron hover (s57.15), a tab dropped
   on a pane edge splitting it (s57.22, over the edge zones and
   `ed.tab.split_*` yw05 ported into `edit.layout` and
   `edit.pane_cmds`). `edit.ctxmenu`: the target captured at open,
   clamped never flipped, greyed never hidden, the bordered themed box,
   hover through mode 1003 (yw01's `term.tty_mouse_motion`, never left
   armed), priority shedding. `edit.ctxrows`: one builder per kind and
   the action table (`yew_ctx_actions`) as data. The three `cmd_owner`
   rows (`ed.ui.context_menu`, `ed.mouse.enable`, `.disable`); s27 §7's
   glyph review and §8's degradation audit. What yw05's merge leaves as
   named refusals for the gesture (today `edit.input`'s `mouse_cancel`
   and `mouse_motion` comments and `edit.draw`'s `draw_panes` header,
   which draws no spawn zone "before it") is filled; whatever of
   `tabs.c`'s float and gap (s57.14 §2), `strip.c`'s explicit scroll
   (s57.15 §1) or `draw.c`'s spawn zone (s57.22 §4) it left unported is
   this deliverable's. Unit: `test_mouse` (61), `test_mouse_click`
   (10), `test_drag` (40), `test_ctxmenu` (24), `test_ctxrows` (17),
   `test_invariant9` (13), `test_degrade` (10) — **175**; the five
   `ctxrows_fuss_*` are registered under `#if YEW_WITH_FUSS`
   (`registry.c:2704-2710`) and build FUSS rows over Git fixtures: red
   by name naming yw13 (re-derive which of `test_mouse`'s cases reach
   `mod/git/fussmode.h`, `test_mouse.c:33`). PTY: `s27_*` (5),
   `chrome_*` (48: s27 §7's twelve elements × truecolor, `_nocolor`,
   `_colors_16`, `_ascii`), `s57_13_*` (9, of which
   `s57_13_fuss_file_menu` and `_fuss_dir_menu` are FUSS rows, yw13's),
   `s57_14_*` (1), `s57_15_*` (2), `s57_22_*` (5) — **70**. Fuzz:
   `fuzz_mouse` (100,000 events × 4 seeds with s57.13's 35-motion and
   ctrl-left mix: no stuck phase, no mutation without its release, 1003
   off whenever no menu is open). Perf: `tests/perf/mouse.c` (a 1,000-
   event burst ≤ 5 ms, ≤ 1 render, no allocation in the router; 1,000
   unheld motions over an open 20-row menu ≤ 20 renders; in-process:
   the port's own harness, the router's allocation read from the
   region ledger).
6. **The field repairs on ported surfaces** (s57.11, s57.12).
   `:!yew FILE` (`shell.c:301-647`): the conservative recognizer's
   table (s57.11 §1), the path from `yew_ws_root`, the destination by
   `yew_group_for_path` (`groups.c:329`, yw05's file), no job and no
   `*job:*` buffer, a ranged `:!` never navigating; its call in
   `yew_shell_cmd_run` (`shell_cmds.c:163`). s57.12's commands are in
   yw03's and yw04's ports (`ed.sel.extend.*`, `ed.clip.*`); its
   goldens are gated here, on yw05's bump (the fake clipboard reader,
   the job return). Unit: `test_shell_self` (4). PTY:
   `s57_11_shell_self_open`, `s57_12_*` (3). Any campaign-04 or -05
   case yw05's merge leaves red naming yw06 (its note's red-by-name
   list) is this deliverable's: the `*jobs*` table's scratch buffer is
   `ed.c:342-602`'s buffer list (Sprint 14's `Workspace`,
   `ed.h:132-155`), not Sprint 25's, so `edit.shell_cmds`'
   `shc_job_list` refusal needs nothing of deliverable 2.
7. **The static binary** (track rule 7, from M-YW5; M-YW-PAX1).
   `tools/build --static` (`target/static/yew`) in a baseline-glibc
   Ubuntu container on kasumi (`localhost/px13-ubuntu`, where pax's
   `tools/mkyew` builds it; never kasumi's CachyOS x86-64-v4 glibc,
   `tools/mkyew`'s header); `readelf` (ET_EXEC, no `PT_INTERP`),
   `yew --version` run, the sha256 read twice with the byte count,
   handed back for pax's `user/yew.pin` (px58's, at yew `77c1083`
   today) — a pax lane's change, never this lane's.
8. **The gates**: `tools/check-test` and `--native` green with the
   per-case checked run for every `[native]` fallback (G29); the **81**
   reachable PTY goldens of deliverables 2–6 and `startup_multiple_files`
   (`s25_*` 2, `s26_*` 5, `startup_explicit_workspace` 1,
   `startup_multiple_files` 1, the router's 68 — its 70 less the two
   FUSS menus — `s57_11_*` 1, `s57_12_*` 3) gated BY NAME in CI beside
   campaigns 03, 04 and yw05's — **M-YW5** as R-yw06-3 shapes it; the
   recorded step narrowed to what is red by design, by owner:
   `s57_9_block_days_*` (2: `wolf.fl`'s highlighting is in the
   golden's style rows, yw10), `s57_13_fuss_*` (2),
   `startup_directory_workspace` and `fuss_drawer_*` (6, s56.5 §2–§4) —
   yw13's. The 2× gates on kasumi under `taskset -c 0-3` in a
   container: `tools/run-perf-editor` over a restored 50-tab workspace
   (`startup.first_paint.workspace50`: C highlights its first `.c`
   buffer and the port cannot until yw10, said beside the ratio),
   `latency.navigate.many_buffers.p99` (`budgets.txt:21`;
   `perf_latency.c:837-866` spawns `--workspace` and 50 buffers) if
   yw05 did not run it, the picker's keystroke and open, and the
   port's harnesses beside C's in-process `perf_state`, `finder` and
   `mouse` rows; `mem.workspace50` recorded beside C's; the port/C
   ratio from the same run, the rig's drift.
9. **The note and the map**: `notes/yw06-workspace-finder-mouse.md`
   with the five sections, the measurements, the `unsafe` census
   delta, the codec's and the router's shapes and why; `docs/MAP.md` §2
   (the `ws` row: `trust*` per R-yw06-5, `state_fletch` yw09's; the
   `ui` row: `ctxmenu` and `ctxrows` here, not yw05, and `filter`), §3
   (the campaign-05 row per R-yw06-4 and **Decided**), §5 (G39's and
   G40's walk rows), §6, §7's yw06 paragraph and M-YW5's wording per
   R-yw06-3; yw07's contract drafted in full from §7.

## Rulings (to ask at launch unless decided)

- **R-yw06-1 — the state codec before Fletch.** MAP §7 says "hand-
  emitted until yw09". At the pin the shipping path is Sprint 36's:
  `state_emit.c` builds an `FlValue` tree in a Fletch VM and writes it
  with `fl_data_write` (`state_emit.c:27-92`), restore reads through
  `yew_fl_parse_fletch` (`state_parse.c:1021`, `state_fletch.c`), both
  over yw07's `fl/data.c`; s25's hand codec (`fl_emit.c`, `fl_parse.c`,
  829 lines) is filtered out of the build (`Makefile:671`) and no test
  or fuzz target links it (`state_lit.c:1`'s "test-only" is stale). The
  format is frozen and Sprint 36 proved the two byte-identical before
  retiring the differential (s25 §9). (A) port the hand codec as the
  interim production path, its strings `List[byte]` (never `str`:
  invariant 2, G40), proved on the corpus (`test_state_corpus`) and by
  a C↔port differential — the `state.fl` C writes in
  `s25_resume_exact`'s session read and re-emitted by the port
  byte-identical, and the port's read by C — retired by yw09's swap
  (recommended); (B) port `fl/data.c`'s pure-literal reader and writer
  here, a slice of yw07 in the wrong lane; (C) s25 waits for yw09, and
  M-YW5's resume box with it.
- **R-yw06-2 — the router's order.** R-yw05-1 put s57.13–s57.15 and
  s57.22 after s27. The pin's `mouse.c` is post-s57.22, and s27's own
  goldens were regenerated by the later sprints: `chrome_ctxmenu*` and
  `s27_group_menu_over_scrolled_strip` by s57.13 (sagitta `0e6006b4`,
  `2b15a4f6`, `771cfaec`, 2026-09-11/12), `chrome_ctxmenu` again by
  s57.22's Open in Split Left row (`59d1250c`, 2026-09-18),
  `chrome_drag*` and `s27_dwell_opens_member_strip` by s57.14
  (`41f0b77b`). No s27-only router can be held to the pin's goldens.
  (A) one router at the pin's state, committed in the narrative's order
  (s27, then s57.13, s57.14/15, s57.22, by C function), its 70 PTY and
  175 unit cases gated as a set at the end (recommended); (B) s27 first,
  its goldens red until the rest lands — a gate that cannot go green
  mid-lane; (C) the four as a lane of their own beside yw06 — two lanes
  in one 3,090-line file.
- **R-yw06-3 — M-YW5's shape.** The index's M-YW5 is "yew's Sprint 42
  field checks run on the wolf binary". Sprint 42 is campaign 08's
  (`08-highlighting/s42-langpack-2.md`), and its §10 is a field-
  evidence gate (`:445-500`): "Automated tests and benchmark runs do
  not count" (`.docs/dogfood-log.md:3-6`), and C yew's own state is
  `PENDING` with nothing recorded (`.docs/milestones.md:8-21`). The ten
  boxes: Duration (`:456`, ≥ 10 working days and ≥ 40 h as the
  maintainer's primary editor — his own `init.fl` needs the Fletch VM,
  yw07–yw09, R-yw03-2's reader refusing the rest), Self-hosting
  (`:463`), Zero data loss (`:469`), Zero crashes (`:473`), Terminal
  restore in the field (`:476`), Latency live (`:480`: `YEW_LATENCY_LOG`
  is read nowhere in `src/` at the pin; the live profiler is `YEW_PROF`,
  Sprint 56's `util/prof.c`, yw15), the other budgets (`:484`: a
  stripped binary ≤ 1.5 MiB full and ≤ 900 KiB minimal — the port is
  always the full build, R4, and size is yw15's), **Highlighting covers
  our own tree** (`:488`: `ed.syn.status`, yw10), Workspace resume in
  anger (`:495`, ≥ 20 cycles: this lane), Modal completeness (`:498`).
  None needs LSP; FUSS only through `yew DIR`'s drawer. (A) M-YW5 at
  yw06 is the automated half: deliverable 8's 81 goldens green by name,
  plus the automated twins of boxes 3–7, 9 and 10 on the wolf binary —
  a scripted 20-cycle quit/reopen loop over `s25_resume_exact`'s
  arrangement compared grid for grid, the three restore trials
  (`SIGKILL`, `SIGSEGV`, the terminal closed) in a container, the
  budgets beside C, `test_invariant9` — the field gate named the
  maintainer's, after yw10 (box 8) and yw09 (his configuration)
  (recommended); (B) M-YW5 waits for the field window after M-YW8; (C)
  M-YW5 is campaign 05's PTY goldens alone, as M-YW3 was worded.
- **R-yw06-4 — the sprints that are not workspace, finder or mouse.**
  MAP §3 and §7 give yw06 s56.5, s57.5, s57.6, s57.7, s57.9, s57.10 and
  s57.20. s56.5 §2–§4 and §7 are FUSS's (`src/mod/git/fussmode.c`,
  Sprints 51–53) and §5 shadow's (`src/ui/shadowdraw.c`, Sprint 43);
  s57.5 is `fusstree` (Sprint 52); s57.6 is binary isolation from
  syntax, LSP and the symbol index plus FUSS path normalisation; s57.7
  is the FUSS off-canvas layout. s57.7 has no yw06 half: every
  deliverable consumes FUSS (`yew_fuss_drawer_rect`, the `git.drawer`
  theme role, `test_fussdrawer.c`), and until yw13 the drawer is
  inactive and `yew_layout` lays out from column 0 — what the
  `MODULES=""` shim returns (s57.7 §4's last row) and what yw05's
  layout already does; the tab strip's offset is yw13's whole. (A)
  yw06 takes s56.5 §1 and §6 (deliverable 3); yw13 takes s56.5 §2–§4
  and §7, s57.5, s57.6 §2–§3 and s57.7 (`fuss_drawer_*` 6,
  `startup_directory_workspace`, `test_fussdrawer` 27,
  `test_fussexpand` 7); yw11 takes s56.5 §5 (`test_shadow_layout` 10)
  and s57.6 §1's LSP and symbol-index halves; yw10 its syntax half
  (recommended: the map corrected, nothing ported early); (B) port the
  drawer here — refused: its model (`FussTree`, Sprint 52) has no port.
- **R-yw06-5 — the trust database.** MAP §2's `src/ws/` row gives
  `trust*` to yw06 and `edit.driver`'s config comment calls the
  `.yew.fl` gate "(yw06, the trust database)". `trust.c` reads and
  writes it through the Fletch VM (`trust.c:168`, `:278`
  `fl_data_read`, `:1069` `fl_data_write`), and its consumers are
  `flconf.c`'s workspace-config gate (`:401`, `:437`) and the AI grants
  (`:715-726`, s50); s25 §9 defers the `.yew.fl` prompt to Sprint 36.
  (A) `trust*` stay yw09's with `flconf.c`, the map and that comment
  corrected (recommended); (B) port `trust.c` here over the hand codec,
  with no consumer until yw09.
- **R-yw06-6 — paths that are not UTF-8 (G40), and G39.** G39 does not
  bite the walk: C reads each directory whole and sorts it before
  descending (`walk.c:285-311`), as `fs_read_dir_entries` does, and its
  slices fall between entries, never inside a read. G40 does: an entry
  whose name is not UTF-8 cannot be listed or stat'ed where C lists it
  (no `test_walk` case has one), and a restored tab whose `path` is not
  UTF-8 (`07-invalid-utf8-path.fl`, `08-control-bytes-path.fl`) cannot
  be opened. (A) the codec carries such a path as bytes and re-emits it
  byte for byte; the walk skips such an entry and logs it naming G40; a
  tab with such a path is restored as an orphan (s25 §6's missing-file
  row: kept, dimmed, counted in the one message), never dropped
  (recommended: no golden reaches it); (B) a STOP by name at the first.
- **R-yw06-7 — reachable PTY count (Decided A, 2026-10-23).** The
  enumerated prefixed cases total 79 after excluding the two FUSS menus;
  both startup cases are separate, so gate all **81**, not the draft's 80.
  No case or golden is removed to keep the old total.
- **R-yw06-8 — jump-state mechanism (Decided A, 2026-10-23).** Port
  `src/ws/state_emit.c:485-520`'s literal entries and their restoration.
  Keep `src/edit/jumplist.c:344-385`'s separate text serializer uncalled,
  as the pin does; share position resolution where it is the same code.
  The earlier instruction to call that serializer was a mechanism error,
  not permission to change the frozen schema. No golden changes.
- **R-yw06-9 — unsigned coordinate wire values (Decided A, 2026-10-23).**
  C loads signed literals into unsigned cursor/view/ring/mark fields and
  emits their signed bit interpretation (`src/ws/state_parse.c:321-334`,
  `src/ws/state_emit.c:550-565`). Preserve out-of-range values as sparse
  raw wire metadata beside safe live coordinates until C's clamp point;
  clear the metadata when an edit or clamp replaces the live value.
  `top_sub` uses the C u32 mask. Keep this state bridge local rather than
  retrofit the earlier text and viewport engines to u64. Prove both the
  no-edit load/save round trip and the same coordinate-moving edit against
  C, including distinct wide cursors, identity retention and removal.
- **R-yw06-10 — disk-ignore loading (Decided A after the C witness,
  2026-10-23).** Match the pinned implementation, not the stronger prose:
  `src/ws/walk.c:378-381` calls the loader on `.git/info`, and
  `src/ws/gitignore.c:479-482` appends `/.gitignore`; `exclude` is not read.
  `src/ws/gitignore.c:505` gives disk-loaded rules a NULL base, so a nested
  anchored rule does not get the in-memory API's base scoping. The C-only
  witnesses in `notes/yw06-evidence/finder-inputs/` confirm both findings;
  require the port's identical listings on those same fixture trees when
  the finder lands. Report the C findings, never silently fix them in the
  port or change a golden. If further measurement contradicts the static
  reading, measured pinned C is the oracle.
- **Decided**: R-yw05-1 = A (2026-10-22). s57.9's C is yw03's `block.c`
  and yw05's `groupfromdir.c` and `groupnav.c` (its unit cases are
  `test_block`'s, `test_groupfromdir`'s and `test_groupnav`'s), its
  `Alt+g` path is FUSS's and its two goldens are yw10's; s57.10's C is
  yw05's `tabs.c` and `groupnav.c` (`test_groupnav`; no `s57_10_*` PTY
  case exists); s57.20 ports nothing — no `--check-runtime`, no
  `yew_runtime_dir`, no staleness message in `src/` at the pin, and
  `print_version` (`main.c:88-100`) prints no runtime line, so building
  the spec would change the `version` golden (rule 2). Sprint 36's
  Fletch data path, the `.yew.fl` prompt and the option model are
  yw09's; multi-session merge is post-1.0 (s25 §5's lock is the 1.0
  answer); middle-click paste stays off by default (s27 §6); LSP
  hover-on-pointer and sub-cell mouse are non-goals (s27 §9).

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`; **`Footprint:
cross-cutting`** — the gate list is CI itself (`.github/workflows/
ci.yml`'s by-name steps, yw04's "goldens, campaign 04" shape), and the
pin if deliverable 1 moves it. Read sagitta's `src/ws/workspace*`,
`state*`, `fl*`, `walk*`, `gitignore*`, `src/ui/picker*`, `pickers*`,
`filter*`, `typejump*`, `mouse*`, `ctxmenu*`, `ctxrows*`,
`src/edit/ws_cmds*`, `ed.c` and `shell.c` freely and cite `file:line`;
facsimile's and fuss's interaction designs only as sagitta's C and
sprint text state them — **no other editor's, finder's, tree walker's,
ignore matcher's or terminal's source, ever** (fzf, git's matcher and
libc's walkers are not read; git is never run to answer an ignore
question, s26 §4). No dependency but wolf-std. No golden edited; a
disagreeing golden is a STOP with the diff. A picker host, a menu kind,
a row builder and a drop target are KINDS matched in one place, never
a function value across a module boundary (G19/G20; if deliverable 1
takes yew#27, one shape per registry, never both); the workspace state,
the walk and the router's state are VALUES threaded through the `Ed`
(E1010). **Every run of C yew and of the port with a scratch `HOME`
and `XDG_STATE_HOME`**: s25 writes `$XDG_STATE_HOME/yew/workspaces/`,
and yew#11 found `tools/goldens` and `tools/oracle --unit` writing
kasumi's `~/.local/state/yew` — fix those two first if it is open
(listed to close, never closed here); the maintainer's state is never
written. The lock's gone pid, the kill-9 torture, every fork and every
PTY golden inside a container (RULES §5); signals only to processes the
test started. The static build never on kasumi's host glibc. The
toolchain rule is deliverable 1.

## Inputs (re-derive)

sagitta at the pin: the ten sprint files of the header with their
line counts, and for R-yw06-4 and **Decided** `s57_5` (545), `s57_6`
(201), `s57_7` (236), `s57_9` (189), `s57_10` (96), `s57_20` (141);
`08-highlighting/s42-langpack-2.md` §10 (`:445-500`),
`.docs/milestones.md`, `.docs/dogfood-log.md`; the C files of the
header with their headers, `ed.c:2815-3030`, `ed.c:342-602`,
`shell.c:301-647`, `shell_cmds.c:150-175`, `groups.c:329`,
`Makefile:671`; `tests/unit/test_{ws_key,ws_save,ws_restore,ws_recover,
ws_history,ws_cmds,state_schema,state_corpus,state_options,walk,
gitignore,picker,pickers,narrow,typejump,mouse,mouse_click,drag,
ctxmenu,ctxrows,invariant9,degrade,startup,shell_self}.c` (24 files,
**399** tests, every one registered in `tests/unit/registry.c`, five
under `#if YEW_WITH_FUSS`) and `fixtures/wsstate/v1/` (46 files);
`tests/pty/registry.c` (the `s25_`, `s26_`, `s27_`, `chrome_`,
`s57_11_`, `s57_12_`, `s57_13_`, `s57_14_`, `s57_15_`, `s57_22_` cases,
the four `startup_` rows, `s57_9_` and `fuss_drawer_` for the recorded
step) and their goldens; `tests/fuzz/fuzz_state.c` (418),
`fuzz_gitignore.c` (272), `fuzz_mouse.c` (464), `Makefile:101`,
`:135-139`; `tests/perf/perf_state.c` (383), `finder.c` (425),
`mouse.c` (451), `perf_startup.c`, `perf_mem.c`, `perf_latency.c`,
`budgets.txt` (`:21`, `:35`, `:62`). The yew repo at yw05's merge:
`src/edit/driver.lu` (the start's refusals, the trust comment),
`input.lu` and `draw.lu` (the gesture's refusals), `layout.lu`,
`pane_cmds.lu`, `tabs.lu`, `region.lu`, `cmd.lu`'s `cmd_owner` and the
twelve `cmdtab.lu` rows it routes here (`ws_cmds.c` 5, `mouse.c` 3,
`pickers.c` 4), `cmdline_hist.lu`, `jumplist.lu`, `shell.lu`,
`shell_cmds.lu`, `cmdedit.lu`'s `ws_scratch_find`, `term/tty.lu`'s
1003 arming, `ws/fuzzy.lu`, `util.f32`, `tools/build`, `tools/goldens`,
`tools/oracle`, `.github/workflows/ci.yml`, `docs/MAP.md`,
`notes/yw05-panes-tabs-groups.md` (its STOPs and its red-by-name
list); wolf 0.2.34's `spec/11-os.md` `[os.fs.stat]` (the twenty words,
`:3070-3110`) and `[os.signal.send]` (`:537-552`), `fs_read_dir_entries`,
`fs_read_at`, `fs_realpath`, `fs_create_dir_mode`; pax trunk's
`tools/mkyew` and `user/yew.pin` (read only).

## Prediction (write before the first change)

The workspace state, the finder and the router port with no golden
edited and none of campaigns 03's, 04's or yw05's changing as the
start, the mouse route and the strip's scroll are widened; the codec
round-trips the corpus (22 canonical documents re-emitted
byte-identical, 4 noncanonical re-emitted canonical, 20 invalid each
reaching a result) and the C↔port differential on `s25_resume_exact`'s
`state.fl` is byte-identical both ways; the permille fixpoint holds for
all 999 values through `util.f32`; a 40-tab restore performs one file
read; the 81 reachable goldens go green, the router's 68 as one set at
the end (R-yw06-2); the walk's determinism and the narrowing
equivalence (10,000 appends against a full rescan) hold; `fuzz_state`,
`fuzz_gitignore` and `fuzz_mouse` hold their invariants; every 2× gate
within 2× of C yew, `workspace50`'s first paint read beside the
highlighting caveat; the static binary builds, is ET_EXEC with no
interpreter and runs `--version`; if a 0.2.35 lands, yew#17, #20, #22,
#23, #24 and #27 retire with their tests green and no golden edited.

## Done-when

Every deliverable with its tests; `tools/check-test` and `--native`
green and the per-case checked run recorded; the 81 goldens of this
contract green by name against the wolf binary as far as the rulings
let them (M-YW5 as R-yw06-3 rules it), the rest named by gap or owner;
the 2× gates recorded on kasumi under `taskset -c 0-3`; the static
binary's digest read twice; `docs/MAP.md` updated; yw07's contract
drafted; CI green; PR open with the five sections, shas as bullets, a
test checklist and its `Footprint:` line; `bash
wolf/tools/lane-audit.sh yew yw06 <PR>` passing but for the final run's
green; hand back per RULES.md §6.
