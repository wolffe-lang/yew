# The map: sagitta to wolf

**yw00, 2026-10-19.** Every sagitta source directory and every one of
its 95 sprint files, the port lane each belongs to, the C it is and the
wolf it becomes; the idiom the port writes in; and every gap in wolf,
wolf-std or lupin the port has met or can see coming, with a witness
where one can be written today. Sizes are C lines at sagitta
`9ace98c2` (`wc -l` over `*.c` and `*.h`, 218,190 in all). The lane
table is the track index's (`sprints/yew/index.md`), corrected where
the source says otherwise; §7 has the one-paragraph contracts for
yw02–yw16.

## 1. The idiom: how wolf stands in for C

Settled by yw00 and binding on later lanes (CLAUDE.md), each measured
on wolf 0.2.32 (`notes/yw00-the-map.md` §4 has the probes):

| C yew | the port | why |
|---|---|---|
| `src/<dir>/` | a module directory `src/<dir>/`, the same name; the entry `src/yew.lu` (`//! member: false`) imports it | D32: a directory is a module; a std module of the same name (`std.unicode`, `std.term`, `std.search`) is imported aliased in the file that needs both (`use std.term as std_term`) — the port's name wins |
| `yew_utf8_decode`, `yew_gb_init` | `unicode.utf8_decode`, `unicode.gb_init`: the family prefix stays, the `yew_` goes | the module name carries it |
| `(const u8 *s, size_t len)` and `s + pos` | `(s: List[byte], at: int, end: int)`, absolute offsets answered | a `List` slice copies; a `read` parameter is lent for free |
| out-parameters (`u32 *out`, a return code) | a tuple `(cp, n)`; absence or failure an error row (`-> T ! {none}`) | rows, never sentinels |
| `Arena`, `yew_xmalloc` | regions: an ordinary function allocates in its caller's region; `region scratch { }` for per-iteration scratch; a trap on failure | regions are the allocator |
| `Vec(T)`, `Bytebuf` | `List[T]`, `List[byte]` | the language's |
| `Strmap`, `Interner` | `util.Strmap[V]` (two `List`s and a `Map` index), `util.Interner` | insertion order kept explicitly (§5 of `s00`); wolf's `Map` promises only that its three iterators agree |
| `yew_sort_stable` | `util.sort_stable` over `std.list.sort_by` (the same bottom-up stable merge) | one name for sagitta's rule |
| `static const` tables (`u8_class[256]`, the Unicode trie) | module `let` **`str` constants** of 7-bit digits, read with `.bytes()[i]` inline | module state of a `List` is refused (`[mem.static.3]`); a `str` is `.rodata`; an inline `.bytes()[i]` is a zero-copy read at 2 ns a lookup (probe t1); a bound `let b = s.bytes()` COPIES and must never be written in a loop (probe t3 took 60 GB) |
| a process-wide option (`width_opts`) | a module `var` behind `unsafe { }` with `// # Safety:` naming invariant 8 (single-threaded core) | `[mem.static.2]`; the `unsafe` census is this table: `unicode.width`'s `ambiguous_wide`, `text.file`'s `temp_counter` and `text.undo`'s `text_hash_calls` (yw02), nothing else |
| `v & ~mask` | `v - (v & mask)` (`unicode.grapheme.without`) | wolf has no bitwise not (§5) |
| a getter returning a field of a `read` parameter | `copy m.vals[i]` | `[mem.tier0.mode.read]`, wolf-lang#366: a lent value is never handed on |
| `bytebuf_printf(b, "%s:%d", …)` | `buf_append_str(mut b, "{s}:{n}")` | interpolation; `std.fmt` for `%02x` and padding |
| `tests/unit/test_x.c`, `T(name)` in the registry | `src/<dir>/x_test.lu`, `fn t_name()` in registry order under a black-box `main` | `wolf test` runs `main` on the checked machine (the ASan/UBSan stand-in, §6) and `tools/check-test --native` the same binaries natively; a `test_*` name is discovered only in a package's first file (§5), so none is used |
| `scripts/gen-unicode-tables.c` | `tools/gen-unicode-tables/main.lu`, a wolf program; the output data-only, the lookups hand-written (`unicode.trie`) | a `{` in an emitted line is an interpolation hole; a generated file that holds code is a generated program |
| typed coordinates (`ByteOff`, `LineNo`, `CCol` as one-field structs) | `distinct int` at FUNCTION BOUNDARIES only; struct fields and locals `int`, converted once at entry (yw02) | a `distinct int` is not `Copy` at 0.2.33 (`x as int` moves `x`, G24) |
| a tree of `malloc`ed nodes (`PieceNode *left`, the undo tree) | a node pool `List[Node]` with indices (-1 none), a free list through a child field, copy-on-write by a `refs` count, a snapshot as a root index and the buffer's id (yw02) | no raw pointers; regions free wholesale |
| a context of pointers (`EditCtx { tb, marks, cset, jrnl, undo, meta }`) | an `EditCtx` that OWNS each with a `has_` flag; C's copy of a context with one field changed is the one context with the flag swapped (yw02) | a stored lent value is E1004/E1002; ownership is the only shape |
| a process-wide registry of run-time values (the journal owner list) | a VALUE threaded through its owner (`text.JournalSet` in `EditCtx.journals`, `Ed` from yw03) (yw02) | module state of a run-time `str` is E1010 |
| an injected clock (`yew_undo_set_clock(ut, mono_fn, wall_fn, ctx)`) | a fake-clock value in the owner (`undo.fake_mono`, `undo.fake_wall`) (yw02) | no function value across a module boundary (G19/G20) |
| `x = xs[i]` of a struct type | `let x = copy xs[i]` | binding a list element moves it (E1001) |
| `static const u64 P = 0x…` | a zero-argument function (`undo.p1()`) (yw02) | a module `const` of `wrapping[u64]` is not static data (G25) |
| `fsync(fd)`, `fsync(dirfd)` at 0.2.33 | a NAMED call that syncs nothing (`text.file`'s `no_sync_g3`, `no_sync_dir_g3`), so the day the pin has the syncs two bodies change (yw02) | G3: never a silent claim of a sync |
| `realpath(3)` at 0.2.33 | `text.file_realpath`, a component walk with `fs_read_link` (yw02) | G4 |

## 2. Source directories

| sagitta `src/` | files | C lines | port lane | wolf unit(s) | what it needs beyond wolf-std |
|---|---|---|---|---|---|
| `src/*.c` (`main`, `args`, `flcli`, `syncli`, `tutor`) | 9 | 3,846 | yw01 (`main`, `args`), yw08 (`flcli`), yw10 (`syncli`), yw16 (`tutor`) | `src/yew.lu` and `args` | — |
| `src/util/` | 31 | 3,572 | **yw00** (arena, vec, strmap, intern, buf, sort), yw01 (`log`, `xdg`, `base64`), yw15 (`prof`, `rss`, `calib`, `memacct`), yw12 (`secret`), yw01 (`runtime_asset`, `runtime_blob`) | `util` | `log`: `$XDG_STATE_HOME` and never fds 0–2 (fine); `rss`/`memacct`: a resident-byte model wolf lacks (§5 G12) |
| `src/unicode/` | 21 | 12,534 | **yw00** (`utf8`, `grapheme`, `width`, `tables`), **yw02** (`coords`, `u16` — ported INTO `text`: `coords` reads the piece tree and the tree calls the grapheme index, a module cycle, E0303), yw03 (`wordbreak`, `tables_wb`), yw04 (`category`, `tables_cat`, `case`, `tables_case`) | `unicode` | none; the generator grows `--word-break`, `--category`, `--case` modes |
| `src/term/` | 10 | 4,910 | **yw01** | `term` (aliasing `std.term`) | the fatal-signal restore (§5 G1); a wait over tty + signals + job pipes (G2) |
| `src/text/` | 21 | 11,688 | **yw02** (with `unicode/coords`, `u16` and the cursor set's core from `edit/multicursor.c`) | `text` | `fsync` of a file and a directory (G3, met by name); `realpath` (G4, a walk); `xattr` (G5, yw14); the clipboard's subprocess backends (G30, a STOP); an inherited descriptor as a handle (G26) |
| `src/edit/` | 80 | 31,689 | yw03 (modes, keymap, dispatch, motion, select, multicursor), yw04 (`shell*`, `shsession`, `job`, `search_cmds`), yw06 (`ws_cmds`, `pane_cmds`), yw09 (`batch`, `flapi_cmds`), yw11 (`lsp_cmds`, `shadow*`, `completion`), yw15 (`prof_cmds`) | `edit` | process groups and the foreground terminal for `:!` (ruling #79, available since 0.2.31) |
| `src/search/` | 16 | 7,491 | yw04 | `search` (aliasing `std.search`) | none; the port's regex is a `std.regex` candidate |
| `src/ui/` | 74 | 46,140 | yw03 (`viewport`, `statusline`, `gutter`, `message`, `draw`, `win`: sprint 15 is campaign 03's — corrected by yw02), yw05 (layout, panes, tabs, groups, cmdline, region, glyphs), yw06 (pickers, finder, mouse, ctxmenu, strip, typejump), yw04 (`cmdcomp`, `compgen`, `compspec`, `comphelp`, `compfish`, `shctx`, `complmenu`) | `ui` | none known |
| `src/ws/` | 28 | 10,820 | yw06 (workspace, state_*, walk, gitignore, trust*), yw11 (`sym*`, `fuzzy`) | `ws` | `realpath` (G4); XDG dirs |
| `src/fl/` | 61 | 26,269 | yw07 (lex, parse, compile, vm, value, gc, opcodes, diag, dump, data, module, std*), yw08 (repl, trace, suggest, vmcheck), yw09 (flapi, flconf, fleval, flhook, flruntime, fltxn, handle, record, macrolib, motion_tab, origin, stdai) | `fl` | a GC's shape in wolf's memory model (G6) |
| `src/syn/` | 14 | 13,064 | yw10 | `syn` | none known |
| `src/mod/lsp/` | 21 | 11,283 | yw11 | `lsp` | `std.json` exists; incremental `didChange` is the port's own |
| `src/mod/ai/` | 37 | 12,093 | yw12 | `ai` | an HTTP/1.1 client over `std.net` (the port's own; a std candidate, G9) |
| `src/mod/git/` | 19 | 15,680 | yw13 | `git` | none known (subprocesses) |
| `src/mod/plug/` | 13 | 7,030 | yw14 | `plug` | none known |
| `src/mod/mods.c` | 2 | 81 | yw01 | `util.base` (`MODULES_LINE`) | the port is always the full build: `MODULES=""` is a sagitta build shape, not a port shape (a ruling if a `minimal` wolf yew is ever wanted) |

Other trees:

| sagitta | port |
|---|---|
| `ucd/16.0.0/` (10 files), `ucd/LICENSE`, `ucd/MANIFEST` | copied verbatim (yw00); the generator reads them; `ucd/MANIFEST` is checked by `shasum -c` |
| `runtime/` (`init.fl`, 48 `syntax/*.fl`, 2 themes, tutor, presets, completions) | Fletch stays Fletch: the files are copied verbatim by the lane that first needs them (yw09 `init.fl`; yw10 syntax and themes; yw16 tutor) and never edited |
| `tests/unit/` (319 files) | ported one for one, per directory, by the lane that ports the directory (`src/<dir>/<unit>_test.lu`) |
| `tests/pty/` (552 goldens, the runner, the VT, `demo_paint`) | the runner and goldens are the oracle's, run by `tools/goldens`; `demo_paint` is ported by yw01 (M-YW1) |
| `tests/script/` (94 `.fl`), `tests/fletch/` (20 `.fl`), `tests/syn/` (432 `.spans`), `tests/roundtrip/`, `tests/torture/` | the oracle's, run by `tools/goldens` (roundtrip is in-process: the port's own harness is yw09's) |
| `tests/fuzz/` (50 targets), `tests/perf/` (48 harnesses), `tests/size/`, `tests/audit/` | ported by the lane that ports the target (wolf has no `fuzz` verb: a bounded seeded driver, as `tools/perf-unicode` is a bounded harness) |
| `scripts/` (ban greps, checkers, generators) | the port's `tools/`; the bans that matter in wolf are the compiler's (`--deny-warnings`) |
| `docs/manual/`, `docs/man/` | yw16 |

## 3. Sprint files

All 95 (`.docs/sprints/`), by campaign; the lane column is binding
for the port's order (the track index's table, corrected: s18.5 and
the `s57_*` sequence are placed with their consumers).

| campaign | sprint files | port lane | gate |
|---|---|---|---|
| 00 scaffolding | s00, s01, s02 | **yw00** | M-YW0: util and unicode unit suites green on three hosts; the tables identical to sagitta's |
| 01 terminal | s03, s04, s05, s06 | **yw01** | M-YW1 first paint: `demo_paint` through the stack; every campaign-01 PTY golden green in four profiles |
| 02 text engine | s07, s08, s09, s10, s11, s12 | yw02 | M-YW2: `make torture`'s save-boundary and SIGKILL campaigns against the wolf binary |
| 03 modal core | s13, s14, s15, s16, s17 | yw03 | M-YW3: campaign 03's PTY and script goldens |
| 04 execute and search | s18, s18.5, s19, s20, s21; s57.17, s57.18, s57.23–s57.32 (the `:` prompt and `:!` completion) | yw04 | M-YW4: the regex corpus and the `:!` goldens |
| 05 UI and workspace | s22, s23, s24, s25, s26, s27; s57.5–s57.16, s57.20, s57.22, s56.5 (the field repairs) | yw05 (s22–s24, s57.8, s57.13–s57.16, s57.22), yw06 (s25–s27, s56.5, s57.5–s57.7, s57.9–s57.12, s57.20) | M-YW5 daily driver; M-YW-PAX1 |
| 06 Fletch core | s28, s29, s30, s31, s32, s33 | yw07 (s28–s31), yw08 (s32, s33) | M-YW6: the Fletch conformance and GC-stress runs |
| 07 Fletch in the editor | s34, s35, s36, s37, s38 | yw09 | M-YW7: round-trip and batch |
| 08 highlighting | s39, s40, s41, s41.5, s42, s42.5 | yw10 | M-YW8: all 432 syntax goldens; M-YW-PAX2 |
| 09 completion and LSP | s43, s44, s45, s46, s47 | yw11 | M-YW9 |
| 10 AI | s48, s49, s49.5, s50 | yw12 | M-YW10 |
| 11 FUSS / git | s51, s52, s53 | yw13 | M-YW11 |
| 12 plugins | s54, s55, s55.5 | yw14 | M-YW12 |
| 13 performance | s56, s57, s57-allocation-audit, s57-closeout | yw15 | M-YW13: every gate within 2x |
| 14 audits and release | s58, s59, s60 | yw16 | M-YW14; M-YW-PAX3 |

## 4. What yw00 measured

C yew at the pin, gcc 16.2.1, kasumi (16 cpus, load < 1.5): `make
test-unit` 3,047 tests, 73,852,037 assertions, 0 failures, 2 skipped,
113 s; `make test-pty` 552 cases, every one `ok`, 758 s; `make
test-script` 93 tests, 951 assertions, 0 failures, 1 skipped;
`make test-fletch` green; `make test-syn-assets` 432 goldens ok;
`make torture`'s batch, live and tty-restore lanes green (32 signal/
moment trials) and its git-hunk lane red at fixture setup
(`git_hunk_kill9: fixture setup failed`, a host condition, not the
oracle's verdict). Fourteen PTY cases of sagitta's own depend on the
checkout path's length (`notes/yw00-the-map.md` §2): green in a short
tree, red under `target/oracle/`. clang 23.1.1 refuses
the tree under `-Werror` (`tests/unit/harness.c:454`
`-Wunused-but-set-global`), a sagitta issue for the maintainer; CI's
clang 18 and Apple clang build it.

The port on kasumi: `wolf test` 11 files green on the checked machine
and natively (`tools/check-test`, `--native`); the grapheme conformance
run 1093/1093; `tools/check-tables` identical to sagitta's arrays
(stage1 1,536, stage2 190 blocks, 41 palette records, 10 high ranges);
`tools/run-fuzz-unicode`: 200,000 mutations at seed 1 (and 2) hold the
nine invariants, the same seed gives the same hash, and the exhaustive
three-byte space round-trips (`notes/yw00-evidence/fuzz-unicode.txt`).

Performance, release tier, under `taskset -c 0-3`
(`tools/run-perf-unicode`, `notes/yw00-evidence/perf-unicode.txt`),
wolf/C: segment + width over 1 MiB of ASCII **1.80** (C 3,333 us,
wolf 6,000 us), CJK **1.47** (14,917 / 22,000), emoji **1.73** (8,646 /
14,968); unpinned 1.45 / 1.31 / 1.38. Cold start of `--version` over
100 runs under the pin: C 3,271 us, the port 2,739 us (**0.84**). No
2x gate crossed; the ratchet's first candidate is the ASCII fast path
(`notes/yw00-the-map.md` §3).

**yw01 (the terminal, 2026-10-19; `notes/yw01-the-terminal.md` §4).**
Every campaign-01 PTY case green by name against the port's
`demo_paint` on the release tier (sixteen `probe_`/`paint_`/`restore_`/
`input_keys_` cases and `osc52_reply`; `version` and `help` against the
port's binary); the restore proven by `restore_quit`, `restore_crash`,
`restore_bus`, `restore_abrt`, `restore_suspend`. The 2× gate
(`tools/run-perf-latency --cpus 0-3`, C first, the port, C again):
cold start → first paint **1.51** (C 4,620 us, wolf 6,973 us), keypress
→ paint over the `damage` scene **1.03** (7.5 / 7.7 us); the unit ratios
`input_chunking_independence` **0.91**, `render_resize_repaint_is_
deterministic` **1.20** (whole process, release tier vs `unit_tests
--filter`). `Cell` 104 bytes against C's 20. `wolf test src` 19 files
on the checked machine, 0 failed; native every suite green.

## 5. The gaps

Each: what the port needs, which campaign, what wolf has at 0.2.32
(read from `spec/prelude.json` at `72de141f` and the probes), the
witness, and where it is filed — LISTED here, filed by the
orchestrator (track rule 4; a lane files nothing). Status `design`
means a ruling is asked (§6), `bug` means a defect with a witness,
`gap` means an absent surface with a proposed shape.

| # | gap | needed by | at 0.2.32 | witness | file to |
|---|---|---|---|---|---|
| G1 | **the terminal restore on a fatal signal.** sagitta restores the terminal from `SIGSEGV`/`SIGBUS`/`SIGABRT`/`SIGTERM` handlers and an `atexit` (`s03` §4). wolf runs no code in a handler (`[os.signal.model]`) and the runtime restores nothing (`[os.term.mode]`). | yw01, invariant 6 | `TERMINATE`/`RELOAD`/`QUIT` are listenable: the program restores itself. The fatal three are the runtime's own: a wolf program reaches `SIGABRT` only through a trap (`wolf-trap: <kind>`, exit 134), `SIGSEGV` only through the stack guard, never through its own code. No hook runs on a trap. | `notes/yw00-evidence/witness/trap-leaves-raw.lu`: raw mode, then a `bounds` trap; the shell's `stty` after is raw | wolf-lang (design; ruling R1 in §6 — **#93 R1: interim B**, realised at yw01 as the guard sibling of sagitta `tty.c:243-349`: `os_exe() --guard`, a pipe at fd 3, the restore on EOF; wolf-lang#794 stands for the runtime's own restore. Its limit: sagitta's harness checks the restore at the reap, one shot, and the guard writes after the death — Linux wins that race, macOS lost it once for `restore_crash` (yew run 39346772578), so a self-raised fatal restores in-process first (`term.tty_fatal`, as C's handler); an outside SIGBUS/SIGABRT still depends on the guard's timing, and macOS lost that race for `restore_bus` (run 39350728011): CI records those two on macOS as an advisory until #794, ruling R-yw01-1 in yw01's note) |
| G2 | **a wait over the tty, the signal pipe and job pipes.** sagitta's loop is one `poll(2)` over the tty, a self-pipe and per-job pipes with a timer as the timeout (`01-architecture.md`). | yw01 (tty + signals), yw04 (jobs), yw11 (LSP pipes) | `os_signal_wait_fd(fd, set)`: ONE descriptor and the signal set, no deadline; `net_wait` is the socket reactor and takes net handles; `os_wait_poll` polls children. No wait over N fs descriptors, no timeout on the signal wait. | the prelude's signatures (no program can be written) | wolf-lang (gap: `os_signal_wait_fds(fds: List[int], set, deadline_ms) -> (int, int)`, the ready descriptor or the meaning, `[os.signal.wait.fd]`'s shape widened; the timer is yew's own heap) — **filed as wolf-lang#795**; the `VTIME` polling interim (#93 R2) is in `term.tty` |
| G3 | **`fsync` of a file and of a directory; create-exclusive; rename-without-replace.** The atomic save (`s08`): write a temp in the same directory, `fsync`, `rename`, `fsync` the directory; the journal appends and syncs. | yw02 | no `fs_sync`/`fs_fsync` in the prelude; `fs_rename` replaces (wolf-lang#706 asked for no-replace); `fs_create_private` is the one `O_EXCL` shape. | the prelude (no name); `fs_write_bytes` then a kernel crash cannot be witnessed in CI, only the absent call. **yw02 met it by name**: the save and the journal call `no_sync_g3`/`no_sync_dir_g3`, which sync nothing; sagitta's fault shim logs C's save as `write, fsync-file, fchown, close, rename, fsync-dir, …` and the port's as `write, fchown, close, rename, close` (`notes/yw02-evidence/g3/`); the kill9 driver is green through every sweep and red at the one lane that needs a directory fsync to fail, and the replica's 500 SIGKILLs never corrupt | **wolf-lang#796**; s248's `fs_sync`/`fs_sync_dir` merged at `808ce11a`, unreleased at yw02's end — the pin that has them turns `save_fault_shim_contract` and the replica's determinism order green |
| G4 | **`realpath`.** Workspace identity is the realpath's hash (`00-decisions.md`, Workspace state). | yw06 | no `fs_realpath`/`fs_canonical`; boreutils walks a path a component at a time with `fs_read_link` (`src/bore/paths.lu`), which is a port-side answer for most paths but not `..` across symlinks. | the prelude (no name); **yw02 needed it first** (the journal and the backup are keyed by the realpath's hash) and walks it (`text.file_realpath`) | **wolf-lang#797**; s248's `fs_realpath` unreleased at yw02's end |
| G5 | **`xattr`** (one use, the cloud-storage save preset, `s55`). | yw14 | none; `fs_stat`'s twenty words carry no attribute (wolf-lang#685). | the prelude | wolf-lang (#685 covers it; a `fs_xattr_get/set` pair) |
| G6 | **a GC for Fletch in wolf's memory model.** sagitta: a mark-sweep over tagged values with explicit roots, collections at opcode boundaries. wolf has no raw pointers and frees regions wholesale. | yw07 | the shapes: (a) an arena of tagged values in one `List[FlValue]` with indices for references and a mark bit, sweep compacting into a fresh list with an index remap (regions and indices, no pointers); (b) a wolf-managed graph with `shared`/`weak` (ruled out: Fletch values are cyclic and `shared` must be acyclic, E1006). | a toy VM measured on both shapes is yw07's first week; (a) is the recommendation | nothing to file: a design choice inside the port (ruling R3 asks for the shape to be fixed before yw07) |
| G7 | **the checked machine as ASan/UBSan/valgrind.** sagitta's CI has gcc, clang, ASan/UBSan, valgrind and a determinism lane. | every lane | `wolf test` runs a test's `main` on the checked machine (`wolf_mem::ubcheck`): every allocation modelled, every UB row an E1401 — that is ASan + UBSan + valgrind's definite-leak check for wolf code, with a step budget. The native run (`tools/check-test --native`) is the determinism twin. What it cannot stand in for: a C library's bugs (none linked), and a budget past which a test is `unsupported`, not `ok` (`notes/yw00-the-map.md` §4: the 3 MiB arena test). | `tools/check-test` on the port: 11 files `ok` on the checked machine | nothing to file |
| G8 | **a sub-millisecond clock.** Every perf gate is nanoseconds (`budgets.txt`); the port's harness needs `CLOCK_MONOTONIC` at ns. | yw01's gates, every lane's ratio | `clock_ms`, `time_now_ms`, `time_unix_ms` — milliseconds. `tools/perf-unicode` batches 32 scans a round to measure. | `notes/yw00-evidence/witness/clock-ms.lu`: two `clock_ms` reads around a 100 us loop answer the same value | wolf-lang (gap: `clock_ns()`); wolf-std (`time.now` at ns) |
| G9 | **an HTTP/1.1 client** (localhost only; TLS through curl). | yw12 | `std.net` has sockets and lobo's server-side; no client. The port writes its own over `net_connect`, a std candidate. | — | wolf-std (candidate, not a gap) |
| G10 | **`wolf test` discovers `test_*` only in a package's alphabetically first file.** | every lane's tests | `ubcheck::discover_tests` reads `pkg.files[0]` (`crates/wolf_mem/src/ubcheck.rs:2356-2374` at `72de141f`): `src/util/arena_test.lu` had its `test_*` run one by one, `src/util/buf_test.lu` beside it fell back to `main`. | `notes/yw00-evidence/witness/test-discovery/` (two files, one `wolf test` run) | wolf-lang (bug) |
| G11 | **no bitwise not.** `~x` is not wolf syntax (E0107). | every bit-field unit | `x - (x & m)` clears bits; `x ^ m` flips them. Grammar has `&`, `\|`, `^`, `<<`, `>>`. | `notes/yw00-evidence/witness/bitnot.lu` | wolf-lang (gap or spec note: `~`, or a `bits.not`) |
| G12 | **a resident-byte model per structure** (`memacct.h`: `arena_resident_bytes`, `strmap_insert_cost`), the symbol index's memory cap (s57.33). | yw11 | `region_bytes(r)` is a region's ledger, per tier; no per-value cost. The cap can be charged by the region holding the index. | — | nothing yet; yw11 decides |
| G13 | **`==` on a `List`** is refused (`no Eq for these this edition`). | tests, buffers | element-wise loops (`same_bytes`). The conservatism ledger, known. | the generator's `--check` needed its own compare | nothing new to file |
| G14 | **a `match` arm cannot assign** (E0208): `0 => d.x = v` | the decoder's state | if-chains (`unicode.utf8.pend_set`). | — | spec question for the orchestrator (grammar), not a bug |
| G15 | **module state of a `List`** is refused (`[mem.static.3]`); only integers, `byte`, `bool`, floats and `str`. | every table | `str` constants of 7-bit digits (§1). The design is sound (static data only); the port's encoding is the cost: 2 chars an entry, 113 KB of source for the trie. | probe c1 | nothing to file (design); a `const` `List[byte]` of literal bytes would be the natural ask if the maintainer wants one |
| G16 | **Linux aarch64 builds no tier** (wolf-lang#614). | CI's third host | asserted by name in CI, as pelt. | — | wolf-lang#614 (open) |
| G19 | **a module-level function used as a function value is refused once its module has more than one file** ("cannot compile this yet — a vtable slot `@term.env_getv.fv` outside this object's subset"). | yw01 | the conservatism ledger. A closure over the function (`fn(k: str) env_getv(k)`) built on the native tier; see G20 for the release tier. The port passes no function values across modules: the environment is a VALUE, `term.Env` (`env_process()`, `env_of(table)`), as every `getenv`-injected API of sagitta's. | yew `7acaa89` (red by name, green as a closure) | wolf-lang (ledger row) |
| G20 | **the release tier refuses a closure made in one object and called in another** ("a vtable slot `@main.cls0` outside this object's subset"), and the inliner moves a closure's making across the partition (a one-line `term.render_new_env` inlined into `main`, refused as `@term.render_new_env.cls0`). | yw01, every lane with a callback | native tier green; single file green; a closure made and called inside one module green (witnesses d, f, g); the entry's closure into a module red (e); the inlined twin red (the demo). The port's answer is G19's: values, not function values, across modules. | the lane's `cls/{a..g}` witnesses on kasumi, `--codegen-report` of the demo (`notes/yw01-the-terminal.md`, Issues) | wolf-lang (bug: the partition must export or not inline a closure's slot) |
| G21 | **`clock_ms()` inside a function of a multi-module program on the release tier** is "calls outside the resolved surface" (the span is the call); `time_now_ms()` in the same place builds. | yw01's demo | — | the demo at yew `4e6e65e`'s parent | wolf-lang (ledger row to name) |
| G22 | **`wolf fmt` is not a fixed point** on `src/term_render_test.lu`: the second pass changes the first's output, the third nothing. | every lane's `check-fmt` | run it twice. | the file at the head, `wolf fmt` twice | wolf-lang (bug) |
| G23 | **`os_exe()` under `wolf test` is `wolf`**: a self-re-executing test (sagitta's child-role tests: the exit-4 bug scenarios) spawns the compiler on the checked machine; `wolf test` takes no `--nocapture`. | every lane with a child-role test | hand-shake first (`--self-check` exits 7), skip LOUDLY on both streams, cover the scenarios in the native run (`tools/check-test --native`). | `src/term_render_test.lu`, `src/util_log_test.lu` | wolf-lang (a child-role facility for `wolf test`) |
| G18 | **a `mut` parameter inside a `region` block is E1010** ("still holds a value allocated in region … when the region is freed"), whatever the struct holds — a scalar-only RNG state too. | every per-turn scratch loop | the conservatism ledger: the analysis does not see that nothing of the region's reaches the struct. Thread the state functionally (`tools/fuzz-unicode/main.lu`: every mutator answers the next RNG state) or keep the loop's scratch out of a region. | `tools/fuzz-unicode/main.lu`'s header; the refused form is in the lane's log (`notes/yw00-the-map.md` §4) | wolf-lang (precision of the region analysis; a bug if the spec says a scalar struct may be written) |
| G17 | **a native `wolf test` harness**: today `test_*` fns run on the checked machine only and `main`-shaped files run natively only as a fallback (`test_cmd.rs:645-665`). | every lane | `tools/check-test --native` builds and runs each test file. | — | wolf-lang (known: "the native multi-test harness lands", `test_cmd.rs:61-65`) |
| G24 | **a `distinct int` is not `Copy`**: `a as int` moves `a`, a second read is E1001, and nothing opts it in (no `Copy` trait, E0301). | yw02's coordinates, every typed id | `distinct` at function boundaries only, `int` fields (§1); `copy a` at a read also works | `notes/yw02-evidence/witness/distinct-copy` | wolf-lang (design: an opt-in, or `distinct` of a Copy type is Copy) |
| G25 | **a module `const` of `wrapping[u64]` is "not static data"** ([mem.static.3], exit 4), an integer literal included. | yw02's hash primes, every hash | zero-argument functions | `witness/wrapping-const`, `wrapping-const-unreached` | wolf-lang (ledger row or bug: a literal is static data) |
| G26 | **an inherited descriptor ≥ 3 is not an fs handle**: `fs_write_chunk(5, …)` answers `io`. | yw02's torture child (`YEW_TORTURE_READY_FD`), every inherited pipe | reopen `/dev/fd/N` (Linux, macOS) | `witness/inherited-fd` | wolf-lang (gap: adopt an inherited descriptor) |
| G27 | **module state of a run-time value is E1010**: a process-wide registry of strings cannot be a module `var`. | yw02 (the journal owner list), yw03 (`Ed`) | a value threaded through its owner (§1) | `witness/module-str` | nothing to file (design); the idiom row is the answer |
| G28 | **E1004 refuses `m.s = copy g(mut t)`** where `g` answers a struct of scalars: "a value from `t`'s region into `m`'s", the `copy` notwithstanding. | yw02's file metadata snapshot | build a fresh literal of the scalar fields | `witness/region-copy` | wolf-lang (precision of the region analysis) |
| G29 | **`wolf test` runs a refused `main` natively and says `ok`**: past the checked machine's 20M-step budget (`wolf_mem/src/ubcheck.rs:228`) a file falls back to one native run (`test_cmd.rs:648-669`), visible only as `detail: "exit(0) [native]"` in `--json`. | every lane's checked-machine claim | read `--json`; run the fallback files case by case on the checked machine (yw02's note §4) | `wolf test --json src` on yw02's head: 10 of 20 `text_*` files `[native]` | wolf-lang (print the fallback in the human output; count it in the summary) |
| G30 | **no non-blocking pipe write and no write-readiness wait**; no `os_fork` at 0.2.33. | yw02's clipboard writer (C forks twice and writes non-blocking so a tool that never reads cannot block the loop) | a STOP: the port exits 4 naming the gap; OSC 52 is unaffected | the fork's `probe/rg1` (a 1 MiB write to an unread pipe never returns), `rg2` (`os_fork`: E0301) | wolf-lang (gap: `O_NONBLOCK` on a pipe end with EAGAIN as a row, and a write-ready wait); `os_fork` is 0.2.34's |
| G31 | **no host OS/arch query** (comptime or run time). | yw02's clipboard (pbcopy is a macOS-arm64 compile-time choice in C) | PATH alone, said in `text.clipboard`'s header (a Linux PATH with a `pbcopy` differs from C) | the fork's `probe/rg0` (`os_abi`: E0301) | wolf-lang (gap) |
| G32 | **the fs rows C yew uses and 0.2.33 lacks**: `access(2)`, `O_NOFOLLOW`, an advisory lock, a handle's dev/ino (`fs_fstat` answers three words), `mkfifo`. | yw02 (save, journal, clipboard, the serial test's FIFO) | each worked around by name (mode bits against uid/gids for `access`; `lstat` before open; the `mkfifo` utility) | the prelude (no name) | wolf-lang (one gap issue listing them) |

## 6. Rulings asked

Each with the lane's recommendation; the orchestrator asks the
maintainer.

- **R1 — the fatal-signal restore (G1).** (A) `os_exit_signal(m)`
  (ruling #88 R2, 0.2.33): the program's own deliberate death after its
  own restore — right for `yew_tty_suspend`'s `SIGTSTP` and a `--crash`
  demo, wrong for a trap, which never returns to the program. (B) a
  supervisor process: `yew` spawns itself (`os_spawn_job` with the tty
  and a flag) and the parent, which never enters raw mode, restores the
  mode it saved when the child ends by any signal (`os_wait_status`
  answers `-N`) and exits with the child's status; works at 0.2.32 with
  no runtime change; costs a second process, a second pid in `ps`, and
  the parent must forward `SIGWINCH`/`SIGTSTP`/`SIGCONT` to the child
  (ruling #79's `os_signal_send`). (C) a runtime call,
  `os_term_restore_at_exit(fd, mode)` (or `os_at_exit_write(fd, bytes)`
  plus the mode): the runtime restores the mode and writes the bytes on
  EVERY exit it owns — a normal return, `os_exit`, and the trap path
  before `abort()` — the same guarantee sagitta's `atexit` + the
  `yew_bug` prehook give, with no wolf code in a handler; a kernel
  `SIGKILL` restores nothing in C either, and the fatal signals a wolf
  program can receive from outside (`TERM`, `HUP`, `QUIT`) are
  listenable and restored by the program. **Recommend C**, with B as
  what yw01 ships if C is not in the release yw01 pins (yw01's contract
  says both). The track index's "s246's `os_exit_signal`" row is A, and
  A alone does not cover a trap.
- **R2 — the multi-descriptor wait (G2).** (A) widen
  `os_signal_wait_fd` to a list of descriptors with a deadline:
  `os_signal_wait_fds(fds, set, deadline_ms) -> (which, meaning)`;
  (B) yew drives its job pipes through tasks and channels (`scope`,
  `spawn`) and the tty through `os_signal_wait_fd` — a second thread
  per job against invariant 8's spirit and sagitta's single-threaded
  core; (C) `net_wait` learns fs handles. **Recommend A** for yw01's
  contract (yw01 needs only the tty and the signal set, which 0.2.32
  has; the list arrives for yw04's jobs).
- **R3 — the Fletch GC's shape (G6).** (A) an arena of tagged values
  with indices and a mark bit, compacting sweep (regions and indices,
  never pointers); (B) `shared`/`weak` graph — refused by E1006 for a
  cyclic heap. **Recommend A**, measured on a toy VM in yw07's first
  deliverable before the real VM.
- **R4 — the modules line.** The port is always the full build; C
  yew's `--version` second line is `modules: lsp ai fuss plugins`.
  (A) keep it byte-identical as the full build (recommended); (B) a
  `yew --version` that says `modules: all` — a golden change, refused
  by rule 2.
- **R-yw02-1 — M-YW2's shape** (yw02's note §5): (A) M-YW2 at yw02 is
  `make torture`'s campaign-02 lane — sagitta's `kill9` driver over the
  port's torture child, green but for G3's named red, plus the late
  lanes through the port's replica in a container; `batch-kill9` moves
  to yw09 (`--batch`) and the live-editor lane to the first lane with an
  editor that takes `:` (yw04, or yw03 with a minimal `:`); (B) M-YW2
  waits for yw09 as worded. **Recommend A** (implemented in CI).
- **R-yw02-2 — the KNOWN-RED shape.** A test that accepts exactly G3's
  red line and fails on anything else, said on both streams, until the
  pin has the syncs (recommended, implemented), against a skip.
- **R-yw02-3 — the clipboard's subprocess backends (G30).** (A) a STOP,
  exit 4 by name, until wolf has a non-blocking pipe write and `os_fork`
  (recommended, implemented); (B) a blocking writer (refused,
  invariant 4); (C) a helper thread per write.
- **R5 — the module-name collisions** (`unicode`, `term`, `search`
  against std): (A) the port keeps sagitta's names and aliases std
  where both are needed (recommended, done); (B) prefix the port's
  (`yew_term`).

## 7. The next contracts

One paragraph each; yw01's is drafted in full
(`notes/contracts/yw01-the-terminal.md`).

- **yw02 — the text engine** (sagitta s07–s12; `src/text/` 11,688
  lines; `src/unicode/coords.c`, `u16.c`). Piece tree with byte and
  line subtree counts (`piece.c`), the line index, byte-exact load with
  binary/CRLF/BOM detection and no mmap (`file.c`), the atomic save
  decision table and the crash journal (`journal.c`), typed coordinates
  and the cursor engine with mark bias rules (`cursor.c`, `mark.c`,
  `coords.c`), the undo tree with transactions and its serialization
  (`undo.c`), registers and the OSC 52 clipboard with subprocess
  fallbacks (`register.c`, `clipboard.c`, `yankstack.c`), the
  differential fuzz against a naive oracle (`fuzz_textbuf`). Goldens:
  `test_piece`, `test_file*`, `test_undo*`, `test_cursor`, `test_mark`,
  `test_register`, `test_coords`, `test_u16*` ported; `make torture`'s
  batch and live lanes against the wolf binary (M-YW2). Gaps: G3
  (fsync, exclusive create), G5 (xattr); until G3 lands the save is
  write-rename without the syncs and says so by name. **Landed by yw02**
  (`notes/yw02-the-text-engine.md`).
- **yw03 — the modal core** (s13–s17; `src/edit/` modes, keymap,
  dispatch, motion, select, multicursor; `src/unicode/wordbreak.c`,
  `tables_wb.c`). The key trie and mode layers, the named-command
  registry, L and I modes (notepad), the viewport and statusline, W and
  B unit engines (word break from the generator's `--word-break`
  mode), H and multi-cursor as one transaction. Goldens: campaign 03's
  PTY and script cases (M-YW3). **Drafted in full by yw02**
  (`notes/contracts/yw03-the-modal-core.md`), with sprint 15's `ui`
  files and the command registry's shape (no function value across a
  module boundary) as its first ruling.
- **yw04 — execute and search** (s18, s18.5, s19, s20, s21, s57.17,
  s57.18, s57.23–s57.32; `src/search/`, `src/edit/shell*`, `job.c`,
  `src/ui/comp*`, `shctx.c`; `src/unicode/category.c`, `case.h`,
  `tables_cat.c`, `tables_case.c`). The `:` prompt with its editing,
  history and completion engine, shell jobs under `$SHELL -c` with the
  terminal handed over and back (process groups and the foreground
  terminal, available since 0.2.31), the Thompson NFA/DFA regex with
  the literal fast path, search and replace. Goldens: the regex corpus
  (`re_golden.h`), the `:!` PTY cases, `fuzz_re_*`. Gaps: G2 for the
  job pipes (ruling R2).
- **yw05 — panes, tabs and groups** (s22, s23, s24, s57.8, s57.13–
  s57.16, s57.22; `src/ui/` layout, tabs, groups, strip, region, draw,
  ctxmenu, menu, panel). The pane tree in cells, the clickable-region
  registry, tab strip and overflow, facsimile's group model, context
  menus. Goldens: campaign 05's PTY cases.
- **yw06 — workspace, finder and mouse** (s25, s26, s27, s56.5,
  s57.5–s57.7, s57.9–s57.12, s57.20; `src/ws/`, `src/ui/picker*`,
  `mouse.c`, `typejump.c`). Workspace state under XDG in Fletch data
  (the frozen schema, hand-emitted until yw09), the fuzzy finder,
  mouse routing, runtime staleness. Goldens: Sprint 42's field checks
  on the wolf binary (M-YW5); pax pins the static binary (M-YW-PAX1,
  track rule 7 from here). Gaps: G4 (realpath).
- **yw07 — Fletch core** (s28–s31; `src/fl/` lex, parse, compile, vm,
  value, gc, opcodes, data, module, std*). The frozen spec
  (`.docs/fletch-spec.md`, copied verbatim), lexer, parser, bytecode,
  the VM with switch dispatch, the GC per ruling R3, the std modules.
  Goldens: `tests/fletch/` conformance through `yew fl`. Gaps: G6.
- **yw08 — REPL, errors, conformance and perf** (s32, s33; `src/fl/`
  repl, trace, suggest, vmcheck; `src/flcli.c`). `yew fl`, stack
  traces, the error-quality pass, `fl_smoke`'s baselines and the
  config-load gate. Goldens: the 39 conformance runs and the GC-stress
  run (M-YW6).
- **yw09 — Fletch in the editor** (s34–s38; `src/fl/` flapi, flconf,
  fleval, flhook, flruntime, fltxn, handle, record, macrolib, origin;
  `src/edit/batch.c`). Editor handles and the capability-checked
  binding layer, the recorder and the round-trip law (the port's own
  round-trip harness, since sagitta's is in-process), `init.fl` and the
  workspace `.yew.fl` trust prompt, `--batch`, the macro UX. Goldens:
  the script suite and the round-trip and batch tests (M-YW7).
- **yw10 — highlighting** (s39–s42.5; `src/syn/`, `src/syncli.c`,
  `runtime/syntax/`, `runtime/themes/`). The incremental line-state
  engine, definitions as Fletch data, the 48 shipped modes and two
  themes, embedded languages. Goldens: all 432 `.spans` through
  `scripts/check-syn-assets.sh` (M-YW8); M-YW-PAX2.
- **yw11 — completion and LSP** (s43–s47; `src/mod/lsp/`, `src/ws/sym*`,
  `src/edit/shadow*`, `completion.c`, `lsp_cmds.c`). Ghost text, the
  symbol index with its resident cap (G12), JSON-RPC over pipes,
  diagnostics, completion, hover, goto, references, rename. Goldens:
  the LSP conformance runs and wolf-lsp's harness replayed against wolf
  yew (M-YW9).
- **yw12 — AI** (s48–s50; `src/mod/ai/`). The HTTP/1.1 client (G9),
  the curl subprocess backend, shadow AI, the privacy defaults and
  redaction. Goldens: the AI script and PTY cases, `fuzz_ai_*`
  (M-YW10).
- **yw13 — FUSS and git** (s51–s53; `src/mod/git/`). Porcelain parsers,
  the status cache on a wall clock, F mode, hunk signs, blame, diff
  views. Goldens: the real-git fixtures and the 19 FUSS PTY cases
  (M-YW11).
- **yw14 — plugins** (s54, s55, s55.5; `src/mod/plug/`). Discovery,
  lifecycle, hooks, capability prompts, `yew pkg`, the two example
  plugins. Goldens: the 53 package cases and the plugin PTY cases
  (M-YW12). Gaps: G5.
- **yw15 — performance** (s56, s57 and its audit; `src/util/prof.c`,
  `rss.c`, `calib.c`, `tests/perf/`, `tests/size/`). Every gate in
  `budgets.txt` measured on kasumi beside C yew, the ratios recorded,
  the ratchet proposed; the size ledger; the static profile through
  muzzle when it links yew. Gate: every ratio within 2x (M-YW13), a
  ruling on each ratchet. Gaps: G8.
- **yw16 — audits and release** (s58–s60; `docs/`, `src/tutor.c`). The
  invariant audits on the port, the checked machine in sagitta's
  sanitizer lanes' place (G7), the manual and man pages, the tutor,
  1.0 (M-YW14); M-YW-PAX3 after pax's storage.

## 8. Corrections to the track index

- The index's campaign-00 row says `std.unicode` "has no width or
  grapheme tables (an `sc` lane later)": true, and yw00 did not wait
  for one — the port's tables are its own, generated from `ucd/`, and a
  std `sc` lane would be a second copy; the row should say "the port's
  own (yw00)".
- The campaign-01 row names "s246's `os_exit_signal`" for the restore;
  it is one of three shapes and does not cover a trap (ruling R1).
- "CI on linux x86-64, macOS arm64 and linux aarch64": the port's
  suites run on two; linux aarch64 asserts wolf's refusal (G16) and
  runs the oracle. The index's M-YW0 "three hosts" holds for the oracle
  job, not the wolf suites, until wolf-lang#614.
- The contract names sagitta's `CLAUDE.md` as an input; it is
  untracked (`.gitignore` excludes it) and exists only in the
  maintainer's checkout, where yw00 read it.
- The contract names the spec clause `[os.signal.gaps.note]`; no such
  anchor exists at `72de141f` (the signal design notes are
  `[os.signal.shell.note]` and `[os.signal.group.note]`).
