# yw10 — highlighting: the syntax engine, definitions as Fletch data, the language pack and themes

**Model per ruling #89 R4, chosen at launch. Drafted by yw09 from
`docs/MAP.md` §7's yw10 paragraph, sagitta campaign 08's six sprint files
and yw09's hand-off.** Ruling #89 (`sprints/yew/index.md`); the track's
seven standing rules (rule 2: no golden edited; rule 4: the 2× gate);
`docs/MAP.md` as yw09 leaves it (§1's campaign-08 rows, §5's gaps, §6's
R-yw09-1..6); `sprints/RULES.md`. It ports campaign 08, "highlighting",
whole:

- s39 (`s39-syntax-engine.md`, 646 lines at `sagitta.pin`): the
  per-line state machine every definition drives, the semantic
  attribute vocabulary themes map onto, the per-buffer line-state array
  and its splice against the edit stream, the settle budget;
- s40 (`s40-syntax-def-format.md`, 675): definitions as pure-literal
  Fletch data (language block, contexts, match rules with attribute and
  push/pop/set/stay), validated and packed into tables;
- s41 (`s41-langpack-1-themes.md`, 614): the first five definitions
  (`c`, `fletch`, `sh`, `make`, `markdown`) and the whole theme layer,
  256-colour degradation included;
- s41.5 (`s41_5-embedded-languages.md`, 676): a line's entry state names
  which definition runs; markdown fences and the other embeddings
  dispatch across definitions;
- s42 (`s42-langpack-2.md`, 646): python, rust, go, js/ts, fortran, json,
  yaml, toml, and the daily-driver milestone;
- s42.5 (`s42_5-native-language-pack.md`, 566): `wolf` and the 48
  built-in modes, the core detector, the native pack compiled through
  yew's own Fletch-data compiler.

None has a "Corrections after landing" list; the DoD walks live in
sagitta's `.docs/audits/closeout-F10-syntax.md` and `audit-10-syntax.md`.
Read those before claiming a DoD row.

The C (line counts at the pin; re-derive): `src/syn/engine.c|h`
(5,488/352), `defs.c|h` (3,742/106), `theme.c|h` (1,087/101),
`langs_gen.c|h` (1,255/12), `synblock.c` (398), `fortran.c|h` (189/30),
`registry.c|h` (168/67), `attr.h` (69); `src/syncli.c` (1,591, the
`yew syn` CLI); the syntax badge and the Fortran-language slot of
`statusline.c` (yw03 left both present and empty); `runtime/syntax/` (48
definitions, copied verbatim, never edited) beside the two themes yw03
already copied; `scripts/check-syn-assets.sh` (416).

The tests (counts are `^void test_` rows; re-derive from
`tests/unit/registry.c`): `test_syn_all` 6, `_attr` 1, `_block` 11,
`_cache` 20, `_defs` 20, `_depth` 2, `_detect` 12, `_diff` 2,
`_discovery` 7, `_embed_pump` 5, `_embed_runtime` 10, `_embed` 8,
`_firstbyte` 4, `_fletch` 1, `_fortran` 2, `_jsvalue` 3, `_line` 16,
`_registry` 5, `_settle` 7, `_splice` 4, `_state` 9, `_state2` 4, `_wolf`
6; `test_theme_256` 1, `_degrade` 1, `_runtime` 5, `test_theme` 4 — 176
cases in 27 files (`syn_toy.c|h` is their fixture). PTY: 97 cases (s39 2,
s41 42, s41.5 4, s42 19, s42.5 30). Goldens: the 432 `tests/syn/**/*.spans`
through `scripts/check-syn-assets.sh` (`make test-syn-assets`,
`Makefile:2452`). Fuzz: `fuzz_syn` (544, `Makefile:2404-2422`, the line
and edit long lanes) and `fuzz_syn_def` (253, `:2424`). Perf: `perf_syn`
(4,562, `:3001`, its gates, the scroll and budget variants).

Owed to this lane by earlier ones (each named where it was deferred):
yw09's `test_macrobrowse` `edit_is_an_ordinary_multicursor_undo_buffer`
three syntax lines (`test_macrobrowse.c:236-239`, `src/edit_macrobrowse_test.lu`'s
header; C attaches `fletch` highlighting to a macro scratch,
`macrobrowse.c:109-120`, which the port names in `ed.buf_languages` and
attaches nothing); `test_fl_cmds`' `ed.buffer.syn.entry.len` lines
(`test_fl_cmds.c:177-184`, `src/fl_cmds_test.lu`'s header); s57.6's syntax
half and s57.9's two goldens (`wolf.fl`'s colours, R-yw06-4); the
statusline's syntax badge and Fortran slot (yw03's interim, `statusline.lu`
slots 11 and 13); `s41_theme_switch_one_repaint` (the `paint` filter
note in `tools/goldens`).

## Deliverables

1. **The toolchain, first.** `gh release list -R wolffe-lang/wolf-lang`
   and `-R wolffe-lang/wolf-interp` read and quoted with their time. A
   release newer than the pin yw09 leaves is this lane's first commit
   with its prediction, and the retirements it names are adopted, each
   in its own commit (G47, G48 for R-yw09-2's tables, G50–G58 wherever
   the release answers them).
2. **The engine** (s39): the line-state machine, the attribute set, the
   line-state array and its splice, the settle budget on the idle path,
   the per-buffer `syn` state the earlier lanes' deferred lines read.
   Unit: `test_syn_line`, `_state`, `_state2`, `_splice`, `_settle`,
   `_cache`, `_depth`, `_firstbyte`, `_diff`, `_attr`, `_block`.
3. **Definitions as data** (s40): the schema read through the Fletch data
   reader yw09 left on the production path (`edit.state_fletch`'s
   reader, not a second literal codec), validation with C's messages,
   the packed tables, `yew syn` (`syncli.c`). Unit: `test_syn_defs`,
   `_registry`, `_discovery`, `_detect`. Fuzz: `fuzz_syn_def` against
   C's driver, its report line byte for byte.
4. **Langpack 1 and themes** (s41): the five definitions, the theme layer
   and its degradation. Unit: `test_theme*`, `test_syn_fletch`; PTY: s41's
   42 by name.
5. **Embedded languages** (s41.5). Unit: `test_syn_embed*`; PTY: 4.
6. **Langpack 2 and the native pack** (s42, s42.5): every shipped
   definition through the detector and the compiler. Unit:
   `test_syn_all`, `_fortran`, `_jsvalue`, `_wolf`; PTY: 19 and 30;
   goldens: all 432 `.spans` (M-YW8).
7. **The deferred lines** above, each restored to its C form and run.
8. **Fuzz and perf.** `fuzz_syn` (and its long lanes as an advisory)
   against C's driver; `perf_syn` beside C's from one run on kasumi under
   `taskset` in a container, every row over 2× named with its issue
   (R-yw10-3).
9. **The note and the map.** `notes/yw10-…md` with the five sections;
   `docs/MAP.md` §2's campaign-08 rows, §5's new gaps, §6's rulings, §7's
   yw10 and yw11 paragraphs, and yw11's contract drafted in full.

## Rulings (to ask at launch unless decided)

- **R-yw10-1 — the packed tables' representation.** (A) wolf structs
  built once from the validated definition and held by the registry,
  matched by kind where a callback would be (R-yw07-10; recommended: one
  representation, no generated source); (B) C's generated
  `langs_gen.c` tables re-generated as wolf source by a tool, checked
  against the pin like `tools/check-runtime`.
- **R-yw10-2 — where a definition is read.** (A) through the Fletch data
  reader on yw09's production path (recommended: one reader); (B) a
  dedicated literal reader beside it, which R-yw06-1's retirement argues
  against.
- **R-yw10-3 — `perf_syn`'s gate.** (A) yw08's harness and gate extended
  to `perf_syn`'s rows, timing advisory on hosted CI and the record on
  kasumi (recommended: one gate, C's policy, as R-yw09-3 A); (B) a
  separate harness.
- **Decided:** R-yw07-1..10, R-yw07b-1..9, R-yw08-1..8 and R-yw09-1..6 as
  the map carries them, subject to the maintainer's batch.

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. `Footprint:
cross-cutting` (CI's by-name steps). Read sagitta's campaign-08 sources,
sprint files, closeout audits, tests and baselines freely and cite
`file:line`. Never another editor's, highlighter's or grammar engine's
source. No golden, unit case, conformance file, `.spans` file, syntax
definition, theme, baseline or ledger edited; a disagreeing one is a STOP
with its diff. Every run of C yew and the port uses scratch `HOME`/`XDG_*`
and an explicit `YEW_RUNTIME_DIR`, inside a container under `taskset` and
the lane's core lock. The PTY goldens drive the real terminal through
`tools/goldens`; signal witnesses are pty bytes, never trap scripts. One
kind-id/match representation for every mutable callback (R-yw07-10).

## Inputs (re-derive)

sagitta at the pin: the six sprint files with their line counts, the
closeout audit and `audit-10-syntax.md`, the C and the tests above,
`Makefile:2404-2452` (fuzz and the asset check) and `:3001` (perf). The
yew repo at yw09's merge: `src/edit/statusline.lu` (the empty slots),
`src/edit/state_fletch.lu` (the data reader), `src/edit/macrobrowse.lu`
and `src/edit_macrobrowse_test.lu` (the deferred syntax lines),
`src/fl_cmds_test.lu`, `tools/goldens` (the `syn` suite),
`tools/fl-headless/compare.py`, `notes/yw09-fletch-in-the-editor.md`,
`docs/MAP.md`.

## Prediction (write before the first change)

To be written by the lane at launch: the 176 unit cases, the 97 PTY
cases and the 432 `.spans` goldens green by name; `fuzz_syn` and
`fuzz_syn_def` equal to C's report lines; each `perf_syn` row's ratio
predicted against the 2× bar; M-YW8's artifacts green in CI.

## Done-when

Every deliverable with its tests. `tools/check-test` and `--native`
green, with the per-case checked run recorded. The PTY cases green by
name; the 432 goldens, the two fuzzers and the deferred lines in CI by
name. The perf rows recorded beside C's from one run, every MISS named
with its issue. M-YW8 met. `docs/MAP.md` updated; yw11's contract
drafted; CI green; the PR open with the five sections, shas as bullets, a
test checklist and its `Footprint:` line; `bash
wolf/tools/lane-audit.sh yew yw10 <PR>` passing but for the final run's
green; hand back per RULES.md §6.
