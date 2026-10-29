# yw09b — runtime skew and table Up

_Materialised from the body of yew#97 at the merge (`254baa80`)._


Addresses #92. Do not merge before the detached final-head gauntlet and CI are green.

## Forbidden

- No C golden, test, runtime asset or pin changed. The two new expected snapshots belong to the port; the harness never updates a golden.
- Down is unchanged. No issue filed/closed, label, tag or release; no planning-repo or `~/.claude` edit; no attribution trailers.
- Runtime/config/state fixtures use owned HOME/XDG directories. The install-prefix witness mounts an owned fixture read-only inside a container, never over the host install.
- Host mistake, disclosed: my first Mac helper incorrectly created a regular file at the shared directory-lock path using `open`/`flock`. The coordinator removed it. I read the existing `heavy.sh` protocol, replaced it with `mkdir` plus pid/lane files and directory cleanup, and reran the final-head Mac row under that protocol. The corrected run acquired and released the directory lock and enforced the 8 GiB gate inside it.

## Inputs, verified

- Base `3133476907f1e59e4ec32c0b2c0d4180cc925a08`, branch `yw09b`, asserted before the first commit.
- Unchanged `sagitta.pin`: `9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a`; unchanged pinned toolchain. C references: `runtime_asset.c:253-349`, `flconf.c:490-503`, `bind.c:647-715`, `cmdline.c:2095-2146`, and `tests/pty/registry.c:4034-4051`.
- Contract, RULES, yew guidance/map, sagitta decisions and architecture, yw09's note and issue #92 read. README read and refreshed in the README-only commit.

## Prediction

`notes/yw09b-evidence/prediction.txt` preceded implementation. The untouched port reproduced the lockup: `runtime_locked_mode: exited=False motion_and_insert=False`.

C's measured user and trusted-workspace policy is preserved: status 3; message `config runtime error: PATH`; built-in `L X: ed.nop` remains; the failed source's Y before the raise and Z after it are both absent. The trace names `unknown command 'ed.theme.pick'` at `init.fl:2:5`. Statements stop at the raise. Verbatim measurement: `notes/yw09b-evidence/c-measurement.txt`.

- **R-yw09b-1 A, implemented:** C's readable-prefix root order stays, but a shared prefix is admitted only when init bytes equal the embedded init. Skew warns once and selects embedded assets, not cwd assets. Explicit `YEW_RUNTIME_DIR` stays authoritative.
- **Built-in bind exception required by item 3:** a refused bind is reported and skipped at its native boundary; prior and subsequent built-in rows survive. It still reports CFG_RUN, not a false successful load. User/workspace raises still tear down only their own registrations.
- **Ruling #135:** entered Up moves above or wraps to the true last reachable row. Tab filters with budget 0; generator arrivals refilter/install their rows before navigation uses the updated `n_items`. Visible page height is not the boundary. Unentered Up remains history. Tab/Up/Down still blurs with the last candidate kept; **R-yw09b-2 recommends leaving Down unchanged unless separately ruled**.
- The ported top-row unit expectation is explicitly renamed for the ruling. The stale-install completion fixture now uses a matching init, preserving its missing-completions premise; skew has separate cases. Neither edits a C test.

## Evidence index

- `f8539ef`: runtime identity, source diagnostics, built-in row recovery and measured user/workspace policy tests.
- `bac67f8`: focused Up wrap; dead top-to-history helpers removed; Down untouched.
- `48a3695`: named, digest-pinned divergence routing, owned snapshot and six rejection/routing controls.
- `c697255`: four individually checked runtime cases plus the one-past-end sentinel.
- `eeba09f`: mandatory runtime PTY/harness CI gates and warning-pin check.
- `d5d7858`, `64e9f2d`: README-only refresh and map.
- `b1b5c44`: one byte-view traversal for identity comparison.
- `20bff45`, `9e467f8`: retain the runner's core limit and name primary PTY failures before secondary quit checks.
- `a75f8ca`: R-yw09b-3 A applies ruling #135 to the second entered-table Up case; only its owned snapshot and digest-list entry are added.
- `254baa8`: `src/edit_prompt_keys_test.lu`'s `table_scene` (behind `prompt_keys_table_rows_on_the_arrows` and `…_on_ctrl_p_and_ctrl_n`) asserts ruling #135: Up on row 0 of the entered table stays in it and wraps to the last row. The history assertions are kept unchanged, now reached from an unentered table.

The two admitted PTY divergences are both under ruling #135:

```
s57_30_table_top_to_history  ruling #135  tests/divergences/s57_30_table_top_to_history.golden
C sha256: 221552412e70f97c31e1f6ae0a3665a897a9d7ed64f985f2d6e5e6aa63e04c0e
s57_17_pager_arrow_up  ruling #135  tests/divergences/s57_17_pager_arrow_up.golden
C sha256: b66374be01e0cbfa760bc2db891139ddc20ab51a6f15767e72528a34934afbfb
```

The first snapshot selects `registers.ring_bytes_max`, **48/48**; the second selects `git.file.rename`, **12/12**. Both are the true last row of an entered table. The harness prints `DIVERGES (ruling #135)` with each case's name; a changed C digest is fatal. No original golden was written.

The first gauntlet at `9e467f8` correctly STOPped on the previously unlisted `s57_17_pager_arrow_up`. C's `registry.c:2981–3002` explicitly says the second Tab enters row 0, then Up leaves for history with no highlight: exactly the old behavior #135 changes. A paired run was C=0/port=1. R-yw09b-3 A authorized this second named divergence, not a new product rule. The complete PTY step was then rerun at `a75f8ca`: **300/300 green**, both divergences named, both C digests unchanged. Evidence: `/home/mfwolffe/lanes/yw09b/pty-a75f8ca.log` and `/home/mfwolffe/lanes/yw09b/pty-a75f8ca-logs/`.

### Ruling #135: the unit test, and the misreported native step

Ruling #135 brings two named PTY divergences from C. Both are listed in `tools/goldens-divergences.txt`, and neither C golden was edited:
- `s57_30_table_top_to_history`: C sha256 `221552412e70f97c31e1f6ae0a3665a897a9d7ed64f985f2d6e5e6aa63e04c0e`, port snapshot `tests/divergences/s57_30_table_top_to_history.golden`.
- `s57_17_pager_arrow_up` (R-yw09b-3 A): C sha256 `b66374be01e0cbfa760bc2db891139ddc20ab51a6f15767e72528a34934afbfb`, port snapshot `tests/divergences/s57_17_pager_arrow_up.golden`.

**The unit test (`254baa8`).** CI run 40786975226 at `9e467f8` failed shard 5/6 at `src/edit_prompt_keys_test.lu:1281`, `assert(!in_table(ed), "out")`, the assertion for pre-#135 behaviour after Up on row 0 of an entered table. The three plant runs failed the same way. The test now asserts the ruled behaviour at that point: `in_table`, `sel == last`, and the shown text is the last row. It then dismisses the table with Ctrl-G, reopens the prompt with the same typed text (an unentered table) and presses Up. From there the old assertions are unchanged: the table is out and closed, the walk's term is the typed text, `file.zzz` comes back from history, Down restores the typed text, and the page keys work. The diff only adds lines; no assertion was removed or changed. A first version (`634ee9e`, never pushed) left out the Ctrl-G and trapped at the prompt helper's `prompt: from L` (`:131:5`). `254baa8` run alone, natively, on kasumi CPUs 8–11 under the cores lock: build exit 0, `edit_prompt_keys_test: 56 cases run`, exit 0, no SKIP (`/home/mfwolffe/lanes/yw09b/prompt-alone-254baa8-job.log`, `prompt-254baa8.log`).

**The "202 native files" was a misreport.** In the `9e467f8` gauntlet, `native-all.exit` was **1**, with `FAILED src/edit_prompt_keys_test.lu exit 134` in `gauntlet-9e467f8-logs/half0.log`. The wrapper's `step()` recorded that exit and carried on to the next step. `native_half` also counted a failed file as "run", so the closing `native files: 202` line read as a pass. That run's final exit 1 came from the later PTY STOP, not from the native step. **The fix** is in the lane wrapper `/home/mfwolffe/lanes/yw09b/gauntlet-gates.sh` (sha256 `85514f70ed81f47ac1a9bd74db267902d90ebf657b16364db10c61ed2b57eccb`; the old one is kept as `gauntlet-gates-pre-failfast.sh`, `96358dbf9cf43d52f7796b98c3e8d0adfd71f5f614a697c011cc51661c6e6aed`). Every step prints one `COUNTS <step> pass=N fail=M` line, then `END <step> exit=N`. The native step counts `pass` and `fail` per file and is green only when `pass` equals the number of files. The first nonzero step, or a `fail>0` beside exit 0, prints `GAUNTLET RED at <step>` and ends the gauntlet with that code. A replay against stubs (four passing files and one trapping file) shows `COUNTS native-all files=5 pass=4 fail=1`, `END native-all exit=1`, and no later step. The wrapper lives outside yew's tree; nothing of it is committed here.

Against implementation tree `9e467f8`, all three deliberate-break branches differ only in their named fault. Local container witnesses are red by name; CI was read once without waiting:

| Branch / draft PR | Row | Local evidence | CI run |
|---|---|---|---|
| `yw09b-plant-prefix`, #94 | `runtime_prefix_skew: no warning` after executing the foreign prefix | `/home/mfwolffe/lanes/yw09b/plant-prefix-red.log` | 40783568169 |
| `yw09b-plant-locked`, #95 | `runtime_locked_mode: quit binding did not answer`, exited=False/motion=False | `/home/mfwolffe/lanes/yw09b/plant-locked-red.log` | 40783690138 |
| `yw09b-plant-up`, #96 | `s57_30_table_top_to_history: golden mismatch` against the ruled snapshot | `/home/mfwolffe/lanes/yw09b/plant-up-red.log` | 40783777551 |

CI plant results are pending, not claimed red yet. No plant is to merge or be closed by this lane.

## Done-when

- [x] Item 1: C measured and original lock reproduced before implementation.
- [x] Items 2–4: identity/override, built-in recovery, source diagnostics and C user/workspace policy; four focused native suites green; four checked cases plus sentinel exit 0.
- [x] Items 5–6: entered Down/Up returns first, Up wraps across pages, Down-at-bottom remains blur, and unentered Up is history; complete PTY step **300/300 green at a75f8ca**, with both #135 cases named; the unit test updated to #135 (`254baa8`), 56 cases exit 0 natively on kasumi 8–11.
- [x] Runtime-implementation head `9e467f8` Linux preflight: fmt, CI shape controls, six harness controls, native build, explicit-runtime PTY and prefix/warn-once-on-reload PTY green. Log `/home/mfwolffe/lanes/yw09b/preflight.log`. The new commit changes only the second snapshot and its list entry.
- [x] Runtime-implementation head `9e467f8` macOS row green under the correct mkdir lock and 8 GiB gate (21,972,484,096 bytes available). Log `/Users/mfwolffe/lanes/yw09b/mac-close.log`.
- [x] Three named local planted reds; each authorized draft PR is open, without labels.
- [x] Gauntlet `254baa8` (`/home/mfwolffe/lanes/yw09b/gauntlet-254baa8.log`) passed fmt, harness, registry, oracle, native-all **202/202**, checked-lane, tools-build **24/24** and release. Then it went red at `runtime-explicit` (06:07:00Z): `motion, Insert and save did not answer`, and the file came out as `first\nsecond\nproof`. **Cause: the fixture root, not the binary.** `runtime-pty.py` keeps yew's workspace state under `<root>/state`, and the wrapper passed the same root (`gauntlet-pty`) that the `9e467f8` run had created fresh. yew restored that run's cursor to line 2, so Down landed on line 3. Same release binary (sha256 `c2cac456…a9f4`), on kasumi 8–11 under the cores lock (`/home/mfwolffe/lanes/yw09b/runtime-explicit-reruns.log`, `runtime-explicit-state-pair.log`): the gauntlet's exact command with its own root went red 5/5, always the same file; a fresh root went green 5/5; the red run's root with only `state/` removed went green; and in the gauntlet's own root, with `state/` cleared, the same command went green once and then red once (restored cursor `pos: 11`). Not flaky. CI is unaffected, since it uses fresh `runner.temp` roots. The red root is kept as `gauntlet-pty-red-254baa8/`.
- [ ] **Resume from `runtime-explicit` at the same head**, under the lane wrapper. The wrapper now gives this step a fresh root per gauntlet (`$logs/runtime-pty-root`); the yew script and its assertions are unchanged. Launched 06:12:44Z: worker PID 1722402 (`/home/mfwolffe/lanes/yw09b/gauntlet-254baa8-resume.pid`), log `/home/mfwolffe/lanes/yw09b/gauntlet-254baa8-resume.log` (it opens with the earlier steps' END lines copied from `gauntlet-254baa8.log`), exit marker `/home/mfwolffe/lanes/yw09b/gauntlet-254baa8-resume.exit`, per-step logs `gauntlet-254baa8-resume-logs/`. `runtime-explicit` was green at 06:12:47Z. Recommended, not done: `runtime-pty.py` should clear its root's state, cache, data, home and config before each run, so a rerun in the same root passes too. That would be a notes-only commit and waits on the orchestrator's word. Earlier runs: `a75f8ca` (PID 1276615) was stopped at 02:56:48Z during native-all, exit 143, after the CI red; `9e467f8` red log `/home/mfwolffe/lanes/yw09b/gauntlet-9e467f8.log`, failed-case fixtures in `/home/mfwolffe/lanes/yw09b/pager-failure-states/`.
- [ ] CI plant rows observed red in their runs; final PR CI green. The PR run at `254baa8` is **40814629206**, read once when it was pending. The lane does not wait on CI or label.
- [ ] Lane audit at the final head; its observed last line is returned at hand-back.

Closure recommendation after green: yew#92. No other issue to file or close is claimed.



