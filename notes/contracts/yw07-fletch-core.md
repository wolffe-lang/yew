# yw07 — Fletch core

**Model per ruling #89 R4, chosen at launch. Crawl 54+. Drafted by yw06
from `docs/MAP.md` §7 and sagitta campaign 06's first four sprints, with
the yw06 carry-overs.** Ruling #89 (`sprints/yew/index.md`) and #93's R3
(the GC's shape); the track's seven standing rules — rule 7 binds (the
static x86-64 binary and its digest); `docs/MAP.md` (the idiom §1, the
gaps §5, the rulings §6, as yw06 left them); `sprints/RULES.md`. Ports
sagitta campaign 06's s28–s31 (`.docs/sprints/06-fletch-core/`:
`s28-fletch-design-freeze.md` 377, `s29-lexer-parser.md` 258,
`s30-values-vm.md` 660, `s31-stdlib.md` 665: 1,960 lines at
`sagitta.pin`) and the language they implement: the frozen
`.docs/fletch-spec.md` (691; the one normative file `.gitignore:3-15`
keeps under `.docs/`) and its design requirements,
`.docs/plan/02-fletch.md` (103). s32 (`s32-repl-and-errors.md`, 581)
and s33 (`s33-fletch-conformance-perf.md`, 485) are yw08's but for what
R-yw07-6 and R-yw07-7 move here. The C it ports is MAP §2's `src/fl/`
row for yw07: s29's `ast.h` (130), `lex.c` (943) + `.h` (149),
`parse.c` (1,410) + `.h` (56); s30's `value.c` (339) + `.h` (349),
`vm.c` (1,777) + `.h` (362), `compile.c` (1,537) + `.h` (74), `gc.c`
(695) + `.h` (129), `opcodes.c` (254) + `.h` (59); s31's `std.c` (396)
+ `.h` (165), `stdstr.c` (975), `stdlist.c` (582), `stdmap.c` (274),
`stdmath.c` (417), `stdfmt.c` (1,276), `stdio.c` (1,007), `stdre.c`
(690), `module.c` (666) + `.h` (94); the diagnostics and the dumper,
`diag.c` (207) + `.h` (123) and `dump.c` (331); and Sprint 36's data
bridge, `data.c` (372) + `.h` (30) (sagitta `8fd95304`, "Route
workspace state through Fletch data") — 31 files, **15,868 lines**,
with the X-macro `opcodes.def` (109) beside them (MAP's 61 files and
26,269 lines for the whole of `src/fl/` count `*.c` and `*.h` only;
both re-derived). As recommended, R-yw07-6 and R-yw07-7 add s32's
`suggest.c` (200) + `.h` (87) and `trace.c` (337) + `.h` (49), s34's
`origin.h` (182) with the check half of `origin.c` (`:203-275`, 73),
`motion_tab.c`'s word check (`:14-40`, 27) and `src/flcli.c` (649, its
REPL branch refusing): **1,604 more**. Not here: s32's REPL (`repl.c`
963 + `.h` 101), `vmcheck.c` (350), `fuzz_fl_vm` and s33 whole (yw08);
the editor API and the rest
MAP gives yw09 (`flapi`, `flconf`, `fleval`, `flhook`, `flruntime`,
`fltxn`, `handle`, `record`, `macrolib`, the rest of `motion_tab` and
`origin`); `stdai.c` (34) is Sprint 48's `ai.backend` (`stdai.c:1`),
campaign 10's, where MAP §2 says yw09 (the note reports which). The
pin's files are post-campaign: `std.c:43-50` registers s34's editor
modules and s48's `ai` beside the seven, its prelude carries `on`,
`record`, `replay`, `set`, `bind` and `unbind` (`std.c:242-257`),
`vm.c` calls s32's suggestions (`:276-336`) and trace (`:1561`) and
s34's receiver bind (`:1199`), `compile.c:678` checks a motion word
against the command registry through `motion_tab.c`, and `value.h:19`
takes `FlOrigin` from s34's `origin.h` (R-yw07-6 says what crosses).
The port inherits the idiom yw00–yw06 set; `fl` is a module of its own
(`src/fl/*.lu` with sagitta's names, R-yw07-5), nothing in it takes the
`Ed`, and its tests are `src/fl_<unit>_test.lu` beside the others.

## Deliverables

1. **The toolchain, first.** `gh release list -R wolffe-lang/wolf-lang`
   and `-R wolffe-lang/wolf-interp` read and quoted with their time at
   the lane's start. yw06 stayed at wolf 0.2.34 / lupin 0.1.55 /
   wolf-std `e036bec` (`wolf-toolchain.toml:57-66`, its retention
   decision at 2026-10-23T06:00:38Z). **v0.2.35 was tagged
   2026-10-23T08:45:33Z** (`cf0c13d38479f444b69bb8356ad5709d07eff323`),
   after that decision; its pairing is lupin **0.1.56**
   (2026-10-23T04:43:45Z, `28547b4324524d5477a6e54e4f6888462461a21f`,
   "spec/corpus pin unchanged at `294d626`") and the archive bundles
   wolf-std `2386522eb059cca5a84108562c2c0a0e72345d34` (sc70, with
   sc69's wrappers). Read twice at this drafting (2026-10-23T15:54:32Z),
   identical both passes: wolf `aarch64-apple-darwin`
   `240b84d079b1b9a0d88681ac08fca4816f84778e2d6c94c435ceb2dd6a5f042a`,
   `x86_64-unknown-linux-gnu`
   `4cc4045bbbb605c07835bc4f32685953c784eeef4cd3139a48b457dfc90dad1a`,
   `aarch64-unknown-linux-gnu`
   `30ccded432264b7ddd4ebf738d4f895d12091ca604e2da4c2f831da807886f3e`;
   lupin `aarch64-apple-darwin`
   `9133bfdbb95f6a18745439bf0b2b5280860a5bfeaf9ae038ea120a72d58f7687`,
   `x86_64-unknown-linux-gnu`
   `ad703550ac4787e8e4bb26989d591a731410274d7332f2b4e8b9a64c878822cc`,
   `aarch64-unknown-linux-gnu`
   `e2719ab28df566ad7b92714191bac00599fbca6c95b6b579d470497b482dd591`.
   The bump (wolf, lupin, the bundled std; digests re-read twice, the
   linux x86-64 pair hashed after download on kasumi) is yw07's FIRST
   commit with its prediction, and it ADOPTS the retirements yw06's
   deliverable 1 listed, each its own commit with its test turned green
   or renamed and no golden edited: yew#17 and #27 (s251,
   wolf-lang#806/#807: `term.Env` in `src/term/tty.lu`, the direct
   `YEW_MOUSE` read in `src/term/input.lu`, `sort_items` in
   `src/text/cset.lu`, the one-`match`-per-registry name tables and the
   injected clock `undo.fake_mono`/`fake_wall`, each with the perf gate
   re-read, as #27 asks); #20 (s250: the `self_reexecutes` SKIP guards
   off, `tools/check-test --nocapture` and `--no-native-fallback`); #22
   (s253: `fs_adopt` for G26's ready descriptor, `os_name`/`os_arch`
   for G31's clipboard choice); #23 (s254: `directory_writable` →
   `fs_access`, the lstat before the open → open bit 16, the path stat
   after it → `fs_fstat_record`, the `mkfifo` utility → `fs_mkfifo`,
   the blocking clipboard write → `fs_set_nonblock`, `fs_write_some`
   and bit 62's write readiness); #24 (sc69's std wrappers:
   `term.Mode`'s `raw_cr`, `raw_output`, `strip8` in
   `src/term/tty.lu:200`'s literal, `signal.wait_fds`,
   `term.restore_at_exit`); #40 (s255's `List.reset`/`reserve` and the
   region per turn: the tab strip's 832 B a frame and the prompt menu's
   ~15 KB a key, its title, and s26 §7's picker refilter, "both vectors
   reserved to `n` at open" — measured with `ptymem.py` before and
   after, C beside it). It retires yw06's two G20 route-arounds:
   wolf-lang#806 (closed by s251) is the dedup twin that refused
   `util.sort_stable`'s closure at 0.2.34, so `ws.state_records_sort`
   (`src/ws/state_lit.lu:305-349`) and `sort_names`
   (`src/edit_state_fuzz.lu:23-25`, `tools/fuzz-state/main.lu:68-70`)
   go back to `util.sort_stable` with the state corpus, `fuzz_state`'s
   `hash=` and `perf_state` unchanged, and
   `notes/yw06-evidence/g20-closure/run.sh` is re-run as the witness
   (its `twin` variant, release tier: 0.2.34 exits 4, "a vtable slot
   `@main.cls0` outside this object's subset"; 0.2.35 builds and prints
   `[1 2 3 3 11 22]` — `run.txt` records both). MAP §5's rows the
   release names are re-read and marked with the commit that retires
   them: G19/G20 (s251), G22, G23 and G29 (s250), G26 and G31 (s253),
   G32 and G30's non-blocking half (s254), G41's trap line
   (`wolf-trap: stack-overflow`, s256; the no-recursion rule stands),
   G11, G18, G24, G25 and G28 (s252). If a newer release is out at
   launch, the same rule takes it.
2. **The toy VM: R3's measurement, before the real VM** (#93 R3 = A;
   MAP §5 G6; R-yw07-1, R-yw07-2). A throwaway program under
   `notes/yw07-evidence/toyvm/`, never linked into `yew`: a dozen-opcode
   stack VM (constants, arithmetic, locals, jumps, call and return, list
   and map construction, an index store, a closure over one upvalue)
   over an arena of tagged values with indices and a mark bit, with the
   roots s30 §9 gives the real one (the stack, the frames' closures,
   open upvalues, globals, a temp-root stack: `s30-values-vm.md:465-480`),
   collecting only at an instruction boundary on a pending flag
   (`gc.c:49-59`) with C's schedule (`next_gc` 256 KiB first, twice the
   live bytes after: `gc.h:97`, `gc.c:458-460`), a stress mode
   collecting at every boundary after an allocation, and two sweeps:
   R3's compacting sweep (live objects copied into the spare half of a
   pair of slot and payload pools, every index remapped, the halves
   swapped and the old one `reset` — s255's `List.reset` keeps its
   buffer, so nothing is held to the region's end, G33) and, as the
   control, a non-moving sweep (a free list through dead slots, a
   reused slot's payload `reset`, a generation per slot). Measured on
   kasumi under `taskset -c 0-3` in a container, native and release,
   beside C's `fl_smoke --perf` from the same run: (a) memory flat —
   `region_bytes` and RSS after 1,000 and after 100,000 collections of
   a garbage loop (G33's failure is growth); (b) the shapes of the three
   smoke programs (`fl_smoke.c:112-123`) within 2× of C (fib24 7.332 ms,
   map10k 2.111, motion100k 29.660: `fletch_smoke.txt:32-34`) and the
   worst pause; (c) a cycle collected once unrooted; (d) each root,
   dropped but one, keeping its object; (e) under stress, a planted
   index held across a re-entrant call (the shape a `list.map` native
   takes) caught — by the swapped-out half's poisoned tags when
   compacting, by the generation when not; (f) the checked machine
   running it (`wolf test`). G6's shape (b) gets its one witness: a
   cyclic `shared` value refused, E1006. The verdict with its numbers is
   R-yw07-1, asked before deliverable 4 is written; the value it
   measures is R-yw07-2's.
3. **The spec and the front end** (s28, s29). `docs/fletch-spec.md`
   copied verbatim from the pin with a drift check (`tools/check-runtime`'s
   shape: the bytes against the pin's), §16 at A1–A4
   (`fletch-spec.md:660-665`): 13 kinds (§9.1, `:389-396`), 22 reserved
   words (§15.1, `:613-620`). `fl.lex`: s29 §1's table
   (`s29-lexer-parser.md:70-87`) — `#` comments keeping their newline,
   `0x` and `_` digits with overflow an error at lex, `1.foo` as INT DOT
   IDENT, the escapes with the caret on the escape, `\u{…}`'s bounds and
   surrogates, keywords by their terminator, `@[` one token entering the
   motion space with a depth counter for `H(`, `a` before an arrow, the
   UTF-8 arrow aliases, counts capped at 65,535, CRLF one NEWLINE and a
   bare CR an error, invalid UTF-8 one error and a resync; a float
   literal's value through R-yw07-4's conversion (C runs `strtod` over
   the token's bytes, `lex.c:335-349`). `fl.ast`: a node pool of
   indices (MAP §1's tree row), child lists sized once, the port's node
   size recorded beside C's 48 B (`s29:244`). `fl.parse`: recursive
   descent with precedence climbing, s29 §3's newline rule in one
   function, `incomplete` never with `had_error` (DoD 10's five cases),
   the depth cap (`parse.c:411-412`; recursion bounded, G41),
   `fl_parse_literal` as its own entry that cannot represent a call
   (§12.1). `fl.diag`: `path:line:col: error: msg`, the source line and
   `^~~~` (`diag.c`), the 20-error cap and its message, expected/found
   wording, the four special-cased messages, panic-mode recovery (the
   eight one-typo fixtures: exactly one diagnostic each). `fl.dump`:
   `fl_ast_dump`'s s-expressions, floats as `%.17g` (`dump.c:271-275`).
   Unit: `test_fl_lex` (27), `test_fl_parse` (21) — **48**. Fuzz:
   `fuzz_fl_lex` (102 lines: forward progress) and `fuzz_fl_parse` (250:
   `fl_parse`, `fl_parse_literal` and `fl_data_read` over the same bytes
   and again inside a plugin-manifest frame, `fuzz_fl_parse.c:213-244`;
   the error cap, the 64 MiB arena guard as a `region_bytes` cap, never
   `incomplete` with `had_error`), both over the `fl_parse` corpus (23
   files; `fuzz_fl_lex.c:100-101`) and `tests/fuzz/dict/fuzz_fl_parse.txt`,
   200,000 iterations at seed 1 (`Makefile:101-102`, `:2266-2267`), on
   `tools/fuzzgen` with `--against-oracle` (the report line C's byte for
   byte, `tools/run-fuzz-state`'s shape); `fuzz-plug-manifest`'s hour
   (`Makefile:2278-2279`) is yw14's. Perf: s29's 500 KiB literal file
   under 50 ms (a smoke, `s29:226-227`), beside C. Differential:
   `fl_ast_dump` of every `.fl` under `tests/fletch/` (56) and of the
   three fuzz corpora (23 + 3 + 7) byte-identical to C's
   `yew fl --dump-ast` (R-yw07-7).
4. **Values, the compiler, the VM and the GC** (s30, at the shapes
   R-yw07-1, -2 and -3 rule). `fl.value`: the 15 tags and
   `fl_type_name` (`s30:47-98`), truthiness, equality (int against float
   numerically, identity for objects), `fl_hash` over str, int and bool
   only, the heap header's mark, flags and `aux` (a string's FNV-1a
   hash, otherwise the insertion sequence `list.sort`'s total order
   reads, `gc.c:43-45` — never an index); strings `List[byte]` held
   verbatim (s30 §10, invariant 2: never `str`), interned at 64 B and
   under (`value.h:321`), compared by length, hash and bytes; `FlMap`
   exactly as s30 §3's table (`s30:130-158`: dense entries in insertion
   order, tombstones, a re-insert at the end, compaction only past
   `ndead > n/2`, growth at 70 %, powers of two, linear probing).
   `fl.opcodes`: the 60 opcodes' operand shapes and stack effects from
   `opcodes.def` as one table with a drift check against the pin
   (`tools/check-cmdtab`'s shape), the 60 and the `0xF0` ceiling
   asserted (`s30:273-278`), `fl_disasm_chunk` byte-identical
   (`0042  12:5  GET_LOCAL   3 ; x`; floats `%.17g`, `opcodes.c:153`).
   `fl.compile`: constant dedup by tag and bits (`5`/`5.0` and
   `0.0`/`-0.0` distinct), 256 locals, `let x = x`'s diagnostic,
   by-reference upvalues shared within a scope, a fresh binding per loop
   iteration, jump patching and its limits, `emit_loop_exit`'s order
   (`s30:328-337`), `max_stack` from the table, the line-run table with
   columns, a motion block preassembled into one `FlMotionProg`
   (`s30:557-568`) with its CMDWORD checked (R-yw07-5, -6). `fl.vm`: the
   dispatch per R-yw07-3; the limits (`vm.h:19-21`: 16,384 stack slots,
   256 frames, 64 handlers) and the step limit raising a catchable
   `"limit"`; `fl_raise`'s unwind order (`s30:419-426`); `edit` a plain
   block and a motion block raising `"motion"` against the null host;
   `error(v)` the prelude's (`std.c:106-146`); `IMPORT` through
   deliverable 5. The C at the pin, not the sprint text: s33 found six
   defects in s30–s32's landed code (`s33:445-468`: `map.clear`, `for
   k, v` over a list, `for x` over a string, the two-deep closure,
   `error(v)` missing, `io.print` in the REPL), fixed only in the C.
   `fl.gc`: R-yw07-1's sweep; s30 §9's eight roots (the stack, the
   frames, open upvalues, globals, modules, the handle table — rooted
   and empty until yw09 —, temps, the compile chain `vm.h:187`); the
   weak intern table cleared before the sweep (`s30:508-511`);
   `YEW_FL_GC_STRESS`/`FL_GC_STRESS` read at VM init (`vm.c:137-138`);
   `bytes` charged at C's LP64 object sizes so `next_gc` falls on C's
   instruction and the collection counts equal C's (0, 0 and 155 over
   the three smoke programs, `fletch_smoke.txt:36-37`). Unit:
   `test_fl_compile` (11), `test_fl_vm` (30), `test_fl_gc` (15),
   `test_fl_motion_compile` (2: `compile.c`'s highlight flattening and
   explicit count, added with Sprint 34's API in sagitta `59969789` but
   `compile.c`'s) — **58**; s30's `test_fl_value`, `_map` and `_closure`
   do not exist at the pin, their cases being `test_fl_vm`'s and
   `test_fl_gc`'s (re-derive which). The GC-stress lane: every `fl`
   unit file under `YEW_FL_GC_STRESS=1` (`Makefile:3118-3123`).
   Differential: the executed-opcode trace of `fl_smoke --trace`'s 21
   fixtures (`fl_smoke.c:60-109`) against C's, built `CFLAGS_FL_TRACE=1`
   in a second BUILD directory of the oracle clone (`Makefile:3136-3167`),
   byte for byte after the `# dispatch:` line and twice across processes
   (`:3152-3167`: map order); `fl_disasm_chunk` of the 56 and the
   corpora against C's `--dump-bytecode`.
5. **The standard library and modules** (s31). `fl.std`: the
   registration table in C's order (`std.c:43-50`: the seven, then `buf
   win cur span opt ed ai` per R-yw07-6) and the prelude
   (`std.c:242-257`); the argument helpers the one place a type error is
   worded; arity checked at `CALL`; s31's 117 natives
   (`s31-stdlib.md:589-599`) and the pin's whole `yew fl
   --list-natives`, read from C, line for line. `str`: grapheme-aware
   over yw00's `unicode.grapheme`, the `_bytes` variants refusing to
   split a cluster (`s31:132-148`), `upper`/`lower` over yw03's
   `unicode.case` (`s31:150-165`), widths over `unicode.width`. `list`:
   the mixed-type total order, mutation during iteration raising, and
   the comparator called in `yew_sort_stable`'s order and count, never
   after it has raised, into a scratch committed on success
   (`stdlist.c:339-411`; a comparator that prints is observable).
   `map`. `math`: `math.random`'s xorshift64* and its fixed seed,
   process-global as C's (`stdmath.c:300`: a module `var` of
   `wrapping[u64]`, static data since s252, behind `unsafe` naming
   invariant 8 — the census grows by one). `fmt`: the directive grammar,
   cell widths and totality (`s31:260-323`), `fmt.repr` as pure-literal
   source, its conversions per R-yw07-4. `io`: capability-checked by the
   calling function's defining module (R-yw07-6's `origin.c:203-275`),
   `io.write` atomic through `text.file`'s save, `io.glob`'s rules
   (`s31:353-362`), errno names per R-yw07-9 (`stdio.c:59-94`), paths per
   R-yw07-8. `re`: over yw04's `search`, the 64-entry LRU held in the VM
   (C's `g_cache` is process-global, `stdre.c:69`; module state of a
   run-time value is E1010, G27; results unchanged past 64 patterns,
   `s31:573-576`), the template language, the empty-match rule.
   `fl.module`: the four rows (spec §11, `fletch-spec.md:452-461`, A3's
   runtime row last; `module.c:236-286`) over R-yw07-5's runtime lookup,
   the `(realpath, origin kind)` cache key, the cycle message naming
   every file in load order, exports. Unit: `test_fl_module` (9),
   `test_fl_caps` (5), `test_fl_std_str` (9), `test_fl_std_list` (5),
   `test_fl_std_map` (4), `test_fl_std_math` (6), `test_fl_std_fmt` (14),
   `test_fl_std_io` (13), `test_fl_std_re` (14, over `re_golden.h`, the
   table `src/search_re_match_test.lu:13` already promises) — **79**,
   over a port of `tests/unit/flfix.h`'s fixture (a result as text, a
   raise as `!kind: msg`). Fuzz: `fuzz_fl_std` (355 lines: random
   arguments through every `str` and `fmt` native, each outcome a value
   or one of the 13 kinds `fl_kinds.h:19-21` lists; corpus `fl_std`, 3
   files) at 200,000 × seed 1 (`Makefile:2268`), `--against-oracle`. s31's
   500-value `fmt.repr` round trip and 100,000-template fuzz
   (`s31:569-572`) inside the unit files, as C has them.
6. **The data bridge, beside the hand codec** (R-yw06-1 = A). `fl.data`
   (`data.c`): `fl_data_read` over `fl_parse_literal` with its caps
   (`data.h:20-25`: 8 MiB, 1,000,000 nodes, depth 32, 4,096-byte
   strings) and its `"pure-literal data: …"` diagnostics;
   `fl_data_write` with bare keys where they are identifiers, C's string
   escapes and `data_float` (`%.17g` with `.0` appended when no `.`,
   `e` or `E` appears, so infinity writes `inf.0`: `data.c:281-299`).
   The state path stays on yw06's hand codec (`ws.fl_emit`,
   `ws.fl_parse`, `ws.fllit`) until yw09's swap retires it; the gate is
   a differential between the two over `tests/unit/fixtures/wsstate/v1/`
   — the 22 canonical documents read and re-written byte-identical by
   both, the 4 `noncanonical/` written to the same canonical bytes, the
   20 `invalid/` refused by both — and over the `state.fl` C writes in
   `s25_resume_exact`'s session. `edit.fldata` (R-yw03-2, R-yw04-4)
   stays until yw09 too. Unit: none of its own (`test_state_*` reach it
   at the pin and are yw06's over the hand codec; `test_state_diff`, 2,
   is yw09's). Fuzz: `fuzz_fl_parse`'s data mode (deliverable 3).
7. **`yew fl` from the command line, its suggestions and its trace**
   (R-yw07-6, R-yw07-7). `src/flcli.c`'s non-interactive forms in place
   of `src/yew.lu:141-142`'s refusal: `yew fl FILE`, `-e EXPR`, `-c
   FILE`, `--dump-ast`, `--dump-bytecode`, `--list-natives`, `--caps`
   and `--origin` (`flcli.c:596-619`), stdin read as one script when it
   is not a tty, the exit codes (`flcli.c:320-333`: a `capability` or
   `io` error escaping is 3, any other 1; compile diagnostics 1; an
   unreadable file 3), no terminal ownership in file mode
   (`s32:80-84`), `--help` byte for byte; the REPL (stdin a tty,
   `flcli.c:619`) and `--selftest-fl-bug` (`:620-628`) refuse by name
   naming yw08. `fl.suggest` (`suggest.c`: OSA distance scaled ×2, the
   case-only half cost, the length floor on the candidate, three
   suggestions, scope then bytes: `s32:255-307`) under the core's own
   messages (`vm.c:276-336`, `motion_tab.c:14-40`). `fl.trace`
   (`trace.c`: `fl_trace_attach` at `vm.c:1561`; `fl_trace_render`'s
   first line `error: KIND: msg`, the frames named by s32 §6's closed
   table, each site the CALL's own pc, elision past 32 frames, the
   innermost caret skipped when its file changed: `s32:204-253`). Unit:
   `test_fl_didyoumean` (6), `test_fl_trace` (7) — **13**. Fletch
   goldens: the **39** units of `tests/fletch/` (the 20 top-level files,
   `11-modules/` 1, `13-capability/` 2 — `run.c:992-1041` takes every
   `*_main.fl` —, `15-style/` 1, `errors/` 14 and `errors/cycle/` 1;
   `meta/`'s 11 and `roundtrip/` are skipped by the walk,
   `run.c:1075-1082`) through `tools/goldens --suite fletch` (the
   oracle's `fletch_run --yew BIN`: a `PASS` or `FAIL` line a unit and
   `fletch: total=… pass=… fail=… skip=…`, `tools/goldens:148-155`).
   What each needs: every uncaught kind is read from the trace's first
   line (`run.c:912-923`); `errors/uncaught_user_error.fl:5`'s
   `ERROR_LINE: 11` from the innermost `  at` line (`run.c:929-935`);
   `errors/kind_name.fl:4`'s "did you mean" from `fl.suggest`;
   `34-editor.fl:18` and `errors/kind_handle.fl:4`'s "no editor" from
   R-yw07-6's headless natives; `09-errors-compile-only.fl`'s `-c`;
   `13-capability/*`'s `--origin` and `--caps` (`run.c:602-632`);
   `errors/runtime_dir_last.fl:3-4`'s `tried:` list ending in
   `/runtime/a3-missing.fl`. Smoke: `scripts/smoke.sh:429-505`'s ten
   `yew fl` rows against both binaries (exit 0, compile 1, runtime 1,
   unreadable 3, io 3, `-e` and its nil, stdin, `--list-natives`,
   `--help`), each citing its line; the eleventh, `--selftest-fl-bug`'s
   4 (`:506-513`), is yw08's. PTY: none — campaign 06's three
   (`s32_repl_session`, `s32_bug_restores_the_terminal`,
   `s33_hello_world_repl`) are the REPL's. Script: none (`--batch`,
   yw09). Differential: each unit's stdout and stderr against C's,
   beyond what its directives check.
8. **The gates**: `tools/check-test` and `--native` green with 0.2.35's
   `--nocapture` and `--no-native-fallback` (yew#20) and the per-case
   checked run for each `[native]` row (G29, which s250 now names and
   counts); the 39 units green by name — 39 of 39 if R-yw07-6 and -7 are
   taken as recommended; otherwise `tools/goldens` gains the fletch
   suite's by-name verdict, each unit's line read against a committed
   list of the units red by design, by owner
   (`tools/goldens-yw06-cases.txt`'s shape) — and again under
   `YEW_FL_GC_STRESS=1` (s33's stress run, `Makefile:4010-4012`; the
   runner reads it at `run.c:1797` and the child inherits it) and twice,
   byte-compared (`Makefile:4015-4026`; the ledger half is yw08's); the
   differentials of deliverables 3–7 and the three fuzzers in CI by
   name; the 2× gates on kasumi under `taskset -c 0-3` in a container,
   the port's own in-process harness beside C's from the same run:
   `fl_smoke --perf`'s three (`fletch_smoke.txt:32-34`) and
   `perf_fletch.c`'s headless rows — `startup` (budget 2 ms),
   `parse_only` over `runtime/init.fl`, `motion_dispatch` (1 µs an op
   against the null host), `fib27`, `strbuild_join`, `strbuild_concat`
   with its `> 20` ratio, `map_heavy`, `list_sort`, and `gc_pause`
   recorded (`perf_fletch.c:1044-1173`; `fletch_dev.txt:44-58`) — each
   absolute budget read beside its ratio and gated by yw08 (s33 §5).
   The live-editor rows (`config_load`, `config_reload_500`,
   `macrolib_scan_200`, `motion_editor`, `query_cur_pos`,
   `insert_100k`) are yw09's. **M-YW6 stays yw08's** (s33 §6's four
   artifacts: the smoke rows, `-e`, `s33_hello_world_repl`, the coverage
   gate); this lane's conformance and stress runs are its first half.
9. **The static binary** (track rule 7).
   `tools/build --static` (`target/static/yew`) in a baseline-glibc
   Ubuntu container on kasumi (`localhost/px13-ubuntu`, where pax's
   `tools/mkyew` builds it; never kasumi's CachyOS x86-64-v4 glibc);
   `readelf` (ET_EXEC, no `PT_INTERP`), `yew --version` and `yew fl -e`
   run, the sha256 read twice with the byte count, handed back for pax's
   `user/yew.pin` — a pax lane's change, never this lane's.
10. **The note and the map**: `notes/yw07-fletch-core.md` with the five
    sections, the measurements, the `unsafe` census delta, the toy VM's
    verdict, the value's and the heap's shapes and why; `docs/MAP.md`
    §1 (the VM's rows: the value, the arena, the dispatch, the native
    table), §2 (the `src/fl/` row and `src/*.c`'s `flcli` per R-yw07-6
    and -7; the `util` row if R-yw07-5 moves the runtime lookup;
    `stdai`'s owner), §3 (the campaign-06 row), §5 (G6 closed by
    deliverable 2; deliverable 1's retirements; G44 recorded as not
    biting Fletch; the float and errno rows R-yw07-4 and -9 may add),
    §6 and §7's yw07 and yw08 paragraphs; yw08's contract drafted in
    full from §7.

## Rulings (to ask at launch unless decided)

- **R-yw07-1 — the GC's sweep, measured** (R3 = A). R3 fixed the shape
  (an arena of tagged values with indices and a mark bit, a compacting
  sweep) and asked for the toy VM first. What R3 did not see: in wolf a
  sweep frees nothing a `List` holds until its region ends (G33), and
  the pin's natives that call back into the VM (`list.map`,
  `list.sort`'s comparator, `re.replace_fn`) hold object references
  across a collection, though the collector itself never runs inside a
  native (`gc.c:49-59`). (A) R3 as ruled, if deliverable 2's criteria
  hold: a compacting sweep into the spare half of a pair of slot and
  payload pools, the old half `reset` (s255), every root and field
  remapped, a re-entrant native re-reading its indices from its rooted
  slots after the call, the swapped-out half's tags poisoned under
  stress (recommended); (B) if the compacting sweep fails a criterion
  (memory grows, or the stress plant goes uncaught), the same arena with
  a non-moving sweep — a free list through dead slots, a reused slot's
  payload `reset`, a generation per slot —, which amends R3's
  "compacting" and is asked with deliverable 2's numbers; (C) a
  `shared`/`weak` graph — refused by E1006 for a cyclic heap (R3's B),
  its witness in deliverable 2.
- **R-yw07-2 — the value's representation.** C's `FlValue` is a tag
  byte and a 64-bit union, 16 B (`s30:60-68`); NaN boxing is refused for
  1.0 because Fletch ints are i64 (`s30:70-79`). (A) a struct of
  scalars — `t` (the tag, `FL_NIL` to `FL_REGEX`), `i` (the int, the
  bool, an object's arena index, the handle slot and generation yw09
  needs), `f` (an `f64`) —: no union, no bit punning, `Copy`, and naming
  no region (s252: a value whose type reaches no storage names none), so
  it is stored anywhere without E1004 (recommended; its size recorded
  beside C's 16); (B) a mixed-payload enum (`Nil`, `Bool(bool)`,
  `Int(int)`, `Float(f64)`, `Obj(int)`, …), which compiles on every
  tier since s257, measured against (A) on the toy VM if the lane wants
  the comparison; (C) one boxed `int` — refused for C's own reasons.
  Floats are `f64` either way (R-yw07-4).
- **R-yw07-3 — the dispatch, and function values across modules**
  (G19/G20). C's reference VM is one `switch` over the opcode byte with
  a computed-goto twin behind a probe, kept from drifting by
  `fl-dispatch-parity` (`s30:380-417`; `Makefile:3136-3167`); its
  natives are `FlNativeDef` rows holding function pointers
  (`s31:49-91`) and its host seam a struct of three function pointers
  and a `void *` (`s30:540-568`). wolf has no label addresses, and at
  0.2.35 a function value crosses a module on every tier (s251), which
  deliverable 1's yew#27 makes the shape of the port's registries. (A)
  the opcode loop is one `match` on the byte in one function (literal
  arms, each `FL_OP_*` name in a comment: a `match` arm on a const name
  binds, W0801), the computed-goto twin not ported (C's own numbers put
  the two within noise, `fletch_smoke.txt:32-41`), the parity gate
  re-aimed as deliverable 4's C↔port trace; the natives and the host
  seam take the one shape deliverable 1 leaves the registries in —
  tables of function values if yew#27's conversion holds the perf gate,
  else a native id per row and one `match` —, never both (yw06's rule);
  a function value taking the VM `mut` that any tier refuses is a STOP
  with its witness, and the natives then take the `match` (recommended);
  (B) natives a kind id and one `match` whatever yew#27 does — two
  shapes once the registries convert; (C) a threaded dispatcher over
  function values — a second dispatcher for no measured gain.
- **R-yw07-4 — floats (G44) and the libc conversions.** G44 does not
  bite Fletch: the spec's float is `f64` (§1.4,
  `fletch-spec.md:100-101`; §4, `:256`), `src/fl/` declares and casts
  to no binary32 `float` at the pin (each of the 39 lines of its `*.c`
  and `*.h` that match the word is a comment or a message), and the
  checked machine runs `f64`. What bites: C prints and reads floats
  through libc — `%.17g` (`data.c:284`, `dump.c:275`, `opcodes.c:153`),
  `%.*e` and
  `%.*f` with the precision clamped to 0..17 (`stdfmt.c:169-187`), the
  shortest of 15, 16 and 17 significant digits that `strtod` reads back
  (`:199-236`), and `strtod` for literals and `str.to_float`
  (`lex.c:335-349`, `stdstr.c:903-913`; its accepted syntax — signs,
  `inf`, `nan`, hexadecimal floats, leading space — is libc's) —, and
  the port may not read a libc's source. (A) measure wolf-std's `f64`
  formatting and parsing against C yew on a generated corpus (every
  special value, subnormals, powers of two and ten, halfway cases,
  100,000 random bit patterns, every precision 0..17) through `fmt.f`,
  `fmt.float`, `fmt.repr`, `str.to_float`, the lexer and the data
  writer, on Linux and macOS; use std for each conversion it matches
  byte for byte, write the port's own exactly rounded conversion from
  IEEE 754 and C11's definitions (§7.21.6.1, §7.22.1.3) for each it does
  not, list the mismatch as the next G row, and STOP with the rows if C
  itself differs by host (recommended); (B) the port's own conversions
  throughout; (C) std's throughout with the mismatches recorded —
  refused by rule 2.
- **R-yw07-5 — where `fl` sits.** The pin's core reaches up:
  `compile.c:678` validates a motion word against the command registry
  (`motion_tab.c:22-31`, `yew_cmd_by_word`); `module.c:254-286`
  resolves the runtime row through `util/runtime_asset.h`, which the
  port keeps in `edit` (`src/edit/runtime.lu`, `runtime_blob.lu`);
  `std.c` includes `edit/ed.h`, `edit/bind.h` and `edit/option.h` for
  the editor's natives, and `stdio.c` includes `edit/ed.h`. yw09's
  editor will call `fl`, so `fl` importing `edit` is a cycle (E0303).
  (A) `fl` is a module below `edit`: the runtime lookup moves down to
  `util`, where MAP §2's `util` row already places sagitta's
  `runtime_asset` and `runtime_blob` (a move with every golden unchanged
  and `tools/check-runtime` green), and the registry's words and the
  editor's natives reach the VM as values its host builds (the `yew fl`
  driver now, yw09's editor later), never `use edit` (recommended); (B)
  the registry's word table moves to `util` too, generated beside
  `edit.cmdtab` — a second copy of the registry, which a plugin's
  run-time command (yw14) would miss; (C) the core inside `edit` — one
  module, no cycle, sixty thousand lines.
- **R-yw07-6 — the pin's core is post-campaign.** yw07's files call
  into files MAP gives later lanes: s32's `suggest.c` (the runtime
  `"name"` and `"key"` messages carry its text, `vm.c:276-336` — a
  `msg` a `catch` reads, so a value and not only stderr — and so does
  the motion-word diagnostic, `motion_tab.c:14-40`) and `trace.c`
  (`fl_trace_attach`, `vm.c:1561`); s34's `origin.h` (`FlOrigin` itself,
  `value.h:19`, `:169-199`) and `origin.c`'s check (`fl_cap_origin`,
  `fl_cap_name`, `fl_origin_name`, `fl_cap_check`, moved from `std.c`
  unchanged, `origin.c:203-275`; a plugin origin with no editor raises
  the same message, `src/mod/plug/sandbox.c:189-191`); `flapi.c` and
  `flruntime.c` (std.c's editor modules and prelude names, and
  `vm.c:1199`'s receiver bind); and s48's `stdai.c`. (A) port yw07's
  files at the pin; pull the pure pieces forward whole — `suggest.c`
  and `.h` with `test_fl_didyoumean` (6), `trace.c` and `.h` with
  `test_fl_trace` (7), `origin.h`'s types and `origin.c:203-275` —,
  `fl_motion_word_validate` over R-yw07-5's word value; register the
  later owners' natives in C's order with their headless path as C runs
  it, native by native (the argument checks and the editor check in C's
  order: `stdai.c:17-18` checks the editor first, `34-editor.fl:61-80`'s
  non-handle cases expect a type check before it; then `"handle"` with
  "no editor is attached", `flapi.c:48-56`) and the editor-attached
  path refusing by name naming its owner, so `--list-natives` and every
  headless answer are C's (recommended; `34-editor.fl` and
  `errors/kind_handle.fl` then hold); (B) s31's surface only — `"name"`
  where C answers `"handle"`, those two units red, `--list-natives`
  short, and `errors/kind_name.fl` and every suggestion-bearing message
  red naming yw08.
- **R-yw07-7 — `yew fl` before yw08.** The 39 units run through
  `yew fl` (`run.c:602-632`: `fl [--caps C] [--origin O] [ARGS] FILE`,
  stdin `/dev/null`), which is `src/flcli.c`, MAP §2's yw08 (the
  `src/*.c` row), while MAP §7 promised yw07 "`tests/fletch/`
  conformance through `yew fl`". (A) yw07 takes `flcli.c`'s
  non-interactive forms (deliverable 7); yw08 keeps the REPL and its
  line editor, history and `:`-commands (s32 §2–§5, `repl.c`),
  `fl_chunk_check` and the structured bug report (§8–§9, `vmcheck.c`,
  `--selftest-fl-bug`), `fuzz_fl_vm`, and s33 whole (recommended); (B)
  the narrowest — `FILE` with `--caps`, `--origin` and `-c`, the trace's
  first line and innermost frame only —, the rest refusing naming yw08;
  (C) none: the 39 wait for yw08 and yw07 is gated by its unit suites
  and the differentials alone, as MAP §7's yw08 paragraph is worded.
- **R-yw07-8 — Fletch strings and paths that are not UTF-8** (G40).
  Fletch strings are bytes held verbatim (`s30:19-21`; `str.from_bytes`
  validates nothing, `s31:127`), so a script can build a path that is
  not UTF-8, which C opens and wolf's `str` paths cannot. (A) every
  Fletch string is `List[byte]`; an `io` path that is not UTF-8 raises
  kind `"io"` naming G40 where C would open it, and `io.glob` skips such
  an entry and counts it among the note's divergences — no unit case,
  conformance unit or golden reaches either (re-derive) (recommended;
  R-yw06-6's shape); (B) a STOP by name at the first.
- **R-yw07-9 — the errno names.** C's `io` errors carry the errno's
  name and the path (`io: ENOENT: /path`, `s31:364-365`) from its own
  26-name table (`stdio.c:59-94`); wolf's fs rows (`not_found`,
  `denied`, `exists`, `io`, …) are coarser, and `test_fl_std_io`
  asserts `ENOENT` (`:95`, `:179`, `:200`, `:215`), `EISDIR` (`:97`)
  and `ENOTEMPTY` (`:198`). (A) each row mapped to C's name where it
  determines one, and where a row covers several, the errno recovered
  by a probe after the failure (a stat of the path for `EISDIR` and
  `ENOTDIR`, a listing for `ENOTEMPTY`), every mapping witnessed against
  C; an errno no probe recovers listed as the next G row (the fs rows
  carry no errno) (recommended); (B) the rows' own names — the asserted
  messages red.
- **Decided**: R3 = A (#93) is the shape; R-yw07-1 asks only the toy
  VM's verdict on its sweep. R-yw06-1 = A: the hand codec is the state
  path until yw09's swap, deliverable 6's differential its gate.
  R-yw03-2 and R-yw04-4: `edit.fldata` reads `init.fl`, the themes and
  the 24 completion specs until yw09; its refusals that name yw07
  (`edit/fldata.lu:286`, `:378`, `:420`, `:445`; `edit/config.lu:289`;
  `edit/compspec.lu:1129`) are re-pointed at yw09, their owner after
  this lane, no golden reaching them. R4: the port is the full build.
  s32's REPL, `vmcheck`, `fuzz_fl_vm` and s33 are yw08's; Sprints
  34–38's editor API, recorder, configuration, `--batch` and macro
  library are yw09's; `shell` and `net` have no stdlib surface in 1.0
  (`s31:531-535`); bytecode serialization is not in 1.0 (`s30:582-584`).

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`; **`Footprint:
cross-cutting`** — the pin moves (deliverable 1) and the gate list is CI
itself (`.github/workflows/ci.yml`'s by-name steps). Read sagitta's
`src/fl/*`, `src/flcli.c`, `tests/unit/test_fl_*` and `flfix.h`,
`tests/fletch/`, `tests/fuzz/fuzz_fl_*`, `fuzzlib.*` and `fl_kinds.h`,
`tests/perf/fl_smoke.c` and `perf_fletch.c`, the spec and the sprint
files freely and cite `file:line`; port the C at the pin, not the sprint
text (s33's six defects, the C1 corrections). **No other language
implementation's, virtual machine's, garbage collector's, compiler's or
interpreter's source, ever** (no Lua, CPython, QuickJS, Wren, no
book's interpreter code), **and no float-conversion library's** (libc's
`printf`/`strtod`, dtoa, Ryu or Grisu sources are not read; the
conversions come from IEEE 754, C11's definitions and black-box runs of
C yew). No dependency but wolf-std. No golden, unit case, conformance
file or baseline edited; a disagreeing one is a STOP with the diff. A
native, a host seam and a registry take the one shape R-yw07-3 rules,
never two; the VM, its heap, its intern table and its caches are VALUES
threaded through their owner (E1010, G27), and the only module state is
`math.random`'s seed behind `unsafe` with its `// # Safety:`. **Every
run of C yew and of the port with a scratch `HOME`, `XDG_CONFIG_HOME`
and `XDG_STATE_HOME` and an explicit `YEW_RUNTIME_DIR`**: import rows 2
and 3 read `$XDG_CONFIG_HOME/yew/fl/` and `~/.config/yew/fl/`
(`fletch-spec.md:452-461`), and `tools/goldens` sets no scratch home
today (yew#11, open: fix it first, listed to close, never closed here);
the maintainer's configuration and state are never read or written.
`13-capability/config_main.fl` writes and removes `build/fletch-tmp-io`
under the runner's directory (`:19-20`, `:96-101`): the conformance
runs, the fuzzers, the stress lane and the perf harnesses run inside a
container (RULES §5), under `taskset -c 0-3` where they time anything.
The toy VM never ships. The static build never on kasumi's host glibc.
The toolchain rule is deliverable 1.

## Inputs (re-derive)

sagitta at the pin: the four sprint files of the header with their
line counts, and s32 (581) and s33 (485) for R-yw07-6 and -7;
`.docs/fletch-spec.md` (691), `.docs/plan/02-fletch.md` (103),
`.docs/plan/00-decisions.md`'s Fletch row; the 31 C files of the header
and `opcodes.def`, `suggest.c`/`.h`, `trace.c`/`.h`, `origin.h` and
`origin.c:203-275`, `motion_tab.c:14-40`, `src/flcli.c`,
`flapi.c:48-56`, `stdai.c`, `src/mod/plug/sandbox.c:178-208`;
`tests/unit/test_fl_{lex,parse,compile,vm,gc,motion_compile,module,caps,
std_str,std_list,std_map,std_math,std_fmt,std_io,std_re,didyoumean,
trace}.c` (17 files, **198** tests: 185 for s29–s31 and 13 for
R-yw07-6, every one an unconditional `T(...)` row of
`tests/unit/registry.c`; `test_fl_repl` 10 and `test_fl_chunkcheck` 5
are yw08's) and `flfix.h`; `tests/fletch/` (56 `.fl` files, 39 units,
`run.c` 1,956 lines, `ledger.txt`, `meta/`); `tests/fuzz/fuzz_fl_lex.c`
(102), `fuzz_fl_parse.c` (250), `fuzz_fl_std.c` (355), `fuzz_fl_vm.c`
(175, yw08's), `fuzzlib.h`, `fl_kinds.h`, `dict/fuzz_fl_parse.txt`, the
`corpus/fl_parse` (23), `fl_std` (3) and `fl_vm` (7) corpora;
`tests/perf/fl_smoke.c` (314), `perf_fletch.c` (1,265),
`baselines/fletch_smoke.txt` (64) and `fletch_dev.txt` (58);
`scripts/smoke.sh:429-513`; `Makefile:101-102`, `:2240-2279`,
`:3102-3167`, `:3966-4026`. The yew repo at yw06's merge:
`wolf-toolchain.toml`, `src/yew.lu` (the `fl` refusal), `src/ws/`
(`state_lit.lu`, `fl_emit.lu`, `fl_parse.lu`, `fllit.lu`),
`src/edit_state_fuzz.lu`, `tools/fuzz-state/main.lu`,
`notes/yw06-evidence/g20-closure/`, `src/edit/{fldata,config,compspec,
cmd,cmdtab,runtime,runtime_blob}.lu`, `src/util/` (`sort`, `intern`,
`buf`, `f32`), `src/unicode/` (graphemes, widths, case),
`src/search/` (the engine `re` binds), `src/text/file.lu` (the atomic
save), `tools/goldens`, `tools/goldens-yw06-cases.txt`, `tools/oracle`,
`tools/fuzzgen/`, `tools/run-fuzz-state`, `tools/check-runtime`,
`tools/check-cmdtab`, `.github/workflows/ci.yml`, `docs/MAP.md`,
`notes/yw06-workspace-finder-mouse.md` (its STOPs and its red-by-name
list); the wolf 0.2.35 release notes (s250–s259) and the issues
deliverable 1 adopts (yew#11, #17, #20, #22, #23, #24, #27, #40); pax
trunk's `tools/mkyew` and `user/yew.pin` (read only).

## Prediction (write before the first change)

The bump to 0.2.35 retires yew#17, #20, #22, #23, #24, #27 and #40 with
their tests green and no golden of campaigns 01–05 changing, and the G20
witness's `twin` builds on the release tier; the toy VM's compacting
sweep holds memory flat over 100,000 collections with s255's `reset`,
catches the planted stale index under stress, and runs within 2× of C,
so R-yw07-1 confirms R3; the front end's AST dumps and disassemblies of
the 56 corpus files and the three fuzz corpora are byte-identical to
C's, and the executed-opcode traces of `fl_smoke`'s 21 fixtures are
identical to C's and stable across processes; the 198 unit cases go
green on the checked machine and natively, again under
`YEW_FL_GC_STRESS=1`; the collection counts over the three smoke
programs equal C's 0, 0 and 155; `fuzz_fl_lex`, `fuzz_fl_parse` and
`fuzz_fl_std` hold their invariants at 200,000 × seed 1 with C's report
lines; the 22 canonical state documents round-trip byte-identical
through `fl.data` and the hand codec alike; the 39 conformance units go
green through `tools/goldens --suite fletch`, under stress and twice
byte-identical; R-yw07-4's corpus decides each conversion, and every
float the port prints or reads — `%.17g` with the data writer's `.0`
(`inf.0`), `fmt.float`'s shortest form, `str.to_float` — matches C's
byte for byte on both hosts; every perf row within 2× of C,
`startup` and `motion_dispatch` under their absolute budgets; the static
binary builds, is ET_EXEC with no interpreter, and runs `--version` and
`yew fl -e`.

## Done-when

Every deliverable with its tests; `tools/check-test` and `--native`
green and the per-case checked run recorded; the toy VM's verdict
recorded and R-yw07-1 answered before the real VM; the 39 units green
by name against the wolf binary as far as the rulings let them, again
under stress, the rest named by owner; the differentials and the three
fuzzers green in CI; the 2× gates recorded on kasumi under `taskset -c
0-3`; the static binary's digest read twice; `docs/MAP.md` updated;
yw08's contract drafted; CI green; PR open with the five sections, shas
as bullets, a test checklist and its `Footprint:` line; `bash
wolf/tools/lane-audit.sh yew yw07 <PR>` passing but for the final run's
green; hand back per RULES.md §6.
