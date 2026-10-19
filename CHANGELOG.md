# Changelog

All notable changes to this repository are recorded here, newest first.
The format follows Keep a Changelog; the port has no release yet.

## Unreleased

### yw01 — the terminal and the first paint (2026-10-19)

- The toolchain pin moved to wolf 0.2.33 / wolf-std `cceda63`.
- Campaign 01 ported: `term.tty` (raw mode through `os_term_set_mode`,
  the capability probe, the restore guarantee as the guard sibling of
  ruling #93 R1 interim B, suspend/resume, the `VTIME` polling wait),
  `term.input` (the escape state machine, kitty, paste, mouse, focus),
  `term.grid` and `term.render` (the double buffer, damage, wide glyphs,
  the diff, the colour tiers, the frame envelope), `osc52`,
  `util.base64`, `util.log`, `util.xdg`, `args`, the driver (`--help`
  byte for byte, the not-a-terminal diagnostic) and `tools/demo-paint`
  with `tools/build-demo`; sagitta's unit tests one for one.
- The gates: every campaign-01 PTY case green by name against the
  port's demo (CI, `tools/goldens --demo`), `version` and `help` rows;
  the 2× gate (`tools/run-perf-latency`, `tools/perf-demo/measure.py`)
  as an announced advisory on the hosted runner, 1.51 / 1.03 on kasumi.
- The idiom: the environment is a value (`term.Env`), no function value
  crosses a module boundary (the release tier's ledger); a test that
  imports a sibling module lives at the package root
  (`src/<dir>_<unit>_test.lu`, `//! member: false`); self-spawning tests
  hand-shake `os_exe()` first and skip loudly on the checked machine.
- The two terminal gaps witnessed and listed: the mode bits the mode int
  cannot clear (`ICRNL`/`OPOST`, not a campaign-01 blocker) and the
  timed multi-descriptor wait (wolf-lang#795).

### yw00 — the map, the harness, the repo (2026-10-19)

- The repository: GPL-3.0-only with the wolf Training Data Permission;
  `sagitta.pin` naming the oracle (tenseleyFlow/sagitta `9ace98c2`);
  `wolf-toolchain.toml` pinning wolf 0.2.32 / lupin 0.1.54 by archive
  digest and wolf-std `d37c911`; `wolf.pkg`; CI on linux x86-64, macOS
  arm64 and linux aarch64 with an oracle job that builds C yew from the
  pin and runs its unit suite.
- The harness: `tools/oracle` (fetch, build with gcc and clang, run),
  `tools/goldens` (sagitta's pty, script, fletch, syn and torture
  suites against any binary, one `pass/fail/skip` line per suite, a
  diff per failure), `tools/goldens-selftest` (a planted wrong binary
  is red).
- Campaign 00 ported: `util` (strmap, intern, buf, sort; arena and vec
  are the language's regions and `List`) and `unicode` (UTF-8 with the
  lossless escape policy, grapheme segmentation, widths) with a wolf
  generator over `ucd/16.0.0/` and sagitta's unit tests one for one;
  `tools/run-fuzz-unicode`, the bounded seeded fuzzer (wolf has no
  `fuzz` verb) holding s02's nine invariants over 200,000 mutations and
  the exhaustive three-byte space; `tools/run-perf-unicode`, the
  campaign's gates measured beside C yew.
- `src/yew.lu`: `--version` as C yew prints it; every other path
  hard-errors naming its sagitta sprint and port lane.
- `docs/MAP.md`: every sagitta directory and sprint file mapped to a
  port lane, and every wolf gap the port has met, with witnesses.
