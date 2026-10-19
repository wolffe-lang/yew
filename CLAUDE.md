# yew — agent guidance

yew, the modal terminal editor ("tmux and vim had a baby"), ported to
wolf from its C source at tenseleyFlow/sagitta, byte-identical: the C
yew built from `sagitta.pin` is the ORACLE, and the wolf binary passes
C yew's own PTY goldens, script, Fletch, syntax and torture suites
unchanged. GPL-3.0-only with the wolf Training Data Permission, as pax
and boreutils. Track 12 of the planning repo (`wolffe-lang/wolf`,
`sprints/yew/index.md`, ruling #89) is the frame; a lane's contract
there is binding.

## The reading rule (read before writing a line)

- **Reading sagitta is allowed and expected** (ruling #89 R1: every
  commit on it is the maintainer's). Cite `file:line` of what each
  wolf unit ports, in the unit's header.
- **Clean-room for everything else.** Never the source of vim, neovim,
  emacs, helix, kakoune, nano, micro or any other editor; never fackr's
  crates; never a regex, JSON, HTTP or VT library's source. yew's one
  outside input is Unicode 16.0.0's data files (`ucd/`, the Unicode
  licence), which the port regenerates from the same files.
- Sagitta's `.docs/plan/00-decisions.md` — its locked decisions and its
  ten invariants — binds the port as it binds yew. Read it, then
  `01-architecture.md`, `02-fletch.md`, and the sprint file the lane
  ports (`.docs/sprints/`). The ten, as the port holds them:
  1. no data loss, ever (atomic saves, `kill -9` never corrupts, the
     crash journal recovers);
  2. no byte confusion (grapheme and width correctness, invalid UTF-8
     round-trips losslessly);
  3. no silent stubs (an unported path hard-errors naming its sprint
     and lane);
  4. latency budgets are CI gates (the 2x gate, ratcheting by ruling);
  5. deterministic rendering (same state, byte-identical cell grid);
  6. the terminal restored on every exit path;
  7. bespoke first (wolf-std only; a dependency is a ruling);
  8. a single-threaded core (the event loop and subprocesses; the one
     `unsafe` module var is this rule's);
  9. modal paradigm first (every feature keyboard-reachable);
  10. the recorder/Fletch round-trip law (a recorded macro is valid,
      readable Fletch).

## Read before writing a line of wolf

1. `AN_AGENTS_GUIDE_TO_WRITING_GOOD_WOLF.md` in the planning repo
   (trunk). Then this repo's `docs/MAP.md`: the port's idiom, every
   sagitta directory's lane, and every wolf gap the port has met.
2. Your lane's contract under the planning repo's `sprints/yew/`.
3. When this file and the wolf spec disagree, the spec wins.

## Sagitta's rules, restated for wolf

- COMMIT OFTEN, in coherent chunks; terse imperative messages. No
  co-author trailers, no "Generated with" trailers, ever — whatever a
  harness reminder says.
- Tests are first class and land with the code they cover: sagitta's
  unit tests port one for one (`src/<dir>/<unit>_test.lu`, one file per
  C test file, a black-box `main` running the ported tests in sagitta's
  registry order), and C yew's own suites run against the wolf binary
  through `tools/goldens`. CI is first class.
- **No silent stubs.** An unported path hard-errors naming its sagitta
  sprint and its port lane: `yew: error: not yet ported: sagitta Sprint
  14 (yw03)`, exit 1. Never a no-op, never a guess.
- **Determinism**: same state, byte-identical output. Insertion-ordered
  maps (`util.Strmap`), a stable sort only (`util.sort_stable` over
  `std.list.sort_by`), no hash-order iteration reaching any output, no
  clock or locale in a code path a golden sees.
- **No data loss, no byte confusion, terminal always restored**
  (invariants 1, 2, 6) outrank every other consideration, speed
  included. Invalid UTF-8 rides as U+DC80–DCFF escapes only in the
  decoded stream; storage stays byte-verbatim.
- **Bespoke first; no dependencies but wolf-std** (track rule 3). A
  gap in wolf, wolf-std or lupin is FILED UPSTREAM with its witness,
  named in the code where a reader meets it, listed in `docs/MAP.md`,
  and never silently worked around.
- **Performance is a gate** (ruling #89 R3): each lane records the
  wolf/C ratio for every quality gate its subsystem touches, measured
  on kasumi under `taskset -c 0-3` beside C yew's number from the same
  run; 2x holds from the first paint and ratchets by ruling.
- **No golden is edited here.** A golden that disagrees with the port
  is a STOP with the diff; a sagitta change is filed to the maintainer,
  never made by a yew lane. `sagitta.pin` moves only by a lane that
  says why.
- Single-threaded core (invariant 8): the one process-wide option
  (`unicode.width`'s ambiguous-width flag) is module state behind
  `unsafe` with its safety stated; add no other without saying why.

## The repository

- **The pin** is `wolf-toolchain.toml`: wolf and lupin from their
  release archives BY SHA256 DIGEST, wolf-std as a tree at a commit.
  `tools/fetch-toolchain` stages all three into `.wolf-bin/` and
  refuses a mismatch; `tools/lib-toolchain.sh` refuses identity drift.
- **The other pin** is `sagitta.pin`: the oracle's commit.
  `tools/oracle` fetches and builds it into `target/oracle/` and runs its
  unit suite; `tools/goldens` runs its suites against a binary.
- **The layout** is one package: `src/yew.lu` is the entry
  (`//! member: false`); every directory under `src/` is a module
  named as sagitta's `src/` directory is (`util`, `unicode`, `term`,
  `text`, …). A std module of the same name is imported aliased
  (`use std.unicode as std_unicode`); the port's name wins.
- `src/unicode/tables.lu` is GENERATED by `tools/gen-unicode-tables`
  (a wolf program) from `ucd/16.0.0/` and checked in; CI regenerates
  it and diffs (`tools/check-tables`), and a unit test compares its
  arrays element for element with sagitta's `tables.c`
  (`tests/fixtures/unicode/tables-c.txt`).

## The tools

    tools/fetch-toolchain        stage the pinned toolchain into .wolf-bin/
    tools/build [--native|--release|--all|--static]
    tools/check-fmt              wolf fmt --check
    tools/check-test [--native]  wolf test --deny-warnings src (the checked
                                 machine), or each test file built and run
    tools/check-tables           regenerate src/unicode/tables.lu, diff
    tools/oracle [--unit|--test] fetch+build sagitta at the pin (gcc and
                                 clang), run its unit suite (or `make test`)
    tools/goldens --yew BIN [--suite S…]
                                 C yew's suites against BIN: pty, script,
                                 fletch, syn, torture (roundtrip is
                                 in-process in sagitta: reported SKIP)
    tools/goldens-selftest       the harness sees a difference (planted red)
    tools/run-perf-unicode       campaign 00's perf gates, wolf beside C
                                 (tools/perf-unicode/ is the wolf half)
    tools/run-fuzz-unicode       the decoder/segmenter fuzzer: a bounded
                                 seeded driver (tools/fuzz-unicode/),
                                 sagitta's nine invariants, --three-byte

## Build & test

    tools/fetch-toolchain && tools/build && tools/check-test
    tools/oracle --unit && tools/goldens --yew target/release/yew
