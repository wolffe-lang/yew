# yw07 — the 0.2.35 pin and the seven retirements

yew#65, merged 2026-10-25 at `ee16798d` (run 40152945796 green, AUDIT CLEAN). The lane's wrapper could not write this file, so the orchestrator materialised it from the PR body at merge; the text below is the PR body as merged.

Footprint: cross-cutting

## Forbidden

Deliverable 1 only: the 0.2.35 pin and the seven retirement tracks. No toy VM, Fletch implementation, merge, tag, release or static-binary/PAX handoff. No third-party implementation source read; sagitta is the unchanged oracle at its pin. No golden or baseline changed. No new unsafe block or module state (18 existing unsafe blocks before and after). All local builds/tests/performance ran in kasumi containers, private HOME/XDG roots and explicit YEW_RUNTIME_DIR; no builds on nomad. CI plants exist only on `yw07-plant-*`, never on this branch.

## Inputs, verified

- `7a9ae6e`: wolf 0.2.35, lupin 0.1.56, bundled std at the recorded revision. All six release archive digests read twice; Linux x86_64 archives hashed twice after download. `notes/yw07-evidence/toolchain/` retains both reads, versions and release notes.
- `sagitta.pin` unchanged: tenseleyFlow/sagitta at `9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a`.
- Adopted contract: `notes/contracts/yw07-fletch-core.md`; implementation cut is deliverable 1. R10 keeps one kind-id/match representation for mutable callbacks; read-only callbacks use function values. R11 calls the middle attribution cell **pin + compile compatibility**, not pin only. Literal pin-only is BUILD-RED.
- Existing upstream reports are wolf-lang#914–#919; this PR files no additional upstream issue. #916 is direct function-field invocation, #917 mutable function values, #918 pin startup cost, #919 the scratch-region buffer escape. yew#53, #54 and #55 retain the performance/harness follow-ups.

## Prediction

The original pre-change prediction is preserved in `notes/yw07-evidence/prediction.txt`. Its complete-retirement and all-ratios-green parts were not met: mutable registries, filesystem limitations and remaining allocation work stay open; measured pin regressions are named MISS, not PASS. Its Fletch/GC/conformance/static claims are out of this cut and have not been tested or claimed complete.

Retirement accounting:

| Track | Commits / result | Remainder |
|---|---|---|
| yew#17 / #27 | `05fd414` environment callbacks; `4c6462c` cursor sort; `f10e937` injected clocks; `c96f823` shared state/fuzz sort | Mutable registry half remains G48 / wolf-lang#917; bound calls retain G47 / #916 |
| yew#20 | `3b519e4` child-role guards removed, output visible and native fallback counted; strict per-case adapter | Checked self-exec remains an explicitly named unsupported case, covered natively |
| yew#22 | `45061a5` adopted inherited descriptor and OS/arch clipboard selection | Complete adoption |
| yew#23 | `5801186` access/no-follow/descriptor identity; `c8446b4` FIFO fixtures; `3256c7c` non-blocking clipboard | Write-only-existing-file open and journal POSIX record-lock contracts remain open |
| yew#24 | `d87a75e` standard terminal mode/restore/wait wrappers; bounded wait scratch | Complete adoption |
| yew#40 | `bff2188`, `b581b2d`, `1f5d46c`: owned interner, frame scratch, picker reserves, fixed-slot menu reuse | Parser/refilter temporaries, line copying, whole-loop scratch and uncompleted allocation rows remain open |

MAP §5 distinguishes upstream release fixes from actual port rewrites: retained scalar literals, integer fields and prime helper functions are not falsely claimed converted. G41's new trap line does not relax the no-input-depth-recursion rule. Recommendation at merge: retire #20/#22/#24; keep #17/#27/#23/#40 open for the named portions.

## Evidence index

### macOS job-cap follow-up

Run **40138357879**, attempt 1, reached the macOS oracle's 210-minute job cap, not a code failure. The other jobs completed green. The editor measurement also exhausted its old 15-minute step cap (GitHub reports the announced-advisory step as success); the pane measurement was cancelled at the job cap and the job-stream measurement was unreached.

| macOS step | Elapsed minutes | Result |
|---|---:|---|
| C oracle build and unit suite | 3.62 | green |
| release editor build | 19.57 | green |
| demo_paint build | 20.02 | green |
| perf_cmdcomp build (hard gate) | 20.37 | green |
| fuzz_cmdparse | 21.60 | green |
| fuzz_panes | 22.05 | green |
| fuzz_tabs | 21.43 | green |
| fuzz_groups | 22.70 | green |
| fuzz_state | 12.77 | green |
| fuzz_mouse | 2.23 | green |
| fuzz_gitignore | 6.15 | green |
| editor advisory measurement | 15.22 | step timeout |
| pane advisory measurement | 2.77 | job-cap cancellation |
| job-stream measurement | 0 | unreached |

`18fce0c` splits macOS into the existing build/golden oracle job plus **four added jobs**: two fuzz families (~59/~50 minutes of previously observed work, plus C build), and two measurement families. Each macOS oracle/family job is capped at 120 minutes. The seven campaign commands, sizes, seeds and native selections are unchanged; all six measurements keep their commands and announced advisory policy. Editor/pane measurements now have 60/35-minute step budgets in their own family. Existing hard compile gates remain hard.

The oracle hands its editor, demo, perf_cmdcomp executable and C tree to measurements via a same-run tar artifact, preserving executable bits and the build symlink; consumers verify the checkout commit before use. The C drivers are rebuilt (~4 minutes) in each fuzz family rather than cached across unrelated runs. Nightly reporting depends on both new job groups. No application code or expected answer changes.

`ee16798` records the original API job/step timestamps and short pool-container validation in `notes/yw07-evidence/macos-ci/`: planner tests, seven-campaign/six-measurement preservation checks, five rejecting mutation controls, and YAML parsing all pass. No local Mac build or test was run. Final CI at this revised head is pending the orchestrator's watch.

- `25f187f`: `notes/yw07-evidence/closeout/closeout.log`, run 18:45:16Z–22:03:09Z on 2026-10-24, measured application head `2e77b34`. Native/release builds, 287/287 PTYs, default unit run **135 passing files, 73 native fallbacks**, full native suite, and **448 per-case checked cases over 24 files, 0 red**. Budget and self-exec allowances are named, not silently called checked passes. Existing FUSS mouse/ctxrows and G40 shell rows remain named. Later changes are documentation, CI and verdict accounting, not a fresh timing claim.
- `a73df60`: exact Linux/x86_64 MISS rows, s265 owner and tabswitch p99 classification. Short container validation passed format, adapter and reader controls; 2.0 stays PASS, missing/other-host/other-metric rows stay FAIL. `closeout/miss-disposition-validation.log`.
- `ab51ff9`: removed the host `/usr` overlay that hid Docker init from the new clipboard CI step. The early plant setup failures were retained and do not count as gate evidence.
- G20 twin: old release build exit 4; new pin prints `[1 2 3 3 11 22]`. State corpus 22 canonical / 4 noncanonical / 20 invalid; state fuzz 200,000 × seed 1 matches C hash `b02af7a3b3cd8bae`; state perf emit/parse/restore 0.60/0.90/1.12.
- Non-blocking clipboard: all 15 C cases plus unread-helper regression passed native/release; roughly 1,001 ms timeout, partial write/busy observed. `notes/yw07-evidence/retirements/clipboard-nonblock.log`.
- Text ratios piece/code/UTF-8/allnl 1.23/1.81/1.62/1.55 at the approved 16 GiB cap. Both original trunk and this lane OOM at 8 GiB for repeated allnl loads, not piece. Existing yew#54 owns the per-load-region harness fix. `notes/yw07-evidence/piece-attribution/results/`.

Startup attribution (three unchanged C→port→C trials per cell):

| Cell | Cold-open port median | Paired ratio median | First Backspace ratio |
|---|---:|---:|---:|
| A: `280012fe`, original 0.2.34 | 7.664176 ms | 2.027 | 2.457 |
| B′: `7a9ae6e` + only required Mode fields and shell-context copy, 0.2.35 | 11.512989 ms | 2.789 | 2.572 |
| C: `35e21b9` | 4.918455 ms | 1.281 | 2.530 |

Pane attribution (trial ratios; `*` means C drift >1.25, retained but unsuitable for inference):

| Cell | many p99, trials 1/2/3 | tabswitch p99, trials 1/2/3 |
|---|---|---|
| A | 1.76 / 1.82 / 1.64 | 1.92 / 1.95 / 1.88 |
| B′ | 2.11 / 1.93 / 2.08 | 0.50* / 3.65 / 3.57 |
| C | 2.11 / 2.07 / 2.00 | 1.14* / 0.48* / 2.05 |

Raw attribution: `notes/yw07-evidence/perf-attribution/results/` and `pane-attribution/`. No extra attribution or selectively chosen port samples were used.

Closeout uses the first five C-stable triples per row, max/min C drift ≤1.25; raw trials and chosen IDs remain in `closeout/closeout-artifacts/`. Ratios: default 1.27, dumb 1.68, keypress 0.83, free cursor 0.92, paced cursor 1.02, backspace max 0.78, two panes p99 1.01 and many buffers p99 1.99 PASS. Named MISS rows:

| Metric | C / port / C-again median (ns) | Ratio | Accepted trials | Owner |
|---|---|---:|---|---|
| startup.first_paint.clean | 2045047 / 14104169 / 1977982 | 6.90 | 2,3,4,5,7 | s265, wolf-lang#918, yew#55 |
| cold_open_to_first_paint | 3787584 / 7842139 / 3869978 | 2.07 | 1,2,3,5,6 | s265, wolf-lang#918, yew#55 |
| tabswitch p99 | 236786 / 487314 / 228111 | 2.10 | 1,3,4,5,8 | s265, pin attribution, yew#55 |
| first Backspace | 249351 / 657723 / 244212 | 2.64 | 1,3,5,6,7 | yw15, yew#53 |

Orchestrator disposition: MISS for the 0.2.35 pin regression, re-measured at the re-pin. The 2× threshold and unlisted host/metric failures stand. Pane p50/max are informational, not gated. The raw logs still say FAIL where the disposition was not yet entered.

RSS, 1,000 keys, identical frozen fixture; bytes per key:

| Phase | Port before / after | C before / after |
|---|---:|---:|
| prompt-menu | 21303.3 / 5521.4 | 397.3 / 286.7 |
| lines40 | 725.0 / 659.5 | 69.6 / 20.5 |
| pane-lines40 | 1007.6 / 528.4 | 0.0 / 69.6 |

`perf-attribution/retirements-red.log` retains the before run; `closeout/memory-after-20261024T191502Z/` the after. Native/release focused ledgers retain zero bytes over 200 menu refills and 30 strip frames, not a whole-loop zero-allocation claim. Checked validates contents/drawing but names its incompatible ledger accounting separately. The abandoned row-pool failure is reduced at `reuse-row-move/` and filed as wolf-lang#919; fixed slots avoid it.

Nine independent implementation regressions were seen red on their PR runs and closed unmerged; expected answers were unchanged. Correct implementations preceded the plants at `a73df60`. The branch-only workflows exercised the same existing assertions, without running the entire matrix. Logs and checked final PR states: `notes/yw07-evidence/plants/`.

| Gate | Draft PR | Red run | Existing assertion |
|---|---:|---:|---|
| checked-adapter | #56 | 40137882552 | native=1 record wrongly accepted |
| miss-host | #57 | 40137894055 | wrong-host FAIL incorrectly passed |
| stable-trials | #58 | 40137899919 | C-unstable triple incorrectly selected |
| clipboard | #59 | 40137885953 | text_clipboard_test.lu:1011 unread writer |
| wait-storage | #60 | 40137905232 | term_wait_storage_test.lu:29 retained storage |
| strip-storage | #61 | 40137901504 | edit_reuse_test.lu:107 retained frame storage |
| clipboard-host | #62 | 40137888626 | text_clipboard_host_test.lu:29 pbcopy on Linux |
| clock | #63 | 40137891640 | text_undo_clock_test.lu:27 callback value |
| stable-sort | #64 | 40137896157 | ws_state_sort_test.lu:21 identity order |


## Done-when

- [x] Pin/digests and retirement implementation commits recorded; MAP/README and open remainders updated.
- [x] Local native/release builds, 287 PTYs, checked/default/native/per-case units; raw exclusions and fallbacks counted.
- [x] Before/after RSS, attribution and named performance MISS ownership recorded without altering the C harness or baselines.
- [x] Verdict/reader/adapter controls passed after the policy patch; nine isolated gate plants documented above.
- [ ] Final PR CI green: the orchestrator watches the run; this lane reads its initial state once and does not wait. The original `730115b` audit ended `AUDIT FAIL (footprint: cross-cutting)` only because its run was in progress; that run later hit the macOS cap documented above. The revised head awaits fresh CI; no prior green or audit is claimed for it.
- [ ] Coordinator writes `notes/yw07-retirements.md` from these five sections at merge (the lane's report-file restriction requires this PR-body fallback).
- [ ] Remaining #17/#27/#23/#40 portions and next-pin performance remeasurement; not represented as complete.
- [ ] Static-binary/PAX handoff: explicitly SKIP in this cut, owed by the fresh Fletch lane.

**yw07b:** start from merged trunk; toy VM and R-yw07-1 measurement first, then Fletch deliverables 2–10 under the adopted contract. Carry G47/G48/G50 and the open retirement portions; do not revive the abandoned row-pool shape or invent a second mutable callback representation. No Fletch source was implemented here.

