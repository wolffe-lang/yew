yw07b lead: the GC-stress run's wolf/C ratio. tools/goldens --suite fletch (39 units)
under YEW_FL_GC_STRESS=1, C yew (target/oracle/sagitta/build/yew) and the port's
release build (target/release/yew) alternating, 7 samples each, in one lane container
(ctr.sh, kasumi CPUs 8-11, the core lock), at the tree of 2c8245b, 2026-10-25 ~11:10Z.
samples.tsv: who, sample, exit, wall microseconds (the whole suite, its process
spawns included), PASS count. summary.txt: medians, minima, the ratio. inner.sh: the run.
