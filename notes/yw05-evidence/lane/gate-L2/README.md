# gate L2: the lane at `c673add` (the final sources: the bump, panes, tabs, groups, the hot paths)

kasumi, the lane tree `~/lanes/yw05/yew` synced from the worktree at
`c673add` (every later commit is notes, docs, CHANGELOG or a tool outside
the editor; the tree's `src/`, `tools/` and `tests/` hash equal to the
worktree's file for file, the build caches aside), in the container on
CPUs 0-3, 2026-10-22T21:32:00Z-23:23:00Z (`lane-gate.sh`, `L2.log`). Both
tiers, the demo and the torture child built with warnings denied (release
`dba78dd07b22`, native `21f1c3ee293d`, demo `d940d4552d4b`, torture
`945039e63056`).

| gate | release | native |
|---|---|---|
| campaign 01 (18) | 18/18 | 18/18 |
| campaign 03 (62) | 62/62 | 62/62 |
| campaign 04 (104) | **104/104** | **104/104** |
| campaign 05, s22 (11) | 11/11 | 11/11 |
| campaign 05, s23 + s57.8 + `startup_multiple_files` (8) | 7/8 | 7/8 |
| campaign 05, s24 (4) | 4/4 | 4/4 |
| the burst pair, 20× each | 20/20, 20/20 | |
| `tools/check-test --native` | | exit 0, 101 files ok, 0 FAILED, 66 SKIP lines |
| `tools/check-test` (checked) | | "101 passed; 0 failed; 0 rejected; 0 unsupported" |
| the replica port/C, C/port, port/port | GREEN ×3 | |
| `tools/torture-live` (no acceptance) | GREEN | |
| `fuzz_panes`, `fuzz_tabs`, `fuzz_groups` against C's drivers | equal hashes, every seed | |

Campaign 05 is **22 of 23** on both tiers: `startup_multiple_files` is the
one red, R-yw05-5 (its tabs are C's; its snapshot is the `:buffers`
picker, Sprint 26, yw06's; `sweep-L2-c05-tabs-cases-*-startup_multiple_files.log`).

The 66 native SKIP lines are 33 cases on two lines each, every one naming
its owner: the workspace walk and state (yw06: four `groupfromdir`
cases, the 100k storm's restore half), the recorder and Fletch's idle hook
(yw09), the option table rows (s36, yw09), the syntax engine (yw10), the
symbol index (yw11), F mode, the git badge and the diff rows (yw13). None
is a toolchain gap: G37's `~user` SKIP is macOS's and the fake clipboard
tool's is CI's port job's (both by name, neither reached here). The
checked lane prints one line per file (`wolf test` at 0.2.34 shows no
program output), so its SKIPs are the forks' per-case runs (the note §4.2-
§4.4).

`tools/torture-live` still prints its one KNOWN-RED by name: with kill9's
shared state home the port's second determinism run lacks the first's
history append (the port's `:` history is global until the workspace
state; yw04's `05391c7`); the lane with a state home per run is GREEN.
yw06's per-workspace history retires it (yw06's draft names it).
