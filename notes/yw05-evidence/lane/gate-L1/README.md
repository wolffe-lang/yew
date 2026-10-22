# gate L1: the lane at `d53daae` (the bump whole: wait, sync, panes, the bits, jobs)

kasumi, the lane tree `~/lanes/yw05/yew` synced from the worktree at
`d53daae` (docs-only commits after it), in the container on CPUs 0-3,
2026-10-22T14:59Z-17:01Z (`lane-gate.sh`, `L1.log`). Both tiers, the demo
and the torture child built with warnings denied (release `84b3d40ca0cc`,
native `cb0282373d29`, demo `342323f79070`, torture `fa4c1d531e73`).

| gate | release | native |
|---|---|---|
| campaign 01 (18) | 18/18 | 18/18 |
| campaign 03 (62) | 62/62 | 62/62 |
| campaign 04 (104) | **104/104** | **104/104** |
| s22 (11) | 11/11 | 11/11 |
| the burst pair, 20× each | 20/20, 20/20 | |
| `tools/check-test --native` | | exit 0, 94 files ok, 0 FAILED, 52 SKIP lines |
| `tools/check-test` (checked) | | "94 passed; 0 failed; 0 rejected; 0 unsupported" |
| the replica port/C, C/port, port/port | GREEN ×3 | |
| `tools/torture-live` (no acceptance) | GREEN | |

The last step, the layout fuzz against C, could not run here: this tree's
oracle predates `tools/oracle`'s `build/fuzz_panes` target (exit 2, "not
built"); the panes fork's gate g3 ran it at `ef7ad62` (equal to C on both
tiers), and CI's oracle job builds and runs it.
