# yw00 — the map, the harness, the repo

**Fable 5.1, crawl 54, 2026-10-19.** Contract: planning repo
`sprints/yew/00-the-map/yw00-the-map.md` at `163b9ae`. The first lane
of track 12 (ruling #89). What landed: the repository, its pins, its
CI, the oracle harness, campaign 00 ported with sagitta's unit tests one
for one, `docs/MAP.md`, yw01's contract (`notes/contracts/`).

## Forbidden

The track's seven standing rules and s243's rules for every lane, held:
sagitta read and cited (`file:line` in every unit's header), no other
editor's source, no regex/JSON/HTTP/VT library's source; no dependency
but wolf-std; no golden edited, no sagitta change (the clang-23 refusal
and the `tutor_ch06` finding are reported, not patched); toolchain from
the release archives by digest read twice (§2); no attribution trailer;
no merge, tag, issue filed or closed; builds and tests on kasumi only;
`setsid` with a pid file for every long job, nothing killed by name;
no package installed (valgrind is absent on kasumi and stayed absent);
`~/.claude` untouched; the maintainer's sagitta checkout read once
(`CLAUDE.md`, untracked there) and never built or written.

## Inputs, verified

- sagitta `9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a` = trunk head on
  2026-10-19 ("Fetch history for Valgrind audit"), `git log
  9ace98c2..HEAD` empty: the pin is the only candidate, and the commit
  the track index measured at. Cloned to `~/lanes/yw00/sagitta` (nomad-1,
  read) and `~/lanes/yw00/sagitta` (kasumi, built); `tools/oracle`
  fetches its own copy into `target/oracle/`.
- wolf 0.2.32 `v0.2.32` tag → `72de141f624662fdff522e8beba459fab7c5cf66`
  (`gh api .../git/tags/d21c4b28`), lupin 0.1.54 `v0.1.54` →
  `0e536e8fb4518eaa798ac426901ab81275db5c9f`; the six archive digests
  read twice from the release API (identical both passes, identical to
  pelt's seventh pin), the linux x86-64 pair hashed after download
  (`notes/yw00-evidence/digests.txt`); wolf-std `d37c911` is what the
  archive bundles (`std/STD-REV`) and is on wolf-std trunk.
- `AN_AGENTS_GUIDE_TO_WRITING_GOOD_WOLF.md` (current at 0.2.14; every
  idiom in §4 was re-measured at 0.2.32), the spec's `[os.term.*]`,
  `[os.signal.model]`, `[os.signal.hub]`, `[os.signal.checked]`,
  `[mem.static.*]`, `[pkg.manifest]`, `spec/prelude.json`; wolf-std's
  `std.unicode` (ASCII predicates only), `std.term`, `std.signal`,
  `std.process`, `std.fs`, `std.sort`/`std.list.sort_by` (a stable
  bottom-up merge), `std.time` (milliseconds).
- pelt's and boreutils' `wolf-toolchain.toml`, `tools/fetch-toolchain`,
  `lib-toolchain.sh`, `build`, `check-*`, CI; pax's `tools/mkpelt`,
  `LICENSE`, `LICENSE-TRAINING-DATA`.
- Not found as named: sagitta's `CLAUDE.md` is untracked (read from
  the maintainer's checkout); the spec has no `[os.signal.gaps.note]`.

## Prediction

Written before the first wolf line (2026-10-19 13:30): campaign 00
ports without a compiler gap — regions, `List`, `Map` and `str`
constants cover arena/vec/strmap/intern/buf and the three tables —
and the generated trie comes out identical to sagitta's on the first
run if the parse order is kept; the grapheme conformance run passes
1093/1093 because the algorithm is a line-for-line port; the wolf/C
ratio on the unicode scans lands between 1.5x and 3x on the release
tier (bounds checks and `.bytes()` indirection); the stub is red on
every golden suite and green on `--version`; the oracle is green on
kasumi under gcc. Hits: the ratios (1.47–1.80 pinned, 1.31–1.45
unpinned, §3), the stub's rows, the oracle under gcc. Misses: the trie
was identical on the SECOND run (the first had `\n`-in-`{}` holes and
`~`, not algorithm errors); `wolf test`'s discovery surprised (G10);
clang 23 refused the oracle; one PTY case of the oracle's own depends
on the tree's path (§2).

## Evidence index

All under `notes/yw00-evidence/` unless a path says otherwise; kasumi
unless said.

1. `digests.txt` — the archives' sha256 after download, `wolf
   --version`, the bundled `STD-REV`, the staged `STAMP`.
2. `oracle/oracle-tool.log` — `tools/oracle --cc gcc --unit`: build
   22 s, `unit: 3047 tests, 73852037 assertions, 0 failures, 2 skipped`.
   `oracle/make-unit-pty.log` — sagitta's own `make test-unit` (112.8 s)
   and `make test-pty` (758 s, every `pty: <name>: ok`, exit 0) in the
   lane's first clone; `oracle/make-script-fletch-syn-perf-torture.log`
   — `test-script` 93 tests / 951 assertions / 0 failures / 1 skipped,
   `test-fletch` green, `test-syn-assets` 432 ok, `perf-unicode`, and
   `make torture` red at `torture-git-hunk` (`git_hunk_kill9: fixture
   setup failed`) after its batch, live and tty-restore lanes passed
   (32 signal/moment trials). `oracle/clang23-refusal.txt` — clang
   23.1.1: `tests/unit/harness.c:454: error: variable 'leak_every' set
   but not used [-Werror,-Wunused-but-set-global]`.
3. `goldens/c-yew-all-suites.txt` — `tools/goldens --yew
   target/oracle/sagitta/build/yew`: version 1/0, pty 553 ok / 1 fail
   (`tutor_ch06`, §3), script 93/1 (`57_embedded_gate`, since excluded as
   the Makefile excludes it), fletch 39/0, syn ok, torture 3/0,
   roundtrip skip; 852 s. After the fix the suites other than pty are
   green; pty's one case is the finding below.
   `goldens/stub-and-selftest.txt` — the stub (`target/release/yew`):
   version 1/0, pty 0/5, script 0/94, fletch 1/38, syn 0/1, RED;
   `tools/goldens-selftest`: `ok — the harness is green on the oracle
   and red on both plants` (19 s).
4. `port/check-test-tables-fmt.txt` — `wolf test --deny-warnings src`:
   11 passed on the checked machine; `--native`: 11 ok, `graphemebreaktest:
   1093/1093 cases pass`; `check-tables`: the generated file and the
   arrays identical to sagitta's; `check-fmt` ok.
5. `perf-unicode.txt` — `tools/run-perf-unicode --taskset 0-3` and
   unpinned, C beside wolf (§3). `startup.txt` — `--version` over 100
   runs each.
6. `witness/run.txt` — the four witnesses' outputs (G1, G8, G10, G11 of
   `docs/MAP.md` §5).
7. `fuzz-unicode.txt` — `tools/run-fuzz-unicode`: seed 1 twice (one
   hash), seed 2, and `--three-byte`; every input held the nine
   invariants.
8. CI: the run ids are in the PR.

## Findings

### 1. The oracle on kasumi

gcc 16.2.1 builds and passes every suite the port is held to (index 2).
clang 23.1.1 refuses the tree under sagitta's `-Werror` on a warning
that did not exist in clang 18 (`-Wunused-but-set-global`,
`tests/unit/harness.c:454`): a sagitta issue for the maintainer (one
`(void)leak_every` or a `-Wno-` in the Makefile); CI's clang 18 and
Apple clang build it. `tools/oracle` takes `--cc` as given and reports
a refusal rather than adding flags.

### 2. Fourteen of sagitta's PTY cases depend on the checkout's path

Sagitta's PTY cases that start a helper or the tutor under the
per-case state directory — the twelve `ai_badge_*_streaming_*` cases
("could not start Sprint 50 badge mockai") and `tutor_ch06` ("tutor
task did not reach its state verdict") — fail when the tree sits at a
long path and pass at a short one, against C yew's own binary, through
sagitta's own `make test-pty` as much as through `tools/goldens`
(`notes/yw00-evidence/tutor_ch06.txt`, `goldens/c-yew-all-suites.txt`):
every case `ok` at `/home/mfwolffe/lanes/yw00/sagitta` (758 s) and
`tutor_ch06` `ok` at a `--depth 1` clone `/home/mfwolffe/lanes/yw00/s2`;
`tutor_ch06` alone red at `…/yew/.oracle/sagitta` (46 characters);
`tutor_ch06` and the twelve badge cases red at `…/yew/target/oracle/
sagitta` (51). The build directory's name, `TMPDIR`, a dot-directory
component and the clone's depth were each ruled out one at a time; the
badge cases tipping over between 46 and 51 characters says a limit on
a path built from the state directory is crossed (the helper is a TCP
server, so not `sun_path`; a `PATH_MAX`-sized buffer on the tutor or
mockai launch path is the suspect). Not the port's doing and not a
golden question: a finding for the maintainer with both paths.
`tools/oracle` keeps its tree under `target/oracle/`, where CI's
checkout is `/home/runner/work/yew/yew/target/oracle/sagitta` (48);
the oracle job runs the unit suite and the `startup_` goldens there,
which do not select these cases. A later lane that runs the whole PTY
suite in CI needs either the maintainer's fix or a shorter checkout
(`tools/oracle --tree <short path>` is a one-line addition when it is
needed).

### 3. The numbers (ruling #89 R3)

Measured on kasumi under `taskset -c 0-3`, release tier, C yew's own
`perf_unicode` beside the port's twin from the same run
(`notes/yw00-evidence/perf-unicode.txt`):

| gate (`s02` DoD 11, `budgets.txt`) | C yew | wolf | ratio |
|---|---|---|---|
| segment + width, 1 MiB ASCII | 3,333 us | 6,000 us | 1.80 (unpinned 1.45) |
| segment + width, 1 MiB CJK | 14,917 us | 22,000 us | 1.47 (unpinned 1.31) |
| segment + width, 1 MiB emoji (ZWJ families) | 8,646 us | 14,968 us | 1.73 (unpinned 1.38) |
| cold start, `--version`, 100 runs | 3,271 us | 2,739 us (release), 2,593 us (native) | 0.84 |

The ASCII scan's fast path is the same in both (a printable byte after
an Other is a boundary with no lookup) and still costs 1.8x pinned: the
per-byte `s[pos] as int` bounds-checked reads and the `gb_boundary`
call per byte are the whole loop there. CJK and emoji pay the trie
lookups and `cluster_width` per cluster, where the port's `.bytes()[i]`
digit decoding shows. No 2x gate is crossed; the 2x gate is a CI gate
from yw01, and the pinned ASCII row at 1.80 is the one to watch — the
first ratchet candidate is the ASCII fast path (one `.bytes()` view per
scan instead of an indexed `List[byte]` read per byte).

### 4. What the language taught (the probes, `notes/yw00-evidence/witness/`
and the kasumi probe directories)

Module state of a `List` is refused and a `str` constant is the table
(`[mem.static.3]`); `.bytes()[i]` inline is a 2 ns read while a bound
`.bytes()` copies (the t3 probe took the host to 60 GB before the OOM
killer ended it — the ssh session with it, twice; recorded here so
nobody repeats it); `~` is not syntax; `==` on a `List` is refused; a
`match` arm cannot assign; a getter on a `read` parameter copies
(E1002); `unsafe` wants `// # Safety:` above the block; a `{` in any
string literal opens a hole; `wolf test` runs `main` on the checked
machine first and natively only when it refuses (`test_cmd.rs:645`),
and discovers `test_*` in a package's first file only (G10); the clock
is milliseconds; a `mut` parameter inside a `region` is E1010 whatever
it holds (G18: the fuzzer's RNG became a returned scalar). Each is in
`docs/MAP.md` §1 and §5.

### 5. The checked machine as ASan/UBSan/valgrind

`wolf test` IS the checked run (every allocation modelled, every UB row
an E1401, a definite leak a fault): all 11 files `ok` there. The native
lane (`tools/check-test --native`) is the determinism twin. What it
cannot do: a C library's defects (none linked) and a budget past which
a test is `unsupported` (the 3 MiB arena allocation; trimmed to 64 KiB
with the reason in the test).

## Issues to file (listed, not filed)

- **sagitta** (the maintainer): clang 23 `-Wunused-but-set-global` at
  `tests/unit/harness.c:454` under `-Werror`; `tutor_ch06` depends on
  the tree's path or build directory name (§2, both paths given);
  `make torture`'s `torture-git-hunk` fixture setup fails on kasumi
  (git 2.x; the C sets its own identity, so the cause is elsewhere).
- **wolf-lang**: G1 the terminal restore on a trap (design; ruling R1);
  G2 a wait over N descriptors with a deadline (`os_signal_wait_fds`);
  G3 `fs_sync`/`fs_sync_dir` and an `O_EXCL` create; G4 `fs_realpath`;
  G8 `clock_ns`; G10 `wolf test` discovers `test_*` in `pkg.files[0]`
  only (witness `witness/test-discovery/`); G11 no bitwise not (`~`);
  G17 the native test harness (known).
- **wolf-std**: wrappers for G3/G4/G8 when they land; `std.time` at ns.
- **wolf-interp**: nothing (lupin runs none of the port's surface: the
  tests are native/checked; lupin has no `fs` on `/dev` and no signals
  — unchanged from pelt's finding).

## Rulings asked

`docs/MAP.md` §6: R1 the fatal-signal restore (recommend C, the
runtime restores on every exit it owns, with B — a supervisor — as
yw01's fallback); R2 the multi-descriptor wait (recommend A); R3 the
Fletch GC's shape (recommend A: an arena of tagged values with
indices); R4 the modules line (recommend A: byte-identical); R5 the
module-name collisions (recommend A: alias std).

## Done-when

- [x] repo `wolffe-lang/yew` private, licences, README, CLAUDE.md,
      `sagitta.pin`, `wolf-toolchain.toml`, `wolf.pkg`, CHANGELOG
- [x] CI: three hosts, the oracle job builds C yew and runs its unit
      suite; the port's jobs; linux aarch64 asserts the refusal
- [x] `tools/oracle`, `tools/goldens` (pty, script, fletch, syn,
      torture; roundtrip skip by name), `tools/goldens-selftest`
      green on the oracle and red on two plants; the stub red
      everywhere but `--version`
- [x] campaign 00: util and unicode ported, the wolf generator over
      `ucd/`, tables identical to sagitta's, the unit tests one for one
      (checked and native), 1093/1093 conformance
- [x] `docs/MAP.md`: every directory, every sprint file, every gap with
      witnesses, the rulings, yw02–yw16 paragraphs
- [x] yw01's contract (`notes/contracts/yw01-the-terminal.md`)
- [x] the wolf/C ratios recorded (§3)
- [ ] PR open with five sections, shas, checklist; CI green on three
      hosts; `lane-audit.sh yew yw00 <PR>` exit 0 (filled in the PR)
