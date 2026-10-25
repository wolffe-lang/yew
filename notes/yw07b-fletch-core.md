# yw07b — Fletch core, deliverables 2–10

yew#70 (draft). Branch `yw07b` from trunk `ee16798d`, under the adopted
contract `notes/contracts/yw07-fletch-core.md` (deliverables 2–10) and the
lane contract `wolf/sprints/yew/07b-fletch-core/yw07b-fletch-core.md`.
The first lead (a Codex lane) stopped at `ce79664a`. The lane continues
from that state with a Claude lead and four forks, `yw07b-front`,
`yw07b-core`, `yw07b-fmt` and `yw07b-io`, every one merged back into
`yw07b` before the final head.

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
- **Rulings.** New questions are recommended as R-yw07b-1..9 in
  `docs/MAP.md` §6, never decided here. The planning repo `wolf/` and
  `~/.claude` were only read.
- **unsafe.** One block was added (15 to 16): `math.random`'s seed at
  `src/fl/stdmath.lu:25`, over the module `var fl_math_rng_state` at line 7.
  Its `// # Safety:` comment names invariant 8, the single-threaded core.

## Inputs, verified

- **Toolchain.** `gh release list` for `wolffe-lang/wolf-lang` and
  `wolffe-lang/wolf-interp` was read at 2026-10-25T08:45:06Z, 10:39:38Z and
  15:55:27Z. Both releases are Latest:
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
- **R-yw07b-5 to R-yw07b-8, recorded for the maintainer's batch and
  implemented as A** (the orchestrator's instruction). Each is in
  `docs/MAP.md` §6:
  - R-yw07b-5: `list.sort`'s default order on the reserved handle tags
    `FL_BUF`..`FL_REGEX`;
  - R-yw07b-6: a comparator that grows the list being sorted;
  - R-yw07b-7: `os_error`'s errno table;
  - R-yw07b-8: `str.repeat`'s wrapped product.
- **R-yw07b-9 (asked, recommend A)**: the Fletch VM's release MISS rows.
  The rows are named and carried to yw08 under R-yw08-3 A. The 2× bar
  stays, no row is waived, and the merge does not wait. See `docs/MAP.md`
  §6 and the performance table below.

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
(`c8545f9`), unchanged since it was written. The core and std predictions
followed it (`740125f`, `6d1cdf9`). Each claim below is set against what
was measured.

| predicted | measured | held? |
|---|---|---|
| The toy arena's `region_bytes` stays flat from collection 1,000 to 100,000; RSS grows by less than one 2 MiB quantum | The release ledger stayed at 484,896 B. RSS went from 2,887,680 to 2,891,776 B (`07965ca`, `a7f90a1`) | held |
| Both sweeps keep the eight root classes, reclaim an unrooted cycle, and reject the stale reference across a re-entrant native | All held. The three controls were seen red (yew#67–#69) | held |
| The compacting toy's release smoke ratios are 1.8 / 1.7 / 1.9 | 1.05 / 0.73 / 0.46 | better than predicted |
| The real VM's release smoke ratios (implied by the 2× bar) | 4.18 / 3.28 / 2.24 (fib24 / map10k / motion100k) | missed; R-yw07b-9 |
| Native may miss the 2× bar | It missed on every row, 60–194× (R-yw07b-1's named backend MISS) | held |
| The value is 24 B, against C's 16 B | `FlValue {t, i, f}` is 24 B | held |
| The first conformance failure is 02-values arithmetic, from the float seam | Wrong. The float seam was settled before the VM ran (R-yw07b-2/3, the Linux corpus, `42354f0`). The first CI conformance run, 40177235318 at `f3c3694`, passed 30 of 39 by name. Its first failing unit was `06-statements.fl`, at line 98 (`["z=1", "a=2"]`), on a pending native's refusal: `not yet ported: sagitta Sprint 31 fmt.int (yw07b)`. The nine reds were fmt's natives, stdio's filesystem rows and the editor API. All have landed since | missed |
| The float corpus needs an exact conversion for at least one libc surface | Yes, `fl.float` (`c1917ec`). NaN sign and payload stay open as G51 | held |
| Checked budget exhaustion is named, never passed | Every budget-bound case is an `allow` row with its reason in `tools/check-test-cases.txt`, and a row that starts passing goes red | held |
| 198 cases and 39 units pass, the units normal, stressed and twice, byte-identical | `check-fl-cases`: 198 rows over 17 files, ok. `check-fletch-goldens`: 39 of 39 by name in all three runs, byte-identical | held |
| The full GC-stress wolf/C ratio is 1.9 | 1.706 at `706933b`, 11 samples (min/min 1.73). It was 1.807 at an earlier tree | held (better) |
| `fl_smoke`'s collection counts are 0, 0, 155 | 0, 0, 155, equal to C's (`notes/yw07b-evidence/core/smoke-c.txt`, `smoke-release.txt`) | held |
| AST and disassembly dumps and opcode traces are byte-identical to the pin | 178 of 178 dumps. 21 of 21 traces, two processes each, normal and stressed | held |
| Three fuzzers match C at 200,000 × seed 1 | `fuzz_fl_lex`, `fuzz_fl_parse` (with its data mode) and `fuzz_fl_std` report C's line | held |
| The data bridge matches the hand codec on 22 canonical, 4 noncanonical and 20 invalid documents | 22 / 4 / 20 (`d5f848c`) | held |
| Every touched perf row meets 2×, and the startup and motion budgets stay hard | `parse_only` meets 2×. 11 of 13 release rows miss. The startup and motion_dispatch budgets hold on release | missed; R-yw07b-9 |
| The static binary is ET_EXEC with no PT_INTERP and runs `--version` and `fl -e` | `tools/build --static` at `706933b` in `localhost/px13-ubuntu` (Ubuntu 24.04.5, glibc 2.39-0ubuntu8.9). The result is `Type: EXEC`, `PT_INTERP=0`, statically linked; `--version` prints `yew 1.0.0-dev`; `fl -e` and `fl FILE` print `hello, world`; sha256 `aa89f0e40ddf35826091dad584bd17ad983561b5ab3c38b2ad4f5a9636b83fb3` (read twice); 21,162,368 bytes | held |
| No golden, oracle fixture, baseline or pin changes | None changed (Forbidden, above) | held |
| No row-pool shape revived; mutable callbacks keep one kind-id/match | Held (Forbidden, above) | held |
| G50 carried, never silently worked around; the #17/#27/#23/#40 portions stay open | G50 stays open, and the four issues stay open as yw07 left them | held |

## Evidence index

### Commits, by deliverable

The branch's own commits through `65acadd`, oldest first in each group
(`git log --no-merges origin/trunk..yw07b`). The one commit that adds this
list comes after them. The merge commits fold each fork back in, and one
brings in trunk's `12442b8`.

- **Predictions**
  - `c8545f9` Record Fletch implementation predictions
  - `740125f` Record core implementation prediction
  - `6d1cdf9` Record standard library continuation prediction
- **Deliverable 2, the toy VM and R-yw07-1's measurement**
  - `07965ca` Measure compacting and nonmoving toy collectors
  - `a7f90a1` Quote the compacting sweep's own residency in R-yw07b-1
- **Deliverable 3, `fl.value`, origins and the float seam**
  - `c1917ec` Add measured Fletch float conversion seam
  - `215cd76` Compare float conversions across libc hosts
  - `c235c8e` Link preserving float bits gap to upstream
  - `6921309` Define pinned Fletch origin and capability types
  - `b05f256` Add scalar values and compacting heap foundations
  - `42354f0` Classify only ruled NaN host differences
  - `f456d70` Index weak strings and widen heap generation coordinates
- **Deliverable 4, the lexer, parser, diagnostics and suggestions (front)**
  - `ad1c83a` Port the Fletch frontend and its 48 unit cases
  - `f2fccf1` Fold else-if chains without adding a depth limit
  - `0ca1c98` Exercise Fletch frontend differentials and bounded fuzz
  - `ea4920b` Centralize native argument diagnostics
  - `24dd675` Port scoped Fletch typo suggestions
  - `a7b139f` Name the didyoumean cases as the registry does
  - `7a259b7` Name the lex and parse cases as sagitta's registry does
  - `825524e` Preserve intermediate runtime name diagnostic limits
  - `bf2ed38` Add front's parse_only harness, profiling driver and A/B runners
  - `1a560e7` Index the Fletch interner with an open-addressing table
  - `ad4bf79` Let p_edges' pushes amortize instead of reserving per node
  - `9e68a8f` Record parse_only's A/B and the reserve witness
  - `4a608e3` Record the gates held across the parse perf fixes
  - `082a615` Give the lex, parse, re and re-direct cases checked-machine selectors
  - `2d5d868` Record the per-case checked, stressed and tier runs
- **Deliverables 5 and 6, the compiler and the VM (core)**
  - `e2faf72` Compile and execute all sixty Fletch opcodes
  - `1cb4db4` Cache frame coordinates until frame or heap changes
  - `b661d40` Leave incomplete input policy to compiler callers
  - `926dea2` Match C raise message truncation and NUL handling
  - `bf2bbad` Port all thirty VM cases with strict per-case evidence
  - `aa0a46a` Construct bounded raise strings without retained temporary lists
  - `98937b8` Verify the final VM case with list natives integrated
  - `2250112` Keep scalar stack transfers free of redundant copies
  - `ac3dc0a` Run all core cases under their pinned registry names
  - `8ab5248` Bind handle receivers before ordinary field lookup
- **Deliverable 7, `fl.gc` (core)**
  - `8c27a84` Port all collector cases with owned host root providers
  - `b8f7255` Avoid resetting already-empty retained heap slots
- **Deliverable 8, the std modules: registration, modules, trace, the fixture (lead)**
  - `515641f` Port the Fletch module loader and capability check
  - `1b0f24d` Register std modules and prelude behind one native dispatcher
  - `83836bf` Add the shared flfix fixture
  - `85f8a22` Port test_fl_trace over flfix.run_trace
  - `0b0540d` Port the Fletch stack trace
  - `059c043` Port module principal drop and the dropped state
  - `08037b2` Port test_fl_module over flfix
  - `35bd529` Echo diagnostics to stderr for the CLI and cap them at C's 511 bytes
- **Deliverable 8: str, list, map, re (front)**
  - `d9780db` Implement ordered map natives with direct tests
  - `bf7ab4a` Checkpoint string natives and scratch lifetime witness
  - `13da844` Port the list natives over yew_sort_stable's merge order
  - `8ba4f87` Test the list natives directly against C-oracle sort logs
  - `23f21fa` Record the list natives' tier runs
  - `3142490` Cite stdstr's C ranges and name str.repeat's wrapped product
  - `6292b28` Test the str natives row by row against the C oracle
  - `ba27112` Port the re natives over yew's regex engine, the cache held by the VM
  - `1d258f7` Test the re natives case by case against the C oracle
  - `f8b249a` Let the detached checked runner take a frozen tree
  - `1295b8b` Port test_fl_std_str's 9 cases over flfix
  - `c1e1caa` Port test_fl_std_list's 5 cases over flfix
  - `9017aea` Port test_fl_std_map's 4 cases over flfix
  - `5b2041f` Port test_fl_std_re's 14 cases over flfix
  - `534371d` Add the test-only fork staging and batched tier runners
  - `441c783` Read re.replace's match record in place, not a copy per match
  - `b9084bb` Fix the batched runner's file list and the old runner's module links
- **Deliverable 8: math, fmt, the data bridge, fuzz_fl_std (fmt)**
  - `78e8bdf` Port math native operations and seeded random state
  - `66e2331` Port fmt's display, repr and repl renderers
  - `9c9bc80` Port the seven fmt natives and retire their pending rows
  - `93ede69` Port test_fl_std_fmt's 14 cases over flfix
  - `fd91db4` Port test_fl_std_math's 6 cases and retire the math placeholder smoke
  - `5c3fcf4` Record fmt's black-box differential against C yew: 195 of 195 identical
  - `26291a7` Port fl.data, the pure-literal data bridge
  - `d5f848c` Gate fl.data against the hand codec over the v1 state corpus
  - `e6dcb7a` Register the fmt, math and data selectors for one-case checked runs
  - `dd3a747` Port fuzz_fl_std: 200,000 x seed 1 reports C's line byte for byte
  - `95f5398` Add fuzz_fl_parse's fl_data_read data mode, raw and framed
  - `87133a2` Pin fl.data's four caps at their exact boundaries
  - `e36606f` Record each fmt-fork gate seen red, and allow the round trip's checked budget
  - `a5b3e8e` Read each canonical state document once in the fl.data gate
  - `86f376c` Allow fl_data_test's three budget-bound cases on the checked machine
  - `6c25710` Stage every src module for the Fletch fuzz drivers: fl now reaches text and search
  - `47d0367` Record the fmt fork's tiers, fuzzers and differential on the merged tree
  - `48eeebc` Record the fmt fork's checked runs: every fmt, math and data case passes or is allowed
- **Deliverable 8: io, the capabilities, the editor API (io)**
  - `449275d` Keep the failing step's errno on text.file's atomic write result
  - `0c13486` Port io.print and io.eprint over fl_fmt_display
  - `dfb31ff` Port the rest of stdio.c: the capability-checked filesystem rows and io.glob
  - `8b38f06` Record the io errno witness: 49 cases, C yew and the port identical
  - `40d029d` Record the io.glob witness: 41 patterns, identical but G40's descents
  - `1a73d49` Record the descriptor-write order probe on native and release
  - `18f1cfd` Record text.file's three test files green on every tier after os_errno
  - `735ab4a` Port the editor API's headless natives as fl.flapi
  - `b05d0af` Record the editor API witness: 82 cases, ed.commands and both units, C yew and the port identical
  - `e72c703` Record the G40 witness: 14 io cases where C reaches bytes the port refuses by name
  - `a3aba10` Port test_fl_std_io's 13 cases over flfix, YEW_IO_CASE per case
  - `6c2bdb6` Port test_fl_caps's 5 cases over flfix
  - `e177428` Test the editor API's headless natives over every line of 34-editor.fl and kind_handle.fl, YEW_API_CASE per case
  - `75cd7f9` Record the io fork's tier runs: three test files native and release, normal and stressed, and 30 checked cases
- **Deliverable 9, `yew fl`'s non-interactive forms (lead)**
  - `2de2ca2` Port yew fl's non-interactive forms
  - `4556407` Re-point edit's Fletch refusals at yw09
  - `ab760eb` Hand edit's command registry to the VM in yew fl for ed.commands
- **Deliverable 10, the cases, conformance, dumps, traces, smoke and CI**
  - `9f0fdec` Port smoke.sh's ten yew fl rows as tools/smoke-fl
  - `ed6b2a4` Add the 198-case Fletch aggregate and its checker
  - `b91d766` Add the 39-unit Fletch goldens gate, by name, stressed and twice
  - `9b6d92c` Add the Fletch dump differential through yew fl
  - `d6f4ddc` Run tools/smoke-fl under scratch homes and an explicit runtime dir
  - `e6795ac` Gate CI on the Fletch cases, conformance, dumps and smoke rows
  - `f3c3694` Run the Fletch case aggregate at the end of the port job
  - `9bc796a` Build the Fletch fuzz drivers, fl_smoke and perf_fletch in the oracle
  - `cd2237d` Gate CI on fuzz_fl_lex against C's driver
  - `7ef9f07` Hold docs/fletch-spec.md to the pin's bytes in CI
  - `91cc4e9` Add smoke.sh's two hello-world rows to tools/smoke-fl
  - `76262f5` Gate CI on fuzz_fl_parse's data mode and fuzz_fl_std against C's drivers
  - `483e2fd` Gate individual core cases with canonical checked selectors
  - `557b32e` Package the pinned Fletch executed-trace gate
  - `e98b696` Gate CI on the Fletch executed-opcode traces against C's
  - `0c56cb3` Name the first differing fixture when the trace gate goes red
  - `9cfaa82` Measure case call order in the unmodified file in check-fl-cases
  - `858f858` Shard check-test-cases' run list with --shard I/N
  - `aaaa987` Run the checked cases in four CI shards with the allowance controls
  - `0692ae2` Keep the checked-cases job's comment beside the job
  - `fb29781` Reuse fuzz_fl_lex's driver build for fuzz_fl_parse in CI
  - `706933b` Hold the checked-cases job to its four ubuntu shards in legs-test
  - `f45ce81` Record the lane's container gates at 706933b
- **Performance: controls, the perf runner and the recorded rows**
  - `f86f727` Record rejected dispatch performance controls
  - `1c314dd` Record the field-lend performance control
  - `303162f` Record plain and profile-guided release controls
  - `39e118b` Package Fletch performance rows and explicit advisory gates
  - `69c6230` Record the release and native perf rows and the GC-stress ratio
  - `98e4b8d` Record the static binary and the GC-stress ratio at 706933b
- **Rulings, MAP, the yw08 draft, the ledger and the note**
  - `6de9bb2` Record yw07b rulings, the tag erratum and gaps G52-G54
  - `8ba6036` Record the yw07b fork scope ledger
  - `07c041f` Record the fmt and io forks in the scope ledger
  - `c9528e7` Ask R-yw07b-5 and R-yw07b-6, the list sort oracle defects
  - `ebf97b8` Name all five reserved handle tags in R-yw07b-5
  - `d373fed` Ask R-yw07b-7 and R-yw07b-8, errno names and str.repeat's product
  - `985dcf2` Map the Fletch VM's idiom rows, its source rows and G6 closed
  - `0b13303` Draft yw08's contract: the prompt, the bug report, the ledger and the perf gates
  - `cbc0767` Place campaign 06's sprint split between yw07b and yw08 in MAP §3
  - `1cb06f5` Add yw07b's paragraph and point yw08's at its drafted contract
  - `2c8245b` Record the six CI plants red by name in the lane note
  - `8b9d5e0` Record the trace plant red by name
  - `5333b30` Map List.reserve's exact growth as a per-append pitfall
  - `149ebc9` Bring yw08's draft to yw07b's head: the trace gate done, the perf harness, parse_only met
  - `8e289e5` Ask R-yw07b-9, the Fletch VM's release MISS rows, and close yw07b's MAP paragraph
  - `be4044a` Write the lane note's five sections and close the fork ledger
  - `65acadd` Complete the lane note: the static binary, the final gates and the GC-stress ratio
- **Lane housekeeping**
  - `a7dc914` Pass YEW_FL_GC_STRESS into the lane container
  - `73a6d21` Format the lead's Fletch files with wolf fmt

### The forks

At most four ran at once: front, core, fmt and io, from about 07:25Z until
core handed back at about 11:00Z. Each fork was a sub-branch of `yw07b`
and was merged back before the final head. Its scope ledger is
`notes/yw07b-evidence/lane/forks.txt`, and its status lines were in
`~/lanes/yw07b/status/`.

| fork | runner | scope | last merged head |
|---|---|---|---|
| (the first lead) | GPT-6-Astra (Codex), to `ce79664a` | the toy VM and R-yw07-1's numbers, the float seam, the front end's first cut | — |
| `yw07b-front` | Astra; the content classifier cut it twice. Then Opus 5.5 from about 06:45Z | lex, parse, diag, suggest; the str, list, map and re natives and their 32 cases; `fuzz_fl_lex`; `parse_only`'s perf; the checked selectors | `2d5d868` |
| `yw07b-core` | GPT-6-Astra | the compiler, the VM, `fl.gc`, the 58 VM and collector cases, the traces and their gate, the perf runner, handle receivers | `39e118b` |
| `yw07b-fmt` | Opus 5.5 from about 07:20Z | `stdfmt`, `stdmath`, `fl.data`, `fuzz_fl_std`, `fuzz_fl_parse`'s data mode | `48eeebc` |
| `yw07b-io` | Opus 5.5 from about 07:25Z | `stdio`, the capabilities, the editor API's headless natives (`fl.flapi`), their tests | `75cd7f9` |

The lead took the rest:
- `flfix`, std registration and the prelude, the global native dispatch;
- the module loader, `trace`, and `yew fl`'s non-interactive forms;
- the gates, CI, docs and this note.

A weekly API limit stopped the lead and the three Opus forks for about four
hours from about 12:00Z. After a re-login the lead resumed each fork by
message from where it stopped, and no detached job was duplicated.

### The final head

- **CI.** The integrated head `706933b` has run 40208663320 (ci), with
  40208663251 (float-hosts) and 40208663236 (toyvm). The final head's run
  is named in yew#70's body. Each run's id and first state were read once;
  the orchestrator watches it to the end.
- **The previous push.** `707b46f`'s ci run 40208511013 went red in
  `legs` on `ci/legs-test.py` L4. That assertion pinned the checked-cases
  job to one host, and `aaaa987` changed the job's shape, so the red was
  correct. `706933b` holds the test to the four-shard shape. It passes on
  `706933b`'s workflow and FAILs on the one-host workflow of `3a2786e`.
- **The local gates** ran on kasumi CPUs 8–11 in one lane container under
  the lock, at the tree of `706933b` (`f45ce81`). After that tree only notes
  and docs change, so these verdicts hold for the final head's code. Logs
  are in `notes/yw07b-evidence/lane/gates/`; every step exited 0.

| gate | verdict |
|---|---|
| `tools/check-fmt` | exit 0 |
| `tools/check-fletch-goldens target/release/yew` | 39 of 39 units PASS by name, normal, under `YEW_FL_GC_STRESS=1` and again; the two runs byte-identical; GREEN |
| `tools/check-fl-dump target/release/yew` | `total=178 pass=178 fail=0` |
| `tools/check-fl-trace` | 60 opcodes match the pin; 21 fixtures, C and the port, two processes each, normal and stressed: PASS |
| `tools/smoke-fl`, C yew and the port | `12 rows ok`, twice |
| `python3 -I tools/check-fl-cases` (and `--selftest`) | `198 rows over 17 files; ok` |
| `tools/check-test-cases-selftest`, `tools/test-check-test-cases` | the 8 adapter controls and the shard partition PASS; the allowance controls OK |
| `tools/check-test-cases` over `fl_std_io_test` and `fl_api_headless_test` | `30 cases over 2 files, 0 red` |
| `fuzz_fl_lex` against C's driver | `seed=1 iters=200000 corpus=120 hash=fbb01f1cebb66b40 ok`, both |
| `fuzz_fl_parse` (its data mode included) against C's driver | `seed=1 iters=200000 corpus=120 hash=5f59d6272d103c77 ok`, both |
| `fuzz_fl_std` against C's driver | `seed=1 iters=200000 corpus=8 hash=18a19f695b1ac125 ok`, both |

The other selector files' checked runs were done by their forks, each
case alone, normal and stressed: core's 41, fmt's fmt, math and data rows,
and front's lex, parse, re and re-direct. They are under each fork's
evidence directory. CI's four checked-cases shards run them all again at
the final head.

### M-YW6 and the GC-stress run

M-YW6 has four artifacts. yw07b's share of them is in CI by name:
- `yew fl FILE` and `yew fl -e` printing `hello, world` (`tools/smoke-fl`'s
  two rows from `smoke.sh`);
- the 39 conformance runs, normal, stressed and twice
  (`tools/check-fletch-goldens`).

The REPL golden `s33_hello_world_repl` and the coverage ledger beside the
conformance gate are yw08's (its drafted contract, deliverables 5 and 7).

**The GC-stress wolf/C ratio is 1.706 at `706933b`**, against a prediction
of 1.9.
- The run: the 39-unit suite under `YEW_FL_GC_STRESS=1`, C yew and the
  port's release build alternating, 11 samples each, the whole suite's wall
  time with its process spawns.
- Medians: 270.0 ms for the port, 158.3 ms for C. The minima are 152.7 ms
  and 88.4 ms, a ratio of 1.73.
- All 39 PASS on both, on every sample.
- Evidence: `notes/yw07b-evidence/lane/gcstress-706933b/`.
- These samples were noisier than an earlier 7-sample run at the tree of
  `2c8245b`, before front's parse changes. That run gave a median ratio of
  1.807 and a min ratio of 1.83, with C at 87–111 ms
  (`notes/yw07b-evidence/lane/gcstress/`). A 7-sample run minutes before
  the final one gave 1.421 (`gcstress-706933b-noisy/`).
- Every run is under 2× and under the prediction.

### Performance (deliverable 10's rows; the 2× bar)

`tools/run-perf-fletch` (core's `39e118b`) ran at the tree of `3bb5f11` on
kasumi CPUs 8–11 in the container. Nothing it builds changed after that
tree: `git diff 3bb5f11 HEAD` over `src` (tests aside), `tools/fl-headless`,
`tools/build-fl-core`, `tools/build-fl-perf-oracle` and
`tools/run-perf-fletch` is empty, so these are the final head's numbers. C's `perf_fletch` rows come from the
same run: one warmup and 11 in-process samples, medians. Evidence:
`notes/yw07b-evidence/lane/perf/`.

| row | release wolf/C | 2× bar | native wolf/C |
|---|---|---|---|
| fib24 | 4.18 | MISS | 189.1 |
| map10k | 3.28 | MISS | 87.6 |
| motion100k | 2.24 | MISS | 83.1 |
| startup | 3.84 (0.190 ms; the 2 ms budget holds) | MISS | 18.2 (0.83 ms; the budget holds) |
| parse_only | 1.30 | MEET | 4.57 |
| motion_dispatch | 2.39 (490 ns/op; the 1 µs budget holds) | MISS | 87.4 (15.9 µs/op; the budget MISSES) |
| fib27 | 4.29 | MISS | 194.3 |
| map_heavy | 5.34 | MISS | 60.9 |
| strbuild_join | 3.96 | MISS | 100.3 |
| strbuild_concat | 3.92 | MISS | 78.3 |
| join5k | 3.37 | MISS | 104.3 |
| list_sort | 4.19 | MISS | 85.5 |
| gc_pause | 13.2 (53.0 vs 4.0 ms) | recorded only | 81.3 |
| strbuild concat/join | 78.9 | requires > 20: MEET | 44.0 |

- Release: 11 of 13 rows miss the 2× bar. `parse_only` meets it since
  front's interner and `p_edges` changes (`1a560e7`, `ad4bf79`; it was 10.4×,
  `notes/yw07b-evidence/front/perf/parse-only-ab.txt`). `startup` and
  `motion_dispatch` hold their absolute budgets.
- Native: every row misses. This is R-yw07b-1's named backend MISS.
- What was tried and kept out:
  - core's rejected controls (`f86f727`, `1c314dd`; patches under
    `notes/yw07b-evidence/core/perf-controls/`);
  - plain and profile-guided release builds (`303162f`). PGO gave 6–8% and
    was not adopted.

  Counts and timers only; no generated code was read.
- Recommended ruling: **R-yw07b-9 = A** (`docs/MAP.md` §6). The rows go
  in a yew issue and are ratcheted in yw08 under R-yw08-3 A: a function
  profile with counts only, and a wolf-lang codegen issue with a reduced
  witness for each row that stays over. The 2× bar stays, no row is
  waived, and the merge does not wait on them. The alternatives are to
  hold the merge (B) or to rebaseline the bar (C), which only the
  maintainer can choose.

### The value, the heap and the toy VM's verdict

- **The value.** `FlValue {t, i, f}`: three scalars, 24 B against C's 16,
  with no union and no bit punning. An object reference is generation ×
  2^32 + physical slot. Why: a value that names no region is stack-movable
  on every tier, and the generation catches a stale reference after a
  compaction (`docs/MAP.md` §1).
- **The heap.** `fl.FlGc` holds paired fixed physical slots (`FlObj`).
  Every payload is a retained `List` that is `reset` and never replaced.
  The compacting sweep runs into the spare half at an instruction boundary
  and remaps every root and field. C's LP64 charges drive `next_gc`, so the
  collection counts equal C's (0, 0, 155 on `fl_smoke`).
- **The toy VM's verdict (R-yw07-1, R-yw07b-1 = A).** The compacting sweep
  held R3's residency:
  - the release ledger stayed flat at 484,896 B from collection 1,000 to
    100,000;
  - RSS went from 2,887,680 to 2,891,776 B, under one 2 MiB quantum;
  - it kept all eight root classes and reclaimed an unrooted cycle;
  - it trapped the planted stale reference (yew#67–#69 red).

  Toy release ratios were 1.05 / 0.73 / 0.46 against C (fib24 / map10k /
  motion100k). The real VM's 4.18 / 3.28 / 2.24 is the cost of the full
  instruction set on that shape, and the MISS rows above carry it.

### The unsafe census

The count went from 15 to 16 blocks. The one added block is `math.random`'s
seed at `src/fl/stdmath.lu:25`, over `var fl_math_rng_state`
(`src/fl/stdmath.lu:7`). Its `// # Safety:` comment names invariant 8, the
single-threaded core. No other module `var` was added under `src/fl`,
`src/flcli` or `src/flfix`.

### C yew against the port, by witness

- **Front end.** The AST and bytecode dumps match, 178/178
  (`tools/check-fl-dump`). The bytecode differential is 89/89
  (`notes/yw07b-evidence/core/bytecode-differential.log`).
- **Fuzzers.** `fuzz_fl_lex`, `fuzz_fl_parse` (with its `fl_data_read` raw
  and framed data mode) and `fuzz_fl_std` each report C's line byte for
  byte at 200,000 × seed 1
  (`notes/yw07b-evidence/fmt/fuzz/merged-6c25710.log`,
  `notes/yw07b-evidence/front/fuzz-lex-200k.log`).
- **fmt.** The black-box differential is 195 of 195 identical (`5c3fcf4`).
- **The data bridge.** It matches the hand codec on the v1 state corpus,
  22 canonical, 4 noncanonical and 20 invalid, and fl.data's four caps hold
  at their exact boundaries (`d5f848c`, `87133a2`).
- **io.**
  - errno: 49 cases identical, 12 of 26 names reached (`8b38f06`).
  - io.glob: 41 patterns identical except G40's five descent lines
    (`40d029d`).
  - G40: 14 io cases where C reaches bytes the port refuses by name
    (`e72c703`).
  - The editor API: 82 cases, `ed.commands` and both units, identical
    (`b05d0af`).
- **str and re.** The str natives match 363 C-oracle rows (`6292b28`), and
  the re natives match 154 C-oracle cases (`1d258f7`).
- **io's own test files** on the final code (`75cd7f9`,
  `notes/yw07b-evidence/io/tiers/`):
  - `fl_std_io_test`: 13 cases on native and release, normal and
    stressed, and 13 of 13 checked one at a time, normal and stressed;
  - `fl_caps_test`: 5 cases on every tier;
  - `fl_api_headless_test`: 17 cases on every tier, and 17 of 17 checked
    one at a time.

### The final run's two red rows: both trunk code, both nondeterministic

yew#70's ci run 40212903979 at `efe5e64` is red on two rows. Neither step
was armed or changed by this lane:
- `git diff origin/trunk..yw07b` does not touch `tools/check-test`,
  `tools/torture-live`, `tools/torture-replica.py` or `tools/build-torture`;
- `ci.yml`'s diff leaves the unit job's `tools/check-test --shard` step and
  the torture-live step as trunk has them;
- the code under both is trunk's.

Both rows were green at `706933b`, in run 40208663320, which the
`efe5e64` push cancelled after these jobs had passed these steps. There
is no difference between `706933b` and `efe5e64` outside `notes/` and
`docs/`.

**Row 1: `unit (linux x86-64, shard 2/3)`.**

At 16:43:39Z the checked run printed `test
src/edit_cmdcomp_shell_test.lu::main ... FAILED (trap(assert))`. The same
job's native lane printed `cmdcomp_shell_test: 18 cases pass` and
`check-test: src/edit_cmdcomp_shell_test.lu [native] ok`.

The checked whole-file verdict of this unchanged file at the 0.2.35 pin:

| run | head | checked verdict |
|---|---|---|
| 40160707930 | trunk `12442b8`, push | `refused it (step budget exhausted); running it natively`, then `ok` |
| 40199656604 | trunk `12442b8`, schedule | the same |
| 40177235318 | `f3c3694` | the same |
| 40208663320 | `706933b` | the same |
| 40167646446 | `42354f0` | `FAILED (trap(assert))` |
| 40212903979 | `efe5e64` | `FAILED (trap(assert))` |

Before the pin, at `280012fe` (40098593868, 40069862282), the checked
run passed outright.

The file runs second in its shard, after `args_test`, on trunk and here
alike. `wolf test` reports the shard's files one at a time in path order,
so the earlier reading, a neighbour rewriting `$PATH` concurrently, does
not fit:
- `text_clipboard_host_test`, the shard's other `$PATH` writer, ran 30
  minutes later;
- the first 31 files of shard 2, `edit_cmdcomp_shell_test`'s
  predecessors among them, are the same on trunk and on this branch.

On kasumi, eight checked runs of the file at `706933b`'s tree, with
`conform-run --checked --json` and the file whole, all answer `unsupported
| step budget exhausted`. The runs were:
- plain;
- at a third of a core;
- at about a fiftieth of a core;
- with `/tmp` on tmpfs.

None gives the trap (`notes/yw07b-evidence/lane/cmdcomp-probe/`). So the
trap is not runner speed and not `/tmp`'s readdir order. `wolf test`
prints no trap message, and that message is what the remedy needs. This
is the yew issue below, not a yw07b change.

**Row 2: `oracle (ubuntu-latest, --cc clang --cc gcc)`, "the live-editor
torture lane in a container".**

The run printed `torture-live: driver: torture: injected ENOSPC did not
preserve/recover (exit=0 expected=0 injected=1 oracle=1 exact=0)`, then
`torture-live: driver RED (exit 1)`, the replica `GREEN`, and `torture-live:
RED`.

The same lane printed `storage ENOSPC preserves old+journal ok` in:
- trunk's 40199656604, 40160707930, 40160662241, 40098593868,
  40069862282, 39968966081 and 39907558934;
- this branch's 40167646446 and 40177235318;
- 40208663320 at `706933b`.

In `kill9.c:929-965`'s terms the red means three things:
- the injected ENOSPC was logged (`injected=1`);
- the journal recovers (`oracle=1`);
- the destination is not the old bytes (`exact=0`).

That is the shape of a fault armed after the save had already replaced
the file. `yew-live-torture.c`'s feeder arms the shim with `SIGUSR2` 50 ms
after the paste's frame and then writes `s`, with no handshake that the
arm landed. Read that way, the red is a race between the arm and the
save, in the oracle's driver against the port's editor. It is a reading,
not a reproduction. It is the second yew issue below.

### Known limits, named in the code

- **G54's temporaries.** Caller-owned native temporaries are
  allocation-pending, with no boundedness claim. One case is the re
  cache: each compile allocates in the VM's region, so an evicted entry
  stays allocated until the VM goes (G33, `src/fl/stdre.lu`).
- **G40.** The port refuses by name the 14 io cases where C reaches
  non-UTF-8 bytes: environment names and values, and glob descents
  (`notes/yw07b-evidence/io/g40/`).
- **G51.** NaN sign and payload. No NaN with its sign bit set appears in
  any differential.
- **The native tier.** R-yw07b-1's backend MISS. For example,
  `fl_re_terminates` takes 32 s natively against C's 0.58 s, while
  `re_search_ws` costs 0.4 µs a call on release.

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
| yew#75 | `4797e9af` | 40208890406 | `tools/check-fl-cases` (a trace case renamed off its registry name) | after `selftest ok (missing, duplicate, reordered refused; ordered short lines kept)`, `trace: no fn fl_trace_carets_the_innermost_frame()` and `198 rows over 17 files; 1 problems` |

### Issues

To file (the orchestrator files them):
- **yew**: the 11 release MISS rows of the Fletch VM, one row per issue
  line, for yw08 under R-yw08-3 and R-yw07b-9. The shape is yew#30's.
- **yew**: `edit_cmdcomp_shell_test`'s whole-file checked run is
  nondeterministic in CI at the 0.2.35 pin.
  - It gives `FAILED (trap(assert))` in 40167646446 and 40212903979. It
    gives `refused it (step budget exhausted)` in 40160707930,
    40199656604, 40177235318 and 40208663320, the last at the same code
    as 40212903979.
  - Eight kasumi runs never trap (`notes/yw07b-evidence/lane/cmdcomp-probe/`).
  - First step: record the trap message, which `wolf test` does not
    print. Run the file under `wolf conform-run --checked --json` in the
    unit job when its checked verdict is a trap.
  - Then fix the test or file the checked machine's nondeterminism
    against wolf-interp.
- **yew**: torture-live's ENOSPC lane races the feeder's fault arm
  against the save.
  - The row: `injected ENOSPC did not preserve/recover (exit=0 expected=0
    injected=1 oracle=1 exact=0)` in 40212903979.
  - It was green in ten other runs, including 40208663320 at the same
    code.
  - The feeder (`yew-live-torture.c`, the pin's oracle, read-only to the
    port) sends `SIGUSR2` and writes `s` with no armed-handshake.
  - Record it as a flaky oracle lane for the maintainer, and watch the
    nightly for a second occurrence.
- **wolf-lang**: none new from this lane. G52 (wolf-lang#942), G53
  (wolf-lang#943) and G54 (wolf-lang#948) are filed. So is G51
  (wolf-std#103).

Recorded for the maintainer, not filed (each is a sagitta defect at the
pin that the port reproduces byte for byte, so the 41-pattern glob
witness matches C):
- **An absolute glob pattern, or the root `/`.** `io.glob` matches
  nothing, because it opens an empty prefix (`stdio.c:945-963` with
  `:756-760`).
- **`**` followed by two components.** After a nested walk,
  `is_dir_nofollow` reads a stale `here` buffer, so `**/**/c.txt` misses
  matches (`stdio.c:790-800`).
- **A NUL in the glob root.** The root's C strings end at the first NUL.

io's proposed G55 (no byte-exact environment read) is not a new gap. It
is G40: environment names and values are `str`, as shsession's
`state_survives_any_bytes` row already names.

To close: none. yw07b answers no open issue whole. The yw07 portions of
yew#17, yew#23, yew#27 and yew#40 stay open as yw07 left them. G50
(wolf-lang#919) stays open.

## Done-when

- [x] Deliverables 2–10 of the adopted contract, each in its own commits
  with its tests (the commit list above).
- [x] The 198 pinned cases by name and in registry order:
  `check-fl-cases` reports 198 rows over 17 files, ok. CI runs it at the
  end of the port job.
- [x] The 39 conformance runs, normal, stressed and twice, byte-identical
  (M-YW6's conformance artifact). Locally green, and in CI by name.
- [x] The GC-stress run with its wolf/C ratio: 1.706 at `706933b`.
- [x] The dump, trace and smoke differentials and the three fuzzers
  against C, in CI by name.
- [x] Every gate seen red on a plant (the table above).
- [x] The perf rows beside C's from one run. Every MISS is named, native
  is the named backend MISS, and R-yw07b-9 is asked.
- [x] Checked budget exhaustion is never a pass. Every allow row names
  its reason, and the CI checked-cases job runs in four shards.
- [x] The pending native refusals are retired as each family landed.
  `native_pending.lu` is deleted (`735ab4a`). The refusals left are
  yw08's (the prompt, `--selftest-fl-bug`) and yw09's (the
  editor-attached natives), each by name.
- [x] `docs/MAP.md`:
  - §1's Fletch rows and the reserve row;
  - §2's `src/fl/` and flcli rows;
  - §3's campaign 06 split;
  - §5's G51–G54 and G6 closed;
  - §6's R-yw07b-1..9;
  - §7's yw07b paragraph and the pointer to yw08.
- [x] yw08's contract drafted in full and brought to this head
  (`0b13303`, `149ebc9`).
- [x] The static binary at `706933b`:
  - ET_EXEC with no PT_INTERP;
  - `--version` and `fl -e` run;
  - sha256 `aa89f0e40ddf35826091dad584bd17ad983561b5ab3c38b2ad4f5a9636b83fb3`,
    21,162,368 bytes, for pax's `user/yew.pin`. That pin is a pax lane's
    change.
- [x] `bash wolf/tools/lane-audit.sh yew yw07b 70` from the org root. Its
  last line is in the PR body.
- [ ] CI green at the final head. The orchestrator watches the run named
  in the PR body.
