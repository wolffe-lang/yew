# yw09 — Fletch in the editor: handles, the recorder, config, `--batch` and the macro UX

yew PR from `yw09`, base trunk `0ccb2c6`. The lane ran on Claude Opus 5.5
throughout, under `notes/contracts/yw09-fletch-in-the-editor.md` (adopted
whole) and rulings R-yw09-1..6 (`docs/MAP.md` §6). It ports sagitta campaign
07 (s34–s38) at `sagitta.pin` `9ace98c2`.

Footprint: cross-cutting

## Forbidden

The contract's rules, as kept:
- No golden, unit case, conformance file, script, recorder file, baseline or
  ledger of the oracle's edited. The 21 recorder `.rec` files and the
  `fuzz_flapi` and `fuzz_record` corpus files are the pin's, copied byte for
  byte (`bdf9637`, `467a985`). The rows added to `tools/perf-fletch-baseline.txt`
  and `tools/perf-fletch-misses.txt` are the port's own measurements and
  dispositions (yw08's two files).
- sagitta read and cited only, at `9ace98c2`; nothing filed in sagitta. The
  nested-eval witness (`notes/yw09-evidence/nested-eval/witness.c`) links the
  oracle's own objects and lives in this repo. No other editor's, VM's,
  recorder's or macro system's source.
- No builds on the Mac: the Mac worktree is git only. Every build and run
  happened on kasumi CPUs 8–11 under `flock
  /home/mfwolffe/lanes/kasumi-cores-8-11.lock`, `taskset -c 8-11`, in the
  `px13-ubuntu` container, with scratch `HOME`/`XDG_*`, `TMPDIR` and an
  explicit `YEW_RUNTIME_DIR`. Hosts synced through git only.
- Signal witnesses are pty bytes: the PTY cases through `tools/goldens`;
  `batch_kill9` is C's own driver.
- No label, merge, tag, issue filed or closed. No attribution trailer. No
  edit to `wolf/` or `~/.claude`.
- One kind-id/`match` representation for every mutable callback (R-yw07-10,
  R-yw09-2). G54's temporaries are untouched (wolf-lang#948 is open).

## Inputs, verified

- **Toolchain (deliverable 1).** Release lists read at 2026-10-27T04:20:59Z
  (`notes/yw09-evidence/prediction.txt`, `4a115fc`). wolf `v0.2.35`
  (2026-10-23T08:45:33Z) is the latest. lupin `v0.1.57` (2026-10-26T20:48:27Z)
  is newer than the declared pairing `0.1.56`; yw06 kept a pairing behind a
  newer interpreter in the same way. No compiler release answers
  G47/G48/G50–G57, so there is no bump and no retirement.
- **Pin and inputs.** `sagitta.pin` is unchanged. These are recorded with
  line counts in `notes/yw09-evidence/inputs.txt` (`4a115fc`):
  - the five sprint files;
  - the three closeout audits (F08, F09, F15). All three still say
    "independent review pending", so their DoD lists are treated as
    obligations, not approvals;
  - every C source the contract names;
  - every pinned test with its `T()` count: 25 unit files, 94 scripts
    (21 `macroux_*`), 21 recorder files, 6 round-trip fixtures, 5 `flapi`
    and 2 `record` fuzz seeds.
- **Rulings.**
  - R-yw09-1..5 decided A (R-yw09-5, the 69-script boundary, 2026-10-27).
  - R-yw09-6, raised by this lane with its witness, decided A by the
    coordinator (2026-10-27).
  - R-yw07-1..10, R-yw07b-1..9 and R-yw08-1..8 stand as the map carries them.

## Prediction

The pre-change prediction is `notes/yw09-evidence/prediction.txt`
(`4a115fc`). Against it:
- **Met.**
  - The ten PTY cases (s35 3, s37 1, s38 6) pass unchanged by name. All 300
    PTY goldens of campaigns 01–07 are green at the final pass.
  - The round-trip report equals C's runner's.
  - `fuzz_flapi` and `fuzz_record` equal C's drivers' lines.
  - M-YW7's artifacts run in CI by name.
  - No toolchain bump; the headless conformance stays 39/39 (normal,
    stressed, again).
- **Changed by ruling.** "The 94 script files pass" became R-yw09-5's 69 by
  name. The other 25 belong to yw11/yw12/yw14/yw15 and are inventoried, not
  claimed.
- **Not met: the perf predictions.** Release ratios, predicted against
  measured (fin2-d184686b, three sessions):

  | Row | Predicted | Measured |
  |---|---|---|
  | config_load | 3.5 | 2.58 |
  | config_reload_500 | 4.0 | 3.0 |
  | macrolib_scan_200 | 3.5 | 1.89–1.98 |
  | motion_editor | 2.8 | 7.1–7.2 |
  | query_cur_pos | 2.0 | 32 |
  | insert_100k | 2.0 | 3.1–3.4 |
  | perf_record tap | 1.8 | 2.5 |
  | perf_record emit | 2.0 | 0.34 |
  | batch | 1.5 | 1.61 |
  | script_suite | 2.0 | 0.98 |

  The editor-attached rows I predicted best were the worst. The prediction
  assumed the attached path costs about what the headless VM costs; at 1e6
  calls, the binding layer's per-call work dominates instead.

## Evidence index

### By deliverable

1. **Toolchain:** above (`4a115fc`).
2. **Handles and the binding layer (s34 §1–§4, §8).**
   - Handles: `6deddaf` (generation-checked slots), `546e591` (resolution
     through live editor identities). Origins: `3f26441` (stable principals
     and masks).
   - The static host (R-yw09-4 A): `b56c828`, and `96ee0f4` (G58 and its
     bound control, `notes/yw09-evidence/host-seam/`).
   - The attached runtime:
     - `e10a772`: the persistent VM, parked across commands;
     - `83f7de4`: attached marshalling and `ed.run`;
     - `7500e38`, `a0e1fc9`: queries;
     - `dd73464`: parking under compacting GC (`notes/yw09-evidence/vm-parking/`);
     - `5a10363`: the park is a move. A plain push copied the VM, 974 KB a
       command, never freed in the ambient region; the perf rows found it
       as two OOM kills at the 12 GB container limit.
   - Byte-exact messages and logs on the API path: `e7cb0b4`, `f60a2a0`,
     `19c1427`, `898c3d9`, `d1aaabe`.
   - Transactions and motion blocks: `1bb688f`, `505bbb9`. `flapi_cmds`:
     `1938d0a`, `2805e95`, `e43f645`, `d7bad21`.
   - Unit cases:
     - `365656e` fl_marshal 10, `e60d921` fl_cmds 9, `0ca6d67` fl_motion 5,
       `60cf72e` fl_txn 11, `5f7fdf8` fl_hook 8, `d5978ce` fl_api_complete 10;
     - `7e547aa` holds them to the registry;
     - fl_handle 8 and fl_origin 6 are in `src/fl_handle_test.lu` and
       `src/fl_origin_registry_test.lu`.
   - `fuzz_flapi`: `bdf9637` (the pin's 5 seeds), `42362f4`, `e66582e`,
     `ba3826e`, `fdd7df4` (CI), `638e2f4` (the driver did not compile after
     `42362f4`; found by fin-dc1dcc9). At the final pass both lines read
     `fuzz_flapi: seed=1 iters=200000 corpus=10 hash=376ccf21cd395b53 ok`.
   - `check-cmd-dispatch.sh` and `check-fl-choke.sh` as tools: `b517deb`,
     `85aa2d6`, `8180648` (CI).
3. **`edit{}`, `on()` and hooks (s34 §5–§7):** `4033a4a`, `d026bad`, and the
   event fire sites `36fcd6a`, `983dada`, `03b7f5a`, `c36cbdd`, `e0506b2`.
   G58 is handled at `hook_fault` (`2fdaedb`) and at its callers' `fl_nil()`
   arguments (`e1229cc`). `tests/fletch/34-editor.fl` stays green headless
   (conformance 39/39).
4. **The recorder and the round-trip law (s35).**
   - `95ce53c` (fl_call_chunk, fl_compile_str, the macro cache), `f7a990d`
     (start, stop, the tap, emission, replay), `7ce741f`, `696cb00`,
     `5c90ef7`, and `bddc31b` (`ed.recording`).
   - Unit cases: `0ca89c8` record 9, `8aeadea` record_integration 17,
     `08c2c4d` record_nested_replay 3, `5633797` fl_replay_runtime 3. The
     first two have one-case selectors for the checked machine (`ecdd79b`,
     `3c5f8b9`, `faa35ce`).
   - The round trip (R-yw09-1 A): `adde271` (the runner and C's generator,
     one region per seed), `2a3c8e9` (`tools/run-roundtrip`), `0bfb3c8`
     (CI). Both lines read `roundtrip: ok seeds=2000 base=0 fixtures=6
     corpus=21 count-sentinel=1 edit-store-noop=1 cross-keymap=1
     third-command-rollback=1 P1-P5`. The planted folding fault shrinks to
     the right operation.
   - `fuzz_record`: `467a985`, `e99e888`, `229b1e3`, `67a34ed`. Both
     drivers give `corpus=7 exact replay ok`, and at 200,000 inputs both read
     `seed=1 iters=200000 corpus=7 hash=0758d1d8d72c0670 ok`.
5. **Config (s36).**
   - Code:
     - `cfe24b5`, `10db251`, `1561faf`: option.c, `:set`, `opt_in`/`opt_out`;
     - `ae45391`: bind.c;
     - `e1ef7ea`, `42ec614`: trust and its prompt;
     - `823b968`, `3192f8b`: flconf; `Opts` mirrors the store;
     - `331eb12`: state_fletch, which retires the hand codec;
     - `474fbd1`, `fb79d72`, `f5bafc0`, `5da0a2a`, `9268b5d`.
   - Unit cases: `a91bce0` trust 8, `785defb` state_diff 2, `36dc1bd`
     option 7, `95d1a85` bind 5, `a5610cd` runtime_defaults 3, `276cd01`
     flconf 12, `0099a41` trust_prompt 2.
   - Case selectors for the checked machine: `a2ee24b`, `e24ede9`,
     `1d7dbce`, `f113bd2`, `fcd8af3`.
6. **`--batch` and the script suite (s37).**
   - Code: `27f03bb`, `c7e2868`, `c842814`, `1384f6f`, `92220a1`,
     `f6ae6ae`, `cb5d621`, `5bc4ebb`, and:
     - `aa10348`: the selfcheck refuses an opened terminal and an installed
       timer;
     - `5818270`: G26, the runner's result descriptor;
     - `a69fc88`: the filter's byte span;
     - `c4854b4`: `opt.set` parks the VM so `macro.dir` rescans;
     - `96f4fb3`: `batch_test.lu` became `batchtest.lu`, because a
       `*_test.lu` file is a test, not a module member.
   - Unit: `b94dfc2` (batch 6; the profiler case SKIPs by name, it is
     yw15's).
   - The script gate (R-yw09-5): `58594de`, `d3344a7`, `c95aa38`, `8581869`,
     `2f51518`, `d184686` (the determinism half in CI).
     - Port and C both read `script: 69 tests, 741 assertions, 0 failures,
       1 skipped`, and all 69 port verdicts equal C's by name.
     - The runner's `--selftest` passes against the port.
     - A second run is byte-identical (the gate's own diff, and det at
       dc1dcc9).
   - `batch_kill9`: `batch-sigkill iterations=200 attempts=200 old=30
     new=170 journals=164 … ok`.
7. **The macro UX (s38).**
   - Code:
     - `10d3f3d`, `6e0853f`, `54fb323`: macrolib;
     - `21ce72c`, `01cfc9b`, `f396f62`: the compiler's validated-globals
       mode and the attached motion-word check (`compile.c:664-745`);
     - `8367470`, `4d6a120`, `7a5f62f`, `a2b6d12`, `f8d9e91`: macrobrowse,
       the picker host, the commands, saving into a register;
     - `8680111`: the REC chip.
   - Unit: `dfa937e` macro_header 5, `88655cb` macrolib 8, `e463925`
     macrobrowse 6.
   - Former SKIPs that now run: `d6c7a5a` (statusline), `17e9f6b`
     (message), `9677a2c` (save_policy's three option rows).
8. **The perf rows (R-yw09-3 A).**
   - The driver and the gate: `f0e4eb3`, `259369c` (one region per sample,
     as C closes its EditorEnv), `0a62b77` (the driver's VM attached to the
     editor, as `editor_env_open` does), `cdef225`, `9074c14`, `42cfdee`.
   - CI and runners: `f5987a7`, `cab3c7f` (the editor rows in their own CI
     step and budget), `6ed7b41`, `ba100bd`, `16e66ea`, `b45d5a1` (C's
     drivers measure their own runtime).
   - Ledgers: `535e586` (baselines), `c3db569` (named rows).
   - The record is fin2-d184686b, three sessions within 2%:
     `notes/yw09-evidence/final/perf/`.

   | Row | port (median) | C (median) | ratio | budget | disposition |
   |---|---|---|---|---|---|
   | config_load | 2.24–2.30 ms | 0.87–0.89 ms | 2.58× | 1 ms, MISS | yew#89 |
   | config_reload_500 | 6.35–6.41 ms | 2.12–2.15 ms | 2.97–3.01× | 5 ms, MISS | yew#89 |
   | macrolib_scan_200 | 1.85 ms | 0.94–0.98 ms | 1.89–1.98× | 5 ms | PASS |
   | motion_editor | 1.06–1.07 s | 0.147–0.149 s | 7.12–7.23× | 1 s, MISS | yew#89 |
   | query_cur_pos | 514–521 ms | 16.0–16.3 ms | 31.7–32.5× | 300 ms, MISS | yew#89 |
   | insert_100k | 206–213 ms | 61–67 ms | 3.11–3.41× | report-only | RECORDED |
   | record tap overhead | 50 ns | 20 ns | 2.50× | 200 ns | yew#89 |
   | record emit 10k | 0.36 ms | 1.07 ms | 0.34× | 10 ms | RECORDED |
   | batch startup | 2.68 ms | 1.66 ms | 1.61× | 8 ms | RECORDED |
   | script suite wall | 9.31 s | 9.49 s | 0.98× | 20 s | RECORDED |

   - Re-judged against the new ledgers with compare.py's own readers and
     regression rule, the three sessions give `failures=0 errors=0`. Before
     the ledgers they gave nine failures each: four unnamed MISS rows and
     five NO-BASELINE rows.
   - query_cur_pos allocates nothing per call (a region ledger of 0 bytes
     over 4,000 calls), so its cost is CPU in the binding path, not memory.
   - The yw08 rows were re-measured in the same sessions. All stay over 2×,
     within their baselines, and named under yew#77; none is retired. In
     perf-3, join5k read 1.94× only because C's sample was 1.29 ms against
     0.69–0.70 ms in the other two; the port's 2.50 ms did not move.
9. **The note and the map:** this file; `e7b6a82`, `dc1dcc9`, `66d3566`
   (MAP §2 rows, G26/G58, §6 R-yw09-1..6, §7); `679e1a2` (yw10's
   contract).

### R-yw09-6: a deliberate divergence from the oracle

`667ce1f`, `ff74570`.
- **C's behaviour.** C compiles every `ed.fl.eval` source as the user
  config (`fleval.c:30-33,263-302`). A chunk that is not the config can
  therefore reach CONFIG's capabilities, and register hooks the config
  owns, through `ed.run("ed.fl.eval", …)`.
- **The port's.** A nested eval runs under the calling chunk's principal
  (`fl_cap_origin`). This is the rule `fl_macro_source_written` already
  keeps (YEW-F-008). With no Fletch frame live, the source still runs as
  the config.
- **The witness.** Both halves at the final pass are in
  `notes/yw09-evidence/nested-eval/c.txt` (C, from the oracle's objects)
  and `port.txt`. Every line is equal except B and D:
  - B, the nested `ed.buf.open`: C opens the buffer; the port refuses it.
  - D, the nested `on("ed.idle")`: C's hook belongs to the config; the
    port's belongs to the caller.

  The later buffer counts differ only by the buffer C's B opened.
- No pinned golden, unit case or script reaches a nested eval from a
  non-config frame.

### Port-only cases changed, disclosed

- `t_port_cmdline_fl_refuses_naming_yw08` became
  `t_port_cmdline_fl_evaluates_in_the_runtime` (`eb87a7e`). It was yw04's
  pin of the interim refusal ("not yet ported: ed.fl.eval … (yw08)"). yw09
  runs C's `ed.fl.eval` (`option.c:1902-1907`), so the case now asserts
  three things: the line evaluates, the prompt closes on success, and the
  result is the message. No oracle file changed.
- `src/fl_nested_eval_test.lu` was pinned to C (`3d755e5`) until R-yw09-6
  was decided; it now holds the port to A (`ff74570`).

### Divergences and boundaries, named

- `Opts` mirrors the option store (`3192f8b`). Code from campaigns 03–06
  reads `ed.opts`; the store is the authority, and every write goes through
  it.
- `t.log` reads the log file back, where C's test module reads its ring.
- The profiler dump (`test_batch`'s sixth case) is yw15's: SKIP by name.
- The macro scratch has no syntax engine. Its language is recorded in
  `ed.buf_languages`, where C attaches `fletch` highlighting
  (`macrobrowse.c:109-120`). The three syntax lines of
  `edit_is_an_ordinary_multicursor_undo_buffer` are yw10's; its contract
  names them.
- A register holding invalid UTF-8 can be searched in the browser by name
  only (G40).
- G58 is named at `flhook.lu`, as at `stdre.lu`.

### The gauntlet, and what it saw red

All runs were on kasumi. The curated logs are `notes/yw09-evidence/final/`
(`f15a689`); `gauntlet.txt` there has every step line.
- **fin-dc1dcc9, at `dc1dcc9`.**
  - Green: 201/201 test files native, the release build, conformance, the
    69 scripts, kill9, the round trip, and both fuzz_record lines.
  - Red, all this lane's:
    - the demo did not build: a `Buffer` literal lacked `macro_reg`
      (`087c406`);
    - `fuzz_flapi` did not compile (`638e2f4`);
    - `fl_hook_test` hit G58 on the checked machine (`e1229cc`);
    - fl_txn case 2 and flconf case 5 are past the step budget even alone.
      They take `allow … budget` rows (`fcd8af3`); both pass natively;
    - the perf driver's VM was not attached, so `insert_100k` was not one
      undo node (`0a62b77`);
    - C's perf drivers refused another runtime (`b45d5a1`);
    - the nested-eval comparison was my harness, and too strict.
  - The determinism check, queued behind it, was identical.
- **fin2-d184686, at `d184686`.** It died with kasumi's reboot at 01:46Z,
  during the PTY step. It had shown the checked lane green and the CI
  checked lane for `edit_message_test` (below).
- **fin2-d184686b, the same pass relaunched.** Every step is green except
  two:
  - tools-build: the harness staged no `fuzzgen` module, so twelve drivers
    refused with E0301. The tools' own build scripts stage it
    (`tools/build-fuzz-flapi:31-33`). The corrected build, tools2, is this
    step's verdict: 24 of 24 drivers that link `edit` or `fl` built at
    d184686 (`final/tools.txt`).
  - perf-1/2/3: the nine NO-BASELINE and unnamed-MISS failures that the
    two ledger commits answer.
  - The green steps: fmt; oracle; hooks native; the checked lane (27 files
    `exit(0)`, 5 case by case, 9 whole-file past the budget as G29's native
    fallback); 300/300 PTY; conformance; 69/69 scripts with the determinism
    half; kill9; round trip; both fuzzers; nested eval; perf-c07.
- **`edit_message_test` on the checked machine.** Under `conform-run`,
  `os_exe()` is the wolf binary, so the bell case's self-exec child exits 2.
  That function is byte-identical to trunk. CI's lane, `wolf test`, runs the
  file `exit(0) [native]` with its self-exec note
  (`final/wolf-test-message.json`).
- The two recorder files that the checked lane ran as whole-file native
  fallbacks now have one-case selectors (`ecdd79b`, `3c5f8b9`, `faa35ce`).
  25 of their 26 cases pass on the checked machine. Case 0 of
  `edit_record_test` builds an editor per frozen motion word, is past the
  budget alone, and takes an `allow … budget` row (`3e01580`). See
  `final/rec-cases.txt` (the first run, red on that case) and
  `rec-cases2.txt` (green with the row, at 3e01580).
- yew#90 (trunk's scheduled macOS port job, `edit_comphelp_test.lu:692`,
  red since 2026-10-26) is not this lane's. If this PR's macOS leg shows
  it, it is that issue, cited by name, not retried.

## Done-when

- [x] Every deliverable with its tests (above).
- [x] `--native` green: 201/201 at dc1dcc9, and the hook files again at
  d184686.
- [x] The checked machine: the 42 lane files; the per-case files case by
  case, the recorder pair included (`final/rec-cases2.txt`).
- [x] The PTY cases green by name (10 of campaign 07; 300 of 300 in all).
- [x] The script suite (R-yw09-5's 69), the round-trip law, the recorder
  corpus and the two fuzzers in CI by name, each equal to C's.
- [x] The perf rows recorded beside C's from one run, every MISS named with
  its issue (yew#89; the yw08 rows under yew#77).
- [x] M-YW7 met.
- [x] `docs/MAP.md` updated; yw10's contract drafted.
- [ ] CI green at the final head: the PR run, its id read once at hand-back.
- [ ] `bash wolf/tools/lane-audit.sh yew yw09 <PR>` passing but for the
  final run's green: its last line is in the PR body.
