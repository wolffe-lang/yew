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

Pending at the final head, except the gates seen red below.

### Gates seen red

Each plant is a draft PR on a `yw07b-plant-*` branch, red on the named
row and closed unmerged by the orchestrator.

| PR | plant head | run | gate | red row |
|---|---|---|---|---|
| yew#67 | `16158a5d` | 40165616674 | collector: the toy VM's root control | `test_compact_roots`, `test_fixed_roots`, `test_compact_cycle` FAILED (trap(assert)) |
| yew#68 | `383a6d3f` | 40165620144 | collector: the generation control | `test_compact_reentry`, `test_fixed_reentry` FAILED (trap(assert)) |
| yew#69 | `8907d201` | 40165623757 | collector: the memory control | `wolf-trap: assert` |
| yew#71 | `9990410f` | 40183128447 | `tools/check-fletch-goldens` (io.print doubles its separator) | `FAIL 01-lexical.fl`, line 58 OUT not satisfied `\|255 255 1000000\|`, then `FAIL 02-grammar.fl`; `again: 19 of 39 units PASS by name`, `RED` |
| yew#72 | `2a88441d` | 40183131866 | `tools/check-fl-dump` (the AST printer's `(let` gains a space) | `FAIL --dump-ast tests/fletch/01-lexical.fl (exit C=0 port=0)`; `total=178 pass=148 fail=30` |
| yew#73 | `1b1474cd` | 40183134255 | `tools/smoke-fl` (an io error exits 1) | after the oracle's 12 rows, the port's `FAIL fl exit 3 (io escaping) (exit 1, want 3)` |

## Done-when

Pending at the final head.
