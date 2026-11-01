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
