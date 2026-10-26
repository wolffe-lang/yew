# yw09 — Fletch in the editor: handles, the recorder, config, `--batch` and the macro UX

**Model per ruling #89 R4, chosen at launch. Drafted by yw08 from
`docs/MAP.md` §7's yw09 paragraph, sagitta campaign 07's five sprint files
and yw08's hand-off.** Ruling #89 (`sprints/yew/index.md`); the track's
seven standing rules (rule 2: no golden edited; rule 4: the 2× gate);
`docs/MAP.md` as yw08 left it (§1's Fletch rows, §5's G47–G57, §6's
R-yw07-10 and R-yw08-1..8); `sprints/RULES.md`. It ports campaign 07,
"Fletch in the editor", whole:

- s34 (`s34-editor-api.md`, 643 lines at `sagitta.pin`): handles,
  origins and capabilities, the binding layer, the API surface, `edit{}`
  over s10's transactions, `on(event, fn)`, hook containment and the
  reentrancy guard, motion-block execution, spec amendment A2;
- s35 (`s35-recorder-roundtrip.md`, 504): the recorder (commands, not
  keys), emission as terse Fletch, storage, replay through the VM only,
  the round-trip law and its harness (the 2026-08-10 implementation
  amendment, `s35:55-78`, binds);
- s36 (`s36-config-system.md`, 608): load order and origins (`flconf`),
  the option table, `bind`/`unbind`, workspace trust, atomic reload,
  `runtime/init.fl` live, workspace state on the Fletch path;
- s37 (`s37-headless-batch.md`, 420): `yew --batch`, no tty, the stdio
  contract, exit codes and traces, batch save semantics, the script-test
  runner;
- s38 (`s38-macro-ux.md`, 365): the REC indicator, replay polish, the
  macro browser, the edit-macro flow, the macro library, the sharing
  format (the completion record `s38:59-74` binds DoD 8 and 13).

None of the five has a "Corrections after landing" list; their DoD walks
live in sagitta's `.docs/audits/closeout-F08-fletch.md`, `F09-recorder.md`
and `F15-ci.md`. Read those before claiming a DoD row.

The C (line counts at the pin; re-derive): `src/fl/handle.c|h` (594/175),
`origin.c|h` (275/182; yw07b ported the check half), `flapi.c|h`
(2,143/70; yw07b ported the headless half, this lane `fl_ed_attach` and
the attached path, `flapi.c:1131-1137`), `flhook.c|h` (329/132),
`motion_tab.c|h` (311/36), `fltxn.c|h` (160/33), `flruntime.c|h`
(507/97), `fleval.c` (327), `record.c|h` (849/84), `flconf.c|h`
(858/69), `macrolib.c|h` (936/72); `src/edit/option.c|h` (1,907/139),
`batch.c|h` (759/41), `keys_default.c` (112), and the dispatch seams of
`cmd.c` (2,242) and `ed.c` (3,142); `src/ws/trust.c|h` (1,099/152),
`trust_prompt.c|h` (207/35), `state_fletch.c` (234); `src/ui/macrobrowse.c|h`
(762/17) and `statusline.c`'s REC chip (885); `runtime/init.fl` (526);
`scripts/check-cmd-dispatch.sh` (42) and `check-fl-choke.sh` (85).

The tests (counts are `T()` rows in `tests/unit/registry.c`): s34's
`test_fl_handle` 8, `test_fl_marshal` 10, `test_fl_origin` 6,
`test_fl_txn` 11, `test_fl_hook` 8, `test_fl_motion` 5, `test_fl_cmds`
9, `test_fl_api_complete` 10; s35's `test_record` 9,
`test_record_integration` 17, `test_record_nested_replay` 3,
`test_fl_replay_runtime` 3; s36's `test_option` 7, `test_bind` 5,
`test_trust` 8, `test_trust_prompt` 2, `test_flconf` 12,
`test_state_diff` 2, `test_runtime_defaults` 3; s37's `test_batch` 6 and
`test_args`' 10 batch rows (of 20); s38's `test_macrolib` 8,
`test_macro_header` 5, `test_macrobrowse` 6, `test_statusline` 8. The
sprint prose names files that do not exist at the pin
(`test_record_emit`, `test_record_tap`, `test_batch_args`,
`tests/script/api_*`, `config_*`, `meta_*`): the pin's names govern.
Re-derive every count at the pin.

## Deliverables

1. **The toolchain, first.** `gh release list -R wolffe-lang/wolf-lang`
   and `-R wolffe-lang/wolf-interp` read and quoted with their time. A
   release newer than 0.2.35 is this lane's first commit with its
   prediction, and the retirements it names are adopted, each in its own
   commit: G47 (wolf-lang#916), G48 (#917) — which decides whether the
   hook and event tables can stay one kind-id `match` (R-yw07-10) or
   become function values —, G50–G54, G55 (ONLCR, filed from yw08), G56
   and G57 wherever the release answers them.
2. **Handles and the binding layer** (s34 §1–§4, §8). Handles as ids
   (`handle`), origins and capability checks on the attached path,
   `flapi`'s editor-attached half (`fl_ed_attach`), `motion_tab`'s
   dispatcher for motion blocks under a live editor host. Unit: the eight
   s34 files above. Fuzz: `fuzz_flapi` against C's driver at
   `Makefile:2270`'s size, its report line byte for byte, over
   `tests/fuzz/corpus/flapi` (5 files). `scripts/check-cmd-dispatch.sh`
   and `check-fl-choke.sh` ported as `tools/` checks or run against the
   port's tree, whichever the scripts allow unchanged.
3. **`edit{}`, `on()` and hooks** (s34 §5–§7): transactions over s10's
   undo groups, the event inventory, error containment and the
   reentrancy guard. `tests/fletch/34-editor.fl` stays green headless.
4. **The recorder and the round-trip law** (s35). Commands recorded as
   terse Fletch, storage, replay through the VM only, the multi-cursor
   and transaction rules. The round-trip harness is the port's own
   (sagitta's `tests/roundtrip/runner.c` links the editor in-process,
   `Makefile:1073-1074`): it replays C's generator (`tests/roundtrip/gen.c`)
   at its 2,000 seeds and the six fixtures, its report compared to C's
   runner's (R-yw09-1). The 21 `tests/corpus/recorder/*.rec` files
   (`test-record-corpus`, `Makefile:2401`) and `fuzz_record` against C's
   driver. PTY: `s35_macro_record_start_message`, `_stop_message`,
   `_replay_from_e_mode` by name.
5. **Config** (s36): `flconf`'s load order and origins, the full option
   table (`option`, retiring `option_cmdline`'s interim), `bind`/`unbind`,
   trust and its prompt, atomic reload, `runtime/init.fl` executed (the
   literal reader `edit.fldata` retires where `init.fl` runs), and the
   workspace state on the Fletch path (`state_fletch`, retiring the hand
   codec of R-yw06-1). The trust prompt has no PTY golden at the pin
   (`test_trust_prompt` is its gate).
6. **`--batch` and the script suite** (s37). The command line, the
   no-tty refusal, the stdio and exit-code contract, batch saves and the
   interactive refusals; C's `tests/script/runner.c` run against the
   port's binary over the pin's 94 `.fl` files, green by name
   (`make test-script`, `Makefile:3851`; determinism `:3930`; budget
   `:3949`). PTY: `s37_batch_never_touches_the_terminal`. Torture:
   `batch_kill9`.
7. **The macro UX** (s38): the REC chip, replay polish and the
   per-register listing, the macro browser, the edit-macro flow, the
   library and the sharing format; the six PTY cases
   (`s38_macro_indicator_80`, `_40`, `_burst`, `_edit_flow`, `_browser`,
   `_browser_actions`) by name and the 21 `macroux_*` scripts.
8. **The perf rows** (R-yw09-3). `perf_fletch`'s editor rows
   (`config_load`, `config_reload_500`, `macrolib_scan_200`,
   `motion_editor`, `query_cur_pos`, `insert_100k`) added to
   `tools/fl-headless`'s harness and yw08's gate (`compare.py`'s budgets
   policy, the regression rule, the baseline and the named-MISS ledger);
   `perf_record`, `batch` and `script_suite` recorded beside C's from the
   same run, on kasumi under `taskset` in a container. Every row over 2×
   named with its issue; the yew#77 rows re-measured and kept named or
   retired.
9. **The note and the map.** `notes/yw09-…md` with the five sections;
   `docs/MAP.md` §2's campaign-07 rows, §5's new gaps, §6's rulings, §7's
   yw09 and yw10 paragraphs, and yw10's contract drafted in full.

## Rulings (to ask at launch unless decided)

- **R-yw09-1 — the round-trip harness.** (A) a port-side driver over C's
  generator, its seeds and fixtures, whose report line equals C's
  runner's (recommended: sagitta's runner links the editor and cannot
  drive a second binary); (B) a protocol the C runner could speak to the
  port (it does not exist at the pin, and inventing it edits the oracle's
  shape).
- **R-yw09-2 — the hook and event tables.** If no release answers G48,
  (A) the kind-id plus one `match` representation stands (R-yw07-10,
  decided) for `on()`, hooks and the option table's setters; (B) a second
  representation, refused by R-yw07-10.
- **R-yw09-3 — the editor perf rows' gate.** (A) yw08's harness and gate
  extended to the editor rows, timing advisory on hosted CI and the
  record on kasumi (recommended: one gate, C's policy); (B) a separate
  harness per row family.
- **Decided:** R-yw07-1..10, R-yw07b-1..9 and R-yw08-1..8 as the map
  carries them, subject to the maintainer's batch. `--batch` never
  touches the terminal (s37). The headless Fletch of yw07b and yw08 stays
  green throughout.

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. `Footprint:
cross-cutting` (CI's by-name steps). Read sagitta's campaign-07 sources,
sprint files, closeout audits, tests and baselines freely and cite
`file:line`. Never another editor's, VM's, recorder's or macro system's
source. No golden, unit case, conformance file, script test, recorder
file, baseline or ledger edited; a disagreeing one is a STOP with its
diff. Every run of C yew and the port uses scratch `HOME`/`XDG_*` and an
explicit `YEW_RUNTIME_DIR`, inside a container under `taskset` and the
lane's core lock. The PTY goldens drive the real terminal through
`tools/goldens`; signal witnesses are pty bytes, never trap scripts. One
kind-id/match representation for every mutable callback (R-yw07-10).
G54's temporaries stay allocation-pending until wolf-lang#948 is
answered.

## Inputs (re-derive)

sagitta at the pin: the five sprint files with their line counts, the
three closeout audits, the C and the tests above, `Makefile:2189-2200`
(the test target's dispatch and choke checks), `:2270`, `:2372`, `:2401`
(fuzz and corpus), `:3851-3949` (the script suite), `:4028-4046` (round
trip), `:2996`, `:3037` (perf). The yew repo at yw08's merge: `src/fl/`
(flapi's headless half, origin's check half, data), `src/edit/`
(`option_cmdline`, `config`, `fldata`, `statusline` without the REC chip),
`src/ws/` (the hand codec), `tools/fl-headless/` and its gate
(`compare.py`, `tools/perf-fletch-baseline.txt`,
`tools/perf-fletch-misses.txt`), `tools/check-fletch-goldens`,
`tools/check-fletch-coverage`, `tools/run-fuzz-fl-vm`,
`notes/yw08-repl-errors-conformance-perf.md`, `docs/MAP.md`.

## Prediction (write before the first change)

To be written by the lane at launch: the PTY cases green by name (s35 3,
s37 1, s38 6); the script suite green by name; the round-trip harness's
report equal to C's; `fuzz_flapi` and `fuzz_record` equal to C's report
lines; each editor perf row's ratio predicted against the 2× bar;
M-YW7's artifacts green in CI.

## Done-when

Every deliverable with its tests. `tools/check-test` and `--native`
green, with the per-case checked run recorded. The PTY cases green by
name; the script suite, the round-trip law, the recorder corpus and the
two fuzzers in CI by name. The perf rows recorded beside C's from one
run, every MISS named with its issue. M-YW7 met. `docs/MAP.md` updated;
yw10's contract drafted; CI green; the PR open with the five sections,
shas as bullets, a test checklist and its `Footprint:` line; `bash
wolf/tools/lane-audit.sh yew yw09 <PR>` passing but for the final run's
green; hand back per RULES.md §6.
