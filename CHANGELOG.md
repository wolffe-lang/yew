# Changelog

All notable changes to this repository are recorded here, newest first.
The format follows Keep a Changelog; the port has no release yet.

## Unreleased

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
  generator over `ucd/16.0.0/` and sagitta's unit tests one for one.
- `src/yew.lu`: `--version` as C yew prints it; every other path
  hard-errors naming its sagitta sprint and port lane.
- `docs/MAP.md`: every sagitta directory and sprint file mapped to a
  port lane, and every wolf gap the port has met, with witnesses.
