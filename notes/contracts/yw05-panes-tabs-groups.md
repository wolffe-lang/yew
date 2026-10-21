# yw05 — panes, tabs and groups

**Model per ruling #89 R4, chosen at launch. Crawl 54+. Drafted by yw04
from `docs/MAP.md` §7 and sagitta campaign 05's first half, with the
yw04 carry-overs.** Ruling #89 (`sprints/yew/index.md`); the track's
seven standing rules; `docs/MAP.md` (the idiom §1, the gaps §5, the
rulings §6, as yw04 left them); `sprints/RULES.md`. Ports sagitta
campaign 05's s22–s24 (`.docs/sprints/05-ui-workspace/`:
`s22-layout-panes.md`, `s23-tabs.md`, `s24-tab-groups.md`, 894 lines at
`sagitta.pin`) and `13-performance/s57_8-modern-tabs.md` (279), the tab
strip's visual refresh. The C it ports: `src/ui/` `layout.c` (745) +
`.h` (210), `region.c` (147) + `.h` (129) — the whole registry, which
yw04 ported narrow for the menu (R-yw04-2) —, `tabs.c` (2,197) + `.h`
(327), `strip.c` (134) + `.h` (83), `groups.c` (507) + `.h` (128),
`groupnav.c` (434) + `.h` (70), `grouppicker.c` (1,164) + `.h` (109),
`groupfromdir.c` (205) + `.h` (20), `glyphs.c` (183) + `.h` (109), and
`src/edit/pane_cmds.c` (555) + `.h` (79), with the border and
dim-inactive half of `ui/draw.c` (s22 §7) over yw03's `edit.draw`:
**7,535 C lines**. The port inherits the idiom yw00–yw04 set and yw03's
module rule (every `ui` file that takes the `Ed` lives in `edit`,
`src/edit/*.lu`, sagitta's names kept); yw03's one-tab strip
(`edit.tabs`, R-yw03-3) and any narrow multi-tab extension yw04 made for
`A-e` (R-yw04-5) are replaced by the full model, and yw04's narrow region
registry (`edit.region`, the menu's rows only) is widened to s22 §6's
table.

## Deliverables

1. **The toolchain, first.** `gh release list -R wolffe-lang/wolf-lang`
   read and quoted with its time at the lane's start. yw04 finished at
   wolf 0.2.33 / lupin 0.1.54 / wolf-std `cceda63`: **v0.2.34 was
   published at 2026-10-21T12:58:10Z**, after yw04 had reached its job
   half (2026-10-20T23:19:20Z), so R-yw04-1 left the bump here. The bump
   (wolf 0.2.34, lupin 0.1.55 — published 2026-10-20T22:11:27Z — and the
   std the archive bundles, digests read twice) is yw05's FIRST commit
   with its prediction, and it ADOPTS what
   yw01–yw04 met as gaps, each with the test that is KNOWN-RED, SKIP or
   interim today turned green: `os_signal_wait_fds` (G2, wolf-lang#795)
   for the loop — the `VTIME` interim (`term.tty_wait`), yw03's drain
   mode and yw04's deadline-first turn order (`edit.loop`'s
   `loop_deadline_passed_first`, `3375b51`) retired — **and yw04's job
   half**, which R-yw04-1 stopped by name: the async stream, the region
   filter's read side, `:r !`, the persistent session, the generators,
   `--help` parsing and the fish oracle (yw04's note §4 lists every
   STOP, every SKIP-by-name unit case and every red golden of its 40;
   each turns green here or stays red by a NEW name); `fs_sync`/
   `fs_sync_dir` (G3, #796) at `text.file`'s and the journal's named
   sync sites — `save_fault_shim_contract`, the replica's determinism
   order and `tools/torture-live`'s known-red branch turn green and their
   acceptances are deleted (the tool fails until they are, by design);
   `fs_realpath` (G4, #797); `os_fork` (G30) for the clipboard writer;
   the `[os.term.mode]` widening (G34, #802), retiring R-yw03-4's
   LF-as-Enter interim; `os_term_restore_at_exit` (G1, #794) if yw01's
   guard is to retire with it. The filter's write side stays R-yw04-3's
   (wolf-lang#818) unless that pin also has it.
2. **The pane tree** (s22): `edit.layout` — `Rect` in cells and the
   layout/draw split (layout computes rects, drawing consumes them; the
   cells-based law that keeps multibyte text from desyncing clicks), the
   binary h/v split tree with ratios and `Win` leaves (node pool of
   indices, yw02's shape), minimum sizes and the refusal rules (s22 §3),
   spatial focus navigation (§4), keyboard and border-drag resize (§5;
   Esc mid-drag restores the entry ratio), the clickable-region registry
   in full (§6: every kind, the payload sign convention for
   `YEW_REGION_TAB`, the 256 cap logging once, cleared at frame START),
   borders and dim-inactive panes (§7) over `edit.draw`, every
   `ed.pane.*` command through the registry (`pane_cmds.c`). The loop's
   mouse route yw04 wired for the menu grows click-to-focus and the
   border drag; drag-reorder, wheel and context menus stay yw06's
   (Sprint 27). Unit: `test_layout` (45), `test_region` (7), `test_draw`
   (4). PTY: `s22_*` (11). Fuzz: s22 DoD 10's 10,000-op layout fuzz
   (region never queried between `frame_begin` and the first `add`).
3. **Tabs** (s23, s57.8): `edit.tabs` in full — `Tab` owns a pane tree
   with a stable `tab_id` surviving compaction and the `group_id` /
   `group_ordinal` fields s24 animates; the strip-layout engine
   (`edit.strip`: entries → cell spans, overflow scrolling, the `<` /
   `>N` indicators — MAP §2 lists `strip` under yw06; it is s23 §3's,
   corrected here); the modified `*` derived from the undo tree, never a
   cached flag (s23 DoD 4's grep); the tab commands, digit jump to tab N
   (`ed.tab.goto 0` reaches tab 10), the 512-tab cap with every
   `tab_open` checked; the close-with-dirty prompt (a read-only `w`
   aborts the close and shows the error, the tab survives); s57.8's
   modern strip (`glyphs.c`, the new-tab control, the theme's
   renditions in truecolor, 256, 16, mono and dumb). Unit: `test_tabs`
   (34), `test_strip` (14), `test_glyphs` (8). PTY: `s23_*` (6),
   `s57_8_click_new_tab` (1). Fuzz: s23 DoD 2's oracle (10,000 ops,
   pinned seed and a random lane).
4. **Groups** (s24): facsimile's model ported whole — groups hold NO
   member lists (membership is `group_id` + a compacted `group_ordinal`
   on the tab, computed on demand), `last_active_member` a PATH, empty
   groups auto-dissolve, deferred tabs cost no file read until first
   viewed (s24 DoD 4: a 40-file group performs exactly one read,
   counted through a hook in `text.file`), residency asked of the
   allocation, never a flag; `groupnav.c`'s continuous line with
   enter-at-edge semantics and N rights then N lefts reversible; the
   digit jump's 500 ms extension window (jump in the same frame, then
   arm); the New/Edit group picker (`grouppicker.c`, ticks as a path
   set surviving directory navigation); row-1 `[label (N)]` entries with
   the negative payload and the row-2 member strip (one renderer for
   pinned and hover preview); `groupfromdir.c`'s `ed.group.from_dir` as
   far as campaign 05 reaches it (F mode is yw13's). Unit: `test_groups`
   (23), `test_groupnav` (35), `test_grouppicker` (19),
   `test_groupfromdir` (5). PTY: `s24_*` (4). Fuzz: the 5,000-op
   membership fuzz (no empty group survives any sequence).
5. **Several startup files** (`startup_multiple_files`, the startup row
   yw03 recorded as yw05's): each file its own tab in C's order.
6. **Allocation-free hot paths** (R-yw03-7 = A, if ruled; yw03's note
   §4.6: ~630 B a line move and ~340 B a typed key kept to the session's
   end, G33/G18): the statusline, gutter, tab strip, theme lookups and
   the prompt's per-keystroke rebuilds (yw04's measurement, its note
   §4) write into storage the `Ed` already owns, digits formatted in
   place, no interpolated `str` per frame — measured with yw03's
   `ptymem.py` before and after, C beside it from the same run.
7. **The gates**: `tools/check-test` and `--native` green with the
   per-case checked run for every `[native]` fallback (G29); the
   **30** campaign-05 PTY goldens of deliverables 2–5 (`s22_*` 11,
   `s23_*` 6, `s24_*` 4, `s57_8_*` 1, `startup_multiple_files`; plus
   whatever deliverable 1 turns green of yw04's 40) gated BY NAME in CI
   beside campaigns 03 and 04 — **M-YW5's first half** (the daily driver
   is yw06's milestone: Sprint 42's field checks need the workspace,
   finder and mouse); the recorded step narrowed to what is still red by
   design, by owner; the 2× gates on kasumi under `taskset -c 0-3` in a
   container (`tools/run-perf-editor` over a two-pane and a many-tab
   session: keypress → paint and the tab switch, the port/C ratio from
   the same run, the rig's drift).
8. **The note and the map**: `notes/yw05-panes-tabs-groups.md` with
   the five sections, the measurements, the `unsafe` census delta, the
   layout tree's and the group model's shapes and why; `docs/MAP.md` §2
   (the `ui` files campaign 05's first half owns), §5 and §6 updated;
   yw06's contract drafted in full from §7.

## Rulings (to ask at launch unless decided)

- **R-yw05-1 — s57.13, s57.14, s57.15 and s57.22.** MAP §3 places them
  with yw05, but each one's prerequisites are Sprint 27's router and
  drag machinery (`src/ui/mouse.c`, `ctxmenu.c`, `apply_drag_preview`,
  `YEW_REGION_TAB_SCROLL`'s ±1/±2 convention, mode 1003 arming —
  `s57_13-mouse-overhaul-context-menus.md:3-14`,
  `s57_14-tab-drag-feel.md:3-14`, `s57_15-strip-scrolling.md:3-10`,
  `s57_22-drag-to-spawn-pane.md`), which MAP places in yw06. (A) move
  the four sprints (17 PTY cases: `s57_13_*` 9, `s57_14_*` 1, `s57_15_*`
  2, `s57_22_*` 5; `test_ctxmenu` 24, `test_ctxrows` 17) to yw06 after
  s27 (recommended); (B) pull s27's router forward into yw05.
- **R-yw05-2 — the 0.2.34 bump's size.** If deliverable 1 lands, yw04's
  job half (deliverable 3 of its contract: `job.c`'s consumers,
  `shsession.c`, the generators, help parsing, the fish oracle, 40 PTY
  cases of which yw04 left the job-bearing ones red by name) arrives
  with it. (A) yw05 takes it as deliverable 1 says (recommended: the
  code is ported to the STOP and the tests are written; the bump turns
  the stops into calls); (B) a lane of its own (yw04b) beside yw05.
- **R-yw05-3 — R-yw03-7 (a turn's temporaries).** yw03 recommended A
  scheduled into yw05 (deliverable 6); if the maintainer ruled B
  (E1010's precision) or C (accept until yw15), deliverable 6 goes.
- **R-yw05-4 — deferred-tab residency.** s24 §3 asks residency of "the
  allocation" (`text.file`'s load is lazy); wolf has no per-value
  resident model (G12): (A) residency is the tab's buffer slot being
  loaded (`Buffer` present in `ed.bufs` with its piece tree built), the
  read counted by a test hook in `text.file` (recommended); (B) a
  region per tab, `region_bytes` as the answer — refused if E1010 bars a
  region outliving the turn that made it.
- **Decided**: the tab strip's FUSS offset (s57.7) is yw13's; mouse
  routing beyond click-to-focus and the border drag is yw06's; groups'
  persistence (s25) is yw06's.

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. Read sagitta's
`src/ui/layout*`, `region*`, `tabs*`, `strip*`, `groups*`, `groupnav*`,
`grouppicker*`, `groupfromdir*`, `glyphs*`, `draw.c` and
`src/edit/pane_cmds.c` freely and cite `file:line`; facsimile's tab
model is ported as sagitta's C states it — **no other editor's or
terminal multiplexer's source, ever** (tmux, screen, vim's windows are
not read). No dependency but wolf-std. No golden edited; a disagreeing
golden is a STOP with the diff. A layout node, a tab, a group and a
region are VALUES threaded through the `Ed`, never module state of a
run-time value (E1010); a strip host or a picker host is a kind matched
in one place, never a function value across a module boundary
(G19/G20). Signals and every PTY golden inside a container (RULES §5).
The toolchain rule is deliverable 1.

## Inputs (re-derive)

sagitta at the pin: the three s22–s24 sprint files and s57.8 with
their line counts; the C files of the header with their headers;
`tests/unit/test_{layout,region,draw,tabs,strip,glyphs,groups,groupnav,
grouppicker,groupfromdir}.c` (10 files, **194** tests, every one
registered in `tests/unit/registry.c`); `tests/pty/registry.c` (the
`s22_`, `s23_`, `s24_`, `s57_8_` cases and `startup_multiple_files`)
and their goldens; s22/s23/s24's fuzz lanes (in their unit files or
`tests/fuzz/`, re-derive which); `tests/perf/budgets.txt` for the tab
and pane rows. The yew repo at yw04's merge: `src/edit/tabs.lu` (the
one-tab strip and any R-yw04-5 extension), `edit.region` (the narrow
registry), `edit.draw`, `edit.loop` (the mouse route, the deadline-first
turn), `edit.ed` (`Tab`, `tab_active`, `tab_scroll`), `edit.cmd`
(`cmd_owner` routes `pane_cmds.c`, `tabs.c`, `groupnav.c`,
`grouppicker.c`, `groupfromdir.c` here), `docs/MAP.md`,
`notes/yw04-execute-and-search.md` (its STOP list and R-yw04-5).

## Prediction (write before the first change)

The pane tree, tabs and groups port with no golden edited and none of
campaigns 03's and 04's changing as the one-tab strip and the narrow
registry are replaced; the 30 campaign-05 cases of deliverables 2–5 go
green; the layout fuzz, the tab oracle and the membership fuzz hold;
s24 DoD 4's one-read-per-group holds through `text.file`'s hook;
keypress → paint with two panes and the tab switch within 2× of C yew;
if 0.2.34 lands, the job half's red goldens of yw04 go green without a
golden edited and every G2/G3/G4/G30/G34 interim retires with its test
turned green.

## Done-when

Every deliverable with its tests; `tools/check-test` and `--native`
green and the per-case checked run recorded; the campaign-05 goldens of
this contract green by name against the wolf binary as far as the
rulings let them, the rest named by gap or owner; the 2× gates recorded
on kasumi under `taskset -c 0-3`; `docs/MAP.md` updated; yw06's contract
drafted; CI green; PR open with the five sections, shas as bullets, a
test checklist; `bash wolf/tools/lane-audit.sh yew yw05 <PR>` passing
but for the final run's green; hand back per RULES.md §6.
