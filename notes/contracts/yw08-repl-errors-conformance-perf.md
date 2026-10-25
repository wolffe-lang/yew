# yw08 — the Fletch REPL, its bug report, the ledger and the perf gates

**Model per ruling #89 R4, chosen at launch. Drafted by yw07b from
`docs/MAP.md` §7's yw08 paragraph, sagitta campaign 06's last two sprints
and yw07b's hand-off.** Ruling #89 (`sprints/yew/index.md`); the track's
seven standing rules (rule 2: no golden edited; rule 4: the 2× gate);
`docs/MAP.md` as yw07b left it (§1's Fletch rows, §5's G51–G54, §6's
R-yw07b-1..8); `sprints/RULES.md`. It ports what the adopted yw07
contract left to yw08 (R-yw07-6 and R-yw07-7 pulled `suggest`, `trace`,
`origin`'s check half and `flcli.c`'s non-interactive forms forward into
yw07b, which landed them):

- s32 (`s32-repl-and-errors.md`, 581 lines at `sagitta.pin`) §2–§5 and
  §8–§9: the prompt and its line editing, multiline continuation, the
  `:`-commands, result printing at the prompt, the VM fuzzer, and the
  structured exit-4 bug report;
- s33 (`s33-fletch-conformance-perf.md`, 485) whole except what yw07b ran:
  the coverage ledger and its CI gate (§3, §4), the bench suite's gates
  (§5), and the milestone (§6, M-YW6's four artifacts).

The C: `src/fl/repl.c` (963) + `.h` (101), `src/fl/vmcheck.c` (350),
`src/flcli.c`'s tty branch and `--selftest-fl-bug` (`:594-628`, the rest
landed in yw07b as `src/flcli/flcli.lu`), `tests/unit/test_fl_repl.c` (10
cases) and `test_fl_chunkcheck.c` (5), `tests/fuzz/fuzz_fl_vm.c` (175) and
its `corpus/fl_vm` (7 files), `tests/perf/perf_fletch.c` (1,265) with
`baselines/fletch_dev.txt` (58), `tests/fletch/run.c --ledger` with
`tests/fletch/ledger.txt` and `scripts/check-fletch-coverage.sh`,
`scripts/smoke.sh:506-525` (the exit-4 row and `YEW_FL_DUMP_BAD_CHUNK`),
and the three PTY goldens campaign 06 owns (`s32_repl_session`,
`s32_bug_restores_the_terminal`, `s33_hello_world_repl`). Re-derive every
count at the pin.

## Deliverables

1. **The toolchain, first.** `gh release list -R wolffe-lang/wolf-lang`
   and `-R wolffe-lang/wolf-interp` read and quoted with their time. If a
   release newer than 0.2.35 is out, the bump is this lane's first commit
   with its prediction, and the retirements it names are adopted, each in
   its own commit. That includes G50 (wolf-lang#919), G52 (#942), G53 (#943),
   G54 (#948) and G51 (wolf-std#103) wherever the release answers them.
   G54's disposition comes first: when #948 is answered, the native
   temporaries yw07b left allocation-pending get their scratch regions and
   a measured bound, never before.
2. **The prompt** (s32 §2–§5). `yew fl` with stdin a terminal: s03's raw
   mode, s04's key decoding, the prompt's text a `TextBuf` edited by the
   one line editor (s18's law: there is exactly one text editor in this
   program). s32 §2's seam is `yew_cmdline_edit_key`, the `Ed`-free half of
   `yew_cmdline_key`, reached by the port's `edit.cmdline` (R-yw08-1).
   - `CmdHist` on kind `"fl"`, under `$XDG_STATE_HOME/yew/history/`.
   - Multiline continuation over `fl_parse`'s `incomplete`, which never
     coincides with `had_error`: DoD's five cases, which yw07b's parser
     already holds.
   - The `:`-commands (s32 §4).
   - Result printing through `fl_fmt_repl` and yw07b's
     `flcli.print_result`. Share it; do not duplicate it.
   - Terminal restore on every exit path (invariant 6).
   - Unit: `test_fl_repl` (10). PTY: `s32_repl_session` and
     `s33_hello_world_repl`, through `tools/goldens --suite pty` by name.
3. **The invariant line** (s32 §9). `fl_chunk_check` and the structured
   bug report: one line per fact, and a static buffer that never walks a
   value. Exit 4 through `util.bug`, with the terminal restored first when
   the prompt owns it.
   - `--selftest-fl-bug` (an opcode the table lacks, driven through the
     VM's own invariant path) and `YEW_FL_DUMP_BAD_CHUNK`.
   - yw07b's `flcli` refuses both by name today; this lane retires those
     refusals.
   - Unit: `test_fl_chunkcheck` (5). PTY: `s32_bug_restores_the_terminal`.
     Smoke: `smoke.sh:506-525`, added to `tools/smoke-fl`, which yw07b
     ported with ten rows.
4. **`fuzz_fl_vm`** (s32 §8: no bytecode verifier, source-level fuzzing
   only). The driver over the `fl_vm` corpus at C's size and seed, its
   report line C's driver's byte for byte (`--against-oracle`, the
   `tools/run-fuzz-fl-front` shape). s32 §8's VM invariants hold after
   every input: frames, handlers, open upvalues and `sp` all clean.
5. **The coverage ledger** (s33 §3, §4). `fletch_run --ledger` output
   against `tests/fletch/ledger.txt`. `scripts/check-fletch-coverage.sh`'s
   verdict against the port's `--list-natives` (byte-identical to C's at
   yw07b). Every native carries a COVERS token. The ledger half of
   `Makefile:4015-4026` completes yw07b's determinism half
   (`tools/check-fletch-goldens`).
6. **The bench suite's gates** (s33 §5; R-yw08-3). `perf_fletch.c`'s rows
   in the port's in-process harness beside C's from the same run, on
   kasumi under `taskset`, in a container, 11 samples with a warmup, the
   median and the min. The rows are `startup` (≤ 2 ms, hard),
   `motion_dispatch` (≤ 1 µs an op, hard), `fib27`, `strbuild_join`,
   `strbuild_concat` (its `> 20` ratio), `map_heavy`, `list_sort`,
   `gc_pause` and `parse_only`. Two parts:
   - Every ratio at the 2× bar. yw07b's named MISS rows are this lane's to
     ratchet or to dispose by ruling, and its final numbers are in
     `notes/yw07b-fletch-core.md`.
   - The regression gate's two conditions (median > baseline × 1.15 and
     min > baseline × 1.10).
   `config_load` needs the config runtime (`bind` and friends,
   editor-attached) and is yw09's, as yw07b named it.
7. **M-YW6** (s33 §6), all four artifacts in CI:
   - `yew fl FILE` prints `hello, world`;
   - `yew fl -e` does the same;
   - the `s33_hello_world_repl` PTY golden;
   - `tools/check-fletch-goldens` (yw07b's 39 units by name, stressed and
     twice) together with the coverage gate.
8. **The dispatch-parity gate re-aimed** (R-yw07-3 A,
   `Makefile:3136-3167`). The 21 `fl_smoke --trace` fixtures against C's
   `CFLAGS_FL_TRACE=1` build, twice across processes. yw07b's core fork
   ran it (`notes/yw07b-evidence/core/oracle-trace*.txt`); this lane makes
   it a CI step by name.
9. **The note and the map.** `notes/yw08-…md` with the five sections;
   `docs/MAP.md` §2's yw08 rows, §5's new gaps, §6's rulings, §7's yw08
   and yw09 paragraphs, and yw09's contract drafted in full.

## Rulings (to ask at launch unless decided)

- **R-yw08-1 — the prompt's line editor.** (A) extract C's
  `yew_cmdline_edit_key` seam as an `Ed`-free function in `edit`, called
  by `flcli` (which may `use edit`: `fl` stays below it, R-yw07-5)
  (recommended: one line editor, s18's law); (B) a second, minimal line
  editor in `flcli` (refused by s32 §2's law).
- **R-yw08-2 — the bug report's static buffer.** C writes the report from
  a static buffer with no allocation, because it may fire mid-collection.
  (A) a fixed `List[byte]` reserved at VM init and only `reset`, written
  with no allocation, named in `vmcheck` (recommended); (B) ordinary
  allocation, which is refused for the case it exists for.
- **R-yw08-3 — yw07b's performance MISS rows.** yw07b recorded release
  ratios above 2× on its smoke rows and several `perf_fletch` rows, with
  native as a named backend MISS (R-yw07b-1). (A) this lane profiles by
  function, using counts only and never generated code, ratchets each row
  it can, and files every row it cannot as a wolf-lang codegen issue with
  a reduced witness. The 2× bar stays, and no row is waived without the
  maintainer (recommended); (B) a ruling that rebaselines the bar for
  Fletch, which only the maintainer can make.
- **Decided:** R-yw07-1..10 and R-yw07b-1..8 stand as yw07b left them,
  subject to the maintainer's batch. The prompt is the only terminal owner
  in `flcli`. `--batch` and the editor-attached natives are yw09's. The
  REPL's completion over the VM (s32 §4's `:` and identifier completion)
  rides `edit.cmdcomp`'s one `match` (R-yw07-10).

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. `Footprint:
cross-cutting` (CI's by-name steps). Read sagitta's `src/fl/repl.*`,
`vmcheck.c`, `flcli.c`, the s32/s33 sprint files, `tests/unit/test_fl_repl.c`,
`test_fl_chunkcheck.c`, `tests/fuzz/fuzz_fl_vm.c`, `tests/perf/perf_fletch.c`,
`tests/fletch/run.c` and the baselines freely, and cite `file:line`.
Never another language implementation's, VM's, GC's, line editor's or
readline's source. No golden, unit case, conformance file, baseline or
ledger edited; a disagreeing one is a STOP with its diff. Every run of C
yew and the port uses scratch `HOME`/`XDG_*` and an explicit
`YEW_RUNTIME_DIR`, inside a container under `taskset` and the lane's core
lock. The PTY goldens drive the real terminal through `tools/goldens`;
signal witnesses are pty bytes, never trap scripts. One kind-id/match
representation for every mutable callback (R-yw07-10). G54's temporaries
stay allocation-pending until wolf-lang#948 is answered.

## Inputs (re-derive)

sagitta at the pin: the s32 and s33 sprint files with their line counts;
the C files and tests of the header; `Makefile:3102-3167` (the fl unit
lanes and the dispatch parity), `:3966-4026` (test-fletch, the ledger,
the stress run and its determinism), `:101-102` and `:2240-2279` (the
fuzz sizes). The yew repo at yw07b's merge: `src/fl/` (the VM, its
`flfix` fixture, `trace`, `suggest`), `src/flcli/flcli.lu` (the
refusals this lane retires), `tools/check-fl-cases` and
`tools/fl-cases.txt` (198 rows; this lane adds test_fl_repl's 10 and
test_fl_chunkcheck's 5 as their own rows), `tools/check-fletch-goldens`,
`tools/check-fl-dump`, `tools/smoke-fl`, `tools/run-fuzz-fl-front`,
`notes/yw07b-fletch-core.md` (its perf table and its open issues),
`notes/yw07b-evidence/core/` (the in-process perf harness and the trace
differential), `docs/MAP.md`.

## Prediction (write before the first change)

To be written by the lane at launch: the prompt's goldens green by name;
`fuzz_fl_vm` equal to C's report line; the ledger byte-identical; each
`perf_fletch` row's ratio predicted against the 2× bar, with yw07b's
measured MISS rows as the starting point; M-YW6's four artifacts green in
CI.

## Done-when

Every deliverable with its tests. `tools/check-test` and `--native` green,
with the per-case checked run recorded. The three PTY goldens green by
name. `fuzz_fl_vm` in CI by name. The ledger gate green. The perf rows
recorded beside C's from one run, every MISS named with its issue.
M-YW6's four artifacts green. `docs/MAP.md` updated; yw09's contract
drafted; CI green; the PR open with the five sections, shas as bullets, a
test checklist and its `Footprint:` line; `bash wolf/tools/lane-audit.sh
yew yw08 <PR>` passing but for the final run's green; hand back per
RULES.md §6.
