# yw06 — workspace, finder and mouse

**GPT-6-Astra (Codex), then Claude Opus 5.5 from the state series on;
crawl 54, 2026-10-23.** Contract: planning repo
`sprints/yew/06-workspace-finder-mouse/yw06-workspace-finder-mouse.md`,
which adopts yw05's draft (this repo's
`notes/contracts/yw06-workspace-finder-mouse.md`) whole. Ports sagitta
campaign 05's second half at `sagitta.pin` (`9ace98c2`): workspace
identity and the session state with its resume (s25), the startup plan
(s56.5 §1 and §6), the workspace walk, `.gitignore`, the incremental
filter, the one list picker and its four instances (s26), the mouse
router with its context menus and drag (s27, s57.13, s57.14, s57.15,
s57.22), and the field repairs on ported surfaces (s57.11, s57.12).

The lane started on GPT-6-Astra. Its state worker was stopped by a
classifier refusal on the API side (request
`d65ef6ae-f6c4-475b-ba18-a94bc956a559`) and its perf worker by a Bash
safety evaluator's timeout; neither was retried or routed around. The
lane moved to Claude at the handoff ledger
(`notes/yw06-evidence/lane-state.txt`, 13:18Z), which names every
branch, every checkpoint it had not verified and every deliverable not
started. Everything from deliverable 2's state series on is the
continuation's, and every "UNVERIFIED" checkpoint commit it took was
verified after the pick (§4.2).

**Forks** (the yw05 pattern, sub-branches merged back before the final
head): `yw06-pick` (deliverable 4), `yw06-mouse` (deliverable 5's
router) and `yw06-ctx` (deliverable 5's menus, `mouse.c:2905-3036` and
`ctxmenu.c`/`ctxrows.c`), **three at once** on kasumi 8–11 beside the
lane's own state, startup, field-repair and gate jobs, each in its own
clone with its own PTY runner (the runner embeds absolute paths), and a
fourth agent drafting yw07's contract from the Mac (reads only). ctx
merged into mouse (`b07f406`, `1a18155`), pick into mouse (through
`eb4cce4`), and mouse and pick into `yw06` (`9046919`, `61b90a3`,
`3f2711c`). hasu's block B was granted to the mouse fork if 8–11 bound;
no fork's evidence names hasu. The Astra half ran its codec, state and
perf workers as forks too (`yw06-codec`, `yw06-state`,
`yw06-perf-state`, `yw06-finder`), taken by cherry-pick.

## 1. Forbidden

Track 12's rules and `sprints/RULES.md` §1–§10, as the contract gives
them. sagitta was read only through `git show 9ace98c2:PATH` (and
`git ls-tree`), never checked out or written; no other editor's, no
library's and no kernel's source was read. Every golden is the pin's,
unedited, run through C's own PTY runner. No build on nomad-1, no host
package installed, no `git config` on the Mac side. kasumi work ran in
containers (yw05's `ctr`, an `archlinux:base-devel` with the host's
`/usr` read-only, scratch `HOME`/`XDG_*`, `ulimit -c 0`, a memory cap)
under `taskset -c 8-11`; px62 held 0–3. **8–11 was shared** all lane
long: with r40 until its STOP 2 (the Astra half), then between this
lane's own jobs and forks (below), so no row here claims a quiet rig.
Long jobs ran under `setsid -f` with pid files and were never killed
by name. Signals, forks and fault injection went only to processes the
tests started, inside the container. No merge, tag, release or issue
filed or closed (§5 lists them). No attribution trailer on any commit.

## 2. Inputs, verified

- The contract's counts, re-derived from the pin: the 81 reachable PTY
  cases are held to `tests/pty/registry.c` by name, count and registry
  order by `tools/check-yw06-cases` (R-yw06-7; its four plants caught
  in every run: reordered, duplicate, foreign, missing).
- The wolf and lupin releases, read twice (deliverable 1, §4.1).
- C witnesses before each preparation question, in C first: the
  codec's corpus and cross-read (`notes/yw06-evidence/codec/`), the
  finder's inputs (R-yw06-10: C ignores `.git/info/exclude`, reads
  `.git/info/.gitignore`, a nested disk pattern's anchor has a NULL
  base; `notes/yw06-evidence/finder-inputs/`), the picker's five
  (`notes/yw06-evidence/pick/`), the trials over C first (§4.8).
- The G20 closure witness reduced to four variants
  (`notes/yw06-evidence/g20-closure/`) and checked on 0.2.35 (§4.2).

## 3. Prediction — the hits and misses

The prediction is `notes/yw06-evidence/prediction.txt`, committed at
`ce28597` before the first change.

| prediction | outcome |
|---|---|
| no golden edited; campaigns 03, 04 and yw05's unchanged as the start, the mouse route and the strip's scroll widen | **HIT** for the edit (no golden touched); campaigns 01–05's gates <<CAMPAIGNS>> |
| the codec round-trips the corpus: 22 canonical byte-identical, 4 noncanonical canonical, 20 invalid each reaching a result | **HIT** (`test_state_corpus`, `ws_state_corpus_test`) |
| the C↔port differential on `s25_resume_exact`'s `state.fl` byte-identical both ways | **HIT**: each editor resumes the other's save to the first grid; the first saves equal (6,182 bytes, `saved_at` aside), the second saves of one S1 equal (6,177) — `tools/run-trials` |
| the permille fixpoint for all 999 values through `util.f32` | **HIT** (`ws_state_lit_test`, 1..=999, checked `exit(0)`) |
| a 40-tab restore performs one file read | **HIT** (`ws_restore_of_forty_tabs_reads_one_file`: 40 restored and the bootstrap tab, `file_load_count() == 1`) |
| the 81 reachable goldens green, the router's 68 as one set at the end | **HIT**: 81 of 81 by name on release at `443d271` (`notes/yw06-evidence/continuation/goldens81-release-443d271.log`); the router's 38 → 64 → 68 |
| the walk's determinism and the narrowing equivalence (10,000 appends against a full rescan) | **HIT** (`test_walk`, `test_narrow`; the narrow cases alone past the checked budget pass natively) |
| `fuzz_state`, `fuzz_gitignore` and `fuzz_mouse` hold their invariants | **HIT**, each report line equal to C's driver's |
| every 2× gate within 2× of C, `workspace50` read beside the highlighting caveat | **MISS on three router rows**: the motion burst 6.68×, the menu hover 2.01×, the chevron hover 2.06× (G45, §4.5); `perf_finder`'s open was 2.08–2.45× until `66fcb40` and `7b44ac4` (now 1.35×); HIT on `perf_state` (0.59/0.96/1.13), `workspace50` (1.68), `mem.workspace50` (1.87, inside the 40 MB budget) and `perf_finder`'s four |
| the static binary builds, is ET_EXEC with no interpreter, runs `--version` | <<STATICHIT>> |
| if 0.2.35 lands, yew#17, #20, #22, #23, #24 and #27 retire | **not reached**: 0.2.35 tagged 2 h 44 min after the pin commit; yw07's |
| every run container-isolated, 8–11, `core=0`, a memory cap; shared with r40 | **HIT**; 8–11 was shared with r40, then with this lane's own forks and jobs |
| yew#45's job-stream stall counted, not silently repaired | not exercised by this lane's runs |
| an exit-2 compile error is never a skip or an advisory pass | **HIT**: the perf harnesses' builds are hard steps (seen red in PR #48 at exit 2) |

The forks' own predictions (`notes/yw06-evidence/{pick,mouse}/prediction.txt`;
ctx forked from the mouse fork's prediction, `65b3f5c`, and wrote none of its own): pick's
missed once — it predicted `ed.find.symbol`'s alias red by name for
yw11, and `test_pickers.c:490-510` only checks the registration, so it
is green — and its "every gate inside 2×" held only after two changes;
the mouse fork's missed four times: one case red by name where it
predicted none (the FUSS path row, yw13), four cases past the checked
budget where it predicted none, 38 router goldens green at the base
where it predicted up to 32, and the burst over 2×.

## 4. The sections, and what yw06 measured

### 4.1 The toolchain (deliverable 1) and yw05-tail

yw05-tail landed first as its own PR (#46, merged `83020234`, run
39892355530 green). At the pin decision (`437f874`, 06:01:53Z) wolf
0.2.34 was still the newest wolf release; lupin 0.1.56 existed
(04:43:45Z) but pairs with 0.2.35, which tagged at **08:45:33Z, after
the pin commit**. The lane therefore kept wolf 0.2.34 (`9da7bdcf`),
lupin 0.1.55 (`e642f26`) and the bundled wolf-std `e036bec`, each
archive's digest read twice (x86-64 `88a9dd3d…`, aarch64 `ca5cadf9…`,
macOS `29c8331f…`, lupin `1152abc0…`). The bump to 0.2.35 with its
issues (yew#17, #20, #22, #23, #24, #27, #40) is yw07's deliverable 1.

Before any workspace code, the two harness gaps the tail left: yew#11
(`tools/goldens` and `tools/oracle --unit` ran C yew with the caller's
homes) is `tools/lib-test-env.sh`, a fresh `HOME`, `XDG_STATE_HOME`,
`XDG_CONFIG_HOME` and `XDG_CACHE_HOME` per invocation, held by
`tools/check-test-env` over fixture executables (`f41313e`,
`1c57369`); yew#44 (a perf harness that does not compile counted as an
advisory timing) is a hard compile step in the oracle job (`7050319`).
Both were planted red in PR #47 (run 39919880434: the home plant at job
120302334000, the compile plant at job 120302334031, E0402, exit 2) and
the PR closed unmerged.

### 4.2 Workspace identity and state (deliverable 2, s25)

**The codec** (R-yw06-1 = A: the hand codec as the interim production
path, retired by yw09's swap). `ws.state_lit` ports `state_lit.c` over
`List[byte]` strings, a tree of arena values and indices, never `str`
(G40). The frozen v1 corpus: 22 canonical documents re-emitted
byte-identical, 4 noncanonical re-emitted canonical, 20 invalid each
reaching its result; all 46 fixture paths, modes and blob ids match the
pin; C's and the port's readers agree on all 59 cross-read inputs
(`notes/yw06-evidence/codec/`); the 512-tab maximal document round
trips at 1.041× C. The pinned reader's and writer's own findings
(`INT64_MIN`, a reserved bare key that does not fix-point) are matched,
not fixed: they are C's behaviour and the goldens' bytes.

**The state series** (`ws.workspace`, `edit.state_*`, `edit.ws_*`): the
key and its directory, scoped `:` history (s25 §8), the schema and
option bridges, restore, the commands, recovery and the debounced,
atomic save. The Astra state worker's committed series was taken by
cherry-pick (`0d4f9fe`..`ee99a60`), then its three checkpoint commits
marked UNVERIFIED (`899c0d6` warnings, `ae0bd46` the key and history
case names, `95fb5fb` the real-editor corpus and fuzz harnesses), each
verified after the pick. At `456e19b`, in the container: every state
file native and green (key 11, history 12, schema 8, options 2,
restore 18, commands 16, recover 15, save 27, the byte and corpus
files); on the checked machine every whole file `exit(0)` or, past the
20M-step budget, every case alone: **141 cases `exit(0)` and one budget
refusal** (`18-maximal-512-tabs.fl` alone, native covers it;
`notes/yw06-evidence/continuation/state-suite.log`). The save's two
fault-shim rows (the atomic order write, fsync-file, rename, fsync-dir;
`kill -9` at each of the 24 fault points) need C's pinned shim, so they
SKIP loudly in the port job and run in the oracle job's container.

**G20, reduced.** The release tier at 0.2.34 refused
`@ws.state_records_finish.cls0` (exit 4, phase `wir`): a dedup twin of
a capture-free closure handed to `util.sort_stable` across a module
boundary. Four variants (`notes/yw06-evidence/g20-closure/`): `twin`
reproduces exit 4 on 0.2.34 and builds on 0.2.35, so it is
wolf-lang#806 (closed in 0.2.35) and needs no new issue. The route
around until the bump is a local bottom-up merge sort
(`ws.state_records_sort`, held to `util.sort_stable` over 400 seeded
rounds by `t_records_sort_matches_sort_stable`) and a local insertion
sort in `edit_state_fuzz`; yw07's bump retires both.

**fuzz_state** (s25 §9): `tools/fuzz-state` ports `fuzz_state.c` over
`tools/fuzzgen` (fuzzlib's generator bit for bit, `mutate_dict` and its
dictionary copied verbatim to `tests/fuzz/dict/fuzz_state.txt`). The
port's report line equals C's driver's. The campaign, 100,000 cases at
each of four seeds, port then C, on kasumi: <<FUZZFULL>>. CI runs 2,000
cases at each seed against C's driver (`tools/run-fuzz-state --native
--campaign --against-oracle`).

**perf_state** (in-process, beside C's `perf_state`, one file read
each, both documents 361,860 bytes): emit **0.59×**, parse **0.96×**,
restore **1.13×** C. CI holds both harnesses to compiling
(`tools/run-perf-state --build-only --native`).

**workspace50** (`tools/run-perf-editor --workspace`, 50 copies of
`c_kitchen.c`): `startup.first_paint.workspace50` **1.68×** (C 29.9 ms,
port 50.2 ms; drift 1.51, the rig shared) — C highlights its first
`.c` buffer and the port cannot until yw10, so the port's paint does
less work than C's; `mem.workspace50` port 20.25 MB against C's
10.83 MB (**1.87×**), both inside the 40 MB budget. The editor's RSS
checkpoints are `util.rss` (`rss.c:1-113`, `YEW_PROF=1`, from
`/proc/self/smaps_rollup` and `status`): `argv`, `config` and `paint`,
as C's.

### 4.3 The startup plan (deliverable 3, s56.5 §1 and §6)

`edit.driver`'s `start_plan_resolve` (`ed.c:2815-2917`): `yew` (cwd,
restore), `yew FILE...` (restore, then each file opened or focused, the
last active), `--workspace DIR FILE...`, a directory beside another
target refused before raw mode, never the first file's parent; restore
BEFORE the files (`ed.c:3012-3015`), the bootstrap tab closed after. A
directory launch resolves and restores its workspace and its
`enter_fuss` refuses by name, naming yw13, leaving L mode. `test_startup`
3 of 3, native and checked; `startup_explicit_workspace`,
`s25_resume_exact` and `s25_resume_survives_resize` green on the native
editor. `startup_directory_workspace` is yw13's (the drawer and Git
discovery), recorded red by name.

### 4.4 The finder and the one picker (deliverable 4, s26) — the pick fork

`ws.walk`: an explicit stack (G41), each directory read whole and
sorted before descent as C's is (`walk.c:285-311`, so G39 does not
bite), the `(dev, ino)` guard from `fs_lstat`, `.git` skipped first,
`max_depth`, `max_entries` and its one message, budgeted slices; a name
that is not UTF-8 skipped with a warning naming G40 (R-yw06-6).
`ws.gitignore`: s26 §4's table, every pinned divergence, nested sets,
and the disk loading as pinned C measures it (R-yw06-10: `.git/info/
exclude` unread, `.git/info/.gitignore` read, a nested disk pattern's
anchor with a NULL base, the in-memory base-scoped compile distinct);
the two fixture trees' listings are byte for byte C's, a CI gate now
(`tools/check-walk-listings` over C's recorded answer,
`tools/walk-listings/c.json`). `edit.filter`: narrowing on append, the
sliced full rescan with ` scanning…`, the cached candidate set, a
bounded top-k, never a sort of the set. `edit.picker`: the filter line
is yw04's `CmdLine`, the selection held by payload across refilters,
the centred box, the under-24-column refusal, `PICK_ROW` regions.
`edit.pickers`: `ed.find.file` (the preview through `fs_read_at`, capped
at 64 KiB, never a `Buffer`), `ed.find.buffer`, `ed.undo.branches`,
`ed.find.command` (the palette, the registry alone). `edit.typejump`.
C's `PickerSpec` function pointers are a host kind matched in one place
(G19/G20); the tests' callbacks are `PICK_HOST_PROBE`.

The C witnesses first (`notes/yw06-evidence/pick/witness/c-witness.log`,
`picker_oracle.c` over the oracle's objects): W1 the file host is
synchronous with a 4,096 cap (200,001 files: "showing the first 200000
files; narrow the workspace"); W2 `finder.c` measures the filter, not
the walk (its "walk slice" is the sliced rescan's; the narrowing total
informational); W3 every editing key in the picker is consumed and the
filter line does not change, so `test_picker`'s two Backspaces leave
`abba`, as in C; W4 nothing in production calls `yew_typejump_key` at
the pin (R-yw06-12); W5 zero allocations over 100 draws with preview
and 100 down-keys.

**Units:** 91 C cases + `groupfromdir`'s 7, all native-green and green
under `tools/check-test`'s checked lane; one case at a time on the
checked machine every case `exit(0)` but four alone past the budget
(`test_narrow` 0, 4, 5 — C's 5,000×10,000, 20,000- and 50,000-item
cases; `test_picker` 9, the 8 MiB custom source, R-yw06-14), each
refused in 3–5 s. Two checked-lane reds were met and fixed on the way:
`test_walk` case 4 ("never loops": a 1 µs step took no entry,
R-yw06-13, `e932a6c`) and `test_picker` case 9 running 16+ minutes at
2–4 GB (G46: the checked machine copies a held `str` on every inline
`.bytes()[i]`; `2726e35`, `ff8ff71`, `5aeb34f`).

**PTY:** `s26_finder_chrome`, `s26_finder_chrome_wide`,
`s26_finder_cjk_highlight`, `s26_buffer_switcher`, `s26_undo_branches`,
`startup_multiple_files` and the four `chrome_picker*` green on release
and native; the harness proved on C's own binary first; the gate seen
red with the count separator planted as `|` (`s26_finder_chrome`,
`chrome_picker` red, then green after the revert).

**fuzz_gitignore:** `tools/run-fuzz-gitignore --campaign
--against-oracle`, 200,000 inputs at seed 1: both print
`hash=d67ee79f885b048f ok`; the answer fold over every match the
campaign asks is `ade5cd1e3574db76` on both sides. Wall time 92.6 s
against C's 41.3 s (2.24×; not a gate).

**perf_finder** (release, `taskset -c 8-11`, C / port / C, worst of 11,
two runs):

| gate (budget) | port | C | port / C |
|---|---|---|---|
| open → first paint (16 ms) | 0.545 / 0.572 | 0.420 / 0.425 | **1.30 / 1.35** |
| first key (5 ms) | 2.009 / 2.010 | 2.010 / 2.010 | 1.00 |
| narrowing frame (5 ms) | 2.014 / 2.015 | 2.013 / 2.012 | 1.00 |
| worst slice (3 ms) | 2.014 / 2.015 | 2.009 / 2.011 | 1.00 |
| narrowing total (informational) | 8.885 / 9.055 | 8.312 / 8.318 | 1.07 / 1.09 |

Both sides match 53,919 candidates. Open was 2.08–2.45× before two
changes: a fresh filter's slots pushed with their values (`66fcb40`),
and a full top-k window rejecting a row that cannot land in one
comparison (`7b44ac4`, C's insertion order's answer; the top-k pass
0.83 → 0.07 ms). Most of what remains is filling a fresh filter by
`push` (no `List.reserve` at 0.2.34; s255's, 0.2.35's): with the
storage held, as the picker holds it after its first open, open is
0.15–0.16 ms against C's 0.42.

### 4.5 The router, the context menus and drag (deliverable 5)

Two forks: **mouse** (`yw06-mouse`, the router and everything in
`mouse.c` but the context-menu command) and **ctx** (`yw06-ctx`, the
menu widget, its rows and `ed.ui.context_menu`, `mouse.c:2905-3036`),
split by C function and agreed before either started; ctx's glue was
written under mouse's names first and folded into the router at
`6dbdaa3`, so no function exists twice.

**The router** (R-yw06-2 = A): one `edit.mouse` at the pin's state,
committed in the narrative's order — s27's router, s57.13's menu
gesture and rows, s57.14/15's drag picture and the strip's scroll,
s57.22's drag-to-spawn — with yw05's router half moved out of
`edit.input`. The drawing it needs is filled: `tabs.c`'s float, gap,
dwell flash and the row-2 member gap (`2ee78b8`), the strip's explicit
scroll, `draw.c`'s spawn zone (`6d9325a`); `ed.mouse.enable` and
`.disable` at IMPL 950–951 (`0a7af7d`). No named refusal is left in
`input.lu`, `draw.lu` or `tabs.lu`. The picker's arms (press selects, a
release on the row accepts, the wheel scrolls `PICK_ROW`, `BLOCK` maps
to `CTX_KIND_PICKER`, `CTX_TGT_PICK` and Close; `f65f812`, `4352ef0`,
`b6cc165`) landed at the pick merge.

**The menus** (`ctxmenu.c`, `ctxrows.c`): `Ed.ctx` — the bordered box,
clamp never flip, greyed never hidden, priority shedding, Home/End,
hover by geometry, drawn last with its `BLOCK`/`CTX_ROW` regions; the
kinds, targets and the action table as data (one `match` on literal
ids, G19/G20), one builder per kind; `ed.ui.context_menu` at IMPL 980.
The three FUSS builders refuse by name, naming yw13 (R-yw06-4 = A).

**Units** (native whole; the checked machine one case at a time, G29):

| C file | cases | native | checked per case | by name |
|---|---|---|---|---|
| `test_mouse` | 61 | 60 + 1 RED | 61 `exit(0)` | RED `mouse_menu_path_target_carries_the_captured_path` (a FUSS file menu, yw13); the panel half of `mouse_context_at_names_every_region_kind` SKIPs (yw11) |
| `test_mouse_click` | 10 | 10 | 9 + 1 budget | case 4 `mouse_double_click_equals_the_word_engine` alone past the budget |
| `test_drag` | 40 | 40 | 37 + 3 budget | cases 36–38 (the row-2 gap ordinal and the two every-step sweeps) |
| `test_invariant9` | 13 | 13 | 13 | — |
| `test_degrade` | 10 + 1 port | 11 | 11 | — |
| `test_ctxmenu` | 24 | 24 | 23 + 1 SKIP | `ctxmenu_a_row_handler_reading_a_payload_is_a_bug` needs the child role (G23); native passes it |
| `test_ctxrows` | 17 + 1 port | 13 + 5 RED | 18 `exit(0)` | the five `ctxrows_fuss_*` RED by name (yw13); two asserts of `ctxrows_doc_optional_sections_are_absent_not_greyed` (no `yew_lsp_attached` before yw11, no `yew_git_repo_cached` before yw13) and the walk's three FUSS kinds (R-yw06-C1) SKIP by name |

The port case `port_s27_s7_glyph_review` holds s27 §7's vocabulary
table row by row in both vocabularies with measured widths (`⇕` one
cell, `[✓]` three); s27 §8's degradation audit is `test_degrade` and
`test_invariant9`.

**PTY:** the router's 68 (its 70 less the two FUSS menus) — the 48
`chrome_*` in four profiles each and the 20 `s27_*`, `s57_13_*`,
`s57_14_15_*`, `s57_15_*` and `s57_22_*` — went from 38 green at the
base (`456e19b`) to 64 at `c0c2723` (the four `chrome_picker*` waiting
on the picker) to **68 of 68** on release and native after the merges;
no golden edited, no STOP.

**fuzz_mouse:** `tools/run-fuzz-mouse --campaign --against-oracle`,
`make fuzz-mouse`'s size (4 sessions of 25,000 events at each of four
seeds, 400,000 events), every report line equal to C's from the same
run on native and on release (hashes `abd0bf2a2b6d3fef`,
`190eb21b38fff4ad`, `084d3f95913a3a46`, `b182e1c71e691840`); the corpus
copied verbatim (git blob `49646e15`).

**perf_mouse** (release, `taskset -c 8-11`, C / port / C):

| gate | port | C (first / again) | port / C | budget |
|---|---|---|---|---|
| motion burst, median | 0.231 ms | 0.035 / 0.034 ms | **6.68** — over 2× | 5 ms |
| burst renders | 0 | 0 | | 0 |
| router allocation | 0 ledger bytes | none (C's source scan) | | 0 |
| menu hover | 19 renders, 0.607 ms | 19 renders, 0.312 / 0.292 ms | **2.01** — over 2× | 20 renders |
| chevron hover | 6 renders, 0.219 ms | 6 renders, 0.097 / 0.116 ms | **2.06** — over 2× | 10 renders |

(18:35Z, after this lane's runs on 8–11 had finished and with the pick
fork's timing held; one niced `fuzz_state` campaign process shared a
core throughout; `notes/yw06-evidence/mouse/perf/attribute-release-684b4ab.log`.
The 17:15Z run read 6.00, 1.89 and 2.35.) The render counts and the
router's zero bytes are C's; the router-bytes gate was seen red first
(48,000 bytes: the harness's `term.key_new` per report, fixed at
`6883ff5`, `perf/native-key-new-per-report-9c29b85.log`).

**Over 2× and named.** Where the burst's time goes, by stage
(`tools/perf-mouse --attribute`): the harness loop, `mouse_event`'s
entry, the descent to `mouse_motion`'s phase test and the armed early
return cost ~2 ns a report together; **`drag_strip_motion`'s body
costs ~229 ns**, of which the strip accessors are ~15 ns (18 calls at
~0.8 ns). The rest is a copy of the editor: in the release binary
`drag_strip_motion` (35,368 bytes of code) has a 20,824-byte frame and
runs ~4,100 moves (`mov`, `movups`, `movaps`) copying ~6.4 KB of `Ed`
into it before it calls `drag_target_slot` and `drag_dwell_slot`, which
take `ed` read-only while it holds `ed` `mut`. A `read` lend of a
`mut`-held struct snapshots the struct: **G45** (§5; witness
`notes/yw06-evidence/mouse/witness/read-lend-copy/`: a 400-field struct
lent read-only gives its caller a 6,416-byte frame on native, 32 bytes
lent `mut`; release removes the copy only where the caller is small
enough to inline). The helpers cannot take `mut ed` (W1002: they never
write it). Without the snapshot the burst would be ~15–20 ns a report
against C's 35. The two hover rows render through `ed_render` (a
22,008-byte frame) and `strip_draw_rows` (13.5 KB); their attribution is
by that frame census, not timed by stage. All three are yw15 ratchet
rows, behind G45.


### 4.6 The field repairs (deliverable 6, s57.11, s57.12)

`:!yew FILE` (`shell.c:301-647`): the conservative recognizer
(`self_word`, the unquoted-special set, `#`, a leading `~` or `=`), the
path from `ws_root`, its group by `group_for_path`, no job and no
`*job:*` buffer, a ranged `:!` never navigating, tried first by
`edit.shell_cmds` when no range is given (`shell_cmds.c:163`). `test_shell_self` 4 of 4 native;
on the checked machine cases 0–2 `exit(0)` and case 3 past the budget
alone. The recognizer's special-character test first walked the set's
bytes; `tools/check-test-cases`' first run caught case 0 newly past the
budget, and it is comparisons again (`2f5d907`). `s57_11_shell_self_open`
and s57.12's three (`s57_12_shift_arrow_highlight`,
`s57_12_clipboard_cut_paste`, `s57_12_job_output_quit_returns`) green;
s57.12 needed no code (yw03's and yw04's commands, on yw05's bump).

### 4.7 The static binary (deliverable 7)

<<STATIC>>

### 4.8 The gates (deliverable 8, M-YW5)

<<GATES>>

### 4.9 The `unsafe` census

**No change**: 18 `unsafe {` blocks under `src/` at trunk (`83020234`)
and 18 at the head; no line of the lane's diff under `src/` adds or
removes `unsafe`. C's statics became fields of the `Ed`, of the walk
and filter values, or of the router's state (the picker's top-k
window, the preview's buffer, the drag's rects), never module state.

## 5. Rulings asked, issues, and what to correct

**Rulings.** R-yw06-1 to R-yw06-10 were taken at launch and on the C
witnesses (A in each) and are implemented as recorded. Four are asked,
each with its recommendation implemented (`docs/MAP.md` §6):

- **R-yw06-11** (the ctx fork's C1) — the FUSS kinds in
  `ctxrows_every_row_resolves_to_a_registry_command`: (A) SKIPped by
  name, the other 54 rows checked and the FUSS actions held by the table
  case (implemented, recommended); (B) C's rows over "unknown" FUSS
  answers; (C) a sixth FUSS red.
- **R-yw06-12** (pick's P1) — type-to-jump's deadline: (A) C's
  timestamp compared on the next key (implemented, recommended; W4);
  (B) a timer-heap entry, as the contract worded it.
- **R-yw06-13** (pick's P2) — the walk's first yield: (A) one entry
  before a step may yield (implemented, recommended; under (B)
  `test_walk` case 4 never progressed on the checked machine); (B) C's
  check before the first entry, exactly (`walk.c:438-443`).
- **R-yw06-14** (pick's P3) — `test_picker` case 9's 8 MiB text: (A) a
  byte at a time, so the checked budget ends the case in ~5 s
  (implemented, recommended); (B) the builtin `repeat`, 16+ minutes at
  2–4 GB under G46.

**Issues to file** (the orchestrator's, track rule 4; both listed in
`docs/MAP.md` §5):
- wolf-lang: **G45**, a `read` lend of a `mut`-held struct snapshots
  the struct (codegen), witness
  `notes/yw06-evidence/mouse/witness/read-lend-copy/` and the release
  disassembly under `notes/yw06-evidence/mouse/perf/`.
- wolf-lang: **G46**, the checked machine copies a held `str` on every
  inline `.bytes()[i]`, witnesses
  `notes/yw06-evidence/pick/witness/checked-bytes/` and
  `checked-repeat/`.
- No new issue for G20: the reduced twin is wolf-lang#806, closed in
  0.2.35 (`notes/yw06-evidence/g20-closure/run.txt`).

**Issues to close at the merge:** yew#11 (the oracle tools' scratch
homes, `f41313e`, `1c57369`, seen red in PR #47) and yew#44 (the perf
harness compile gate, `7050319`, seen red in PR #47 and again in
PR #48). **Unchanged:** yew#45 (the job-stream stall; not exercised
here). **yw07's bump owes** yew#17, #20, #22, #23, #24, #27 and #40, and
retires `ws.state_records_sort` and `edit_state_fuzz`'s `sort_names`
(G20's route-around).

**Findings about pinned C** (recorded, never fixed in the port, no
golden touched): C's `fuzz_state` loads its 32 seeds in `readdir`
order (`seeds_load_dir`, `fuzz_state.c:85-128`), so which 32 of the 45
corpus documents seed a run is the filesystem's choice — the port takes
them name-sorted and no report line sees the difference; C ignores
`.git/info/exclude` and reads `.git/info/.gitignore`, and a nested disk
pattern's anchor has a NULL base (R-yw06-10); the pinned reader's
`INT64_MIN` and a reserved bare key that does not fix-point (§4.2). The
port's terminal guard sibling (ruling #93 R1 B) restores the terminal
after a `SIGKILL`, which C cannot; `trial_restore_sigkill` allows the
primary screen for that reason.

**Corrections.**
- `docs/MAP.md` §2 gives `stdai.c` to yw09; it is Sprint 48's
  `ai.backend` (`stdai.c:1`, campaign 10). yw07's draft flags it,
  undecided.
- `docs/MAP.md` §2's `ws` and `ui` rows, §3's campaign-05 row, §5's G39
  and G40 rows and §7's yw06 paragraph are corrected here (R-yw06-1, -2,
  -4, -5, -6).
- Two pushed commit messages of the mouse fork cite lines slightly off,
  not rewritten: `3deb7b9` cites `test_mouse_click.c:1-412` (the file has
  480 lines); `f65f812` cites `mouse.c:1424-1426` for the press arm
  (1428-1430).
- The router's release `PICK_ROW` arm calls `region_hit` once where C
  calls it twice; only the registry's empty-query diagnostic counter
  differs.
- Three checkpoint commits taken from the Astra state worker keep
  "UNVERIFIED" in their subjects (`899c0d6`, `ae0bd46`, `95fb5fb`); each
  was verified after the pick (§4.2), the history not rewritten.
- `edit_shell_self_test`'s case 0 went past the checked budget alone at
  the router's merge (`9046919`; `exit(0)` at `2f5d907`) and is an
  `allow` row; native covers it.

**Paths to prune** (the orchestrator's): the remote branches
`yw06-{codec,state,perf-state,finder,plant-harnesses,plant-gates,wip,
pick,mouse,ctx,yw07}` once `yw06` merges; on kasumi `~/lanes/yw06/`
(`yew`, `state`, `codec`, `perf-state`, `tail`, `main`, `g20`,
`fuzzrun`, `fork-pick`, `fork-mouse`, `fork-ctx`, `static-*`,
`wolf-0.2.35`, `input`, every `scratch-*` and the `*.bundle`/`*.tgz`
transfers; each `target/oracle` is ~0.5 GB); on the Mac
`~/lanes/yw06/` (`yew`, `state`, `codec`, `finder`, `perf-state`,
`plant`, `fork-pick`, `fork-mouse`, `fork-ctx`, `fork-yw07`).
