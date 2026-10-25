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
| a process-wide option (`width_opts`) | a module `var` behind `unsafe { }` with `// # Safety:` naming invariant 8 (single-threaded core) | `[mem.static.2]`; the `unsafe` census is this table: `unicode.width`'s `ambiguous_wide`, `text.file`'s `temp_counter` and `text.undo`'s `text_hash_calls` (yw02), `edit.gutter`'s warn-once mask (yw03), nothing else in the editor (yw04 added none; three test files keep a fixture-name counter each) |
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
| a rebuilt array swapped in and the old one freed (`free(old)`) | in a value that lives for the session, a spare `List` pair rebuilt in place and swapped (the grapheme index); per-iteration scratch in a `region` block (yw02) | G33: a replaced `List` is held until its owner's region ends |
| a function-pointer table (`CmdDesc.fn`, `UnitEngine` vtables) | a handler KIND and an implementation id per row, and ONE `match` on literal ids (`edit.impl.run_impl`, each arm's `IMPL_*` name in a comment; the unit engines `edit.unit_next`'s `match` on the kind) (yw03) | no function value across a module boundary (G19/G20, wolf-lang#806); a `match` arm on a const NAME is a binding that matches everything (W0801) |
| a pointer lent into another struct for one call (the window's `CursorSet` as `ec.cset`, the editor's journals) | a swap through a local (`let t = a; a = b; b = t`) out and back around the call (`edit.edit_take`/`edit_give`), every return path restoring it (yw03) | a moved field must be stored back (E1001); a placeholder `List` costs 48 B an edit (G33) |
| `ed.c` calling `ui/*.c` that take `Ed *` | one module: the `ui` files campaign 03 owns are `src/edit/*.lu` with sagitta's names (yw03) | a module cycle is E0303 |
| a `poll(fd, 0)` between reads (the typeahead drain) | `term.tty_drain_begin`/`tty_drain_end`: `VMIN=0, VTIME=0` for the drain, the wait's mode after (yw03) | no zero-timeout readiness query on a tty at 0.2.33 (G2) |
| a field or local named `impl`, `take`, `use` or `scope` | another name (`impl_id`, `n_take`, `keep`) (yw03) | keywords |
| two files of one module each with a private `push_str` | one helper per module (yw03) | a module's private names are module-wide (E0302): file boundaries create no scopes |
| C's callback registries (`YewCompSource.enumerate`, a job's consumer, a generator, the menu's row source, `on_change`, `search_idle`) | an implementation id or kind per row and ONE `match` (`edit.cmdcomp`'s `comp_request`, `edit.cmdcomp_shell`'s source kinds, `INPUT_DONE_*` for a prompt's done callback, `TIMER_SEARCH_COUNT`); an arrival is a call by name (`cmdline_compgen_arrived`) (yw04) | no function value across a module boundary (G19/G20) |
| a per-keystroke rebuild inside the session-long `Ed` (the completion filter's ranked rows, the menu's items) | a pure function whose body is `copy region NAME { … }`, the result copied out once (yw04) | G33: a `List` replaced inside `Ed` is held to the session's end; `region { …; copy x }` is E1010, only the `copy region` form compiles (`notes/yw04-evidence/witness/region-copyout/`: 434 KB → 41 KB a rebuild) |
| per-call `malloc`/`free` of engine storage (the Pike VM's thread lists, the DFA's cache), a process-lifetime static cache | a caller-held `ReScratch`/`ReWorkspace` lent `mut`, a threaded `ReCache` (yw04) | G33 at the engine: 58.8 µs a call with fresh storage against 17.5 µs held (`notes/yw04-evidence/regex/engine-storage.txt`) |
| a struct holding `const TextBuf *` (`YewReInput`) | `ReInput` (the shape) plus the backing passed at each call, `tb` or `bytes` (yw04) | a stored lent value is E1004/E1002 |
| recursive descent over a parse tree (the regex AST, the Thompson construction) | explicit stacks and a pass in node-index order (yw04) | a deep native recursion is a bare SIGSEGV (G41) |
| libc `memchr` in a prefilter | a stride filter over the needle's rarest byte (yw04) | no vectorized byte search (G42) |
| `posix_spawn` with `envp` and a working directory | the process's own environment and cwd set around a SYNCHRONOUS spawn and restored (`edit.job_run_sync`, `:!!` and `A-h`) (yw04) | G36 |
| a list of C strings dropped from the front (the history cap) | a byte pool with offsets (`edit.cmdhist`'s `CmdHist`) (yw04) | G33: dropping the oldest never rebuilds the list |
| a `{` in a pattern literal | `{{` (yw04) | every string literal interpolates |
| `poll(2)` with a sub-tick timeout (the 25 ms ESC, a 16 ms idle timer) | `term.tty_wait`'s fine wait — the signal set and a `VMIN=0`/`VTIME=0` read polled each ms when a deadline is under the 100 ms tick — and `edit.loop`'s deadline-first turn when a tick read outlives a deadline (yw04, `3375b51`, `57f47dd`) | G2: no wait with a deadline at 0.2.33 |

## 2. Source directories

| sagitta `src/` | files | C lines | port lane | wolf unit(s) | what it needs beyond wolf-std |
|---|---|---|---|---|---|
| `src/*.c` (`main`, `args`, `flcli`, `syncli`, `tutor`) | 9 | 3,846 | yw01 (`main`, `args`), yw08 (`flcli`), yw10 (`syncli`), yw16 (`tutor`) | `src/yew.lu` and `args` | — |
| `src/util/` | 31 | 3,572 | **yw00** (arena, vec, strmap, intern, buf, sort), yw01 (`log`, `xdg`, `base64`), yw15 (`prof`, `calib`, `memacct`), **yw06** (`rss`: `YEW_PROF=1`'s checkpoints from `/proc/self`, which `mem.workspace50` reads), yw12 (`secret`; its name fragments pulled forward by yw04 for the history suggestions), yw01 (`runtime_asset`, `runtime_blob`) | `util` | `log`: `$XDG_STATE_HOME` and never fds 0–2 (fine); `memacct`: a resident-byte model wolf lacks (§5 G12; `rss` reads `/proc` on linux, and off linux answers 0 where C's macOS reads `ru_maxrss`, G12's) |
| `src/unicode/` | 21 | 12,534 | **yw00** (`utf8`, `grapheme`, `width`, `tables`), **yw02** (`coords`, `u16` — ported INTO `text`: `coords` reads the piece tree and the tree calls the grapheme index, a module cycle, E0303), **yw03** (`wordbreak`, `tables_wb`; `case`, `tables_case` — the selection case commands, `sel_actions.c:665`, needed them first), **yw04** (`category`, `tables_cat`: the generator's `--category`, byte-identical to sagitta's arrays) | `unicode` | none; the generator grew `--word-break` and `--case` (yw03) and `--category` (yw04) |
| `src/term/` | 10 | 4,910 | **yw01** | `term` (aliasing `std.term`) | the fatal-signal restore (§5 G1); a wait over tty + signals + job pipes (G2) |
| `src/text/` | 21 | 11,688 | **yw02** (with `unicode/coords`, `u16` and the cursor set's core from `edit/multicursor.c`) | `text` | `fsync` of a file and a directory (G3, met by name); `realpath` (G4, a walk); `xattr` (G5, yw14); the clipboard's subprocess backends (G30, a STOP); an inherited descriptor as a handle (G26) |
| `src/edit/` | 80 | 31,689 | **yw03** (`cmd`, `keymap`, `keys_default`/`keys_highlight` → `edit.keys`, `mode`, `dispatch`, `motion`, `word`, `block`, `indent`, `select`, `sel_actions`, `multicursor`'s editor half, `ed`, `loop`, `edit_cmds`, `file_cmds`, and `pairs` — s57.16's, ported here because `runtime/init.fl` sets `autopair`; `bind`/`option` only as far as `init.fl`'s `set` and `bind` rows reach, through `edit.config` and the literal reader `edit.fldata`, R-yw03-2), **yw04** (`readline_cmds` — the prompt's and I mode's readline keys; sagitta has no `s57_21` sprint file, `d52250b9`; `jumplist` with the change list's ring in `text.jumpring`, since the edit choke point records it; `search_cmds`; `shell`, `shell_cmds`, `job` and `shsession` as their SYNCHRONOUS half — `:!!`, `A-h`'s man, the environment table, the quoting — the async half, streaming, the filter, `:r !` and the session, refusing by name until `os_signal_wait_fds`, R-yw04-1; the named marks of `ed.c:1070-1100` as `edit.ed_marks`), **yw05** (`pane_cmds`: every `ed.pane.*` command through the registry), yw06 (`ws_cmds`), yw09 (`batch`, `flapi_cmds`, the full `bind`/`option`/`flconf`), yw11 (`lsp_cmds`, `shadow*`, `completion`), yw15 (`prof_cmds`) | `edit` | process groups and the foreground terminal for `:!` (ruling #79, available since 0.2.31); `ICRNL`/`OPOST`/`ISTRIP` in the raw mode (G34) |
| `src/search/` | 16 | 7,491 | **yw04** (`parse`, `compile`, `pike`, `dfa`, `literal`, `pack`, `regex`, `search` and `replace` → `search`, below `edit`; `overlay` and `searchui` take the `Ed` and are `edit.overlay`, `edit.searchui`) | `search` (aliasing `std.search`) | none; the port's regex is a `std.regex` candidate; a vectorized byte search (G42) |
| `src/ui/` | 74 | 46,140 | **yw03** (`viewport`, `statusline`, `gutter`, `message`, `draw`, `win`: sprint 15 is campaign 03's — corrected by yw02 — and every one takes the `Ed` that `edit` calls them with, a cycle wolf refuses (E0303), so they are `src/edit/*.lu` with sagitta's names; plus the two interims the goldens need: `tabs`' single-tab strip, `edit.tabs`, R-yw03-3, and a narrow `:` from `cmdline`, `edit.cmdline`, R-yw03-1), **yw05** (`layout` — the pane tree in cells, the ratio as C's float bits (G44) —, `region` in full, `glyphs`, `tabs` in full, `strip` — s23 §3's engine, corrected from yw06 —, `groups`, `groupnav`, `grouppicker`, `groupfromdir`, the border and dim-inactive half of `draw`, and the mouse router's click-to-focus, border drag and strip press/release; every one takes the `Ed`, so `src/edit/*.lu` with sagitta's names), **yw06** (`filter`, `picker`, `pickers`, `typejump`, the rest of `mouse` — one router at the pin's state, R-yw06-2 —, `ctxmenu` and `ctxrows` with `mouse.c`'s `ed.ui.context_menu` as `edit.ctxcmd`; all take the `Ed`, so `src/edit/*.lu`), **yw04** (`cmdline` in full as `edit.cmdline` with `cmdline_hist`, `cmdline_comp`, `cmdline_shell`, `cmdline_seams` and the interim `option_cmdline` — `:set NAME VALUE` over `Opts` until yw09; `cmdhist`, `cmdparse`, `cmdedit` — `A-e`'s `*command-line*` tab over a narrow `ed.tab.close`, R-yw04-5 —, `cmdcomp` with its `:!` half in `edit.cmdcomp_shell`, `compgen`, `compspec` — the 24 `runtime/completions/*.fl` copied verbatim, read by `edit.fldata` (R-yw04-4) —, `comphelp`, `compfish`, `shctx`, `menu` — s18.5 §5's ranked list, `menu.h:4-13` — and a narrow `region`, the menu's rows only, R-yw04-2), yw11 (`complmenu`, s44's) | `edit` (campaign 03's), `ui` (later) | none known |
| `src/ws/` | 28 | 10,820 | **yw06** (`workspace`, `walk`, `gitignore`, the hand codec `fl_emit`/`fl_parse`/`fllit`/`state_lit` as the interim production path — R-yw06-1, its strings `List[byte]` —, and `state_emit`/`state_parse`/`state_save`, which take the `Ed` and are `edit.state_*`), **yw04** (`fuzzy` with `finder.h`, pulled forward from s26 by s18.5 §1, `finder.h:5-7`: `ws.fuzzy`, the `ws` module's first file), yw09 (`state_fletch`, the swap to Fletch data that retires the hand codec, and `trust*` with `flconf.c`, its only consumer: R-yw06-5), yw11 (`sym*`) | `ws` | `realpath` (G4); XDG dirs; non-UTF-8 entry names (G40: skipped by the walk and logged, R-yw06-6) |
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
| `runtime/` (`init.fl`, 48 `syntax/*.fl`, 2 themes, tutor, presets, completions) | Fletch stays Fletch: the files are copied verbatim by the lane that first needs them and never edited. **yw03** needed `init.fl` and the two themes first (every editor frame paints in `quiver-dark` with `init.fl`'s keys and options): copied verbatim, embedded by `tools/gen-runtime` as `edit.runtime_blob` (the last resort after `$YEW_RUNTIME_DIR`, the install prefix and `./runtime`), checked against the pin by `tools/check-runtime`, and read by `edit.fldata`'s literal reader until Fletch (R-yw03-2); yw10 syntax; yw16 tutor |
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
| 04 execute and search | s18, s18.5, s19, s20, s21; s57.17, s57.18, s57.21, s57.23–s57.32 (the `:` prompt, its readline keys and `:!` completion; s57.21 placed by yw03) | yw04 | M-YW4: the regex corpus and the `:!` goldens |
| 05 UI and workspace | s22, s23, s24, s25, s26, s27; s57.5–s57.16, s57.20, s57.22, s56.5 (the field repairs) | yw05 (s22–s24, s57.8), **yw06** (s25–s27, s56.5 §1 and §6, s57.11, s57.12, and s57.13–s57.15 and s57.22 after s27's router, R-yw05-1 = A); **Decided** (R-yw06-4 = A): yw13 takes s56.5 §2–§4 and §7, s57.5, s57.6 §2–§3 and s57.7 (the FUSS drawer: `fuss_drawer_*` 6, `startup_directory_workspace`, `test_fussdrawer` 27, `test_fussexpand` 7), yw11 s56.5 §5 (`test_shadow_layout` 10) and s57.6 §1's LSP and symbol-index halves, yw10 s57.6's syntax half and s57.9's two goldens (`wolf.fl`'s colours); s57.9's and s57.10's C is in files yw03 and yw05 ported; s57.20 has no C at the pin; s57.16's auto-pairing landed early in yw03 (`edit.pairs`: `init.fl` turns it on, so every campaign-03 bracket goes through it) | M-YW5 as R-yw06-3 = A shapes it: the 81 reachable goldens by name and the automated twins of s42 §10's boxes (yw06's gate: CI's `goldens, campaign 05's workspace, finder and mouse` and `M-YW5's trials` steps; the field gate stays the maintainer's, after yw10 and yw09); M-YW-PAX1 |
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
| G1 | **the terminal restore on a fatal signal.** sagitta restores the terminal from `SIGSEGV`/`SIGBUS`/`SIGABRT`/`SIGTERM` handlers and an `atexit` (`s03` §4). wolf runs no code in a handler (`[os.signal.model]`) and the runtime restores nothing (`[os.term.mode]`). | yw01, invariant 6 | `TERMINATE`/`RELOAD`/`QUIT` are listenable: the program restores itself. The fatal three are the runtime's own: a wolf program reaches `SIGABRT` only through a trap (`wolf-trap: <kind>`, exit 134), `SIGSEGV` only through the stack guard, never through its own code. No hook runs on a trap. | `notes/yw00-evidence/witness/trap-leaves-raw.lu`: raw mode, then a `bounds` trap; the shell's `stty` after is raw | wolf-lang (design; ruling R1 in §6 — **#93 R1: interim B**, realised at yw01 as the guard sibling of sagitta `tty.c:243-349`: `os_exe() --guard`, a pipe at fd 3, the restore on EOF; wolf-lang#794 stands for the runtime's own restore. Its limit: sagitta's harness checks the restore at the reap, one shot, and the guard writes after the death — Linux wins that race, macOS lost it once for `restore_crash` (yew run 39346772578), so a self-raised fatal restores in-process first (`term.tty_fatal`, as C's handler); an outside SIGBUS/SIGABRT still depends on the guard's timing, and macOS lost that race for `restore_bus` (run 39350728011): CI records those two on macOS as an advisory until #794, ruling R-yw01-1 in yw01's note); **yw05, at 0.2.34**: `os_term_restore_at_exit` is registered (`3f35e72`) and restores on a trap, `os_exit`, `os_exit_signal` and a return from `main`, never on an outside signal (`notes/yw05-evidence/wait/witness/restore-at-exit/`), so the guard sibling stays for an outside `SIGSEGV`/`SIGBUS`/`SIGKILL`; the editor listens for `ABORT` and restores before that death in process, as C's handler table (`ccfddaa`), so `restore_abrt` is gated on macOS again; `restore_bus`, `notepad_restore_segv` and `notepad_restore_kill` stay macOS advisories (R-yw01-1) |
| G2 | **a wait over the tty, the signal pipe and job pipes.** sagitta's loop is one `poll(2)` over the tty, a self-pipe and per-job pipes with a timer as the timeout (`01-architecture.md`). | yw01 (tty + signals), yw04 (jobs), yw11 (LSP pipes) | `os_signal_wait_fd(fd, set)`: ONE descriptor and the signal set, no deadline; `net_wait` is the socket reactor and takes net handles; `os_wait_poll` polls children. No wait over N fs descriptors, no timeout on the signal wait. | the prelude's signatures (no program can be written) | wolf-lang (gap: `os_signal_wait_fds(fds: List[int], set, deadline_ms) -> (int, int)`, the ready descriptor or the meaning, `[os.signal.wait.fd]`'s shape widened; the timer is yew's own heap) — **filed as wolf-lang#795**; the `VTIME` polling interim (#93 R2) is in `term.tty`; **yw04** found its 100 ms granularity reordering events — a lone ESC followed by a key 25–100 ms later decoded as Alt-key, so sagitta's live-editor kill9 lane typed `:ed.quit_force` into the buffer, and `s21_search_word_under_cursor`'s 16 ms timer fired at ~211 ms — and refined it: the deadline's turn runs before bytes a tick read returns after it (`3375b51`), and a deadline under a tick waits finely, polled each ms (`57f47dd`, `620817e`); every mode switch of the interim is a `tcsetattr(TCSADRAIN)`, which on macOS can wait on output sagitta's harness does not read while it writes a burst, so `notepad_burst_keys`/`_paste` are an announced advisory there until the bump; the job half's red goldens and SKIPs (R-yw04-1, `notes/yw04-execute-and-search.md` §4) are this gap's; **Retired by yw05 at 0.2.34** (`1ebff08`): one `os_signal_wait_fds` over the tty, the jobs' descriptors and the signal set with the timer heap's deadline; the tick, the drain, the fine wait and the deadline-first turn are gone with every termios switch in the wait, the burst pair is gated on macOS again (yew#28), and the job half is green (campaign 04 104/104) |
| G3 | **`fsync` of a file and of a directory; create-exclusive; rename-without-replace.** The atomic save (`s08`): write a temp in the same directory, `fsync`, `rename`, `fsync` the directory; the journal appends and syncs. | yw02 | no `fs_sync`/`fs_fsync` in the prelude; `fs_rename` replaces (wolf-lang#706 asked for no-replace); `fs_create_private` is the one `O_EXCL` shape. | the prelude (no name); `fs_write_bytes` then a kernel crash cannot be witnessed in CI, only the absent call. **yw02 met it by name**: the save and the journal call `no_sync_g3`/`no_sync_dir_g3`, which sync nothing; sagitta's fault shim logs C's save as `write, fsync-file, fchown, close, rename, fsync-dir, …` and the port's as `write, fchown, close, rename, close` (`notes/yw02-evidence/g3/`); the kill9 driver is green through every sweep and red at the one lane that needs a directory fsync to fail, and the replica's 500 SIGKILLs never corrupt | **wolf-lang#796**; s248's `fs_sync`/`fs_sync_dir` merged at `808ce11a`, unreleased at yw02's end — the pin that has them turns `save_fault_shim_contract` and the replica's determinism order green; **Retired by yw05 at 0.2.34** (`452128f`): `fs_sync`/`fs_sync_dir` at C's sites; every acceptance deleted |
| G4 | **`realpath`.** Workspace identity is the realpath's hash (`00-decisions.md`, Workspace state). | yw06 | no `fs_realpath`/`fs_canonical`; boreutils walks a path a component at a time with `fs_read_link` (`src/bore/paths.lu`), which is a port-side answer for most paths but not `..` across symlinks. | the prelude (no name); **yw02 needed it first** (the journal and the backup are keyed by the realpath's hash) and walks it (`text.file_realpath`) | **wolf-lang#797**; s248's `fs_realpath` unreleased at yw02's end; **Retired by yw05 at 0.2.34** (`f249cbb`): `text.file_realpath` is `fs_realpath` |
| G5 | **`xattr`** (one use, the cloud-storage save preset, `s55`). | yw14 | none; `fs_stat`'s twenty words carry no attribute (wolf-lang#685). | the prelude | wolf-lang (#685 covers it; a `fs_xattr_get/set` pair) |
| G6 | **a GC for Fletch in wolf's memory model.** sagitta: a mark-sweep over tagged values with explicit roots, collections at opcode boundaries. wolf has no raw pointers and frees regions wholesale. | yw07 | the shapes: (a) an arena of tagged values in one `List[FlValue]` with indices for references and a mark bit, sweep compacting into a fresh list with an index remap (regions and indices, no pointers); (b) a wolf-managed graph with `shared`/`weak` (ruled out: Fletch values are cyclic and `shared` must be acyclic, E1006). | a toy VM measured on both shapes is yw07's first week; (a) is the recommendation | nothing to file: a design choice inside the port (ruling R3 asks for the shape to be fixed before yw07) |
| G7 | **the checked machine as ASan/UBSan/valgrind.** sagitta's CI has gcc, clang, ASan/UBSan, valgrind and a determinism lane. | every lane | `wolf test` runs a test's `main` on the checked machine (`wolf_mem::ubcheck`): every allocation modelled, every UB row an E1401 — that is ASan + UBSan + valgrind's definite-leak check for wolf code, with a step budget. The native run (`tools/check-test --native`) is the determinism twin. What it cannot stand in for: a C library's bugs (none linked), and a budget past which a test is `unsupported`, not `ok` (`notes/yw00-the-map.md` §4: the 3 MiB arena test). | `tools/check-test` on the port: 11 files `ok` on the checked machine | nothing to file |
| G8 | **a sub-millisecond clock.** Every perf gate is nanoseconds (`budgets.txt`); the port's harness needs `CLOCK_MONOTONIC` at ns. | yw01's gates, every lane's ratio | `clock_ms`, `time_now_ms`, `time_unix_ms` — milliseconds. `tools/perf-unicode` batches 32 scans a round to measure. | `notes/yw00-evidence/witness/clock-ms.lu`: two `clock_ms` reads around a 100 us loop answer the same value | wolf-lang (gap: `clock_ns()`); wolf-std (`time.now` at ns) |
| G9 | **an HTTP/1.1 client** (localhost only; TLS through curl). | yw12 | `std.net` has sockets and lobo's server-side; no client. The port writes its own over `net_connect`, a std candidate. | — | wolf-std (candidate, not a gap) |
| G10 | **`wolf test` discovers `test_*` only in a package's alphabetically first file.** | every lane's tests | `ubcheck::discover_tests` reads `pkg.files[0]` (`crates/wolf_mem/src/ubcheck.rs:2356-2374` at `72de141f`): `src/util/arena_test.lu` had its `test_*` run one by one, `src/util/buf_test.lu` beside it fell back to `main`. | `notes/yw00-evidence/witness/test-discovery/` (two files, one `wolf test` run) | wolf-lang (bug) |
| G11 | **no bitwise not.** `~x` is not wolf syntax (E0107). | every bit-field unit | `x - (x & m)` clears bits; `x ^ m` flips them. Grammar has `&`, `\|`, `^`, `<<`, `>>`. | `notes/yw00-evidence/witness/bitnot.lu` | wolf-lang (gap or spec note: `~`, or a `bits.not`)  **yw07 adoption:** 0.2.35 / s252 clarifies integer `!x` (not `~x`); release adopted in `7a9ae6e`. Existing explicit mask expressions remain; no new port-wide rewrite is claimed. |
| G12 | **a resident-byte model per structure** (`memacct.h`: `arena_resident_bytes`, `strmap_insert_cost`), the symbol index's memory cap (s57.33). | yw11 | `region_bytes(r)` is a region's ledger, per tier; no per-value cost. The cap can be charged by the region holding the index. | — | nothing yet; yw11 decides |
| G13 | **`==` on a `List`** is refused (`no Eq for these this edition`). | tests, buffers | element-wise loops (`same_bytes`). The conservatism ledger, known. | the generator's `--check` needed its own compare | nothing new to file |
| G14 | **a `match` arm cannot assign** (E0208): `0 => d.x = v` | the decoder's state | if-chains (`unicode.utf8.pend_set`). | — | spec question for the orchestrator (grammar), not a bug |
| G15 | **module state of a `List`** is refused (`[mem.static.3]`); only integers, `byte`, `bool`, floats and `str`. | every table | `str` constants of 7-bit digits (§1). The design is sound (static data only); the port's encoding is the cost: 2 chars an entry, 113 KB of source for the trie. | probe c1 | nothing to file (design); a `const` `List[byte]` of literal bytes would be the natural ask if the maintainer wants one |
| G16 | **Linux aarch64 builds no tier** (wolf-lang#614). | CI's third host | asserted by name in CI, as pelt. | — | wolf-lang#614 (open) |
| G19 | **a module-level function used as a function value is refused once its module has more than one file** ("cannot compile this yet — a vtable slot `@term.env_getv.fv` outside this object's subset"). | yw01 | the conservatism ledger. A closure over the function (`fn(k: str) env_getv(k)`) built on the native tier; see G20 for the release tier. The port passes no function values across modules: the environment is a VALUE, `term.Env` (`env_process()`, `env_of(table)`), as every `getenv`-injected API of sagitta's. | yew `7acaa89` (red by name, green as a closure) | wolf-lang (ledger row)  **yw07 adoption:** RETIRED at 0.2.35 / s251: environment function values `05fd414`, shared cursor sort `4c6462c`, undo clocks `f10e937`. Mutable registries are a separate OPEN gap, G48 / wolf-lang#917. |
| G20 | **the release tier refuses a closure made in one object and called in another** ("a vtable slot `@main.cls0` outside this object's subset"), and the inliner moves a closure's making across the partition (a one-line `term.render_new_env` inlined into `main`, refused as `@term.render_new_env.cls0`). | yw01, every lane with a callback | native tier green; single file green; a closure made and called inside one module green (witnesses d, f, g); the entry's closure into a module red (e); the inlined twin red (the demo). The port's answer is G19's: values, not function values, across modules. | the lane's `cls/{a..g}` witnesses on kasumi, `--codegen-report` of the demo (`notes/yw01-the-terminal.md`, Issues) | wolf-lang (bug: the partition must export or not inline a closure's slot)  **yw07 adoption:** RETIRED at 0.2.35 / s251: shared stable state/fuzz sort `c96f823`, environment `05fd414`, clocks `f10e937`; the twin prints `[1 2 3 3 11 22]` on release, while 0.2.34 refuses it (evidence `b78fd68`). G47/G48 remain separate. |
| G21 | **`clock_ms()` inside a function of a multi-module program on the release tier** is "calls outside the resolved surface" (the span is the call); `time_now_ms()` in the same place builds. | yw01's demo | — | the demo at yew `4e6e65e`'s parent | wolf-lang (ledger row to name) |
| G22 | **`wolf fmt` is not a fixed point** on `src/term_render_test.lu`: the second pass changes the first's output, the third nothing. | every lane's `check-fmt` | run it twice. | the file at the head, `wolf fmt` twice | wolf-lang (bug)  **yw07 adoption:** Upstream fixed by s250, adopted in `7a9ae6e`; two test files canonicalized in `35e21b9`, closeout format check passes. No port-local second-pass workaround added. |
| G23 | **`os_exe()` under `wolf test` is `wolf`**: a self-re-executing test (sagitta's child-role tests: the exit-4 bug scenarios) spawns the compiler on the checked machine; `wolf test` takes no `--nocapture`. | every lane with a child-role test | hand-shake first (`--self-check` exits 7), skip LOUDLY on both streams, cover the scenarios in the native run (`tools/check-test --native`). | `src/term_render_test.lu`, `src/util_log_test.lu` | wolf-lang (a child-role facility for `wolf test`)  **yw07 adoption:** Guard workaround RETIRED in `3b519e4` and the undo fixture in `f10e937`. `wolf test` now refuses self-exec by name and runs those files natively; strict checked case 12 records unsupported, never a false checked pass. Direct conform-run does not acquire the test runner behavior. |
| G18 | **a `mut` parameter inside a `region` block is E1010** ("still holds a value allocated in region … when the region is freed"), whatever the struct holds — a scalar-only RNG state too. | every per-turn scratch loop | the conservatism ledger: the analysis does not see that nothing of the region's reaches the struct. Thread the state functionally (`tools/fuzz-unicode/main.lu`: every mutator answers the next RNG state) or keep the loop's scratch out of a region. | `tools/fuzz-unicode/main.lu`'s header; the refused form is in the lane's log (`notes/yw00-the-map.md` §4) | wolf-lang (precision of the region analysis; a bug if the spec says a scalar struct may be written)  **yw07 adoption:** 0.2.35 / s252 removes the scalar-only region refusal (`7a9ae6e`); tab-frame scratch is adopted in `b581b2d`. Storage-bearing ownership is not generally cleared: G50 / wolf-lang#919 remains open. |
| G17 | **a native `wolf test` harness**: today `test_*` fns run on the checked machine only and `main`-shaped files run natively only as a fallback (`test_cmd.rs:645-665`). | every lane | `tools/check-test --native` builds and runs each test file. | — | wolf-lang (known: "the native multi-test harness lands", `test_cmd.rs:61-65`) |
| G24 | **a `distinct int` is not `Copy`**: `a as int` moves `a`, a second read is E1001, and nothing opts it in (no `Copy` trait, E0301). | yw02's coordinates, every typed id | `distinct` at function boundaries only, `int` fields (§1); `copy a` at a read also works | `notes/yw02-evidence/witness/distinct-copy` | wolf-lang (design: an opt-in, or `distinct` of a Copy type is Copy)  **yw07 adoption:** Upstream resolved by s252 at `7a9ae6e`: an adapter of a Copy scalar is Copy. Existing integer fields/explicit copies are retained; wholesale coordinate-representation conversion is not part of this cut. |
| G25 | **a module `const` of `wrapping[u64]` is "not static data"** ([mem.static.3], exit 4), an integer literal included. | yw02's hash primes, every hash | zero-argument functions | `witness/wrapping-const`, `wrapping-const-unreached` | wolf-lang (ledger row or bug: a literal is static data)  **yw07 adoption:** Upstream resolved by s252 at `7a9ae6e`: wrapping module state is static data. Existing zero-argument prime functions remain; their source conversion is not claimed. |
| G26 | **an inherited descriptor ≥ 3 is not an fs handle**: `fs_write_chunk(5, …)` answers `io`. | yw02's torture child (`YEW_TORTURE_READY_FD`), every inherited pipe | reopen `/dev/fd/N` (Linux, macOS) | `witness/inherited-fd` | wolf-lang (gap: adopt an inherited descriptor)  **yw07 adoption:** RETIRED in `45061a5`: the torture ready descriptor is adopted with `fs_adopt`, not reopened through /dev/fd. |
| G27 | **module state of a run-time value is E1010**: a process-wide registry of strings cannot be a module `var`. | yw02 (the journal owner list), yw03 (`Ed`) | a value threaded through its owner (§1) | `witness/module-str` | nothing to file (design); the idiom row is the answer |
| G28 | **E1004 refuses `m.s = copy g(mut t)`** where `g` answers a struct of scalars: "a value from `t`'s region into `m`'s", the `copy` notwithstanding. | yw02's file metadata snapshot | build a fresh literal of the scalar fields | `witness/region-copy` | wolf-lang (precision of the region analysis)  **yw07 adoption:** Upstream scalar-only region precision shipped in s252 (`7a9ae6e`); descriptor metadata adoption is `5801186`. Existing fresh scalar literals are retained, not represented as a new witness of every former refusal. |
| G29 | **`wolf test` runs a refused `main` natively and says `ok`**: past the checked machine's 20M-step budget (`wolf_mem/src/ubcheck.rs:228`) a file falls back to one native run (`test_cmd.rs:648-669`), visible only as `detail: "exit(0) [native]"` in `--json`. | every lane's checked-machine claim | read `--json`; run the fallback files case by case on the checked machine (yw02's note §4) | `wolf test --json src` on yw02's head: 10 of 20 `text_*` files `[native]`; at yw04's head the per-case runs are in each fork's evidence (`notes/yw04-evidence/*/percase*`) | wolf-lang (print the fallback in the human output; count it in the summary)  **yw07 adoption:** Reporting workaround RETIRED in `3b519e4`: --nocapture plus explicit --no-native-fallback support and strict JSON adapter. Closeout: 135 passing files, 73 native fallback, 0 failed; 448 individual checked cases over 24 files with named allowances. Budget exhaustion is never a SKIP. |
| G30 | **no non-blocking pipe write and no write-readiness wait**; no `os_fork` at 0.2.33. | yw02's clipboard writer (C forks twice and writes non-blocking so a tool that never reads cannot block the loop) | a STOP: the port exits 4 naming the gap; OSC 52 is unaffected | `notes/yw02-evidence/witness/clip-pipe-write-blocks` (a 1 MiB write to an unread pipe never returns), `clip-no-fork` (`os_fork`: E0301); the reader: `clip-wait-no-deadline`, `clip-no-wait-fds`; yw04: the prompt's Shift-selection copy reaches the writer's STOP (`s57_29_prompt_select_and_copy`, exit 4, R-yw04-6) and its paste the reader's refusal (R-yw03-6 = B), the region filter's interleaved write (R-yw04-3, wolf-lang#818) | wolf-lang (gap: `O_NONBLOCK` on a pipe end with EAGAIN as a row, and a write-ready wait, #818); `os_fork` is 0.2.34's; **yw05, at 0.2.34**: `os_fork` serves the writer and the reader as C's (`c2535bf`) and a job's stdin beyond the inline size through a forked writer child (`job_fork_writer`, the region filter's write side, R-yw04-3); the non-blocking write itself (#818) is still absent and no longer needed  **yw07 adoption:** Non-blocking writer half RETIRED in `3256c7c`: parent-owned data fd, `fs_set_nonblock`, `fs_write_some`, bit-62 write readiness and deadline. C fakeclip hang regression verifies an unread pipe cannot stall the editor; CI helper coverage `2e77b34`. |
| G31 | **no host OS/arch query** (comptime or run time). | yw02's clipboard (pbcopy is a macOS-arm64 compile-time choice in C) | PATH alone, said in `text.clipboard`'s header (a Linux PATH with a `pbcopy` differs from C) | `witness/host-os` (`os_name`: E0301; none in the prelude) | wolf-lang (gap)  **yw07 adoption:** RETIRED in `45061a5`: automatic pbcopy requires macOS/aarch64; forced override is preserved. A private fake pbcopy on Linux verifies the distinction. |
| G33 | **a `List` that replaces a field of a long-lived value is held until the value's region ends** — no per-object free, so a rebuild-and-swap that C does with malloc/free leaks the old storage. | yw02 (the grapheme index: 670 KB per edit of a 1 MiB buffer), yw03 (`Ed` lives for the session) | rebuild into a spare pair and swap, or edit in place (`pop`, element writes); `std.list.clear`/`truncate` themselves allocate a new list | `src/text_coords_test.lu`'s `t_port_coords_index_edits_reuse_storage` (red at yw02 `02806d4`'s parent); yw03: the editor keeps ~630 B a line move and ~340 B a typed key (a turn's temporaries live in the loop's region; a per-turn `region` is E1010, `notes/yw03-evidence/witness/turn-region/`); **yw04**: a `:` keystroke keeps ~210 KB to the session's end against C's 0.3–0.5 KB — ~182 KB of it the full repaint C's refilter asks for on every key (`cmdline.c:923-965`), ~30 KB the prompt's own (`notes/yw04-evidence/prompt/ptymem.txt`); the completion rebuild cut from 1.9 MB to 386 KB a key by `copy region` (`notes/yw04-evidence/comp/`) | wolf-lang (design note for the guide; a reclaiming assignment or a storage-reusing `clear`) |
| G32 | **the fs rows C yew uses and 0.2.33 lacks**: `access(2)`, `O_NOFOLLOW`, an advisory lock, a handle's dev/ino (`fs_fstat` answers three words), `mkfifo`. | yw02 (save, journal, clipboard, the serial test's FIFO) | each worked around by name (mode bits against uid/gids for `access`; `lstat` before open; the `mkfifo` utility) | the prelude (no name) | wolf-lang (one gap issue listing them)  **yw07 adoption:** PARTIAL: `5801186` adopts access, no-follow opens and descriptor identity; `c8446b4` creates FIFOs directly. Write-only-existing-file open semantics and journal POSIX record locking remain OPEN; `fs_lock` is not silently substituted for a different lock contract. |
| G34 | **the raw mode cannot clear `ICRNL`, `OPOST` or `ISTRIP`**: `[os.term.mode]` reaches five termios bits (`ICANON`, `ECHO`, `ISIG`, `IXON`, `IEXTEN`) and `VMIN`/`VTIME`; C yew's raw mode clears the `cfmakeraw(3)` set (`tty.c:521-543`). With `ICRNL` set the kernel turns the CR a legacy terminal sends for Enter into LF, so Enter reads as `C-j`; kitty's `\x1b[>21u` (`input.c:58`) leaves Enter, Tab and Backspace as legacy bytes, so this is every terminal's Enter, not only a legacy one's. | yw01 (measured, not needed: campaign 01 presses no Enter), **yw03** (Enter accepts `:` and is I mode's newline; sagitta's `perf_latency` quits with `:q!\r`) | the interim (ruling R-yw03-4): while the port's raw mode is in force (`term.tty_icrnl_stuck`) the decoder reads a legacy LF as Enter (`term.input_set_lf_enter`); a raw `C-j`, unbound in every campaign-03 mode, reads as Enter too; a written LF still reaches the wire as CRLF (`OPOST`; the renderer writes none) | yw01's W1 (`notes/yw01-evidence/witness/enter/`, `opost/`); yw03: the port at `bcf2163`'s parent did not quit on `\x1b[27u:q!\r` under a PTY and does at `bcf2163` (`port_input_lf_is_enter_while_icrnl_stuck` in `src/term_input_test.lu`) | **wolf-lang#802** (closed 2026-10-20: s248's widening, wolf-lang#804, merged at `808ce11a`, unreleased at 0.2.33 — read 2026-10-20T19:52Z); the pin that has it clears the bits in `term.rawios` and retires the interim; **Retired by yw05 at 0.2.34** (`21532a2`): `rawios` sets `RAW_CR | RAW_OUTPUT`, the LF-as-Enter interim is gone; the goldens cannot see the bit (modern Enter is CSI u), the live torture lane can (the RAW_CR plant is red there) |
| G35 | **a `take` parameter stored into a FIELD of a `mut` parameter's list element is E1004** ("parameter regions are independent by default"), though the same store of the whole element builds. | yw03 (`finish_lift`: the lifted cursor set replacing the window's) | store in the caller, where the value was built (`edit_cmds.lu`'s three lifts) | `notes/yw03-evidence/witness/take-region/` (`main.lu`, `run.txt`: exit 2) | wolf-lang (precision of the region analysis: `take` is a hand-over; or the planned shared-region signature) |
| G36 | **a spawned process takes no environment or working directory**: `std.process` has no `set_cwd`/`set_env` for a child; only `exec` takes an environment. | yw04 (`:!!`, `A-h`'s man, the `:!` environment table, s19 §7) | `edit.job_run_sync` sets the editor process's own environment and cwd around a SYNCHRONOUS spawn and restores them; an async job (R-yw04-1) could not do that safely | `notes/yw04-evidence/witness/spawn-takes-no-env-or-cwd/` (E0301 ×2) | wolf-std/wolf-lang (gap: `spawn` with `env` and `cwd`, as `posix_spawn` takes them) |
| G37 | **no name-service lookup** (`getpwnam`, `getpwuid`): `std.os.users` parses passwd TEXT only. | yw04 (`~user` completion, the `USER` source, the login shell) | `std.os.users` over `/etc/passwd`'s text; an NSS/LDAP user is invisible where C sees it | `notes/yw04-evidence/witness/no-user-database/` | wolf-lang (gap) |
| G38 | **a shift count is inferred as `wrapping[u64]`** from the shifted operand, so `1 << n` with an `int` `n` computed elsewhere took a type the program never wrote. | yw04 (the shell fork's hash; a runaway it caused got the lane's container OOM-killed twice, after which `ctr` gained a memory cap) | annotate the count | `notes/yw04-evidence/witness/shift-count-infers-wrapping/` | wolf-lang (bug or spec note) |
| G39 | **no resumable directory read**: `fs_read_dir_entries` reads a whole directory at once. | yw04 (the completion engine's sliced listing, s18.5 §4's keystroke budget); yw06's walk does not meet it: C reads each directory whole and sorts it before descending (`walk.c:285-311`), so the walk's slices fall between entries, never inside a read (R-yw06-6) | the port slices the keep/push work, not the read; the cold key pays the whole read | the prelude (no name) | wolf-lang (gap: an opendir/readdir handle) |
| G40 | **fs paths are `str`**: a directory entry whose name is not UTF-8 cannot be stat'ed or opened. | yw04 (completion over arbitrary trees); yw06 (the workspace walk; a restored tab whose `path` is not UTF-8, `07-invalid-utf8-path.fl`, `08-control-bytes-path.fl`) | such an entry answers `none` (`comp_entry_path`) where C lists it; the walk skips it and logs a warning naming G40; the state codec carries such a path as bytes and re-emits it byte for byte, and its tab restores as an orphan, never dropped (R-yw06-6) | the prelude's signatures | wolf-lang (gap: `List[byte]` paths, invariant 2) |
| G41 | **a native or release stack overflow is a bare SIGSEGV** (exit 139) with no `wolf-trap` line: native dies between 50k and 100k three-argument frames, release between 150k and 200k. | yw04 (the regex parser and compiler, written with explicit stacks because of it) | no recursion on input-sized depth | `notes/yw04-evidence/witness/deep-recursion/` (run in the container; the first run on the host is the lane's slip, its note) | wolf-lang (the stack guard's trap line)  **yw07 adoption:** s256 / 0.2.35 (`7a9ae6e`) reports `wolf-trap: stack-overflow` instead of a bare SIGSEGV. Release-note adoption only here; the no-input-depth-recursion rule and explicit stacks remain unchanged. |
| G42 | **no vectorized byte search** (`memchr`): the literal prefilter is 1.60× C's on its throughput row. | yw04 (`search.literal`) | a stride filter over the needle's rarest byte | `notes/yw04-evidence/regex/perf-re-1gib.txt` | wolf-std (candidate) |
| G43 | **the checked machine traps `use-after-move` binding a nested field of a `read` parameter** (`let tb = ed.bufs[b].tb`) that builds with warnings denied and runs natively. | yw04 (the search fork's range resolution) | read through the path, or `copy` | `notes/yw04-evidence/witness/read-field-move/` | wolf-lang (bug: one machine refuses what the other runs) |
| G44 | **the checked machine has no `f32`** ("unsupported `f32` in checked execution (f64 is the supported float)"), and 0.2.34 casts no float to the other width on either tier ("float-width casts (`f32`↔`f64`)", exit 4). | yw05 (the pane ratio: C's `float`, `layout.h:62`, rounded in single precision at `split_cells` and `yew_pane_resize`; double precision moves a border by a cell at some spans) | the ratio is C's float BITS in an `int`, rounded exactly by `util.f32` in integers; `src/util/f32_test.lu` checks it against C's twelve float-vs-double rows and against wolf's own `f32` natively | `notes/yw05-evidence/panes/f32-bits/` (an `f32` ratio: `edit_layout_test` 0 of 46 cases on the checked machine; the bits: 45 of 46) | wolf-lang (gap: `f32` on the checked machine; the width casts) |
| G45 | **a `read` lend of a `mut`-held struct snapshots the whole struct** into the caller's frame: on native, and on release wherever the caller is too large to inline. | yw06 (the router: `drag_strip_motion` holds `mut ed` and lends it read-only to `drag_target_slot` and `drag_dwell_slot`, which never write it — W1002 refuses `mut` there — so every motion report copies ~6.4 KB of `Ed` into a 20,824-byte frame, ~214 of the burst's 231 ns, 6.68× C; `ed_render` 22,008 bytes, `tab_member_strip_draw` 21,368 and `ws_cmd_save_state` 49,960 carry Ed-sized frames too) | none in source: the helpers stay `read`; the burst is a yw15 ratchet row behind this gap | `notes/yw06-evidence/mouse/witness/read-lend-copy/` (a 400-field struct: a 6,416-byte frame lent `read`, 32 bytes lent `mut`, native) and `notes/yw06-evidence/mouse/perf/` (the release disassembly) | wolf-lang (codegen: lend a `read` view of a `mut` binding by address) |
| G46 | **the checked machine copies a held `str` on every inline `.bytes()[i]`**: a read costs the whole string's length (10,000 reads of a 1 MiB field 1,288 ms against 32 ms for 1 KiB), where native reads in place; the builtin `repeat` is cheap. | yw06 (the picker's custom search over C's 8 MiB borrowed source, `test_picker.c:402-468`: the case ran 16+ minutes at 2–4 GB and was stopped by its pid) | read through one lent view a step (`2726e35`), consume the byte before rather than the text (`ff8ff71`), and build the 8 MiB test text a byte at a time so the budget ends the case in ~5 s (R-yw06-14); native `test_picker` fell from 4.41 s to 0.31 s | `notes/yw06-evidence/pick/witness/checked-bytes/`, `checked-repeat/` | wolf-lang (bug: the checked machine's cost model, one machine's time unbounded where the other's is linear) |
| G47 | **A function-valued field called directly is refused by both compiled tiers**: `s.clock(s.ctx)` is "an indirect callee without a recorded type" (exit 4), though checked execution prints 7. | yw07 (the injected undo clocks) | bind the typed function value first (`let clock = s.clock; clock(s.ctx)`), which prints 7 on checked, native and release; named at `text.undo`'s two clock calls, not a second callback representation | `notes/yw07-evidence/callback-fields/direct/`, `bound/`, `run.log` (wolf 0.2.35, warnings denied) | **wolf-lang#916** (codegen: preserve the field callee's function type) |
| G48 | **A function with `mut` or `take` parameters cannot be used as a value**: a function type carries no modes (`fn(mut Vm, int)` is not grammar); assigning the named `fn add(mut vm: Vm, n: int)` to a grammar-valid `fn(Vm, int) -> int` table field is refused at resolve on all three tiers. | yw07 (command registries, Fletch natives and the host seam, R-yw07-3's explicit STOP) | no mutable callback table is implemented; decided R-yw07-10 = A retains kind ids plus one `match` consistently for these surfaces. s251 retires G19/G20's object-boundary failure, not this separate mode limitation. | `notes/yw07-evidence/callback-fields/mut-vm/`, `run.log`: checked `unsupported`, native/release build 4, exact refusal "a fn with `mut` or `take` parameters used as a value (a fn type carries no modes; call it by name)" | **wolf-lang#917** (function-value parameter modes) |
| G49 | **The 0.2.35 pin adds cold-open startup cost to unchanged editor source.** | yw07's pin attribution, not a block at its rewritten head | 280012fe/0.2.34: 7.664 ms median; 7a9ae6e plus only R-yw07-11 compile compatibility/0.2.35: 11.513 ms (about +3.849 ms); C stays near 3.8–4.0 ms. 35e21b9 is 4.918 ms, paired median ratio 1.28, and remains gated. First Backspace is a separate pre-existing yw15 ratchet, yew#53 (2.46 at trunk, 2.53 at 35e21b9), listed by exact host/row in tools/perf-editor-misses.txt. | `notes/yw07-evidence/perf-attribution/results/rows.tsv`, `summary.tsv`, three full C→port→C trials per cell; literal pin-only is BUILD-RED, not timed | **wolf-lang#918** (release startup); **yew#53** (pre-existing first Backspace, owner yw15)  **yw07 adoption:** Closeout at `2e77b34`: clean startup 6.90x, cold open 2.07x, and tabswitch p99 2.10x. Orchestrator disposition is named MISS at this pin, yew#55 / s265 / wolf-lang#918, re-measured at the re-pin; `a73df60` adds only exact Linux/x86_64 metric rows. The 2x threshold remains, including all unlisted rows and hosts. |

| G50 | **A List owned outside `region scratch`, then `reserve()`d inside it, can take a region buffer that escapes its lifetime.** The checked machine passes; native and release terminate with SIGSEGV (139). | yw07 (reusable menu rows) | avoid the pop/refill/push pool idiom; retain fixed physical slots and refill directly, with a separate live prefix. The no-region and direct-in-place witness controls pass all three tiers. | `notes/yw07-evidence/reuse-row-move/main.lu`, `plain/`, `inplace/`, `run.log` (wolf 0.2.35) | **wolf-lang#919** (region-escape buffer ownership) |


| G51 | **The public std float conversion/bit APIs canonicalize NaN sign and payload**, while C's conversion sites preserve a negative NaN spelling (`-nan`, `-nan.0`) and `strtod("nan(123)")`'s payload on Linux. | yw07b, R-yw07-4 | OPEN, not accepted: finite/inf/negative-zero conversions matched the generated Linux corpus; NaN identity/spellings did not. Host-C agreement is a separate pending CI gate; stop if it differs. | `notes/yw07b-evidence/floats/linux-comparison.json`: 110963 bit inputs, 221904 parses, 4771387 answer lines; signed/payload NaN witness in `probe/main.lu`; `src/fl/float.lu` names the limitation. | **wolf-std#103** (preserving binary64 bit conversion; host-C agreement remains an independent gate) |


### yw07 retirement cut

The pin is wolf 0.2.35 / lupin 0.1.56. This lane ends at deliverable 1;
no Fletch implementation or toy VM is claimed. yew#20, #22 and #24's
adoptions are complete. #17/#27 retain the mutable-registry portion
under G48; #23 retains G32's two filesystem limitations; #40 retains
parser/refilter temporaries, line copying and whole-loop scratch.
The callback representation remains one kind-id/match for mutable APIs,
function values for read-only environment/sort/clock callbacks.

#40's fixed slots, interner ownership and frame scratch are `bff2188`,
`b581b2d`, `1f5d46c`. The port's RSS slopes before/after (bytes per key,
1,000 keys) are prompt-menu 21,303.3/5,521.4, lines40 725.0/659.5,
pane-lines40 1,007.6/528.4. C's after slopes are 286.7, 20.5, 69.6.
Native/release focused ledgers retain zero bytes for 200 menu refills
and 30 strip frames; this does not claim whole-loop zero allocation.
Raw closeout trials and logs are in `notes/yw07-evidence/closeout/`.
No new unsafe block or module state was added.

The next lane, yw07b, starts from merged trunk. It owns the toy VM and
R-yw07-1 measurement before the real Fletch VM, then deliverables 2–10
under the adopted contract. It must carry G47/G48/G50, the explicit
retirement remainders above and the next-pin performance remeasurement.
The static-binary/PAX handoff is skipped in this cut, not marked done.

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
- **R-yw03-1 — a narrow `:` in yw03.** Every one of campaign 03's 62
  PTY cases tears down through `esc : ed.quit(_force) enter`
  (`tests/pty/registry.c:679-700`), `notepad_restore_suspend` types
  `:ed.suspend`, and the case's verdict is its snapshot AND its exit, so
  M-YW3 needs a `:` the launch decision ("yw03 carries no `:` line")
  did not foresee. (A) the narrowest one — E mode entered by `:`, `e`
  and `!`, printable text and paste collected into a hidden one-line
  buffer, `<cr>` resolving the first word by name or abbreviation and
  invoking it through the registry with its string or integer
  argument, `<esc>` cancelling, the line drawn over the footer;
  ranges, history, completion, the menu and the editing keys refuse
  naming yw04 (`edit.cmdline`, implemented); the live-editor kill9 lane
  stays yw04's (R-yw02-1 = A); (B) no `:`, M-YW3 deferred to yw04.
  **Recommend A** (implemented).
- **R-yw03-2 — the runtime files before Fletch.** Every frame is painted
  in `quiver-dark` with `init.fl`'s keys and options, which C gets by
  running `init.fl` in the Fletch VM (yw07–yw09). (A) copy the files
  verbatim, embed them (`tools/gen-runtime`, `tools/check-runtime`),
  and read their flat shape — call statements, `let NAME = literal`
  (the PTY harness's user `init.fl` is `let lsp = {servers: {}}`) and
  literals — with a reader that refuses anything else by line and
  column naming the VM's lane (`edit.fldata`, `edit.config`), the
  `bind` rows going through the same builder Fletch's `bind()` will
  feed; (B) hard-code the 381 bindings in wolf. **Recommend A**
  (implemented); the reader is retired by yw09.
- **R-yw03-3 — the single-tab strip.** Row 0 of every editor golden is
  the tab strip (`ui/tabs.c`, campaign 05's). (A) paint the one-tab
  strip campaign 03 needs (`edit.tabs`: the label, the dirty mark, the
  `+` tail), several tabs refusing naming yw05; (B) wait for yw05.
  **Recommend A** (implemented).
- **R-yw03-4 — Enter while `ICRNL` cannot be cleared (G34).** (A) read a
  legacy LF as Enter while the port's raw mode is in force (a raw
  `C-j` then reads as Enter too; campaign 03 binds Enter in I, E, H and
  F and `C-j` nowhere), retired by the pin that widens
  `[os.term.mode]`; (B) leave LF as `C-j` — Enter then neither accepts
  `:` nor breaks a line on any terminal (kitty keeps Enter legacy at
  C's flags). **Recommend A** (implemented, `bcf2163`).
- **R-yw03-5 — `test_multicursor`'s two sync-count cases** (G3): (A)
  KNOWN-RED by name, the bodies green, the one `fsync-file` per
  transaction reported unobservable — R-yw02-2's shape (recommended,
  implemented); (B) SKIP.
- **R-yw03-6 — the paste key reaches R-yw02-3's STOP** (G30): (A) the
  editor exits 4 by name where a subprocess clipboard reader is
  detected, as yw02's reader does (implemented); (B) the paste refuses
  with C's deferred status and a message naming G30, the session kept.
  **Recommend B**, in yw04.
- **R-yw03-7 — a turn's temporaries** (G33/G18: the editor keeps ~630
  B a line move to the session's end; `notes/yw03-the-modal-core.md`
  §4.6): (A) allocation-free hot paths in the port, a lane before
  M-YW5 (recommended, in yw05); (B) E1010's precision, so the loop can
  wrap a turn in a region; (C) accept until yw15.
- **R-yw04-1 — the job pipes at 0.2.33 (G2)** (taken at launch: A). The
  job half — the async stream, the region filter, `:r !`, the persistent
  session and, as yw04 found, every completion source that runs a child
  (generators, `--help`, fish) — STOPs by name until `os_signal_wait_fds`
  is pinned; 20 of campaign 04's 104 goldens and 80 unit cases wait on it
  by name. v0.2.34 was published (2026-10-21T12:58:10Z) after the job half
  was reached at 0.2.33 (2026-10-20T23:19:20Z), so the bump is yw05's.
- **R-yw04-2 — the menu's mouse rows** (taken: A). The narrow region
  registry (`edit.region`, the menu's rows) and the loop's mouse route;
  `s18_5_cmdline_click_row` green.
- **R-yw04-3 — the filter's write side (G30)** (taken: A). A STOP by name
  until wolf-lang#818.
- **R-yw04-4 — completion specs before Fletch** (taken: A). The 24 spec
  files read by `edit.fldata` extended; a statement it cannot take refused
  by line and column naming yw07.
- **R-yw04-5 — `A-e`'s second tab.** `s57_31_edit_in_buffer_open` and
  `_roundtrip` open `*command-line*` in a NEW tab and close it on accept
  (`cmdedit.c:341-364`). (A) a narrow `tab_open_buffer` and
  `ed.tab.close` (the `A-e` tab, the last tab or an unmodified one; a
  modified tab refuses naming yw05) over yw03's strip, which already lays
  out several tabs (implemented; both goldens green); (B) both red naming
  yw05. **Recommend A**; yw05 replaces it with `tabs.c`'s full open.
- **R-yw04-6 — the clipboard writer's STOP in the prompt (G30).** The
  prompt's Shift-selection copy reaches yw02's writer, which exits 4 by
  name (R-yw02-3 = A): `s57_29_prompt_select_and_copy` ends the session.
  (A) keep the STOP; (B) refuse the copy with C's deferred status and a
  message naming G30, the session kept, as R-yw03-6 = B does for the
  paste (the golden stays red either way: C copies through `fakeclip`).
  **Recommend B**, in yw05 or with 0.2.34's `os_fork`.
- **R-yw04-7 — `:set NAME VALUE` before the options model.** The prompt's
  goldens set options at `:`; C runs `option.c`. (A) an interim over
  `Opts` (`edit.option_cmdline`), every other name refusing naming yw09,
  retired by yw09 as R-yw03-2's reader is (implemented, recommended);
  (B) refuse `:set` until yw09.
- **R-yw05-1 — s57.13–s57.15 and s57.22** (taken at launch: A). Their
  prerequisites are Sprint 27's router; the four move to yw06 after s27
  (17 PTY cases, `test_ctxmenu`, `test_ctxrows`; yw06's draft).
- **R-yw05-2 — the 0.2.34 bump's size** (taken: A). The bump and yw04's
  job half inside yw05: campaign 04 104/104.
- **R-yw05-3 — R-yw03-7's turn temporaries** (taken: A, as the draft
  recommended): deliverable 6, yw05's allocation-free hot paths.
- **R-yw05-4 — deferred-tab residency** (taken: A). Residency is the
  buffer slot's own (`Buffer.resident`, set where the piece tree is
  built); s24 DoD 4's one read counted by `text.file_load_count`.
- **R-yw05-5 — `startup_multiple_files`.** Every file is its own tab in C's
  order (rows 1–2 of the snapshot are C's), but the case snapshots after
  `:buffers` Enter, `ed.find.buffer` (Sprint 26 §6). (A) it moves to yw06
  with the finder, recorded under that owner (implemented, recommended);
  (B) pull the buffer picker forward into yw05. **Recommend A.**
- **R-yw06-1 to R-yw06-10** (taken at launch and on the C witnesses: A
  in each; the contract, `notes/contracts/yw06-workspace-finder-mouse.md`):
  the hand codec as the interim state path, retired by yw09's swap; one
  router at the pin's state, its goldens and units gated as a set; M-YW5
  as the 81 goldens and the automated twins of s42 §10's boxes; the map
  corrected, nothing of FUSS or shadow ported early; `trust*` yw09's;
  non-UTF-8 paths as bytes, skipped by the walk, restored as orphans;
  all 81 reachable cases; the jump state as literal jumps; the
  coordinates' raw wire values; the disk-ignore quirks C measures.
- **R-yw06-11 — the FUSS kinds in `test_ctxrows`' every-row walk.**
  `ctxrows_every_row_resolves_to_a_registry_command` walks every kind's
  rows; the three FUSS builders refuse by name until yw13. (A) the walk
  SKIPs the three FUSS kinds by name, the other 54 rows checked and the
  FUSS actions held by the table case (implemented, recommended); (B)
  build C's rows over "unknown" FUSS answers; (C) a sixth FUSS red.
- **R-yw06-12 — type-to-jump's deadline** (`typejump.h:36`, 500 ms). (A)
  C's shape, a timestamp the next key compares against: no production
  host calls `yew_typejump_key` at the pin, only FUSS clears its jump (the
  C witness W4) (implemented, recommended); (B) a timer-heap entry, as the
  contract worded it.
- **R-yw06-13 — the walk's first yield** (`walk.c:438-443`). (A) every
  budgeted step takes one entry before it may yield (implemented,
  recommended: under (B) `test_walk` case 4's 1 µs step made no progress
  on the checked machine, trap "never loops"; the listing is the same
  either way, and nothing at the pin walks with a budget in production);
  (B) C's check before the first entry, exactly.
- **R-yw06-14 — `test_picker` case 9's 8 MiB text** (`test_picker.c:
  402-468`). (A) built a byte at a time, so the checked machine's step
  budget ends the case in ~5 s, native unchanged (implemented,
  recommended); (B) the builtin `repeat`, where G46 runs the case 16+
  minutes at 2–4 GB.
- **R5 — the module-name collisions** (`unicode`, `term`, `search`
  against std): (A) the port keeps sagitta's names and aliases std
  where both are needed (recommended, done); (B) prefix the port's
  (`yew_term`).

- **R-yw07-10 — mutable callback modes (G48), decided A** (the
  orchestrator under ruling #118, 2026-10-24; subject to override).
  The mutable command registries, Fletch natives and host seam keep ONE
  representation: a kind id per row and one `match`, R-yw07-3's fallback.
  Read-only environment, clock and sort callbacks use function values,
  bound locally before calling a field (G47, wolf-lang#916). #17/#27's
  read-only retirements proceed; their mutable-registry half stays open
  under G48, wolf-lang#917. Never two representations for one registry.


- **R-yw07-11 — the performance attribution control, decided A** (the
  orchestrator under ruling #118, 2026-10-24). Compare 280012fe on its
  original pin, 7a9ae6e plus ONLY the three missing Mode fields set false
  and `out.shell = copy c`, and 35e21b9, three times each. The middle
  cell is "pin + compile compatibility", never "pin only"; literal
  7a9ae6e is BUILD-RED (E0408, then E1004), not a timing row. Preserve
  the existing explicit RAW_CR/RAW_OUTPUT additions. The first Backspace
  sample follows motions, Insert, newlines and an idle pause, not a first
  callback invocation. No attribution claimed until the table is read.


- **R-yw07-12 — cold-open sampling, decided A** (the orchestrator under
  ruling #118, 2026-10-24). The port's gate reader takes the median of
  five C-stable trials for every editor ratio (extended A), retaining every
  raw trial. C-again fold drift above 1.25 discards that row's trial and
  asks for another; the first five valid triples are used, never selected
  by port speed. C's harness is unchanged.
  A bounded same-bits original-path/copy-path comparison is also approved,
  five observations per path, interleaved. The 2× limit is not relaxed.

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
  module boundary) as its first ruling. **Landed by yw03**
  (`notes/yw03-the-modal-core.md`): the 62 PTY goldens gated by name
  (the script suite's campaign-03 rows need `--batch`, yw09), with a
  narrow `:`, the runtime files read before Fletch and the one-tab
  strip as interims (R-yw03-1..3).
- **yw04 — execute and search** (s18, s18.5, s19, s20, s21, s57.17,
  s57.18, s57.23–s57.32; `src/search/`, `src/edit/shell*`, `job.c`,
  `src/ui/comp*`, `shctx.c`; `src/unicode/category.c`, `case.h`,
  `tables_cat.c`, `tables_case.c`). The `:` prompt with its editing,
  history and completion engine, shell jobs under `$SHELL -c` with the
  terminal handed over and back (process groups and the foreground
  terminal, available since 0.2.31), the Thompson NFA/DFA regex with
  the literal fast path, search and replace. Goldens: the regex corpus
  (`re_golden.h`), the `:!` PTY cases, `fuzz_re_*`. Gaps: G2 for the
  job pipes (ruling R2). **Drafted in full by yw03**
  (`notes/contracts/yw04-execute-and-search.md`): with s57.21's readline
  keys and s21's jump list, the full `:` replacing yw03's narrow one,
  the live-editor kill9 lane (R-yw02-1 = A), and the 0.2.34 bump as its
  first commit if released (G2/G3/G4/G30/G34 adopted).
  `test_job_handover` is Sprint 52's (yw13); the eight `chrome_cmdline_*`
  and `chrome_search_*` cases are Sprint 27 §7's (yw06) over yw04's
  screens. **Landed by yw04**
  (`notes/yw04-execute-and-search.md`): the full prompt, the regex engine,
  search, replace and the jump lists, the shell completion engine and the
  synchronous job route at wolf 0.2.33; 83 of campaign 04's 104 goldens
  gated by name (M-YW4), the 21 others red by R-yw04-1 (20) and G30 (1);
  the live-editor kill9 lane over the port's editor (G3 known-red by
  name). The bump to 0.2.34 and the job half are yw05's first deliverable.
- **yw05 — panes, tabs and groups** (s22, s23, s24, s57.8; `src/ui/`
  layout, region in full, tabs, strip, groups, groupnav, grouppicker,
  groupfromdir, glyphs, `src/edit/pane_cmds.c`). FIRST the 0.2.34 bump
  with yw04's job half (R-yw04-1's stops become calls) and every
  G1/G2/G3/G4/G30/G34 interim retired; then the pane tree in cells, the
  clickable-region registry in full, tab strip and overflow, facsimile's
  group model, several startup files; allocation-free hot paths
  (R-yw03-7 = A, if ruled). Goldens: the `s22_`, `s23_`, `s24_`,
  `s57_8_` cases and `startup_multiple_files`. **Drafted in full by
  yw04** (`notes/contracts/yw05-panes-tabs-groups.md`), with s57.13–
  s57.15 and s57.22 proposed for yw06 after Sprint 27's router (R-yw05-1:
  their prerequisites are `mouse.c`'s). **Landed by yw05**
  (`notes/yw05-panes-tabs-groups.md`): the 0.2.34 bump with every
  G1/G2/G3/G4/G30/G34 interim retired and yw04's job half (campaign 04
  104/104); the pane tree (its ratio C's float bits, G44), the region
  registry in full, tabs, the strip, s57.8 and groups — 22 of the 23
  campaign-05 goldens by name, `startup_multiple_files` to yw06 with the
  buffer picker (R-yw05-5); the pane, tab and group fuzzers equal to C's
  drivers; the allocation-free hot paths (a `:` key 208 KB → 21 KB).
- **yw06 — workspace, finder and mouse** (s25, s26, s27, s56.5,
  s57.5–s57.7, s57.9–s57.12, s57.20; `src/ws/`, `src/ui/picker*`,
  `mouse.c`, `typejump.c`). Workspace state under XDG in Fletch data
  (the frozen schema, hand-emitted until yw09), the fuzzy finder,
  mouse routing, runtime staleness. Goldens: Sprint 42's field checks
  on the wolf binary (M-YW5); pax pins the static binary (M-YW-PAX1,
  track rule 7 from here). Gaps: G4 (realpath). **Drafted in full by
  yw05** (`notes/contracts/yw06-workspace-finder-mouse.md`): s25–s27 with
  s56.5's startup resolver, s57.11 and s57.12, and s57.13–s57.15 and
  s57.22 after s27's router (R-yw05-1 = A); 14,554 C lines, 24 unit files
  (399 tests), 80 reachable PTY cases; M-YW5's shape, the state codec
  before Fletch, the trust database and the non-UTF-8 paths asked as
  R-yw06-1..6 (§8's correction). **Landed by yw06**
  (`notes/yw06-workspace-finder-mouse.md`), at wolf 0.2.34 (0.2.35
  tagged after the pin commit): workspace identity and the session state
  over the hand codec (the frozen v1 corpus 22/4/20, the C↔port state
  differential byte-identical both ways), the startup plan, the walk,
  `.gitignore` (C's measured disk quirks), the filter and the one
  picker with its four instances and type-to-jump, one router at the
  pin's state with the context menus and drag, and `:!yew FILE`; the
  **81** reachable goldens green by name on release and native, and
  M-YW5's automated twins (twenty resume cycles grid for grid, the
  restore after SIGKILL, SIGSEGV and a closed terminal) gated in CI;
  `fuzz_state`, `fuzz_gitignore` and `fuzz_mouse` equal to C's drivers;
  the per-case checked lane as a CI job (`tools/check-test-cases`); G45
  (a `read` lend's snapshot, the router's burst 6.68× C) and G46 (the
  checked machine's per-byte `str` copy) listed; R-yw06-11..14 asked.
- **yw07 — Fletch core** (s28–s31; `src/fl/` lex, parse, compile, vm,
  value, gc, opcodes, data, module, std*). The frozen spec
  (`.docs/fletch-spec.md`, copied verbatim), lexer, parser, bytecode,
  the VM with switch dispatch, the GC per ruling R3, the std modules.
  Goldens: `tests/fletch/` conformance through `yew fl`. Gaps: G6.
  **Drafted in full by yw06** (`notes/contracts/yw07-fletch-core.md`):
  the bump to 0.2.35 first (yew#17, #20, #22, #23, #24, #27, #40, and
  G20's two local sorts retired); 31 files, 15,868 C lines, 185 unit
  tests; R-yw07-1..9 asked (the sweep after the toy VM, the value's
  shape, dispatch without function values across modules, the float
  conversions, `fl` below `edit`, `suggest`/`trace`/`origin`'s check
  half pulled forward with their 13 tests, `flcli.c`'s non-interactive
  forms so the 39 conformance units run, non-UTF-8 paths as bytes,
  errno names); `stdai.c` is Sprint 48's (campaign 10), not yw09's as
  §2 says — the draft flags it, undecided.
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
- The campaign-04 row reads "execute and search (s18–s22)"; s22 is
  panes, campaign 05's (yw05). The row is s18, s18.5, s19, s20, s21 and
  the `s57.x` prompt rows (§3) — yw03, from the yw04 draft.
- The campaign-03 row's M-YW3 is "campaign 03's PTY and script
  goldens"; the script suite runs `yew --batch` (`tests/script/
  runner.c:958`), yw09's, so M-YW3 is the 62 PTY goldens (yw03's
  contract says so) and the script rows move to M-YW7.
- **yw04**: §2 lists `strip` under yw06's `ui` files; `strip.c` is the
  tab strip's layout engine (s23 §3, `yew_strip_layout`), yw05's with the
  tabs. §3 places s57.13–s57.15 and s57.22 with yw05; each one's
  prerequisites are Sprint 27's router and drag machinery (`mouse.c`,
  `ctxmenu.c`, yw06's), so yw05's contract proposes them for yw06
  (R-yw05-1). The campaign-04 row's "`:!` PTY goldens" are 40 of the 104;
  at 0.2.33 20 of those 40 complete or refuse without a child's pipe and
  are green (R-yw04-1 holds the rest). s57.21's commands also reach I mode
  (the four `s57_21_insert_*` cases), not only the prompt.

- **yw05**: the index's campaign-05 row reads "s23–s28"; it is s22–s27.
  yw05's draft counted "30" campaign-05 goldens for deliverables 2–5;
  sagitta's registry holds 23 (`s22_*` 11, `s23_*` 6, `s24_*` 4,
  `s57_8_*` 1, `startup_multiple_files`). The prediction that wolf's `f32`
  reproduces C's float ratio holds natively but not on the checked
  machine (G44). §7's yw06 paragraph, re-derived for yw06's draft
  (`notes/contracts/yw06-workspace-finder-mouse.md`): "Sprint 42's field
  checks" are Sprint 42's (campaign 08, yw10) and field evidence, not
  automated tests (`dogfood-log.md:3-6`; C yew's own milestone is
  `PENDING`, `milestones.md:8`), so M-YW5's shape is a ruling (R-yw06-3);
  s56.5 §2–§5 and §7, s57.5, s57.6 and s57.7 are FUSS's, shadow's and
  syntax's (yw13, yw11, yw10), s57.7 with no yw06 half; s57.9 and s57.10
  land in files yw03 and yw05 ported (s57.9's two goldens carry `wolf.fl`
  colours: yw10); s57.20 has no C at the pin; the pin's shipping state
  path is already Fletch's (`state_emit.c:27-92`) and the hand codec is
  built out (`Makefile:671`), R-yw06-1; `trust*` is `flconf.c`'s (yw09,
  R-yw06-5); G4 is closed at 0.2.34; all 48 `chrome_*` cases are Sprint
  27 §7's.
