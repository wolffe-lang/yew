# yw05-tabs: the evidence

The `tabs` fork of lane yw05 (Sprint 23 and s57.8: the tab model, the strip
engine, the commands, the dirty-close question, several startup files, the
tab oracle). Every run below is on kasumi inside the lane's container
(`~/lanes/yw05/bin/ctr`, archlinux:base-devel under podman, `taskset -c
8-11`, `ulimit -c 0`, 8 GB, no network), never on nomad-1. The kasumi
tree's sources were checked against the commit named (`rsync -rcn
--delete`, content: no difference) before each run was kept.

## The final gate, `fg1` (`gate-fg1/`)

Started 2026-10-22T14:00:14Z (`fgate.sh`, one `step NAME rc N` line a
step, each exit read directly). Its binaries — both tiers of the editor,
the demo, the tab fuzz driver on both tiers — were built from **`4d3b453`**;
its unit-test steps (`check-test --native`, `percase.py`, `check-test`)
ran over **`863e39a`**, which differs from `4d3b453` in one test file
only (`src/edit_modes_test.lu`, the tab-jump case run whole; the tree was
re-synced and checked before those steps began). No file under `src/`
other than test files changed between the two.

Ended 2026-10-22T16:20:58Z, `fg1.rc` 0. The binaries' digests are on
each sweep file's first line (native editor `a20f791ffce7`, release
`b9f1fef56cae`, demo `b2baba051cb6`).

| step | native | release |
|---|---|---|
| `tools/check-fmt` | rc 0 | |
| `tools/build` (warnings denied) | rc 0 (45 s) | rc 0 (703 s) |
| `tools/build-demo` | rc 0 | |
| the tabs fork's 8 (`c05-tabs-cases.txt`: `s23_*` 6, `s57_8_click_new_tab`, `startup_multiple_files`) | **7/8**, red: `startup_multiple_files` (the STOP below) | **7/8**, the same |
| `s22_*` (11) | 11/11 | 11/11 |
| campaign 03 (62) | 62/62 | **61/62**, red: `notepad_burst_keys` (`raw-key burst rendered 2 frames, expected 1`, taken at a host load average of 33 on 16 cpus; 6 of 6 reruns green at load 14.6, `burst-reruns.txt`) |
| campaign 04 (104) | 84/104 | 84/104 |
| the tab oracle against C's driver (10,000 sessions a seed) | seed 1 and the random lane 3150417451: port and C report lines equal | seed 1 and the random lane 1238879250: equal |
| s57.8's renditions (`renditions.py`) | | rc 0 (below) |
| `tools/check-test --native` | rc 0: 96 files `[native] ok` | |
| `percase.py` (G29) over the two new files | strip 14 cases: 14 checked-pass (1 of them the SKIP); tabs 35: 34 checked-pass (2 of them SKIPs), 1 unsupported (`tabs_cap_refuses_and_mutates_nothing`, the step budget: 512 tabs; it rests on the native run) | |
| `tools/check-test` (the checked machine) | `wolf test: 96 passed; 0 failed; 0 rejected; 0 unsupported` | |

Campaign 04's 20 reds on both tiers are exactly the 20 job rows the lane
records by owner (diffed by name; the jobs fork is not on this base), and
`s57_31_edit_in_buffer_open`, `_roundtrip` and `s57_31_toggle_sudo` are
green on both. The pinned seed's `hash=7f6650298b07dd0e` is C's on both
tiers, the witness both drivers ran the same 10,000 sessions (~1.2 M
operations: 80 to 159 a session) with the whole id list and the active id
compared after every one.

## STOP: `startup_multiple_files` (`startup_multiple_files-fulldiff.txt`)

Red on both tiers, and it stays red by a new name: its snapshot is the
`:buffers` picker. The case (`tests/pty/registry.c:8573-8606`) starts the
editor on two files, checks both tab labels and the second file's text on
screen, then types `:buffers` Enter and snapshots — `ed.find.buffer`,
`yew_find_cmd_buffer` in `src/ui/pickers.c`, "Sprint 26 §6": the fuzzy
finder, campaign 05's second half (yw06). The full diff (`YEW_PTY_DIFF=full`,
at `9f8b3f9`, the startup code unchanged since): rows 1-2 are C's cell for
cell (` 1 start-one.txt  2 start-two.txt  + ` with the second active, then
`    1 startup second file` — each file its own tab in C's order, the last
read and shown, the first non-resident); every row after differs because
the port answers `E: not yet ported: ed.find.buffer: sagitta Sprint 26
(pickers) (yw06)` where C draws the picker (`find.buffer`, the two rows,
the deferred first one dim, the `2/2 …` footer). No golden edited. CI keeps
it in the recorded `startup_` step, its warning renamed to that owner.

## The plants (`plants/`)

Each a one-line break in the kasumi tree only, run, seen RED, restored
from a backup (`cmp` clean), never committed (`plants.sh`, run over `169c84c`'s sources — the same
as `4d3b453`'s — 2026-10-22T13:55Z):

| plant | the break | the red |
|---|---|---|
| P1, `edit_strip_test` | `strip.lu:144` the follow walk steps `first += 2` | exit 134, `edit_strip_test.lu:140` ("by one": scroll minimality) |
| P2, `edit_tabs_test` | `tabs.lu:469` `tab_shifted_index`'s `i <= to` as `i < to` | exit 134, `shifted_index(1, 0, 1) = 1, simulation says 0` (`:392`) |
| P3, `edit_tabs_test`'s port row | `tabs.lu:1564` a refused `w` falls through to the close | exit 134, `:923` ("the tab survives the refused write") |
| P4, `fuzz-tabs` | `tabs.lu:424` the close keeps the active INDEX, clamped, instead of the survivor's id | exit 1, `FAIL seed=1 iter=0 … active tab has id 8, oracle says 7`, the input as hex |

P5 (`plant5.sh`, `plant5.log`, at `863e39a`'s sources, after fg1): the
digit window's Insert rule dropped (`tabs.lu:1312`, `ed.mode != MODE_I &&
ed.mode != MODE_F` as `ed.mode != MODE_F`) turns `edit_modes_test` red:
exit 134 at `edit_modes_test.lu:168` ("no window in Insert"); restored.

## The contract's checks

- **The modified `*` is derived, never cached (s23 DoD 4).** `grep -n
  "dirty\|modified" src/edit/tabs.lu` at `863e39a`: every hit is a call of
  `tab_modified` (`tabs.lu:505-515`, which asks `buf_dirty` — the buffer's
  undo tree away from its save point, `ed.lu:543-545`), a style named
  `modified`, `StripEntry.modified` (C's `StripEntry` field, filled from
  that call each frame, `tabs.c:733-788`), or `layout_dirty`/
  `footer_dirty` (damage flags). `Tab` (`ed.lu:81-95`) holds no modified
  or dirty field. `Ed.drawn_tab_marks` is C's `tab_marks_record`
  (`ed.c:2609-2618`): what the strip DREW last frame, for the redraw
  check, recomputed from `tab_modified` each frame and never read as the
  marker. Witnessed by `tabs_modified_derives_from_undo_state` (edit →
  marked, undo to clean → not, redo → marked) and `s23_modified_marker_
  follows_undo`.
- **The 512-tab cap, every `tab_open` checked (DoD 6).** `TAB_MAX` 512;
  over it `tab_open` and `tab_open_buffer` answer -1 with `too many tabs
  (max 512)` (C's message, `tabs.c:297-299`) before any id is issued.
  Every caller (`grep -rn "tab_open(\|tab_open_buffer(" src`, test files
  aside): `driver.lu:230` (`if idx < 0` → `cannot open tab`, exit 3),
  `cmdedit.lu:362` (`if idx >= 0 … else` shows the buffer in place),
  `tabs.lu:1203` and `:1216` (`ed.tab.new`, `ed.tab.open`: `if idx < 0`
  → `CMD_ERR_STATE`). No bare call. Witnessed by `tabs_cap_refuses_and_
  mutates_nothing` (no tab, no active change, no id burned).
- **A read-only `w` aborts the close (DoD 7).** No C unit row or golden
  reaches it (`s23_dirty_close_*` answer `d`), so `edit_tabs_test`'s
  `port_tabs_dirty_prompt_write_refused_keeps_the_tab` pins it: the file
  0444 in a 0555 directory, the question answered `w`, the save refused,
  the tab still there and still modified, `could not write …` on the
  message line as an error, the bytes on disk untouched. Plant P3 saw it
  red.
- **`ed.tab.goto 0` reaches tab 10 (DoD 8).** `tabs_goto_maps_zero_to_
  ten_and_refuses_out_of_range` (0 → index 9; 99 refused, the active tab
  unmoved), and `modes_tab_jumps_are_global_and_insert_keeps_its_digits`
  (alt+1 from L, W, B, I and H; the 500 ms window armed except in Insert)
  run whole.
- **s57.8's renditions** (`renditions.py`, `gate-fg1/renditions-release.log`):
  the strip is C's cell for cell in every rendition. Whole screens
  equal: truecolor (`chrome_tabs`), 16 colours (`chrome_tabs_colors_16`,
  `s57_29_prompt_select_colors_16`), mono (`chrome_tabs_nocolor`,
  `s57_29_prompt_select_nocolor`), ASCII (`chrome_tabs_ascii`,
  `s57_29_prompt_select_ascii`) and dumb (`s41_theme_term_dumb`, TERM=dumb
  in the dumb profile). C's suite draws the 256-colour tier only under a
  syntax-coloured document (Sprint 41/42.5's kitchens, yw10's), so there
  the STRIP ROW alone is compared — its text and every cell's resolved
  style: equal in `s41_c_dark_colors_256` and `s41_c_light_colors_256`
  (and `s41_c_dark_colors_16`, `s41_theme_nocolor_empty`, `_set`), each red
  from row 2 on (the document's syntax colours). The `chrome_tabs*` cases
  are Sprint 27 §7's chrome review (yw06's) but draw nothing beyond s23
  and s57.8's strip.
- **yw04's `s57_31_edit_in_buffer_open` and `_roundtrip`** are in campaign
  04's 84 green rows on both tiers (A-e's tab over the full open and
  close).

## Unit tests: what is ported, what SKIPs

- `src/edit_tabs_test.lu`: `test_tabs.c`'s 34 in registry order
  (`registry.c:1721-1741`, `:2554-2566`): 32 run, **2 SKIP by name**
  (`tabs_group_label_clips_before_trailing_padding`, `tabs_negative_
  region_payload_enters_the_group`: they create a group, `yew_group_create`
  and `yew_group_add_member`, Sprint 24's values, the groups fork's), +1
  port row (DoD 7).
- `src/edit_strip_test.lu`: `test_strip.c`'s 14 (`registry.c:2546-2553`,
  `:2567-2572`): 13 run, **1 SKIP by name** (`strip_rows_own_their_
  offsets_independently`, the same group values).
- `src/edit_modes_test.lu`: `modes_tab_jumps_are_global_and_insert_keeps_
  its_digits` runs whole; the file's SKIPs drop from 4 to 3 (F mode, yw13).

The three group SKIPs turn into runs when `edit.groups` gains
`group_create`/`group_add_member` (the groups fork, `yw05-groups`): the C
bodies port as written against `edit.tab_row1_entries`, `edit.tab_strip_
click` over a hand-built region, and two `st_paint`s.
