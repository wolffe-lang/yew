# yw02 — the text engine

**Opus 5.5, crawl 54, 2026-10-20.** Contract: planning repo
`sprints/yew/02-the-text-engine/yw02-the-text-engine.md` at `5d22be7`
(adopted from this repo's `notes/contracts/yw02-the-text-engine.md`).
Ports sagitta campaign 02 (`s07`–`s12`): `src/text/*`,
`src/unicode/coords.c`, `u16.c`, their unit files, the torture child
`tests/torture/yew-torture.c` and `tests/fuzz/fuzz_textbuf.c`.

## The toolchain at the lane's start

`gh release list -R wolffe-lang/wolf-lang` on 2026-10-20: the latest
release is **v0.2.33** (2026-10-19T18:37Z); s248 (`fs_sync`,
`fs_sync_dir`, `fs_realpath`, the restore, the mode bits) is wolf-lang#804,
open, its `tier full` queued; r39 (0.2.34) has not started. So the pin
yw01 left stands — wolf 0.2.33 `85dab5d7`, lupin 0.1.54, wolf-std
`cceda63` — and **gap G3 is met, not adopted**: there is no `fsync` of a
file or a directory in wolf 0.2.33 (`spec/11-os.md` `[os.host.sigs]`, 140
lines, no sync), so the port's save is temp-in-the-same-directory and an
atomic `rename` **without the two syncs**, said by name where the code
skips them. G4 (`realpath`) is met the same way: the journal and the
backup are keyed by the realpath's hash, and 0.2.33 has no `fs_realpath`,
so the port resolves the path a component at a time with `fs_read_link`
(boreutils' answer), named in the code.

## Prediction (written 2026-10-20, before the first port line)

The contract's, kept: G3's syncs are absent at 0.2.33, so the save is
write-temp + atomic `rename` without `fsync`/`fsync_dir`; the piece tree
ports without a compiler gap (a tree of indices into two `List[byte]`
stores, no raw pointers); the differential fuzz holds byte-equality over
200,000 ops at two seeds; the 100 MB load within 2x of C's (the per-byte
bounds checks are the cost); `test_undo`'s serialization round-trips byte
for byte.

The lane's own, from reading sagitta's torture tree before any code:

1. **M-YW2 as the contract words it cannot be green at yw02.**
   `make torture`'s **batch-kill9** lane drives `yew --clean --batch
   save-heavy.fl` (a Fletch script: `import buf`, `edit { }`,
   `buf.save(b, {force: true})`; `tests/torture/batch_kill9.c:192-221`),
   which is campaign 07's `--batch` (yw09); its **live-editor** lane
   (`yew-live-torture.c`) types `Ndd`, a bracketed paste in I mode, `s`
   and `:ed.quit_force` into the real editor in a PTY — campaign 03's
   modal core (yw03). Both answer "not yet ported" against the wolf `yew`
   at yw02, by name. The campaign-02 surface of `make torture` is its
   FIRST lane: sagitta's own `kill9` driver over a headless torture child
   (`yew-torture --save/--check`, the save-boundary sweeps and the
   external SIGKILL campaign). The port builds that child in wolf
   (`tools/yew-torture/`) and runs sagitta's driver and shim against it
   unchanged. A ruling is asked (§ Rulings).
2. **Against the wolf torture child at 0.2.33, sagitta's driver is green
   through every sweep and red at exactly two checks, both G3**: the four
   atomic-path sweeps (seeds 1, 7, 42, 8675309), the hard-link sweep, the
   late-hard-link, EXDEV and fchown fallbacks, the in-place sweep and the
   ten-backup rotation pass; then `inplace_write_failure_check` fails (its
   EIO is armed by the first directory `fsync` the shim sees,
   `faultshim.c:456-462`, and the port makes none), and so would
   `determinism_check` (its log-order assertion wants `write…`,
   `fsync-file`, `rename`, `fsync-dir`, `kill9.c:321-391`). The driver
   stops at the first red, so its external-SIGKILL lane does not run in
   that invocation; the port's replica of that lane (the same seeds,
   delays and checker) shows no corruption.
3. **Never corrupts**: in every sweep and every kill the destination is
   the old bytes or the new, never a mix, and the old bytes plus the
   journal replay to the new — the rename is atomic whatever the syncs.
4. **The journal is byte-compatible with C's**: C yew's `yew-torture
   --check` replays the port's journals and the port's replays C's.

Hits and misses are recorded in §3 as they were measured.

## 1. Forbidden

The track's seven standing rules and `sprints/RULES.md` held, with one
slip and one host write reported in §5: sagitta's `src/text/*.c`,
`src/unicode/coords.c`, `u16.c`, the torture tree and the fuzz target
read and cited `file:line` in every unit; no other editor's buffer,
rope, piece-table, undo, register or clipboard source; no dependency but
wolf-std; no golden edited; no merge, tag, release or issue (the issues
are listed in §5); no attribution trailer; builds and tests on kasumi
only, under `~/lanes/yw02/yew` (25 characters), never on nomad-1; long
jobs under `setsid -f` with a pid file and killed by recorded pid only
(none was killed); the maintainer's sagitta checkout read-only (the lane
cloned it to `~/lanes/yw02/sagitta` on both hosts at the pin); signals
only to processes the lane started, inside a container — the kill9
campaigns run in a throwaway `archlinux:base-devel` podman container on
kasumi (`--network none --userns=keep-id`, the lane directory mounted at
its own path), and in CI inside `docker run ubuntu:24.04`.

## 2. Inputs, verified

wolf 0.2.33 `v0.2.33` → `85dab5d7`, lupin 0.1.54, wolf-std `cceda63`: the
pin yw01 left (`wolf-toolchain.toml`, the archive digests read twice by
yw01), fetched by `tools/fetch-toolchain` on kasumi, which refuses a
digest mismatch. `gh release list -R wolffe-lang/wolf-lang` read three
times — at the lane's start, when the save was written, and at
2026-10-20T07:31Z — and every time the latest is **v0.2.33**
(2026-10-19T18:37Z): s248's calls are merged on wolf-lang trunk at
`808ce11a` (the orchestrator's note) but unreleased, so the pin stands
and G3/G4 are met, not adopted. sagitta `9ace98c2` (`sagitta.pin`):
`s07`–`s12`, `src/text/*.c|h` (14,576 lines with `coords.c|h` and
`u16.c|h`), the unit files below, `tests/torture/{kill9.c,
batch_kill9.c,yew-torture.c,yew-live-torture.c,faultshim.c}`,
`tests/fuzz/fuzz_textbuf.c`, `tests/perf/{perf_piece.c,
perf_textbuf.c,fixtures.sha}`; the oracle built by `tools/oracle` (gcc)
on kasumi into `target/oracle/sagitta/build-gcc`. The spec's
`[os.fs.*]` and std's `fs`, `process`, `time` at the pin (`fs.lu`:
`set_times`, the twenty `stat` words, no sync; `time.lu`: milliseconds,
"a library cannot invent precision it was not given").

## 3. Prediction — the hits and misses

The contract's:

- **The save is write-temp + atomic `rename` without the syncs: HIT, by
  name.** Every one of sagitta's sync sites (19 in `file.c`, 17 in
  `journal.c` by `grep -c fsync`) is a call to `no_sync_g3(fd)` or
  `no_sync_dir_g3(path)` (`src/text/file.lu:262-273`: "this call SYNCS
  NOTHING"; 19 call sites in `file.lu`, 12 in `journal.lu`). **G3's
  witness**, sagitta's fault shim logging one clean save of each child
  (`notes/yw02-evidence/g3/`): C `0 write, 1 fsync-file, 2 fchown,
  3 close, 4 rename, 5 fsync-dir, 6 close, 7 fsync-dir, 8 close,
  9 close`; the port `0 write, 1 fchown, 2 close, 3 rename, 4 close`.
- **The piece tree ports without a compiler gap: HIT for the tree, with
  costs.** A node pool of indices into two `List[byte]` stores, the
  free list through `left`, copy-on-write by reference counts, a
  snapshot as a root index plus the buffer id; 1,000,000 random inserts
  build the same tree as C's (`pieces=1755012` both, §4). What the
  idiom paid: `distinct` coordinates are not `Copy` (G24, so they live
  only at function boundaries and every struct field is `int`); the
  module cycle `unicode.coords` ↔ `text.piece` is E0303, so `coords`,
  `u16` and the cursor set's core live in `text`; a 64-bit `const` is
  not static data (G25).
- **The differential fuzz holds byte-equality over 200,000 ops at two
  seeds: HIT, and more.** The port of `fuzz_textbuf.c` (C's generator
  bit for bit, its twelve checks, its oracle, shrinker and trace format)
  prints the SAME `trace=` and `final=` hashes as C's own binary in all
  twelve cells of sagitta's `make fuzz-textbuf` matrix (4 seeds × 3
  mixes × 200,000 ops), every cell exit 0 on both sides; the smoke trace
  replays to C's `final=4a5adab78b64d0b6` (§4).
- **The 100 MB load within 2× of C's: HIT** — 1.60–1.83 on
  `100m-code`, 1.34–1.60 on `100m-utf8` (§4).
- **`test_undo`'s serialization round-trips byte for byte: HIT after two
  fixes.** `test_undo_serial`'s CRC-valid out-of-bounds op crashed the
  port (yew internal error "delete range [-1,6)") because a forged
  UINT64_MAX offset reads as -1 and the port tested only `off > len`
  (C's compare is unsigned); a second field of the same kind (a repair's
  `rel_off`) had no C test. Both fixed (`cd28a56`), each with a case
  seen red first; and the end-of-line goal now crosses a `.yewu` as C's
  eight 0xff bytes (`274409d`; the port's `CCOL_EOL` is the largest
  `int`).

The lane's own:

1. **M-YW2 as worded cannot be green at yw02: HIT.** Against the wolf
   `yew`, sagitta's `batch-kill9` stops at its first trial ("batch
   reopen failed after trial=0", the binary answering `not yet ported:
   --batch: sagitta Sprint 37 (headless batch) (yw09)`), and the
   live-editor lane at its first save ("atomic invariant failed seed=1
   at=0"; under a PTY the binary says `not yet ported: the editor:
   sagitta Sprint 14 (modes L and I) (yw03)`) —
   `notes/yw02-evidence/torture/{batch,live}-kill9-port.log`,
   `wolf-yew-entry.txt`. A correction to the prediction: the live lane
   also types `:ed.quit_force` (`yew-live-torture.c:189`), E mode,
   sprint 18 — so it flips at yw04 unless yw03 carries a `:` (ruling
   R-yw02-1).
2. **The driver is green through every sweep and red at exactly G3:
   HIT.** sagitta's `kill9` over the port's child, in the container:
   `atomic seed=1 syscalls=12 ok`, seeds 7/42/8675309 ok, `hardlink
   syscalls=8 ok`, the late-hard-link, EXDEV and fchown fallbacks ok,
   `inplace backup_keep=10 syscalls=18 ok`, the rotation ok, then
   `torture: injected inplace write did not fail` (exit 1) — the EIO the
   shim arms after the first directory fsync the port never makes
   (`kill9-port-child.log`; C's child, the same container:
   `kill9-c-child.log`, every lane ok, 500 SIGKILLs, 5.9 s). The
   syscall counts are lower than C's (12 against 17 on seed 1): the
   syncs.
3. **Never corrupts: HIT.** In every sweep and in 500 external SIGKILLs
   (the port's replica of kill9.c's late lanes, `tools/torture-replica.
   py`, in the container) the destination held the old bytes or the new,
   and old plus journal replayed to the new: `external-sigkill
   iterations=500 attempts=500 old=500 new=0 ok`. The only red is the
   determinism lane's ORDER check, `fchown where fsync-file is wanted` —
   G3 again (`replica-port-port.log`).
4. **The journal is byte-compatible both ways: HIT.** C's `yew-torture
   --check` replays the port's journals (`replica-port-cchk.log`:
   EINTR, ENOSPC, 500 SIGKILLs, GREEN) and the port's replays C's
   (`replica-c-portchk.log`, all four lanes GREEN including C's sync
   order).

## 4. The sections, and what yw02 measured

All on kasumi (16 cpus; other lanes' jobs ran during some measurements,
said where it mattered), the release tier of wolf 0.2.33 against the
oracle's gcc build.

- **`text.piece`** (`piece.lu`, 1,582 lines; C `piece.c` 1,411): the
  tree with byte, LF and node counts per subtree, the line index the
  stores carry (`TextStore.lfs`), snapshots, the chunk and line
  iterators, the checker after every edit in the tests, the grapheme
  index (checkpoints, pending edits replayed). `test_piece` 27/27,
  `test_piece_regress` 5/5, `test_textbuf_props` 12/12 at C's 500
  cases × 4 seeds with C's generator bit for bit.
- **`text.file`** (1,805; C 1,698): byte-exact load (binary, CRLF/LF/
  mixed, BOM, invalid UTF-8 kept, missing final newline), the save
  decision table (atomic temp-and-rename, the hard-link and symlink
  in-place fallbacks, the backup and its rotation, the content and mtime
  disk checks, `fchown`/`fchmod` restore), G3 named at every sync,
  `file_realpath` as a component walk with `fs_read_link` (G4).
  `test_file` 17/17, `test_save_paths` 9/10 + the shim contract
  KNOWN-RED by its exact G3 line (accepted by the test, said on both
  streams), `test_save_policy` 4/4 with the option table's three rows
  SKIP by name (the table is sprint 36's, yw09).
- **`text.journal` and `text.edit`** (1,099 + 241; C 1,504 + 186): the
  append-and-sync journal (syncs named, G3) with the pinned base, the
  valid prefix at every cut, the stale and legacy preservation; the
  edit choke point `EditCtx`, which OWNS what C's points at, and the
  journal owner list as a threaded `JournalSet` (C's is process-wide;
  module state of a run-time `str` is E1010). `test_journal` 14/14.
- **`text.coords`, `text.cursor`, `text.u16`, `text.cset`** (1,606 +
  145 + 91 + 661): typed coordinates at function boundaries,
  byte↔grapheme↔cell columns with tabs and wide glyphs, the cursor with
  its lazy goal, UTF-16 columns, the cursor set's core from
  `edit/multicursor.c`. `test_coords` 10/10 (the motion golden copied
  verbatim) and the port's own 1 (§4, memory), `test_cursor` 12/12, `test_u16` 5/5 (`test_u16_diff` is
  yw11's).
- **`text.undo` and `text.mark`** (3,353 + 297; C 3,205 + 357): the
  tree with transactions, merging, branches, the clock (a fake clock
  value in place of C's function pointers), trimming and re-rooting,
  the `.yewu` sidecar with the block identity hash (xxh64-shaped, the
  two vectors verified); marks with gravity behind generational handles
  and the repair runs. `test_undo` 31/31, `test_undo_tree` 11/11,
  `test_undo_marks` 5/5, `test_undo_trim` 6/6, `test_undo_serial` 14/14
  and the port's own 2, `test_mark` 3/3.
- **`text.register`, `text.yankstack`, `text.clipboard`** (a fork of the
  lane, `yw02-reg`): the register file, the kill ring, paste, the
  clipboard queue with OSC 52 after the frame. `test_register` 12/12,
  `test_register_append` 7/7, `test_yankstack` 6/6, `test_clipboard`
  15 ported (5 whole, 3 in part, 7 SKIP by name): **the subprocess
  backends are a STOP** — the writer needs a non-blocking pipe write and
  a fork (C forks twice so the tool is not the editor's child), the
  reader a timed wait on a pipe; reaching either exits 4 naming the gap
  (four self-spawned witnesses). The demo's `osc52` scene: sagitta's
  `osc52_frame` green against the port's demo (and red against the
  yw01 demo, the plant), `osc52_reply` and every other campaign-01 case
  still green.
- **The torture child** (`tools/yew-torture/main.lu`, C
  `yew-torture.c` 354): `--save`, `--save-insert`, `--check`,
  `--check-batch`, `--atomic-result`, C's exit codes; an inherited
  descriptor ≥ 3 is not a handle (G26), so the ready byte goes through
  `/dev/fd/N` reopened.
- **The differential fuzz** (a fork of the lane, `yw02-fuzz`;
  `tools/fuzz-textbuf/main.lu`, `tools/build-fuzz-textbuf`,
  `tools/run-fuzz-textbuf`): `fuzz_textbuf.c` ported whole — the
  generator (the RNG, the four mixes, the op weights, the position and
  content classes, the forced ops that open each epoch, the 8 MiB trace
  rollover with C's own arithmetic), all twelve checks with C's ids and
  cadence, C's naive oracle, the trace writer and `--replay`, the
  four-phase shrinker with C's budget, the failure report (seed, op,
  check, the shrunk trace under `target/fuzz-textbuf-crashes/`); C's
  bounds (64 KiB, 8192 lines, 4 snapshots, 8 marks, 200,000 ops). The
  port's own `--plant-at=N` adds a byte to the oracle after op N: red
  at op 50, check 1, shrunk to one op in ten replays, exit 1
  (`notes/yw02-evidence/fuzz/planted-red.log`). The matrix, port beside
  C on kasumi under `taskset -c 0-3`: 40.0–47.3 s against 34.9–39.7 s
  a cell (1.12–1.23×), peak RSS 357–556 MB against 74–138 MB — the
  port holds an epoch's scratch until the epoch's region ends, where C
  frees per op (`campaign-4x3-200k.log`, `two-seeds-200k.log`). Re-run
  after the index fix below: the same hashes at both seeds, 42.1 s and
  40.9 s. CI runs both seeds in the port job.

**The ratios** (`tools/run-perf-text --taskset 0-3`, sagitta's own
`perf_piece` and `perf_textbuf` beside the port's twin
`tools/perf-text/main.lu`, sagitta's fixtures from its own `gen-bigfile`
verified against `fixtures.sha`; three runs — the first quiet, the
second (`--huge`) while a fork's fuzz shared the pinned cpus, the third
quiet after every fix; the first run's output was not kept as a file
(the second run's staging replaced it) and its numbers are quoted here,
the other two are `notes/yw02-evidence/perf/run-perf-text-huge-1.log`
and `run-perf-text-quick-2.log`):

| metric | C | wolf | ratio |
|---|---|---|---|
| `piece.insert` (1M random inserts, best of 3) | 1,294 / 2,102 / 1,228 ms | 1,579 / 2,416 / 1,522 ms | **1.22 / 1.15 / 1.24** |
| `open.100m-code` (median-run p50) | 71.1 / 79.8 / 70.0 ms | 128 / 128 / 128 ms | **1.80 / 1.60 / 1.83** |
| `open.100m-utf8` | 36.2 / 41.9 / 35.6 ms | 57 / 56 / 57 ms | **1.57 / 1.34 / 1.60** |
| `open.100m-allnl` (informational in C) | 614.7 / 666.6 / 622.5 ms | 1,060 / 993 / 999 ms | 1.72 / 1.49 / 1.60 |
| `line_of.1g-code` (C per-query p50, wolf batch mean) | 319 ns | 370 ns | 1.16 |
| `line_start.1g-code` (the same) | 82 ns | 20 ns | 0.24 |

Resident bytes at the 100 MB load: C 120 MB, wolf 136 MB (`100m-code`);
`100m-allnl` C 0.95 GB, wolf 2.0 GB. Both keep an 8-byte offset per LF
(`piece.h:56`, `YewU64Vec lfs`; the port's `TextStore.lfs`), so C's
figure is the file plus its 100M offsets; the port's second gigabyte is
not attributed at yw02 (a `List`'s growth and the load's copy are the
suspects) and is yw15's to measure against the `mem.clean_open` budgets
(1.6× the file, `budgets.txt:57-59`; allnl is informational there). The two query
rows compare a mean against a p50 that carries C's own `clock_gettime`
pair (C's `line_start.1g-noline`, a one-piece no-LF buffer, reads 14 ns
— the timer's floor): read them as "the same order", not as a ratio.
Every ratio the contract names is within 2×.

**The checked machine.** `wolf test` at 0.2.33 runs a file's `main` on
the checked machine and, when the machine refuses it (its 20M-step
budget, `wolf_mem/src/ubcheck.rs:228`), runs it ONCE NATIVELY and still
says `ok` — visible only as `detail: "exit(0) [native]"` in `wolf test
--json` (the fork that ported `test_undo_serial` found it). Of the 20
`text_*` files, 10 ran checked whole (clipboard, file, journal,
piece_regress, register, register_append, save_paths, save_policy,
undo_tree, yankstack) and 10 fell back (coords, cursor, mark, piece,
textbuf_props, u16, undo_marks, undo, undo_trim, undo_serial). The
fallback files were then run CASE BY CASE on the checked machine (each
`t_` renamed `test_`, `main` dropped, a scratch copy,
`notes/yw02-evidence/checked/percase.py`): **97 cases pass on the
checked machine, 0 fail, 30 `unsupported`** (the step budget): the
three streaming/index cases of `coords`, the four-seed motion fuzz of
`cursor`, `mark`'s 10,000-mark oracle, three of `piece`'s (the mixed
fixture, the fan-out coalescing, the snapshot under middle edits),
`u16`'s large astral line, `undo_marks`' 1000-mark oracle, `undo`'s
redo cycles, two of `undo_trim`'s, five of `undo_serial`'s (the 500
binary nodes, every node's CRC, the persist budget, the rerooted
depths, 5,000 ops), and all twelve properties at C's 500 cases — which
pass on the checked machine at `YEW_PROP_N=5` (12/12,
`percase-props5.log`). The 30 run natively in full.
The SKIPs on the checked machine (printed on both streams, counted by
reading each file): `piece` 3 (the exit-4 bug cases), `mark` 1 (the two
stale-handle exits), `undo` 1 (the open-transaction save), `clipboard`
the 7 subprocess cases plus its 4 gap witnesses, `save_policy` the 3
option rows; natively only the clipboard's 7 and the option rows.
`tools/check-test --native`: all 39 files green, 1:55 on kasumi.

**Memory: a replaced `List` is never freed before its region ends.**
The PR's first run (39388476890) lost its linux port job to the runner's
shutdown signal in the middle of `wolf test`: the suite peaked at 12 GB
on kasumi, the hosted runner has 16. Three causes, each measured alone
(the per-case native runs, `/usr/bin/time`): `test_undo_serial`'s
corrupt-CRC loop held 501 reads of a 1 MiB tree to the test's end (a
function allocates in its caller's region; each read now runs in its
own `region` block, 12 GB → 0.36 GB); `undo_dump` built its text with
`out = out + line`, every line a whole new string held to the end
(5,000 nodes: 6 GB → 53 MB, 1.9 s → 0.2 s, now one byte buffer); and —
the one that matters past the tests — **the grapheme index rebuilt an
edited buffer's checkpoint lists into fresh `List`s on every second
edit**, as C does with malloc and free, but a wolf value that replaces
a list field leaves the old one allocated in the owner's region: 200
appends at the end of a 1 MiB buffer cost 134 MB (an editor session
would grow without bound). The index now rebuilds into a spare pair
and swaps (`02806d4`; 134 MB → 0.9 MB), pinned by the port's own
`text_coords_test` case, seen red at `02806d4`'s parent; an abort
truncates the undo blob store in place (`b08f59b`). `wolf test` over
the whole suite now peaks at 0.99 GB. The same shape remains, smaller
or rarer, where a long-lived value's list is rebuilt: the undo tree's
compaction (`undo.lu:1765-1770`, O(the arena) per compaction), the
cursor set's normalize and the undo cursor restore (O(cursors) per
call), the clipboard queue's copies — the rule for yw03, whose `Ed`
lives for the session (G33).

**`unsafe` census delta: +2 module vars** — `text.file`'s
`temp_counter` (the temp-name serial, C's `static u64` in
`file.c`; `file.lu:256`) and `text.undo`'s `text_hash_calls` (C's
`undo.c:35` test hook; three blocks, `undo.lu:269-284`). The register
and clipboard state is a value owned by the register file. The
repository's census: `unicode.width`'s `ambiguous_wide`, these two.

**The save's shape, and why** (the G3 interim): sagitta's decision
table unchanged — temp in the same directory, the bytes, `fchown` and
the mode restored, `rename`, the directory — with every sync a named
call that syncs nothing, so the day 0.2.34 is pinned two function
bodies change (`no_sync_g3`, `no_sync_dir_g3`) and the KNOWN-RED rows
turn green: `save_fault_shim_contract`, the replica's determinism
order. What the interim costs: after a `kill -9` the destination is old
or new (the rename is atomic, §3), but after a POWER loss the new bytes
may not be on the platter when the rename is — the guarantee the syncs
buy and the one the port does not claim.

## 5. Rulings asked, issues, and what to correct

**Rulings asked** (each with the lane's recommendation):

- **R-yw02-1 — M-YW2's shape.** (A) M-YW2 at yw02 is `make torture`'s
  campaign-02 lane: sagitta's `kill9` driver over the port's torture
  child, green but for G3's named red until 0.2.34, plus the replica's
  late lanes; `batch-kill9` moves to yw09 (`--batch`) and the
  live-editor lane to the first lane with an editor that takes `:`
  (yw04, or yw03 with a minimal `:`). (B) M-YW2 stays as worded and
  waits for yw09. **Recommend A** (implemented: the CI gate is A's).
- **R-yw02-2 — the KNOWN-RED shape.** The shim-contract test and the
  CI replica accept exactly G3's line and fail on anything else. (A)
  keep that until the pin has the syncs (recommended, implemented);
  (B) skip the test until then (hides the eleven lanes that do hold).
- **R-yw02-3 — the clipboard's subprocess backends.** (A) a STOP until
  wolf has a non-blocking pipe write with a write-readiness wait and
  `os_fork` (0.2.34) — the port exits 4 by name (implemented); (B) a
  blocking writer that can hang the editor on a tool that never reads
  (refused: invariant 4); (C) a helper thread per write.
  **Recommend A**, and ask wolf-lang for the non-blocking pipe write.

**Issues to file** (listed, not filed):

- wolf-lang: G24 `distinct int` is not `Copy` and nothing opts it in
  (`notes/yw02-evidence/witness/distinct-copy`); G25 a module `const`
  of `wrapping[u64]` is "not static data" (`witness/wrapping-const`,
  `wrapping-const-unreached`); G26 an inherited descriptor ≥ 3 is not
  an fs handle (`witness/inherited-fd`); G28 the E1004 conservatism on
  a `copy` of a scalar struct (`witness/region-copy`); G29 `wolf test`
  falls back to native and says `ok` (the `[native]` detail is the only
  trace — print it in the human output, or count it); G30 no
  non-blocking pipe write / write-readiness wait (the clipboard writer,
  the fork's `probe/rg1`); G31 no host OS/arch query (`probe/rg0`);
  G32 no `access(2)`, no `O_NOFOLLOW`, no advisory lock, `fs_fstat`'s
  three words (no dev/ino on a handle), no `mkfifo` — each met as a
  prelude absence and worked around by name; G33 a `List` that replaces
  a field of a long-lived value is held until the value's region ends
  (no per-object free; the measured case above, the port's own coords
  test) — a design note for the guide at least, a reclaiming
  assignment or a `List` that reuses its storage at most; the guide
  note for the wrapping-literal inference (`witness/wrapping-infer`: a
  countdown inferred `wrapping[u64]` never ends); from the fuzz fork:
  G18 confirmed for a call ARGUMENT (`bump(mut g)` inside a `region`
  block is E1010 for a scalar-only struct), a whole scalar struct
  assigned across a region boundary is E1010 too, `let tb = run.ec.tb`
  moves the field out of a read parameter (E1001), a multi-line `if`
  condition cannot put `{` on its own line (E0201), and a local named
  `clock_ms` is W0304 (it shadows a prelude name).
- wolf-lang: G3 (#796) and G4 (#797) stand until 0.2.34 is released;
  nothing new.
- yew: `tools/goldens` and `tools/oracle --unit` run C yew without a
  scratch `HOME`/`XDG_STATE_HOME`, so the oracle writes kasumi's
  `~/.local/state/yew` (created 2026-10-19T18:37Z by those runs).

**Reported, not fixed by the lane:**

- **RULES §5 slip.** At 2026-10-20 00:00 the lane ran sagitta's C
  `kill9` baseline on kasumi's host process table before moving it into
  the container (it SIGKILLs only its own children, 500 of them); every
  later signal campaign ran in the container, and the baseline was
  re-run there (`kill9-c-child.log`).
- **A host write.** Three of the lane's test files (`undo_tree`,
  `undo_marks`, `piece_regress`; and the fork's `yankstack`) did not
  set `YEW_LOG`, so their warnings — 5,709 "wall clock stepped
  backwards; clamped", 100 "over budget, nothing trimmable", 25
  "dropped … .yewu" — were appended to kasumi's
  `~/.local/state/yew/log` (2026-10-20T07:00–07:34Z), as were 37
  "loading large file" lines from C's `perf_textbuf --huge`
  (07:15:52–07:16:01Z, the lane's own perf run). The lane
  did not truncate the file (it is not the lane's to edit); the mains
  now log nowhere (`fac5fd5`) and `tools/check-test` and
  `tools/run-perf-text` export a scratch log and state (`ded0e81`,
  `20437a2`).

## Evidence index

- G3's witness: `notes/yw02-evidence/g3/{c,port}-shim.log`.
- The torture runs: `notes/yw02-evidence/torture/` — `kill9-c-child.
  log`, `kill9-port-child.log`, `replica-{port-port,port-cchk,
  c-portchk}.log`, `batch-kill9-port.log`, `live-kill9-port.log`,
  `wolf-yew-entry.txt`, `oracle-build.log`.
- The ratios: `notes/yw02-evidence/perf/`.
- The gap witnesses: `notes/yw02-evidence/witness/` (source, the
  build's and the run's output beside each).
- The per-case checked run: `notes/yw02-evidence/checked/`.
- The differential fuzz: `notes/yw02-evidence/fuzz/` (two seeds, the
  4×3 matrix port beside C, the planted red).
- CI (yew#7): run 39388476890 at `56ce65b` — the linux port job lost
  to the runner's shutdown signal mid-`wolf test` (the 12 GB above) and
  the oracle's driver step red on a missing `YEW_ROOT` export, both
  fixed (`055de26`, `5c1beaa`, `02806d4`, `9e3e62e`); run 39393219720 at
  `a8f9236` green on linux in both jobs (the driver over the port's
  child, the replica three ways, `osc52_frame`, the text fuzz at two
  seeds), and on macOS too: there the driver interposes the fault shim
  with `DYLD_INSERT_LIBRARIES` over the wolf binary and answers exactly
  the linux lines (the step runs RECORDED on macOS; no plant has seen it
  red there, so the next lane that plants on macOS promotes it). The
  final run is the PR's.
- The plants (RULES §7, draft PRs closed unmerged, each on `a8f9236`):
  yew#8 (`da7eafb`, the journal record never written) seen red in run
  39393453647, oracle linux, "sagitta's kill9 driver over the port's
  torture child" (`wolf-trap: assert at src/text_save_paths_test.lu:451`,
  the every-lane-holds assertion; the driver's own line on kasumi:
  `torture: atomic invariant failed seed=1 at=0`); yew#9 (`65d3572`, a
  failed save write taken for a whole one — the driver's kill sweeps
  stay green) seen red in run 39393461050, oracle linux, "kill9's late
  lanes in a container" (`storage ENOSPC preserves old+journal FAILED
  (exit=0 expected=3 …)`); yew#10 (`0f52f69` the demo's osc52 scene
  reverted, `b4161d9` the fuzz step with `--plant-at=50`) seen red in
  run 39393467096 at port linux, "the differential fuzz of the text
  engine" (`divergence seed=0x…01 mix=typing op=50 check=1`), and at
  oracle linux, "goldens, campaign 01" (`osc52_frame: child exited
  before synchronized frame`).

## Done-when

Every deliverable with its tests (§4); `tools/check-test` and `--native`
green (with the checked machine's fallback said by file, §4); M-YW2 as
ruled (R-yw02-1, A); the unit files ported one for one (20 files, 226 C
tests and the port's own 3, the counts above); the save's no-corrupt property shown
and G3 met with its witness; the ratios recorded on kasumi under
`taskset -c 0-3`; `docs/MAP.md` updated; yw03's contract drafted
(`notes/contracts/yw03-the-modal-core.md`); CI green; the PR open with
the five sections; `lane-audit.sh yew yw02 <PR>` passing but for the
final run's green.
