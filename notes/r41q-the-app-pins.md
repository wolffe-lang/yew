# r41q — yew to wolf 0.2.36 / lupin 0.1.58

_yew's part of r41q (the apps, the games and the docs to the published pair). The pin only, and what
0.2.36's documented changes force; yw13 rebases onto this once it merges._

## Prediction

Written before the first change (2026-11-01, base trunk `f1b68316`).

- `wolf-toolchain.toml` moves to wolf **0.2.36** (`v0.2.36`, tag object `86d61559` peeling to `5adf3d91`),
  lupin **0.1.58** (`v0.1.58` at `6240efe5`, spec pin `a5378e3`) and the std the 0.2.36 archive bundles,
  wolf-std **`78b9d3cb`**, the six archive digests read twice from the release API (r41q's two passes,
  identical, equal to r41's record) and held to them by script. `tools/fetch-toolchain` accepts them and
  `tools/lib-toolchain.sh` accepts `wolf 0.2.36 (wolfgang, pin 5adf3d9)`, `lupin 0.1.58 (wolf-interp,
  reference interpreter at pin a5378e3)`.
- **Nothing in the source moves.** 0.2.36's documented changes that could reach yew do not: no `.lu` file
  declares a new prelude name (`VaList`, the four `va_*`, `env_arg0`, `env_args_bytes`), so the builds
  under `--deny-warnings` see no W0304; every script yew's tests spawn starts with `#!` (s260's spawn no
  longer runs a `#!`-less file under `/bin/sh`); and wolf-lang#948's E1010 for `fl/gc.lu:123-124`
  (yew#98) lands at `a246580b`, 41 commits after the 0.2.36 tag, so it is not in this pin.
- The linux x86-64 `port` job stays green: fmt, the scratch homes, the golden divergence controls, both
  tiers built with warnings denied, `--version` as C yew's two lines, the tables, the walk listings, the
  283 Fletch cases, the command dispatch and the Fletch choke point. On linux aarch64 both tiers are still
  refused by name (wolf-lang#614 open; 0.2.36 adds no tier there).
- The `unit`, `checked-cases`, `fuzz` and `oracle` jobs stay green as on yw09b's last PR run
  (40814629206). One exception may show, not this change's: `fuzz (macOS arm64, against-c-2)` went red on
  trunk's push run 40842204620 at `f1b68316` (C's own `fuzz_gitignore` driver over its 329 ms budget,
  then two knock-on rows), a notes-only commit after the green `254baa80`, so it is a timing flake.
- The perf rows (advisories on the hosted runner) may improve at start-up: 0.2.36 carries s265's
  start-up fix (wolf-lang#918). Re-measuring yew#55's rows by R12 is yew's own lane's, listed, not done.

## Forbidden

No merge, label, tag, release, issue filed or closed; no attribution trailer. No build on the Mac; local
runs on hasu (one block per run, both its lock names held); kasumi not touched. No sagitta or other
implementation source read for this pass. No source, test, tool, workflow or golden of yew changed:
`wolf-toolchain.toml`, the README's Status sentence, one CHANGELOG entry and this note. The port's
adoptions of 0.2.36 (start-up re-measure, the byte argv) are yew's own lanes and are not here.

## Inputs verified

- Base: yew trunk `f1b68316`, as the contract read it on 2026-10-31 and again before branching; yw13 is
  paused on it and rebases onto this once.
- The pair: wolf `v0.2.36` is tag object `86d61559` peeling to `5adf3d91`; lupin `v0.1.58` is tag object
  `dc4689e3` peeling to `6240efe5`; the archive's `std/STD-REV` is `78b9d3cbc41d51db44d18c40b6694403644d1c83`.
  The six digests: the release API's asset `digest` fields in two passes (00:11:56Z and 00:11:57Z),
  identical and equal row for row to r41's eleven-row record; the archives downloaded and hashed twice
  (linux x86-64 on hasu, the other four on nomad, download and hash only). `wolf-toolchain.toml` is held
  to both passes by script: six digests, both versions, both revs, both `version_line`s and the std rev
  green (the gauntlet's `prove-pin`).
- 0.2.36's documented changes, read against yew: no `.lu` file declares `VaList`, a `va_*`, `env_arg0` or
  `env_args_bytes`; the scripts the tests spawn all start with `#!`; `fl/gc.lu:123-124` (yew#98) meets
  wolf-lang#948's E1010 only past `a246580b`, which the compare API puts 41 commits after `5adf3d91`
  (`behind_by=41`). wolf-lang#614 (linux aarch64 builds no tier) is open and 0.2.36 names no aarch64
  tier, so the aarch64 `port` leg's by-name refusal should hold.
- What waits for this pin, from the open issues: yew#55 (start-up rows; wolf-lang#918's fix is in this
  pin as s265, re-measuring by R12 is yew's next lane's), yew#98 (not this pin), yew#17/#23/#27 (0.2.35-era
  retirements, untouched here), yew#78 (a nondeterministic checked file at 0.2.35, untouched). yew#49
  (nightly red): trunk's last push run 40842204620 at `f1b68316` is red only in `fuzz (macOS arm64,
  against-c-2)`, C's own `fuzz_gitignore` driver over its 329 ms budget and two knock-on rows, after a
  green run at `254baa80` one notes-only commit earlier; not this change's, and not re-run by this lane.
- README read: the Status sentence names the pinned pair and moves (a README-only commit); "The 0.2.35
  adoption …" is that lane's history and stays; it states no test counts that a pin moves.
- **R-r41q-6, the local gauntlet's scope:** (A) yew's linux x86-64 `port` job step for step in the
  container, the `unit`, `checked-cases`, `fuzz` and `oracle` jobs left to the PR's own run; (B) the
  whole suite locally (the six unit shards alone are about 6.5 runner-hours). Recommend and implemented
  (A): the pin moves no source, and CI is this repository's build host.

## Evidence index

- `905f7d8` the prediction, before any change.
- `6c859e8` `wolf-toolchain.toml`: the fifth pin and its paragraph; the `[lupin]` and `[std]` comments.
- `52b1768` README only: the pinned pair in the Status sentence.
- `9bedbd6` CHANGELOG: r41q's entry.
- The gauntlet at the final head, on hasu (`/home/mfwolffe/lanes/r41q/bin/gauntlet-yew.sh <sha>` under
  `bin/block`, its log under `/home/mfwolffe/lanes/r41q/logs/`): the head asserted, the pin proved
  against both API passes, `tools/fetch-toolchain`, then in the container on the block's CPUs:
  `tools/check-fmt`, `tools/check-test-env`, `tools/goldens-pty-test.py`, `tools/build --all`, the
  `--version` lines, `tools/check-tables`, `tools/check-walk-listings`, the 283 Fletch cases, the command
  dispatch and the Fletch choke point (each with its selftest). Every step prints `END <step> exit=N`;
  the wrapper stops at the first nonzero one. The END lines are in the PR body.

## Done-when

The PR is open at its final head with its CI run green there (`port`, `unit`, `checked-cases`, `fuzz`,
`oracle`, `perf` on the plan's legs), `Footprint: cross-cutting` (a pin), and the audit run once. yw13
rebases onto the merge. Nothing to close or file; the start-up re-measure (yew#55) and the byte-argv
adoption are listed for yew's own lanes.
