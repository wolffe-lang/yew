# gate g3: the panes fork at `ef7ad62` (the ratio as C's float bits)

The dev tree on kasumi checked against the worktree with `rsync -rcn`
(content) before saving: no source differs. In the container on CPUs
12-15, 2026-10-22T13:12Z-13:48Z: both tiers and the demo built (release
`b98978d3a3d4`, native `8616bb51e878`); s22's 11 by name 11/11 on both
tiers; `tools/run-fuzz-panes --campaign --against-oracle` on both tiers
(four seeds × 10,000, every hash equal to C's driver) and 200,000 at seed
1 equal to C's (`d67ee79f885b048f`).
