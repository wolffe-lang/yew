# yw07b — Fletch core, deliverables 2–10

yew#70 (draft). Branch `yw07b` from trunk `ee16798d`, under the adopted
contract `notes/contracts/yw07-fletch-core.md` (deliverables 2–10) and the
lane contract `wolf/sprints/yew/07b-fletch-core/yw07b-fletch-core.md`.
The first lead (a Codex lane) stopped at `ce79664a`. The lane continues
from that state with a Claude lead and its two forks, `yw07b-front` and
`yw07b-core`.

Footprint: cross-cutting

## Forbidden

Pending at the final head.

## Inputs, verified

Pending at the final head.

### Rulings in force

- R-yw07-1..9 as the adopted contract recommends (ruling #118), and
  R-yw07-10 = A: one kind-id/match representation for mutable callbacks
  (natives, the host seam, registries); read-only callbacks are function
  values.
- **R-yw07b-1 = A**: R3's compacting sweep, measured on the toy VM. The
  native tier's misses are a named backend MISS, never a waiver.
  `docs/MAP.md` §6.
- **R-yw07b-2 and R-yw07b-3**: Linux glibc C is the float seam's oracle.
  Exactly two exception classes are excluded from the cross-host identity
  claim (1,080 NaN-sign presentation rows, one `nan(+1)` grammar row), and
  every other difference is fatal (`42354f0`). The port's own NaN
  differences against Linux stay open as G51 (wolf-std#103).
- **R-yw07b-4 (provisional)**: DIV on a non-numeric operand raises
  `cannot apply '/' to <left type> and <right type>` (kind `type`) instead
  of reproducing `vm.c:793-807`'s read of pointer bits. The two C runs
  differ between processes (`notes/yw07b-evidence/core/div-c-{1,2}.txt`).
  This is one named oracle-defect exception, and the defect goes to the
  maintainer.
- **The 17-tag erratum**: the pinned `value.h` has 17 tags (`FL_MOTION_PROG`
  and `FL_UPVAL` separate, `FL_TYPE_COUNT` 17). The contract's "15 tags"
  yields to the pin.

### Gaps met (docs/MAP.md §5)

G51 (wolf-std#103, NaN sign and payload), G52 (wolf-lang#942, the lent
`bytes()` copy), G53 (wolf-lang#943, the checked machine's `reset`+push
ledger) and G54 (wolf-lang#948, a tier disagreement: a region-built
100,000-byte value exits 0 on checked and 139 on native and release).
Under G54, caller-owned native temporaries stay allocation-pending with no
boundedness claim, and no scratch region wraps a native's allocation until
the issue is answered.

## Prediction

The pre-change prediction is `notes/yw07b-evidence/prediction.txt`
(unchanged). Its outcome is pending at the final head.

## Evidence index

Pending at the final head.

## Done-when

Pending at the final head.
