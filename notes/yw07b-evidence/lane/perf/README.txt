yw07b lead: tools/run-perf-fletch --release, then --native, at the tree of 3bb5f11
(front's parse fixes and core's 39e118b merged), kasumi CPUs 8-11 in the lane
container (ctr.sh) under ~/lanes/kasumi-cores-8-11.lock, 2026-10-25 11:17-11:46Z.
C's rows are perf_fletch's from the same run (one warmup + 11 in-process samples,
medians). Exit 1 on each: the runner prints every MISS and is not --advisory here.
release.log, native.log: the runner's verdict lines, unedited.
