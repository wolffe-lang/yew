# yw08 — the Fletch REPL, its bug report, the ledger and the perf gates

yew PR #88 from `yw08`. The lane ran on GPT-6-Astra from launch to `111742b`
(deliverables 1–3), was cut twice by that provider's content classifier while
working on the VM report and the VM fuzzer, and was continued on Claude Opus
5.5 from `111742b` (the fuzzer, the coverage ledger, the perf gate, the folded
issues and the closeout) under the same contract.

Footprint: cross-cutting

## Forbidden

The contract's rules, as kept:
- No golden, unit case, conformance file, sagitta baseline or ledger edited.
  The two new files under `tools/` (`perf-fletch-baseline.txt`,
  `perf-fletch-misses.txt`) are the port's own measurements and dispositions.
  The two guided fuzz seeds are copied from the pin byte for byte, blob shas
  `dd1912e4` and `7927d4a4`.
- sagitta read and cited only, at `9ace98c2`. No other editor's, VM's,
  line editor's or readline's source. The wolf-lang repository was read for
  its spec and its inliner's documented rules (`spec/01-grammar.md` §3.2;
  `crates/wolf_wir/summary-format.md`; `midend/inline.rs`), never a
  program's generated code.
- No builds on the Mac. Every build and run happened on kasumi CPUs 12–15
  under `flock /home/mfwolffe/lanes/kasumi-cores-12-15.lock`, `taskset -c
  12-15`, in the `px13-ubuntu` container (`notes/yw08-evidence/lane/ctr.sh`),
  with scratch `HOME`/`XDG_*` and an explicit `YEW_RUNTIME_DIR`.
- No label, merge, tag, issue filed or closed. No attribution trailer. No
  edit to `wolf/` or `~/.claude`.
- One kind-id/`match` representation for mutable callbacks (R-yw07-10).
  G54's temporaries are untouched (wolf-lang#948 is still open).
- No row waived. The 2× bar stands for every Fletch row, and a named MISS is
  still held to its baseline.

## Inputs, verified

- **Toolchain (deliverable 1).** `gh release list` read at
  2026-10-26T20:25:53Z: wolf `v0.2.35` (2026-10-23T08:45:33Z) and lupin
  `0.1.56` (2026-10-23T04:43:45Z) are still the latest, so there is no bump.
  The launch read is in `notes/yw08-evidence/releases.txt`. G50–G54 have no
  release that answers them: wolf-lang#919, #942, #943, #948 and wolf-std#103
  are all OPEN.
- **Pin.** `sagitta.pin` is unchanged at `9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a`.
  The base is trunk `1ef15c24`.
- **Contract.** Adopted: `notes/contracts/yw08-repl-errors-conformance-perf.md`,
  deliverables 1–9; the launch file `08-the-repl/yw08-the-repl.md`; the track
  index and RULES §1–§10.
- **The takeover state, checked before use.**
  - `111742b` = `origin/yw08`.
  - The kasumi clone sat at `b24f255` with a subset of the later work
    uncommitted. It was stashed reversibly (`stash@{0}`, "pre-takeover"),
    not discarded, then moved to `111742b`.
  - The previous model's uncommitted VM fuzzer was reviewed:
    - The watchdog (`watch.py`) was kept, with its expected-expiry noise
      quieted.
    - The driver was revised: C's line citations, the parse-cap constant, a
      stress predicate whose precedence the selftest pins, and a tally.
    - The runner gained a tally floor, a real exit status and a header.
    - The corpus was missing the pin's two guided seeds. The corpus count
      found it: 16 entries against C's 18.
- **Rulings in force.**
  - R-yw08-1 is corrected (C has no cmdline seam: s32 C1). The crawl logs
    the correction.
  - R-yw08-5 = A: `YEW_FL_VM_CHECKS` mirrors C's `FL_CHECKS`. The crawl's
    2026-10-26 entry accepts it.
  - R-yw08-4 (no Tab completion, per the pinned key switch) is recorded in
    MAP as the coordinator's, but **the crawl does not log it**. The
    orchestrator confirms.
  - R-yw07-1..10 and R-yw07b-1..9 stand.

## Prediction

The pre-change prediction is `notes/yw08-evidence/prediction.txt`
(`3b8ccea`). Against it:
- **Met.**
  - No toolchain bump.
  - The three PTY goldens pass unchanged.
  - The 10 REPL and 5 chunk-check cases keep their pinned names and order.
  - `fuzz_fl_vm`'s report line equals C's at its size and seed.
  - The ledger is byte-identical and every native carries a COVERS token.
  - M-YW6's four artifacts run in CI.
  - Trace parity stays green with no new step.
  - The regression gate is C's two conditions.
  - Native remains a backend MISS.
- **Not met.** Every release ratio was predicted to improve by about 10%
  (fib27 4.29 to 3.9, and so on). No change that moved a row beyond host
  drift was found, so nothing was adopted. Same-session control rows read
  2.4–5.7× (table below). The cold-start prediction (about 1.5×) came out
  better: 1.31 for the clean start and 1.03 on the observer's cold row.

## Evidence index

### By deliverable

1. **Toolchain:** above. `3b8ccea` (prediction, release read), `4f2ccbd` (pinned
   inputs).
2. **The prompt (s32 §2–§5):** `879a7c2`, `1b076bf` (the continuation
   classifier: `fl_parse`'s `incomplete` matrix and the 12-line entry, the
   trial parse silent), `80f69dd` (the `:`-commands, result printing shared
   with `flcli` through `print_result_into`), `1981d81` (line-oriented raw
   output; the ONLCR gap G55), `a94fc2e` (the prompt over TextBuf/Cursor/
   EditCtx, `fl` history under `$XDG_STATE_HOME/yew/history/`, the restore on
   every exit), `b24f255` (the goldens by name in CI). `test_fl_repl`'s 10
   cases in `tools/fl-cases.txt` (213 rows over 19 files). C's key switch
   (`repl.c:807-926`) and the port's are the same set: Enter/Ctrl-J, the
   editing keys, Up/Down history, Ctrl-C/D/L, printable insertion; no Tab
   (R-yw08-4).
3. **The invariant line (s32 §9):** `c3a8c7b` (`fl_chunk_check`, 5 cases),
   `d9190ed`, `9839687` (the report from reserved storage, R-yw08-2),
   `09f09b2` (`--selftest-fl-bug` and `YEW_FL_DUMP_BAD_CHUNK` through the
   CLI and the prompt; the refusals retired; fourteen smoke rows), `84bac47`,
   `55568bd` and `58dc06d` (the thirteen guards exit 4 and name their owning
   file), `503b317`, `111742b`, `c6b40b0` (formatting).
4. **`fuzz_fl_vm` (s32 §8):** `6caa3ae` (the pin's `fl_vm` corpus and its two
   guided `fuzz_fl_vm` seeds), `270370c` (C's driver in `tools/oracle`),
   `e9ad748`, `4804236` (the driver), `d7d72c6` (the five-second per-input
   watchdog, R-yw08-6), `aa538dd` (the runner and its tally floor), `64fa4c3`
   (evidence), `0928c50` (CI, `fuzz (linux x86-64, against-c-2)`).
   - At 200,000 inputs and seed 1 both lines read `fuzz_fl_vm: seed=1
     iters=200000 corpus=18 hash=38da7a4436621be9 ok`, C's and the port's.
   - The tally: 24,778 inputs reached the VM and 15,103 raised. 367 ran under
     C's one-in-sixteen stress slice, with 390 collections. With
     `YEW_FL_GC_STRESS=1`, all 24,778 ran stressed, with 26,647 collections.
   - The slowest input took 1 ms against the 5,000 ms watchdog. C's driver
     takes 8.8 s; the port's campaign takes about 23 s.
   - Every input's VM is checked for sp, frames, handlers and open upvalues
     clean.
5. **The coverage ledger (s33 §3–§4):** `726e9b1` (`tools/check-fletch-coverage`:
   sagitta's own `scripts/check-fletch-coverage.sh` from the pinned tree
   with `YEW` pointed at the port; then the ledger twice, byte-compared,
   `Makefile:4021-4025`; then `--list-natives` against C's; two controls go
   red on every run, a dropped native by check 7 and an invented one by
   check 3), `53eadf4` (CI), `778976a` (first run). The ledger: `sections
   16/16 productions 47/42 natives 187/187 kinds 13/13 opcodes 60/60`, equal
   to the pin's `tests/fletch/ledger.txt`.
6. **The bench gates (s33 §5):** `00c0627` (`tools/fl-headless/compare.py`:
   C's integer two-condition rule, `perf_fletch.c:862-874`, with C's seven
   selftest cases and two more; `perf_policy.h`'s advisory boundary; a
   baseline ledger with its required `why`; a named-MISS ledger on
   `tools/perf-editor-misses.txt`'s pattern), `117cdc0` (the eleven release
   rows named on yew#77), `776fd30` (the kasumi baseline, R-yw08-7),
   `69d02d5` (CI: timing advisory, sanity hard, C's policy for a shared
   runner), `c9efa0e` (the starting rows and why they are the code),
   `ca37d5e`, `eaa3d62` (the profile, the witnesses and the four rejected
   experiments). Table below.
7. **M-YW6 (s33 §6) in CI:**
   - `yew fl FILE` and `yew fl -e` print `hello, world`: `tools/smoke-fl`'s
     rows.
   - The `s33_hello_world_repl` golden: the REPL goldens step.
   - `tools/check-fletch-goldens` (39 units by name, stressed and twice) and
     the coverage gate: two steps.
8. **Trace parity:** `tools/check-fl-trace` stays green (21 fixtures, two
   processes each, normal and stressed). No step was added.
9. **The note and the map:**
   - This note.
   - `81bfa1b` (`docs/MAP.md`):
     - §2's yw08 cells.
     - §5's G11 correction and G56–G57.
     - §6's R-yw08-2..8.
     - §7's yw08 and yw09 paragraphs.
   - `c6d2f6a` (`notes/contracts/yw09-fletch-in-the-editor.md`, drafted in
     full from an inventory of the pin's campaign 07).
   - `450a459` (README, RULES §10: the status had said Fletch was not
     implemented).
   - `e2510ad` (CHANGELOG).

Also: `4edfd56` (`tools/check-fmt` names every non-canonical file; under `set
-e` the first miss had hidden the tools directories), `d93dd6c` (yew#78's
diagnostic), the yew#12 commits `2a290fc`..`cda7f43` and `d703f73`, and
`585b57f` (yew#55's start-up rows back on the editor's gate).

### The closeout at the final code head (`778976a`)

kasumi CPUs 12–15 in the lane container, a frozen `git archive` tree, started
2026-10-26T22:46:53Z (`notes/yw08-evidence/closeout/`). Every step green but the three unit lanes still running at hand-back:
`fmt`, `registry` (213 rows over 19 files), `release` and `native` (the whole
editor), `fuzz-vm` and `fuzz-vm-stress` (both report lines C's), `coverage`,
`conformance` (39/39 normal, stressed, again; byte-identical), the three PTY
goldens on both tiers (six runs), `dumps`, `smoke` against C, release and
native (14 rows each), `report`, `invariants` (13 rows), `traces`, the 35
`src/fl_*_test.lu` files natively, `perf-release` in gate mode (eleven rows
MISS-NAMED on yew#77, every row inside its baseline, `failures=0`, exit 0),
`perf-regression-plant` (red, below), `perf-editor` (every row PASS:
clean start 1.30, cold open 1.24, first Backspace 1.11) and `perf-panes`
(two panes p99 1.01, fifty buffers p99 1.85, tab switch p99 1.67, all
PASS). Logs: `notes/yw08-evidence/closeout/`. The unit lanes
(`check-test-cases`, `check-test`, `check-test --native`) run in the same
job: pid 1172215, log `/home/mfwolffe/lanes/yw08/o55/closeout.log`, step
markers `/home/mfwolffe/lanes/yw08/o55/gates-closeout-778976a/check-test-*.exit`,
job marker `/home/mfwolffe/lanes/yw08/o55/closeout.exit`.

### Performance: the bench rows (yew#77, R-yw08-3)

Release tier, wolf/C, the port's in-process harness beside C's pinned
`perf_fletch` from the same run, one warmup plus 11 samples, medians:

| row | yw07b (8–11) | start `0928c50` | closeout `778976a`: C / port | wolf/C | verdict |
|---|---|---|---|---|---|
| fib24 | 4.18 | 4.51 | 6.038 ms / 26.171 ms | 4.33 | MISS, named (yew#77) |
| map10k | 3.28 | 3.39 | 1.232 ms / 4.259 ms | 3.46 | MISS, named (yew#77) |
| motion100k | 2.24 | 2.52 | 17.100 ms / 42.736 ms | 2.50 | MISS, named (yew#77) |
| startup | 3.84 | 2.51 | 47.6 µs / 118.9 µs (2 ms budget holds) | 2.50 | MISS, named (yew#77) |
| parse_only | 1.3 | 1.26 | 203.5 µs / 252.4 µs | 1.24 | PASS |
| motion_dispatch | 2.39 | 2.75 | 178.395 ms / 505.384 ms (505 ns/op; 1 µs budget holds) | 2.83 | MISS, named (yew#77) |
| fib27 | 4.29 | 4.48 | 25.056 ms / 111.289 ms | 4.44 | MISS, named (yew#77) |
| map_heavy | 5.34 | 5.71 | 58.237 ms / 391.470 ms | 6.72 | MISS, named (yew#77) |
| gc_pause | 13.2 | 22.16 | 1.713 ms / 44.595 ms | 26.03 | recorded only |
| strbuild_join | 3.96 | 4.27 | 2.777 ms / 11.794 ms | 4.25 | MISS, named (yew#77) |
| strbuild_concat | 3.92 | 4.30 | 42.983 ms / 185.664 ms | 4.32 | MISS, named (yew#77) |
| join5k | 3.37 | 3.76 | 697.3 µs / 2.647 ms | 3.80 | MISS, named (yew#77) |
| list_sort | 4.19 | 4.54 | 27.994 ms / 125.889 ms | 4.50 | MISS, named (yew#77) |
| concat/join (port) | 78.9 | 70.77 | — | 70.14 | > 20: PASS |

The misses are the code, not the host:
- C and the port are timed in the same run, row by row.
- C itself ran at 0.66–1.02 of its own developer-machine baseline
  (`fletch_dev.txt`).
- The ratios sit within 3–9% of yw07b's run on another block.

Evidence: `notes/yw08-evidence/perf/start/analysis.txt`.

The ratchet (R-yw08-3 A):
- **Counts by function.** `wolf build --release --profile-gen` and `wolf
  profile show`, named through `--codegen-report`'s content hashes
  (`perf/profile/named.txt`). In each fib27 run, `fl_read8` is entered 13.0M
  times, `fl_push` 5.7M and `fl_pop` 4.4M, with one `fl_close_upvals` and
  one `fl_map_probe` per call.
- **The inliner never takes those helpers.** All carry effect-token
  parameters and several blocks, and `wolf_wir`'s inliner skips such
  callees (`inline.rs:22-27`).
- **Four experiments against same-session controls**
  (`perf/experiments/summary.txt`):
  - The helpers written inline: fib +82%, rejected.
  - The cold arms outlined: within the session drift; list_sort +18%.
  - The outlining refined: within drift, with motion_dispatch +5%.
  - The reference assert dropped, as a measurement only: within drift.
- **Nothing adopted.** Session drift on the unmodified tree reached 16% on
  one row, so a change under about 10% cannot be separated from the host
  here.
- **Two witnesses.**
  - `perf/witness-match/`: the native tier dispatches a 60-arm `match` by
    compare chain (1.4/4.3/7.4 ns per op at arms 0/30/59; release is flat
    at 1.5–1.6). This is G56.
  - `perf/witness-inline/`: a helper call costs 2–4% on release in a small
    loop, while in the VM writing the 43 calls inline makes fib 1.8×
    slower. This is G57.

  These are the codegen issues to file.

### Plants and controls

- **Plants from the previous model**, draft PRs on `yw08-plant-*`:
  - #80: run 40356160617, `s32_repl_session: expected |3\x0d\x0a|` on both
    oracles. The orchestrator recorded it red (crawl-54).
  - #81: report field, run 40375209092 red.
  - #82: report allocation.
  - #83: collector invariant.
  - #84: empty compiler chunk.
- **This lane's plants**, draft PRs:
  - #85 `yw08-plant-vm-reset`: `fl_vm_run` leaves `sp` above the floor.
    Expected red: the `fuzz_fl_vm` step.
  - #86 `yw08-plant-uncovered-native`: `--list-natives` loses a native.
    Expected red: the coverage step.
  - #87 `yw08-plant-perf-sanity`: a wrong expected fib27. Expected red: the
    Fletch bench step, an error, hard under advisory.

  Their PR runs at opening: #85 run 40414713880, #86 run 40414830098, #87 run 40414908598, all queued at hand-back; the orchestrator reads them.
- **Local reds, cited by file.**
  - `notes/yw08-evidence/fuzz/plants-local.log` and `plants-local-p2.log`:
    - The driver's body skipped: the selftest traps at `main.lu:167`.
      Without the selftest, the report line *still equals C's*, and only
      the tally floor turns it red (`ran=0`).
    - `fl_vm_run`'s reset removed: the selftest traps at `main.lu:163`.
      Without the selftest, the campaign's own invariant fails at iteration
      0 (`after execution: sp+1`).
  - `notes/yw08-evidence/coverage/first-run.log`: both coverage controls
    red.
  - The closeout's `perf-regression-plant` step: every row against a halved
    baseline reads REGRESSION. `notes/yw08-evidence/closeout/perf-regression-plant.log`: all twelve gated rows `REGRESSION`, `failures=12`, exit 1, against the same samples that pass the real baseline (`perf-release.log`, `failures=0`).

### Issues: dispositions (filing and closing are the orchestrator's)

- **yew#77 (11 of 13 release rows over 2×):** ratcheted per R-yw08-3 (A)
  and nothing moved.
  - The rows are named in `tools/perf-fletch-misses.txt` and held to the
    baseline.
  - **Keep open.**
  - File the two wolf-lang issues from G56 (native: a jump table for a
    dense integer `match`) and G57 (release: the large-function cliff and
    the token-parameter inline rule).
- **yew#55 / #66 (cold-open rows):** measured over enough starts, per #66.
  - `startup.first_paint.clean` is 1.31 over 3×50 interleaved starts and by
    the R12 method; `cold_open_to_first_paint` is 1.19 by R12. Both are back
    on the 2× gate (`585b57f`, R-yw08-8).
  - Tab-switch p99: 1.67 at the closeout (`notes/yw08-evidence/closeout/perf-panes.log`), back on the gate (`ffc5ab3`).
  - Recommend closing #66 and #55's start-up half. With the tab switch, every #55 row passes.
- **yew#78 (checked trap in `edit_cmdcomp_shell_test`):** not reproduced.
  - kasumi: 3 of 3 whole-file checked runs answer `unsupported | step budget
    exhausted`.
  - CI: run 40243191387 (trunk push) and run 40357616516 (nightly) both refuse
    on the budget and pass natively.
  - The fixture uses `/tmp/yew-cmdexec-<os_random>` paths and rewrites
    `$PATH`, so an environmental cause remains plausible but unproven.
  - The issue's first step is done: `tools/check-test` now prints each
    trapped file's conform-run verdict and `trap_message` (`d93dd6c`).
  - **Keep open** until a trap prints its message.
- **yew#76 (`edit_ws_recover_test` checked trap in wl70's container):**
  environmental.
  - All 15 cases pass on the checked machine one at a time in the nightly
    (run 40357616516, checked-cases).
  - Whole, the file never completes on the checked machine: 3 of 3 runs in
    this lane's container stop on the step budget.
  - Recommend closing, with `notes/yw08-evidence/triage/index.txt`.
- **yew#79 (torture-live ENOSPC race):** not in reach. The race is in the
  oracle's feeder (`yew-live-torture.c`, no arm handshake), which the port
  only reads. The maintainer's, as the issue says.
- **yew#27 / #23 / #17 (pin retirements):** no release since 0.2.35, so
  nothing new is answered.
  - #17/#27's remainder is G47/G48 (wolf-lang#916, #917 OPEN).
  - #23's remainder is G32's write-only-existing open and record locks.
  - **Keep all three open.**
- **yew#12 (G11's bitwise not):** retired. Twenty mask clears in eleven
  shipping files now read `x & !m` (`2a290fc`..`cda7f43`, `d703f73`), and
  MAP's G11 row is corrected. Recommend closing #12.

### Issues to file (the orchestrator's)

- **wolf-lang, G55: ONLCR in the terminal output-flag surface.** The draft
  is `notes/yw08-evidence/onlcr/issue.txt`, from the previous model.
- **wolf-lang, G56: the native tier's compare-chain `match`.** The witness
  is `notes/yw08-evidence/perf/witness-match/`.
- **wolf-lang, G57: release codegen of the dispatch loop.** The witnesses
  are `notes/yw08-evidence/perf/witness-inline/` (reduced) and
  `perf/experiments/` (the VM half; `inline-exec.py` regenerates it).

### Rulings (each the lane's recommendation; none decided here)

- R-yw08-1 correction, logged.
- R-yw08-2 = A, implemented.
- R-yw08-3 = A, carried out. The bar stays, and (B), a Fletch-specific bar,
  is not recommended.
- R-yw08-4 = A, to confirm.
- R-yw08-5 = A, accepted.
- **R-yw08-6** (the fuzz watchdog as a wall-clock progress pipe) = A.
- **R-yw08-7** (the baseline as the maximum of three control sessions,
  until yw15's quiet host) = A.
- **R-yw08-8** (the start-up rows back on the gate) = A. It reverses yw07's
  disposition on measurement.

The full text is in `docs/MAP.md` §6.

## Done-when

- [x] Deliverables 1–9, each with its tests (above).
- [x] The three PTY goldens green by name. The previous model ran them on
  both tiers; the closeout reruns them.
- [x] `fuzz_fl_vm` in CI by name, its line equal to C's.
- [x] The ledger gate green, and in CI.
- [x] The perf rows recorded beside C's from one run, every MISS named with
  its issue (yew#77) and its witnesses (G56, G57).
- [x] M-YW6's four artifacts in CI.
- [x] `docs/MAP.md` updated; yw09's contract drafted.
- [x] README read and refreshed (`450a459`).
- [ ] `tools/check-test` and `--native` green, with the per-case checked run
  recorded. Running at hand-back in the closeout job (pid 1172215; markers above). The previous model's checkpoint ran both lanes green at `879a7c2` (`checkpoint.exit` = 0); this lane's changes since touch the unit files only through yew#12's mask clears and the Fletch tools.
- [ ] CI green at the final head: the PR run at the final head, read once at hand-back; its id is in the PR body.
- [ ] `bash wolf/tools/lane-audit.sh yew yw08 #88` passing but for the final
  run's green: its last line is in the PR body.

Test checklist (CI's by-name steps this lane adds or relies on):
- [ ] `fuzz (linux x86-64, against-c-2)` › `fuzz_fl_vm, source execution
  against C's driver (200,000 inputs)`
- [ ] `oracle` › `goldens, campaign 06's Fletch conformance by name, stressed
  and twice (yw07b's gate)`
- [ ] `oracle` › `the Fletch coverage gate and its ledger, against the port
  (yw08)`
- [ ] `oracle` › `goldens, the Fletch REPL and hello world, by name (yw08)`
- [ ] `oracle` › `the Fletch invariant report uses its reserved buffer (yw08)`
- [ ] `oracle` › `the thirteen actual Fletch invariant guards (yw08)`
- [ ] `oracle` › `the Fletch executed-opcode traces against C's, twice`
- [ ] `oracle` › `yew fl's fourteen smoke rows, C yew and the port`
- [ ] `oracle (ubuntu)` › `the Fletch bench rows against C's perf_fletch
  (timing advisory, sanity hard)`
- [ ] `unit (linux x86-64, shard N/3)` and `checked-cases (shard N/4)`
- [ ] `the 213 pinned Fletch cases, by name and in registry order`
