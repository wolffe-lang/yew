# yw07b — Fletch core, deliverables 2–10

yew#70 (draft). Branch `yw07b` from trunk `ee16798d`, under the adopted
contract `notes/contracts/yw07-fletch-core.md` (deliverables 2–10) and the
lane contract `wolf/sprints/yew/07b-fletch-core/yw07b-fletch-core.md`.
The first lead (a Codex lane) stopped at `ce79664a`. The lane continues
from that state with a Claude lead and its two forks, `yw07b-front` and
`yw07b-core`.

Footprint: cross-cutting

## Forbidden

The lane kept the adopted contract's Forbidden section, `sprints/RULES.md`
§1–§10 and the lane contract's rules. Each item below was checked at the
final head.

- **No golden edited.** No golden, unit case, conformance file, fixture,
  baseline, oracle or pin changed. Two checks at the head:
  - `git diff --numstat ee16798d..HEAD -- tests/ sagitta.pin
    wolf-toolchain.toml` shows no deleted line.
  - The 27 files the lane added under `tests/fuzz` are the pin's fl_parse
    and fl_std corpora and `dict/fuzz_fl_parse.txt`. `cmp` finds them
    byte-identical to `sagitta.pin`'s.

  No golden disagreed, so there was no STOP.
- **Clean room.** sagitta at the pin is the only implementation read, and
  it is cited by `file:line`. No other language implementation's, VM's,
  GC's, regex library's or float-conversion library's source was read.
  - The Codex content classifier cut the Astra front fork twice.
  - From then on no Codex fork worked on the fl scope, on the
    orchestrator's ruling. An Opus fork took the front scope.
- **One kind-id/match for every mutable callback (R-yw07-10).** It covers:
  - the natives (`fl_native_dispatch`);
  - the collector's host root providers;
  - the host command rows (`vm.host_cmds`);
  - the handle receivers (`fl_api_bind_receiver`).

  No production row-pool shape was revived.
- **G54 (wolf-lang#948)** is a tier-disagreement row and nothing more: the
  witness program, its exit status per tier and the issue link in MAP. No
  core dump, signal mask, memory layout or disassembly was read.
  Caller-owned native temporaries stay allocation-pending with no
  boundedness claim, and no scratch region wraps a native's allocation.
- **Hosts.** Nothing was built on nomad. Every Linux job ran on kasumi
  CPUs 8–11 under `flock ~/lanes/kasumi-cores-8-11.lock`, in the container
  `notes/yw07b-evidence/lane/ctr.sh`:
  - `--network none`, `taskset -c 8-11` and `ulimit -c 0`, under an 8 GiB
    cap;
  - a scratch `HOME` and `XDG_*`, and an explicit `YEW_RUNTIME_DIR`, for
    every run of C yew and the port;
  - `YEW_FL_GC_STRESS` passed through since `a7dc914`.
- **Commits.** One per deliverable or chunk, terse and imperative, with no
  attribution or co-author trailer:
  `git log --format=%B ee16798d..HEAD | grep -ci co-authored` is 0.
- **Plants.** Each was a draft PR on a `yw07b-plant-*` branch, red on its
  named row and closed unmerged by the orchestrator (the table under the
  Evidence index).
- **Rulings.** New questions are recommended as R-yw07b-1..8 in
  `docs/MAP.md` §6, never decided here. The planning repo `wolf/` and
  `~/.claude` were only read.
- **unsafe.** One block was added (15 to 16): `math.random`'s seed at
  `src/fl/stdmath.lu:25`, over the module `var fl_math_rng_state` at line 7.
  Its `// # Safety:` comment names invariant 8, the single-threaded core.

## Inputs, verified

- **Toolchain.** `gh release list` for `wolffe-lang/wolf-lang` and
  `wolffe-lang/wolf-interp` was read at 2026-10-25T08:45:06Z and again at
  10:39:38Z. Both releases are Latest:
  - wolf v0.2.35, 2026-10-23T08:45:33Z;
  - lupin 0.1.56, 2026-10-23T04:43:45Z.

  `wolf-toolchain.toml` pins exactly these, so there is no bump.
- **The oracle.** sagitta is at `sagitta.pin` `9ace98c2`. C yew is built by
  `tools/oracle` with `fletch_run`, `fl_smoke`, the three Fletch fuzz
  drivers and `perf_fletch` (`9bc796a`). The trace build is separate, with
  `CFLAGS_FL_TRACE=1`.
- **Counts re-derived at the pin:**
  - 198 unit cases over 17 files (`tools/fl-cases.txt`, with sagitta's
    registry names);
  - 39 conformance units (`tools/fletch-units.txt`);
  - 178 dump comparisons: `--dump-ast` and `--dump-bytecode` over the
    oracle's 56 `tests/fletch` files and its fl_parse 23, fl_std 3 and
    fl_vm 7 corpora;
  - 21 `fl_smoke --trace` fixtures and 60 opcodes;
  - 187 natives, where the port's `--list-natives` is byte-identical to
    C's;
  - 17 value tags (the erratum);
  - `smoke.sh`'s 12 `yew fl` rows.

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
| yew#74 | `7d6c2d69` | 40185456135 | `tools/check-fl-trace` (the VM leaves POP out of its executed trace) | after `PASS all 60 opcode discriminants/operands/effects match pinned C`, `FAIL fl-trace normal: 21 fixtures, C/port, two processes each` and the same for stress; since `0c56cb3` the gate also names the first differing fixture |

## Done-when

Pending at the final head.
