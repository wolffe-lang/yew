yw07b lead: the GC-stress run's wolf/C ratio at the tree of 706933b (the final head's
code), the same method as ../gcstress/ (39 units under YEW_FL_GC_STRESS=1 through
tools/goldens --suite fletch, C yew and the port's release build alternating) with 11
samples, 2026-10-25 ~16:39Z. Median ratio 1.706; min/min 152685/88431 = 1.727.
The samples are noisier than ../gcstress/'s (C 88-268 ms against 87-111 ms there);
../gcstress-706933b-noisy/ is a 7-sample run minutes earlier (median 1.421, min/min
1.778). Every sample of all three runs: exit 0, 39 PASS.
