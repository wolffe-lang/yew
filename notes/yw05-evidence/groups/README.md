# yw05 — the `groups` fork's evidence (Sprint 24, tab groups)

kasumi, wolf 0.2.34 / lupin 0.1.55 / wolf-std `e036bec`, in `ctr`'s
container on CPUs 4-7 (`taskset`, `ulimit -c 0`, 8 GB, no network), the
fork tree `~/lanes/yw05-groups/yew`, synced from the Mac worktree and
checked against it by content (`rsync -rcn`: no source differs) before
every run kept here. sagitta at `9ace98c2`.

## What the fork ports

Sprint 24 (`s24-tab-groups.md`) over the tabs fork's model, contract
deliverable 4, ruling R-yw05-4 = A:

- `edit.groups` (`244790d`'s hook aside, `bdd1b53`): `groups.c` whole —
  the `TabGroup` with NO member list (membership is `Tab.group_id` and a
  compacted `Tab.group_ordinal`, counts and members computed on every
  ask), create/find/dissolve (stragglers ungrouped), add (out of the old
  group first) and remove (ordinals compacted, an emptied group
  AUTO-DISSOLVES), the live `label (N)`, the derived active group,
  `group_for_path`, `prune_empty`, `set_ordinal` (the final order built
  first: the rightward off-by-one), `reorder_block` (the destination
  computed as tab IDs first: the interleave), the resume point as a PATH
  that may dangle; and s24 §3's defer half (`yew_buf_defer`,
  `yew_tab_defer`, never the active tab). Residency is asked of the
  buffer slot (`Buffer.resident`, set where the piece tree is built,
  cleared where `buf_defer` releases it); `Tab` has no residency field.
- `text.file_load_count` (`244790d`): C's `file_load_calls`, bumped at the
  top of `file_load` (`file.c:347`), the counter s24 DoD 4 is counted
  through — one new `unsafe` module var (census +1, invariant 8's).
- `Ed.groups`, `Ed.next_group_id`, `Ed.gp`, `Ed.group_resume_reads`
  (`aacf788`): C's `Groups`, the picker's file static, groupnav's DoD 6
  hook — values of the `Ed` (E1010).
- `edit.groupnav` (`60196fe`): the continuous line (`file_step`: inside a
  group by ordinal, off either end the fall-through to row 1, wrapping),
  `enter_at_edge` (first member moving right, last moving left, never the
  resume point), the explicit `group_enter` (resume by path, dangling to
  the first), `group_leave`, and `ed.file.next/prev`, `ed.group.next/prev`,
  `.enter`, `.leave`, `.close` (one gesture, refused before any mutation),
  `.dissolve`, `.remove_tab`, `.add_tab`, `.rename`.
- `edit.grouppicker` (`4ce6473`): the one New/Edit dialog — ticks a SET of
  canonical paths in insertion order surviving every walk, `preselect`
  and the dirty bullet, the listing (`../` pinned, directories then
  regular files by `stat`, case-folded stable sort), the keys, the chrome
  and its regions (`REGION_BLOCK`, `GP_NAME`, `GP_ROW` from one row
  arithmetic), the click, the apply (New: create, adopt or open deferred,
  join; Edit: additions first, then the leavers closed by tab ID), and
  `ed.group.new`, `.edit`, `.pick.toggle`, `.pick.confirm`.
- `edit.groupfromdir` (`6b9f557`): `ed.group.from_dir` with a directory
  (the picker on its canonical path, nothing ticked; a file refused) and
  `group_from_files`, the half of `yew_group_from_dir` after its walk.
- `651a055`: the fourteen handlers through the registry (ids 800-813);
  `0a03f61`: the picker owns the keyboard after the prompt
  (`ed.c:2350-2358`) and its row/name presses (`mouse.c:1443-1446`), draws
  after the cursor (`ed.c:2732-2746`); the strip click, the numbered jump
  and the mouse release note the group's resume point before entering.

What refuses by name, and why: `yew_group_from_dir`'s WALK (sorted,
recursive, gitignore-aware: `ws/walk.c`, `ws/gitignore.c`) is sagitta
Sprint 26's (yw06) — the message names it; the F-mode selected directory
(`yew_fuss_selected_directory`) is Sprint 53's (yw13), unreachable while F
mode itself refuses at its entry; the 100k audit storm's every-1,000-op
restore through `state.fl` is Sprint 25's (yw06). Hover preview, drag into
a group and the group menus are Sprint 27's (yw06); persistence is s25's.

## The gates

`gate-g1/`, head `e90401f` (before the tabs fork merged): both tiers and
the demo built, 2026-10-22T14:52Z; s22's 11, the tabs fork's 8 (7/8:
`startup_multiple_files` RED, the STOP below), s24's 4, campaign 03 62/62
and campaign 04 104/104 by name on both tiers; `check-test --native` 97
ok, 1 FAILED — `edit_modes_test` at `:153`, the tabs fork's own
`tab_jumps_are_global` case, which still expected `alt+1` to refuse by
name and which the tabs fork had already rewritten on its branch
(`863e39a`). The run was stopped there (the merge below supersedes it);
the sweeps and the native lane's log are kept.

`gate-g2/`, head `3842fd5` (`origin/yw05-tabs` `fa71296` merged, the
three group SKIPs turned into runs), 2026-10-22T16:39Z, the tree checked
against the worktree by content before the launch (identical). Release
`8397d9fdde16`, native `057784270331`, demo `dcf5be29df3e`.

| gate | result |
|---|---|
| s22's 11, release and native | 11/11, 11/11 |
| the tabs fork's 8, release and native | 7/8 both: `startup_multiple_files` RED (the STOP) |
| **s24's 4**, release and native | **4/4, 4/4** (`s24_click_enters_a_group`, `s24_digit_jump_is_immediate`, `s24_group_two_row_bar`, `s24_picker_chrome`) |
| campaign 03, release and native | 62/62, 62/62 |
| campaign 04, release and native | 104/104, 104/104 (the jobs fork is in `yw05`) |
| `check-test --native` | exit 0: 100 files ok, 0 failed, 68 SKIP lines |
| per-case checked (`percase.log`) | groups 21/23 (the two storms: step budget), groupnav 35/35, grouppicker 19/20 (the key storm: step budget), groupfromdir 8/8, tabs 34/35 (`cap_refuses_and_mutates_nothing`: step budget, the tabs fork's row), strip 14/14; 0 fail — the four `unsupported` rows exhaust the 20M-step budget and rest on the native run (G29) |
| `run-fuzz-groups --campaign --against-oracle` | four seeds × 250 sessions, every report line equal to C's `build/fuzz_groups`: `5e2c4f62b62bdb1e`, `a6ff09d5651172b8`, `db82ea1477b0f0ae`, `e2db6cf3c8453317` |
| `run-fuzz-tabs --campaign --against-oracle` | seed 1 `7f6650298b07dd0e` and the random lane (seed 1948741335) `c5f6a18d6b0ecf60`, both equal to C's |
| `check-test` (the checked lane, `wolf test`) | exit 0: `100 passed; 0 failed; 0 rejected; 0 unsupported` (`check-checked.log`), ended 2026-10-22T18:50Z |

No golden edited. The six files' own lines in `check-native.log`:
`groups_test: 23 cases pass, 1 SKIP by name (the 100k storm's restore
half, yw06)`; `groupnav_test: 35 cases pass, 0 SKIP`; `grouppicker_test:
19 cases pass, 0 SKIP; 1 port case passes`; `groupfromdir_test: 1 case
passes, 4 SKIP by name (the walk, yw06); 3 port cases pass`; `tabs_test:
34 cases pass (+1 port, which SKIPs by name under root)` — the two group
cases the tabs fork left SKIPped now run; `strip_test: 14 cases pass, 0
SKIP` — its group case runs. Every SKIP prints on both streams with its
owner; the native log holds 10 such lines from the group files (each
said twice).

**The STOP (unchanged from the tabs fork):** `startup_multiple_files`'s
golden shows the `:buffers` picker (Sprint 26, yw06); the tabs fork
recorded its full diff (`notes/yw05-evidence/tabs/`). It stays RECORDED
in CI.

## Plants (`plants/`)

One break per new test file and for the fuzz, planted in the code the
file covers, run natively in the container, seen red, the file restored
from a pristine copy (the tree's sources then compared with the worktree
by content: identical):

| plant | the break | red |
|---|---|---|
| `groups-test.txt` | `group_set_ordinal` keeps the moved member while inserting (the rightward off-by-one) | `edit_groups_test` trap at `:258` (`set_ordinal_moves_right_by_exactly_one`), exit 134 |
| `groupnav-test.txt` | `group_enter_at_edge` always enters at the first member | `edit_groupnav_test` trap at `:177` (`walk_is_reversible`), exit 134 |
| `grouppicker-test-set.txt` | `gp_tick` appends a path already ticked | `edit_grouppicker_test` trap at `:225` (`ticks_are_a_set`), exit 134 |
| `grouppicker-walk.txt` | a walk drops every tick (`gp_walk_to` clears the set) | `edit_grouppicker_test` trap at `:558` (the port case), exit 134 |
| `groupfromdir-test.txt` | `ed.group.from_dir` takes a file for a directory | `edit_groupfromdir_test` trap at `:194` (the command case), exit 134 |
| `fuzz-groups.txt` | `group_remove_member` never auto-dissolves | `fuzz_groups: FAIL seed=1 iter=0 … group count 3, oracle 2`, exit 1 |

`grouppicker-walk-uncaught.txt` is the walk plant against C's nineteen
alone: GREEN. C's `ticks_survive_directory_navigation` presses Down — a
cursor move — and never walks, so a picker that loses its ticks at every
re-list passes C's whole file; the port case
`port_grouppicker_ticks_survive_a_real_walk` (`e90401f`) walks into
`sub/` and back and is the one that goes red.
