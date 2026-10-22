# gate g2: the panes fork's sources at 3592b3f

The dev tree on kasumi (`~/lanes/yw05-panes/dev`) was checked against the
worktree with `rsync -rcn` (content checksums) before these sweeps were saved:
only `tools/run-perf-panes` differed, and it was not yet written when the
gate ran. Every source the sweeps exercise is 3592b3f's.

Run in the container on CPUs 12-15 (`CTR_CPUS=12-15 ~/lanes/yw05/bin/ctr`).

| sweep | release | native |
|---|---|---|
| c05, s22's 11 | 11/11 | 11/11 |
| c03 | 62/62 | 62/62 |
| c04 | 83/104 | 83/104 |

c04's 21 reds are the same 21 names on both tiers and the same 21 as the
milestone tree's sweep (yw04's job half, s19 and s57.24-29), which this fork
does not touch.
