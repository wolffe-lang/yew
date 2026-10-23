# Changelog

All notable changes to this repository are recorded here, newest first.
The format follows Keep a Changelog; the port has no release yet.

## Unreleased

### yw06 — workspace, finder and mouse (2026-10-23)

- yw05-tail first (PR #46); the pin kept at wolf 0.2.34 / lupin 0.1.55 /
  wolf-std `e036bec` (0.2.35 tagged after the pin commit: yw07's bump).
  The oracle tools run C yew with fresh scratch homes (yew#11,
  `tools/lib-test-env.sh`, `tools/check-test-env`) and a perf harness that
  does not compile is a hard step (yew#44).
- Workspace identity and the session state (s25): the workspace key, `:`
  history scoped by it, the frozen v1 schema over the hand codec
  (`ws.state_lit` and `fl_emit`/`fl_parse`, bytes throughout, R-yw06-1),
  restore, the commands, recovery and the debounced atomic save; the
  corpus 22/4/20, the C↔port differential byte-identical both ways;
  `fuzz_state` equal to C's driver at 100,000 cases × 4 seeds; G20's
  closure twin routed around by two local sorts until 0.2.35.
- The startup plan (s56.5 §1, §6): resume, files, `--workspace`, a
  directory launch, restore before the files.
- The finder (s26): the walk (an explicit stack, C's measured
  `.gitignore` disk quirks, R-yw06-10), the matcher, the incremental
  filter with its bounded top-k and sliced rescan, the one picker and
  its file, buffer, undo-branch and command instances, type-to-jump;
  `fuzz_gitignore` equal to C's; `perf_finder` within 1.35× C.
- The mouse (s27, s57.13–s57.15, s57.22): one router at the pin's state,
  the context menus and their rows, drag with its previews, the strip's
  scroll and drag-to-spawn; `fuzz_mouse` equal to C's at 400,000 events.
- `:!yew FILE` inside yew (s57.11); s57.12's goldens gated.
- The gates: the 81 reachable campaign-05 goldens by name, M-YW5's
  trials (`tools/run-trials`: twenty resume cycles, the restore after
  SIGKILL, SIGSEGV and a closed terminal, the state differential both
  ways), the checked machine one case at a time as a CI job
  (`tools/check-test-cases`), the walk's listings against C's
  (`tools/check-walk-listings`); the fuzzy fuzzer's staging fixed for
  `ws`'s new imports; yw07's contract drafted.

### yw05 — panes, tabs and groups, and the 0.2.34 bump (2026-10-22)

- The toolchain to wolf 0.2.34 / lupin 0.1.55 / wolf-std `e036bec`, every
  gap yw01–yw04 met adopted: one `os_signal_wait_fds` over the terminal,
  the jobs' descriptors and the signals (the `VTIME` interim, the drain,
  the fine wait and the deadline-first turn gone; the burst pair gated on
  macOS again); `RAW_CR | RAW_OUTPUT` in the raw mode (the LF-as-Enter
  interim gone); `os_term_restore_at_exit` registered and `ABORT`
  listened; `fs_sync`/`fs_sync_dir` at C's sites (every acceptance
  deleted); `fs_realpath`; the clipboard writer and reader forked as C's.
- yw04's job half over the wait: `job.c`'s table, the stream, the footers
  and badge, the region filter both ways (its stdin through a forked
  writer), `:r !`, the `*jobs*` table, the persistent session, the
  generator, `--help` and fish jobs. Campaign 04: 104 of 104 gated by name.
- Campaign 05's first half: the pane tree in cells (`edit.layout`, its
  ratio C's float bits through `util.f32`, the checked machine having no
  `f32`), the region registry in full, glyphs, `pane_cmds`, borders and
  dim-inactive, click-to-focus and the border drag; tabs in full with the
  strip engine, its overflow and s57.8's modern strip; tab groups
  (facsimile's model: membership on the tab, deferred tabs, groupnav, the
  New/Edit picker, from-dir as far as campaign 05 reaches); every startup
  file its own tab. The s22, s23, s24 and s57.8 goldens gated by name;
  `startup_multiple_files` recorded on the `:buffers` picker (s26, yw06).
- Allocation-free hot paths (R-yw03-7 A): the document rows, gutter,
  statusline, prompt row, overlay and strip controls drawn into storage
  the editor owns (`edit.drawbufs`), byte-identical: a `:` key keeps
  ~21 KB where it kept ~208 KB, a line move ~0.5 KB where it kept ~74-121 KB.
- Fuzzers against C's own drivers (`tools/fuzz-{panes,tabs,groups}`), the
  2× tools `tools/run-perf-panes-tabs` (two panes, fifty buffers, the tab
  switch) and `tools/run-perf-jobstream`; yw06's contract drafted.

### yw04 — execute and search (2026-10-21)

- Campaign 04 ported at wolf 0.2.33: the full `:` prompt replacing
  yw03's narrow one (`edit.cmdline` with its history, grammar and ranges,
  completion engine, ranked menu, ghost, hint, pager, selection and the
  readline set; `edit.cmdparse`, `edit.cmdhist`, `edit.cmdcomp`,
  `edit.menu`, `edit.region`, `edit.cmdedit`, `edit.readline_cmds`,
  `ws.fuzzy`); the regex engine (`search`: Thompson NFA, Pike VM, lazy DFA,
  the literal prefilter, pack; `unicode.category` from the generator's
  `--category`); search, replace and the jump lists (`search.replace`,
  `edit.overlay`, `edit.searchui`, `edit.search_cmds`, `edit.jumplist`,
  `text.jumpring`); the shell completion engine and the synchronous job
  route (`edit.shctx`, `compspec` over the 24 runtime specs, `compgen`,
  `comphelp`, `compfish`, `shell`, `shell_cmds`, `job`, `shsession`), the
  job half refusing by name until `os_signal_wait_fds` (R-yw04-1).
- 83 of campaign 04's 104 PTY goldens gated by name (M-YW4), the 21 others
  recorded by owner; campaign 03's 62 unchanged. The live-editor kill9 lane
  over the port's editor (`tools/torture-live`, the replica's `--live` and
  `--state-per-run`), G3's determinism order known-red by name.
- The `VTIME` interim no longer reorders events: a deadline's turn runs
  before bytes a tick read returns after it, and a deadline under the tick
  waits finely (`edit.loop`, `term.tty`); a history append opens once.
- Fuzzers (`tools/fuzz-{cmdparse,fuzzy,re,shctx,comphelp,search}`, C's
  generator bit for bit, hashes equal to C's drivers) and perf harnesses
  (`tools/run-perf-{cmdcomp,re,search,search-session}`); the regex golden
  table and the shell corpora drift-checked against the pin.

### yw02 — the text engine (2026-10-20)

- Campaign 02 ported into `text`: the piece tree with its snapshots,
  iterators, checker and grapheme index (`text.piece`); byte-exact load
  and the save decision table (`text.file`); the crash journal and the
  edit choke point (`text.journal`, `text.edit`); typed coordinates, the
  cursor, UTF-16 columns and the cursor set's core (`text.coords`,
  `text.cursor`, `text.u16`, `text.cset` — in `text`, a module cycle
  otherwise); the undo tree with transactions, trimming and the `.yewu`
  sidecar, marks with gravity (`text.undo`, `text.mark`); registers, the
  kill ring and the OSC 52 clipboard (`text.register`, `text.yankstack`,
  `text.clipboard`); sagitta's unit tests one for one (20 files).
- The save has no fsync at wolf 0.2.33 (G3, wolf-lang#796): every sync
  is a named call that syncs nothing, and the fault shim's log of one
  save is the witness. `realpath` is a component walk (G4).
- The torture gate: sagitta's `kill9` driver and fault shim over the
  port's torture child (`tools/yew-torture`, `tools/build-torture`),
  green through every sweep and red only at G3's line, accepted by
  name; kill9.c's later lanes in a container through the port's replica
  (`tools/torture-replica.py`); journals cross between C and the port
  both ways. `osc52_frame` gated against the demo's new `osc52` scene.
- The ratios beside C's own harnesses (`tools/run-perf-text`,
  `tools/perf-text`): piece inserts 1.15–1.24×, the 100 MB load
  1.34–1.83×; `tools/oracle` builds `perf_piece`, `perf_textbuf` and
  `gen-bigfile` too.
- The differential fuzz (`tools/fuzz-textbuf`, `tools/run-fuzz-textbuf`):
  `fuzz_textbuf.c` ported whole, the same trace and final hashes as C's
  in all twelve cells of sagitta's matrix; CI runs two seeds.
- Two `.yewu` reader fixes (a negative offset refused as C's unsigned
  compare does; the end-of-line goal as C's UINT64_MAX); the grapheme
  index rebuilds into a spare pair instead of leaking a list per edit
  (G33), `undo_dump` into one buffer; the tests and tools keep their log
  and state off the host's.

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
