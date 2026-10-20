# yw04 — Execute and search

**Model per ruling #89 R4, chosen at launch. Crawl 54+. Drafted by yw03
from `docs/MAP.md` §7 and sagitta campaign 04 with the s57 rows that
land on its surfaces.** Ruling #89 (`sprints/yew/index.md`); the track's
seven standing rules; `docs/MAP.md` (the idiom §1, the gaps §5, the
rulings §6, as yw03 left them); `sprints/RULES.md`. Ports sagitta
campaign 04 (`.docs/sprints/04-execute-search/`: `s18-cmdline.md`,
`s18_5-reactive-cmdline.md`, `s19-shell-execution.md`,
`s20-regex-engine.md`, `s21-search-replace.md`, 2,726 lines at
`sagitta.pin`) and the prompt and shell rows of campaign 13 that build
on it (`13-performance/s57_17` the pager, `s57_18` shell completion,
`s57_23`–`s57_32` the shell context engine, specs, help parsing, the
fish oracle, the persistent session, prompt editing and the yank stack,
prompt selection and the clipboard, history and the table, the fish
extras, cd-aware completion; 3,592 lines), plus **s57.21, the readline
insert keys**, which MAP §7's list omits: there is no `s57_21` sprint
file at the pin (the commands landed unsprinted, sagitta `d52250b9`,
2026-09-14; s57.28's prerequisites name them), but the PTY registry
labels its four cases `s57_21_*` and yw03's `edit.cmd_owner` already
routes `src/edit/readline_cmds.c` here. The C it ports: `src/ui/`
`cmdline.c`, `cmdcomp.c`, `cmdhist.c`, `cmdparse.c`, `cmdedit.c`,
`comphelp.c`, `compfish.c`, `compgen.c`, `compspec.c`, `shctx.c`,
`menu.c` with their headers (23,328 lines); `src/ws/finder.h` and
`fuzzy.c` (394 — s18.5 §1 pulls them forward from s26, `finder.h:5-7`);
`src/edit/` `shell.c`, `shell_cmds.c`, `shsession.c`, `job.c`,
`search_cmds.c`, `jumplist.c`, `readline_cmds.c` with headers (7,229);
`src/search/` whole (7,491); `src/unicode/category.c`, `category.h`,
`case.h` (108) and the generated `tables_cat.c`, `tables_case.c`
(5,693). **38,550 hand-written C lines** and 25 completion specs
(`runtime/completions/*.fl`, 6,743 lines of Fletch data, copied
verbatim). The port inherits the idiom yw00–yw03 set (regions/`List`/
`Map`, `str` tables, `(s, at, end)` byte conventions, `copy` on lent
getters and list elements of struct type, `distinct` coordinates at
boundaries only, node pools of indices, the one `unsafe` module var per
`[mem.static.2]`, no `.bytes()` re-bound in a hot loop — bind once, the
environment and every registry a threaded VALUE, never module state of a
run-time value (E1010), never a function value across a module boundary
(wolf-lang#806, G19/G20): a completion source, a generator, a job's
consumer and a menu's host are KINDS matched in one place, as yw03's
command registry is), and yw03's module rule: every `ui` file that takes
the `Ed` lives in `edit` (`src/edit/*.lu`, sagitta's file names kept).

## Deliverables

1. **The toolchain, first.** The pin at yw03's merge (wolf 0.2.33 /
   lupin 0.1.54 / wolf-std `cceda63`) unless 0.2.34 (s247 + s248) is
   released at the lane's start (`gh release list -R wolffe-lang/
   wolf-lang`, read and quoted with its time; at yw03's drafting,
   2026-10-20T19:43Z, the latest is **v0.2.33**). If it is, the bump is
   yw04's FIRST commit with its prediction, and it ADOPTS what yw01–yw03
   met as gaps, each with the test that is KNOWN-RED, SKIP or interim
   today turned green: `os_signal_wait_fds` (G2, #795) for the loop —
   the `VTIME` interim (`term.tty_wait`) and yw03's drain mode
   (`term.tty_drain_begin/end`) retired — and for the job pipes;
   `fs_sync`/`fs_sync_dir` (G3, #796) at `text.file`'s named sync sites
   and the journal's (`save_fault_shim_contract`, the replica's
   determinism order); `fs_realpath` (G4, #797) for
   `text.file_realpath`; `os_fork` (G30) for the clipboard writer's
   double fork; the `[os.term.mode]` widening (G34, wolf-lang#802) for
   `ICRNL`/`OPOST`/`ISTRIP`, which retires yw03's LF-as-Enter interim
   (`term.input_set_lf_enter`, `term.tty_icrnl_stuck`, R-yw03-4) — the
   port then reads CR as Enter and LF as `C-j`, as C does
   (`tty.c:521-543`); and `os_term_restore_at_exit` (G1, #794, #93 R1 =
   C) if yw01's guard is to retire with it (yw01's own lane decides; a
   note, not a deliverable here).
2. **E mode, whole** (s18, s18.5, s57.17, s57.21, s57.28–s57.31):
   yw03's narrow `:` (`src/edit/cmdline.lu`, R-yw03-1) replaced by C's
   prompt — a one-line `TextBuf` with a real cursor set in its own
   `Win` (yw03's hidden target buffer and window already are that
   shape), the history (`cmdhist.c`: cap, dedupe-to-end, frozen-stem
   walk, concurrent append under `$XDG_STATE_HOME`, no history I/O
   under `--batch`/`--clean`), the grammar (`cmdparse.c`: tokens, the
   9-row expansion table, the three quoting forms, range prefixes with
   the six `range_policy` rows — today's "command ranges" refusal goes
   — and the 13 error messages verbatim with the caret at `tok_lo`),
   the completion engine (`cmdcomp.c`: sources as a registration of
   KINDS, the LCP, quoting), the ranked-list widget (`menu.c`, s18.5
   §5 — `menu.h:4-13`), the fuss-derived fuzzy scorer and ranker
   (`ws.fuzzy`, s18.5 §1, at s26's paths so yw06 inherits it), ghost
   preview, the parser's hint, every menu action a named
   `ed.cmdline.menu.*` command, the pager and its `… and N more` tail
   (s57.17), history versus the table (s57.30), the full readline set
   over yw02's `text.yankstack` (s57.28), Shift-selection with the
   system clipboard (s57.29, `text.clipboard`: OSC 52 in a terminal, the
   subprocess backends G30's STOP), `A-s`/`A-e`/`A-h` (s57.31; `A-e` is
   `ui/cmdedit.c`'s `*command-line*` buffer), and the Insert-mode
   readline commands (`readline_cmds.c`: kills, transposes, word case,
   aggregate over every cursor as one transaction). `:fl` refuses naming
   yw08 (s32); option and value completion stay the empty providers
   s18.5 ships until the options model (s36, yw09); `:g` is the
   permanent non-goal (s21 DoD 12) with its Fletch-query guidance. The
   menu's clickable rows (s18.5 §8, `s18_5_cmdline_click_row`) need
   s22's region registry (yw05): ruling **R-yw04-2**. Unit:
   `test_cmdcomp` (31), `test_cmdhist` (7), `test_cmdparse` (9),
   `test_cmdrange` (3), `test_cmdline` (44), `test_menu` (11),
   `test_fuzzy` (14), `test_prompt_keys` (56), `test_readline_keys`
   (33). PTY: `s18_cmdline_*` (16), `s18_5_*` (6), `s57_17_*` (3),
   `s57_21_*` (4), `s57_28_*` (4), `s57_29_*` (6), `s57_30_*` (5),
   `s57_31_*` (3) — **47**. Fuzz: `fuzz_cmdparse` (1,000,000 inputs,
   the `tok` invariant), `fuzz_fuzzy`. Perf: `perf_cmdcomp` (C's links
   the engine in-process: the port's own wolf harness beside C's
   numbers, the 2× rule).
3. **Jobs and the shell** (s19, s57.18, s57.23–s57.27, s57.32):
   `job.c`'s model over `std.process` (`start_job`/`start_foreground`
   with process groups and the foreground terminal, ruling #79,
   available since 0.2.31; exec failure distinguishable from exit 127,
   s19 DoD 3), the three consumption modes — the async stream into a
   job buffer with follow-tail, the synchronous region filter (timeout,
   cancel, rollback, ONE undo transaction, the six §5 outcome rows), read
   at the cursor — the pinned environment table (§7, `YEW_COL` by
   grapheme), the job table, the exit footers, `yew_shell_quote`; the
   terminal handover for `:!!` and interactive commands (s57.18: routing,
   not emulation — `ed.shell.term` keeps refusing as the permanent
   non-goal); the shell context lexer (`shctx.c`, s57.23, "shape beats
   position, position refines"), completion specs and generators
   (`compspec.c`, `compgen.c`, s57.24; the 25 `runtime/completions/*.fl`
   copied verbatim and read with yw03's literal reader `edit.fldata`,
   **R-yw04-4**), `--help` parsing with its on-disk cache keyed by the
   executable's identity (`comphelp.c`, s57.25), the fish oracle and
   history suggestions (`compfish.c`, s57.26: fish is RUN, black box,
   `complete -C`; the CI hosts have no fish and the stub case covers
   it), the persistent shell session (`shsession.c`, s57.27, on by
   default), cd-aware completion (s57.32). The wait over the tty, the
   signals and N job pipes is G2: at 0.2.33 there is one descriptor
   (`os_signal_wait_fd`) — ruling **R-yw04-1**; the filter's
   interleaved write is G30 (s19 DoD 6: 1 MiB of output before stdin is
   read must complete, a blocking write deadlocks) — ruling **R-yw04-3**;
   the history's advisory lock and the help cache's dev/ino are G32's
   rows. Unit: `test_job` (29), `test_job_stream` (7),
   `test_shell_quote` (3), `test_shell_term` (4), `test_shctx` (14),
   `test_compspec` (19), `test_compgen` (12), `test_comphelp` (21),
   `test_compfish` (21), `test_shsession` (17). PTY: `s19_*` (12),
   `s57_18_*` (3), `s57_23_*` (6), `s57_24_*` (6), `s57_25_*` (3),
   `s57_26_*` (4), `s57_27_*` (4), `s57_32_*` (2) — **40**. Fuzz:
   `fuzz_shctx`, `fuzz_comphelp`; `yew_shell_quote` round-trips 100,000
   random strings through `/bin/sh` (s19 DoD 10). Perf: `perf_jobstream`
   (drives a binary: run over both, the 2× rule; 50 MiB streamed keeps
   keypress p99 ≤ 5 ms, s19 DoD 13). Every test that times out, cancels
   or reaps a group (`kill(-pgid)`, SIGCHLD) runs inside a container
   (RULES §5); zero zombies and zero leaked descriptors after the
   200-cycle and 500-spawn lanes (s19 DoD 8).
4. **The regex engine** (s20): `src/search/` `parse.c`, `compile.c`,
   `pike.c`, `dfa.c`, `literal.c`, `pack.c`, `regex.c` — a Thompson NFA,
   the Pike VM for captures, the lazy DFA whose cache flushes rather
   than grows and falls back to the Pike VM after two flushes, the
   literal prefilter, matching that streams through `text.TextIter`
   with chunk carry across pieces (no materialization: the 1 GB test's
   RSS delta < 4 MiB), the §5 limits each with a firing test, the §8
   error rows verbatim (lookaround, backreference and atomic groups give
   the permanent-non-goal message, not a deferral), **no backtracking
   anywhere** (`a(a*)*b` × 100,000 within 50 ms; the four scaling
   patterns `t(10⁵)/t(10⁴) ≤ 15`). Unicode classes and case folding
   from `unicode.category` and `unicode.case`, the generator's new
   `--category` mode (data-only, checked against sagitta's arrays as
   `tools/check-tables` does the grapheme, word-break and case tables);
   `--case` and `unicode.case` landed in yw03 for the selection case
   commands (`sel_actions.c:665`), so only `--category` is new. The module is
   `search` (sagitta's name, std aliased, ruling R5); no `std.regex`
   exists and the port's becomes a candidate (index row 04). Unit:
   `test_re_engines` (8), `test_re_match` (12, over the 188-row golden
   table `re_golden.h`, carried as data so yw07's `re` module replays
   the SAME rows), `test_re_parse` (9), `test_re_unicode` (13). Fuzz:
   `fuzz_re_diff` against `re_ref.c`'s naive oracle ported beside it as
   yw02 ported fuzz_textbuf's (≥ 5,000,000 pairs × 4 seeds, zero
   mismatches), `fuzz_re_compile` (1,000,000 inputs, `err.off` in
   range), `fuzz_re_quote`. Perf: `perf_re_pathological`,
   `perf_re_throughput` (C's are in-process: the port's own harnesses,
   the 2× rule; G8's millisecond clock batches as `tools/perf-unicode`
   does).
5. **Search, replace and jumps** (s21): `search_cmds.c`, `searchui.c`
   (the search prompt IS the s18 widget, `yew_cmdline_edited` firing
   `yew_search_input`), `search.c`, `overlay.c` (the highlight overlay
   bounded by the viewport plus look-ahead — no whole-file scan on a
   keystroke — and damage only where the highlight set changed),
   `replace.c` (the template rows, `&` literal, the `p`-flag case
   inference, the confirm answers, every replace-all and confirm run ONE
   undo transaction, `:%s/^/> /` and `:%s/x*/-/g` terminating),
   smartcase, `jumplist.c` (the jump list and the change list: the push
   rows, the five dedupe/coalesce rules, wraparound at exactly 100, dead
   marks skipped, the 499/501 ms boundary; the serializer round-trips in
   memory and is called by nobody until s25, yw06), named marks and the
   `'a` and `/re/` addresses through the s18 parser. Unit:
   `test_jumplist` (18), `test_overlay` (14), `test_replace` (11),
   `test_search_smartcase` (6), `test_searchui` (21). PTY: `s21_*`
   (17). Fuzz: `fuzz_search` (10,000 ops × 4 seeds). Perf:
   `perf_search_latency` (the port's own harness beside C's), and the
   editor's `latency.search.huge.p99` through sagitta's
   `perf_latency_s56` search session over both binaries (the 2× rule;
   the `search.*_1g_*` rows are `designated` in `budgets.txt` and run on
   the record rig only).
6. **The live-editor torture lane** (R-yw02-1 = A, the launch ruling of
   yw03): sagitta's `kill9` driver with its fault shim over the port's
   live editor (`tests/torture/yew-live-torture.c`, which types `Ndd`, a
   bracketed paste, `s` and `:ed.quit_force\r`, `:181-219`, and arms
   the shim with SIGUSR2 — the port's binary stays dynamically linked
   for `LD_PRELOAD`), in a container on kasumi and in CI's docker step;
   G3's red by its exact line until the pin has the syncs (R-yw02-2's
   KNOWN-RED shape). yw03's narrow `:` with the G34 interim already
   accepts `:ed.quit_force\r`, so the lane is reachable on the first
   day.
7. **The gates**: `tools/check-test` and `--native` green with the
   per-case checked-machine run for every `[native]` fallback (G29);
   campaign 04's **104** PTY goldens (deliverables 2, 3 and 5) against
   `target/release/yew` gated BY NAME in CI beside campaign 03's 62,
   the regex golden table and the differential fuzz green — **M-YW4**
   (index row 04: "the regex corpus and the `:!` PTY goldens"); the
   recorded step narrowed to what is still red by design and names its
   owners: `chrome_cmdline_*` and `chrome_search_*` (8, Sprint 27 §7's
   chrome review, yw06, over this lane's surfaces), `s57_11_*` and
   `s57_12_*` (4, yw06, over this lane's job layer),
   `s35_macro_record_replay_from_e_mode` (yw09), the `startup_` rows;
   the 2× gates on kasumi under `taskset -c 0-3` in a container
   (`tools/run-perf-editor` grown by the editor-driving rows,
   `perf_jobstream` and the search session; the port's own harnesses
   for the in-process C rows), every ratio recorded beside C from the
   same run with the rig's drift.
8. **The note and the map**: `notes/yw04-execute-and-search.md` with the
   five sections, the measurements, the `unsafe` census delta, the job
   layer's shape and why (the kinds that stand in for C's callbacks);
   `docs/MAP.md` §2 (the `ui`/`ws`/`edit` files campaign 04 owns), §5
   and §6 updated; yw05's contract drafted in full from §7.

## Rulings (to ask at launch unless decided)

- **R-yw04-1 — the job pipes at 0.2.33 (G2).** If 0.2.34 is not pinned:
  (A) the job half (deliverable 3's streaming, filter and session) STOPs
  by name until `os_signal_wait_fds` is, the prompt, regex and search
  halves land; (B) a reader task per job (`scope`/`spawn`) feeding a
  channel the loop drains on its `VTIME` tick — #93 R2 chose the
  multi-descriptor wait over threads, so B needs the maintainer's word;
  (C) block the loop on a job (refused: invariant 4). Recommended: A
  while r39 (0.2.34) is in flight; B only if it is not released within
  the lane.
- **R-yw04-2 — the menu's mouse rows.** (A) port the narrow region
  registry s18.5 §8 assumes (`yew_region_frame_begin`/`add`/`hit`,
  last-added-wins, the menu's rows only) and the loop's mouse route;
  yw05 widens it with panes and yw06 with drag and scroll (recommended:
  sagitta itself built §8 narrow); (B) clicks refuse by name until yw05,
  `s18_5_cmdline_click_row` recorded.
- **R-yw04-3 — the filter's write side (G30).** (A) a STOP by name for
  the filter until wolf has a non-blocking pipe write and a write-ready
  wait (R-yw02-3's shape, recommended unless a witness shows B sound);
  (B) a writer task per filter, measured against s19 DoD 6's 1 MiB
  fixture first.
- **R-yw04-4 — completion specs before Fletch.** The 25 spec files are
  literal Fletch data (`compspec.c:938` reads them with
  `fl_data_read`): read them with yw03's `edit.fldata` (R-yw03-2's
  interim, extended), a statement it cannot take refused by line and
  column naming yw07 (recommended).
- **Decided**: `:g` and terminal emulation are permanent non-goals
  (s21 DoD 12; s19 §10 as s57.18 amends it); `:fl` is yw08's; the
  options model and config reload are yw09's.

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. Read sagitta's
`src/ui/cmd*`, `comp*`, `shctx.c`, `menu.c`, `src/ws/fuzzy.c`,
`src/edit/shell*`, `job.c`, `search_cmds.c`, `jumplist.c`,
`readline_cmds.c`, `src/search/*` and `src/unicode/category.c` freely
and cite `file:line`; **no other editor's, shell's, completion
system's or regex library's source, ever** (fish, bash and zsh are run
as black boxes where a sprint runs them, never read). No dependency but
wolf-std. No golden edited; a disagreeing golden is a STOP with the
diff. A completion source, generator, job consumer or menu host is a
kind matched in one place, never a function value across a module
boundary (G19/G20). Signals, process groups, timeouts and reaping only
to processes the test started, inside a container or PAX, never on a
host's process table (RULES §5: yw03 slipped twice, its note §5). The
toolchain rule is deliverable 1.

## Inputs (re-derive)

sagitta at the pin: the five campaign-04 sprint files and the s57.17,
s57.18, s57.23–s57.32 files above with their line counts; the C files of
the header with their headers; `tests/unit/test_{cmdcomp,cmdhist,
cmdparse,cmdrange,cmdline,menu,fuzzy,prompt_keys,readline_keys,job,
job_stream,shell_quote,shell_term,shctx,compspec,compgen,comphelp,
compfish,shsession,re_engines,re_match,re_parse,re_unicode,jumplist,
overlay,replace,search_smartcase,searchui}.c` (28 files, **467** tests,
every one registered in `tests/unit/registry.c`) with `re_golden.h`
(188 rows), `shctx_corpus.h`, `compspec_corpus.h`, `compspec_fix.h`;
`tests/pty/registry.c` (the 104 campaign-04 cases by the prefixes above)
and their goldens; `tests/fuzz/` `fuzz_cmdparse.c`, `fuzz_fuzzy.c`,
`fuzz_re_compile.c`, `fuzz_re_diff.c`, `re_ref.c`, `fuzz_re_quote.c`,
`fuzz_search.c`, `fuzz_shctx.c`, `fuzz_comphelp.c`;
`tests/perf/` `perf_cmdcomp.c`, `re_pathological.c`, `re_throughput.c`,
`search_latency.c`, `perf_search.c`, `jobstream.c`, `perf_latency.c`,
`budgets.txt`, `component-limits.txt`;
`tests/torture/yew-live-torture.c`; `scripts/gen-unicode-tables.c` (the
`--category` and `--case` modes, `:1356-1370`), `ucd/16.0.0/
UnicodeData.txt`, `SpecialCasing.txt`, `DerivedCoreProperties.txt`;
`runtime/completions/`. The yew repo at yw03's merge: `src/edit/
cmdline.lu` (the narrow `:`), `cmd.lu` (`cmd_owner`: every handler of
`cmdline.c`, `cmdedit.c`, `comphelp.c`, `search_cmds.c`, `shell_cmds.c`,
`jumplist.c` and `readline_cmds.c` refuses today naming this lane),
`edit_cmds.lu`'s `ec_shell_prompt` (the `!` seed, ported), `loop.lu`
and `term.tty`'s wait and drain, the G34 interim, `edit.fldata`,
`docs/MAP.md`, `notes/yw03-the-modal-core.md`; wolf-std `std/process`
(`start_job`, `start_foreground`, `group_of`, `poll`, `kill`),
`std/signal`, `std/fs`; the spec `[os.process.*]`, `[os.signal.*]`,
`[os.term.*]`.

## Prediction (write before the first change)

The regex ports with no backtracking, the 188 golden rows and the
differential fuzz green and the pathological table inside its bounds;
the prompt's 47 cases and search's 17 go green without a golden edited
and without one of campaign 03's 62 changing as the narrow `:` is
replaced; the job half's 40 cases are green only on a pin with
`os_signal_wait_fds` (G2) — at 0.2.33 they reach R-yw04-1 and the
filter's interleave reaches G30; `--category`/`--case` regenerate
byte-identical to sagitta's arrays; keypress → paint in the prompt and
the search session within 2× of C yew, regex throughput within 2×, and
`perf_jobstream`'s streamed 50 MiB holding keypress p99 within 2× where
the job half runs.

## Done-when

Every deliverable with its tests; `tools/check-test` and `--native`
green and the per-case checked run recorded; campaign 04's PTY goldens
green by name against the wolf binary as far as the rulings let them
(M-YW4), the rest named by gap; the 2× gates recorded on kasumi under
`taskset -c 0-3`; `docs/MAP.md` updated; yw05's contract drafted; CI
green; PR open with the five sections, shas as bullets, a test
checklist; `bash wolf/tools/lane-audit.sh yew yw04 <PR>` passing but
for the final run's green; hand back per RULES.md §6.
