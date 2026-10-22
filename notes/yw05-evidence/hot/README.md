# yw05-hot: allocation-free hot paths (deliverable 6)

The contract's deliverable 6 (R-yw05-3 = R-yw03-7 A): the per-frame
temporaries that wolf 0.2.34 keeps to the session's end (G33: a function
allocates in its caller's region and the loop's is the session's; a
per-turn region is E1010 while the turn mutates the editor, wolf-lang#839,
s255 = 0.2.35) written into storage the editor owns instead, byte-identical
output. Everything here ran on kasumi in the lane's container
(`~/lanes/yw05/bin/ctr`, archlinux:base-devel, `taskset -c 12-15`,
`ulimit -c 0`, 8 GB, no network).

## Heads

| what | head | binaries (sha256 prefix) |
|---|---|---|
| the baseline ("before") | `7249ff8` (the lane's `yw05` when the fork started: the pin, wait, sync, panes) | release `257520c64b63`, native `c15fe223e569` (`target/hot/base/`) |
| the fork's own head | `dbf6129` (its sources; `d4c3896` revises the test file only) | release `4dcc38461ba3`, native `103dd9ac13b1`, demo `ede413498b02` (`target/hot/final/`, `gate/build-f1b.log`) |
| the branch head ("after": the gate's, the final matrix's, the plant's second run) | `0d8fc52` = `d4c3896` + `origin/yw05` at `1cd63b9` (the jobs, tabs and groups forks merged into the lane) | release `dba78dd07b22`, native `7cfeaa31ecca` (`target/hot/final2/`, `gate/build-f1c.log`: its `sha256sum` lists native first) |
| C yew | the oracle's `target/oracle/sagitta/build/yew` at `9ace98c2` | `51247fc5590d` |

The kasumi tree's sources matched the commit for each run of record
(`rsync -rcn` against the Mac worktree, empty; the clone reset to the pushed
head before each gate and matrix; the build logs print the head and
`git status`'s entry count, 0 at `dbf6129` and 6 untracked evidence files
at `0d8fc52`).

## The instruments

- **`ptymem-hot.py`** (the measurement of record): resident memory of an
  editor across N keys in a PTY, C and the port under the same driver.
  yw03's `ptymem.py` and yw04's `ptymem-prompt.py` (copied here unchanged:
  `ptymem-yw03.py`, `ptymem-prompt-yw04.py`) with the window set to 24x80,
  their phases plus `lines40` (40 down, 40 up: README.md's 71 lines keep
  every move a move) and a two-pane session (`ctrl+w s`, ONE write: the
  first baseline run sent it as two writes 0.5 s apart and the chord raced
  its timeout, so that run's pane rows differ between tiers and are not
  used), and the bytes the editor writes during the measured keys counted
  and hashed (`out_sha`). **`run-ptymem.sh OUT N LABEL=BIN...`** runs every
  phase over every binary in turn, C first, each on a fresh copy of its file
  and an empty yew state; then yw04's driver unchanged over its worst row.
  **`table.py`** renders a run as the tables below.
- **`hotprobe.lu`** (the diagnostic): the loop's turn and each draw
  component in process over the driver's session (README.md, the config,
  24x80 truecolor), the editor built INSIDE a named region so
  `region_bytes` counts every byte the calls allocate, exactly (ledger
  units differ by tier; zero is zero); VmRSS beside it. Phases: `comp`
  (B/call of each component), `keys` (B/key through the turn, with and
  without the render), `after` (each component after a key), `prow` (the
  prompt row's parts), `prim` (single primitives). **`run-probe.sh TAG
  PHASE [ROOT] [SRC]`** builds it against a source root (a git worktree at
  the baseline under `target/hot/basesrc` for "before"; `PROBE=` names the
  source: `runs/hotprobe-base.lu` is the probe with the two calls the head
  added replaced by the baseline's forms, `statusline_build` and
  `cmdline_ghost`, which build the same text).
- **`src/edit_drawbufs_test.lu`**: the same ledger as a unit gate: document
  rows, gutter, statusline, cursor overlay, an idle frame and the prompt
  row (four seeds) each allocate 0 bytes over 30 draws; the in-place
  writers equal what they replace (digits against interpolation, a held
  reader's boundaries and clusters against fresh queries over a document
  with seams and invalid UTF-8, a reused statusline against a fresh
  editor's, the ghost against `cmdline_ghost`). On the checked machine the
  zero-ledger cases SKIP by name (below).

## The PTY table (the measurement of record)

`runs/ptymem-final2.txt`: N=2000 keys a phase, C, the baseline and the
branch head `0d8fc52` from ONE run (2026-10-22T20:28Z, load 4-6; the
unit lanes of the gate ran beside it). R = README.md (3,470 B, two
non-ASCII lines), K = yw03's 10,000-line ASCII fixture. "port bytes same":
the four port binaries wrote byte-identical output during the measured
keys (`out_sha`), before and after: **yes on every row**.

| phase | file | C B/key | base-release B/key | base-native B/key | hot-release B/key | hot-native B/key | head / C (release) | before / head (release, native) | port bytes same |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| prompt-menu | R | 297 | 208,460 | 209,191 | 20,967 | 22,080 | 71x | 9.9x, 9.5x | yes |
| prompt-type | R | 293 | 237,279 | 237,795 | 26,452 | 27,148 | 90x | 9.0x, 8.8x | yes |
| type | R | 53 | 37,202 | 37,528 | 2,054 | 2,417 | 39x | 18.1x, 15.5x | yes |
| type | K | 72 | 17,285 | 17,613 | 901 | 1,294 | 13x | 19.2x, 13.6x | yes |
| arrows | K | 41 | 74,381 | 74,617 | 473 | 1,202 | 12x | 157.2x, 62.1x | yes |
| lines40 | R | 0 | 120,943 | 121,178 | 518 | 1,264 | - | 233.4x, 95.9x | yes |
| pane-lines40 | R | 64 | 123,500 | 123,533 | 936 | 1,100 | 15x | 132.0x, 112.3x | yes |
| pane-arrows | K | 20 | 89,971 | 90,102 | 1,200 | 1,397 | 59x | 75.0x, 64.5x | yes |
| pane-type | R | 33 | 137,413 | 137,761 | 2,779 | 3,172 | 85x | 49.4x, 43.4x | yes |
| pane-prompt-menu | R | 328 | 231,799 | 232,512 | 21,010 | 21,926 | 64x | 11.0x, 10.6x | yes |
| yw04-driver prompt-menu | R | 285 | 208,456 | 208,800 | 20,980 | 22,067 | 74x | 9.9x, 9.5x | (not hashed) |

The fork's own head `dbf6129` measured the same (`runs/ptymem-final.txt`,
2026-10-22T17:34Z: prompt-menu 20,978 / 22,084, prompt-type 26,452 /
27,341, type R 2,023 / 2,454, lines40 518 / 1,196): the lane's tabs and
groups merges changed no row by more than noise. The first baseline run
(`runs/ptymem-base.txt`, 2026-10-22T14:31Z, the same binaries, the
two-write chord) agrees on every single-pane row (prompt-menu 208,437 /
209,019; yw04's driver 208,337 / 208,929 against yw04's own 208,417 /
208,976 at `c76281d`, `notes/yw04-evidence/prompt/ptymem.txt`).

C's resident growth is at the noise floor of its allocator (its rows move
between runs: 262-297 B a prompt key, 0-78 B a line move); C's output
differs from the port's in the prompt rows (C 679 B a menu key against the
port's 626: C's menu lists commands the port has not ported). The output
comparison of record is the port's, before against after.

## The ledger tables (in process, exact)

`runs/probe-base-all.txt` (before) and `runs/probe-final2.txt` (after, at
`0d8fc52`; `runs/probe-final.txt` at `dbf6129` is identical in every row),
both tiers; the ledger is identical on native and release in every row.

| component, one call | before B | after B |
|---|---:|---:|
| a full repaint (`ed_render` under full damage) | 181,328 | 832 |
| the document rows (`draw_document_rows`, all rows) | 177,200 | 0 |
| the gutter | 7,040 | 0 |
| the statusline (`draw_footer`, no prompt) | 2,352 | 0 |
| the prompt row (`draw_footer`, `:` open) | 256 | 0 |
| the tab strip (`tab_strip_draw`) | 921 | 841 |
| the cursor overlay (`draw_cursor`) | 240 | 0 |
| the frame's encoding (`render_frame`) | 176 | 0 |
| an idle frame (`ed_render`, nothing damaged) | 512 | 0 |
| two panes, a full repaint | 199,136 | 832 |
| `text.grapheme_next_boundary` (the fresh-reader form, kept for other callers) | 112 | 112 |

| a key through the turn | before B/key | after B/key | of it, without the render |
|---|---:|---:|---:|
| `:` prompt, `f`/Backspace (prompt-menu) | 206,005 | 19,493 | 18,661 |
| `:` prompt, typing (prompt-type) | 211,966 | 6,424 | 5,590 |
| I mode, typing | 46,189 | 1,796 | 1,252 |
| line moves, 40 down 40 up | 116,603 | 473 | - |
| two panes, line moves | 122,084 | 930 | - |
| two panes, prompt-menu | 229,693 | 19,493 | - |

The "without the render" column is the same at both heads: it is the
key's own work (the parse, the completion filter, the edit), which this
deliverable did not reach (below).

After a key (`runs/probe-base-after.txt`, `runs/probe-final2-after.txt`,
native; the render after it not counted), B/key before → after: I-mode key
render 48,908 → 624 (the 624 is the statusline's `off_to_gcol`, below);
prompt-type render 205,684 → 835; prompt-menu render 187,344 → 832 (the
strip); line move render 121,336 → 0; the frame's encoding after a prompt
key 7,384 → 0.

## Prediction #10 (the lane note's)

"The `:` keystroke's ~210 KB falls by 10x or more, but does not reach C's
0.3-0.5 KB." **In process: HIT** (206,005 → 19,493 B/key, 10.6x; the
document rows' 177 KB to 0). **Under the PTY driver, the measurement of
record: a narrow MISS on "10x or more"** — 208,460 → 20,967 B/key on the
release tier (9.9x) and 209,191 → 22,080 on native (9.5x); the two-pane
prompt row is 11.0x / 10.6x. **"Does not reach C": HIT** — 21 KB against
C's ~0.3 KB. What separates the PTY's 21 KB from the probe's 19.5 KB is the
loop's own turn (the read, below; the wait; the idle turns' completion
slices) and, on native, ~0.4-1.1 KB a key that release does not have
(every row; unexplained here: the in-process ledger is identical on both
tiers, so it is in the PTY path's native code).

## What changed (each cites the C it mirrors)

- `text.coords`: `ClusterReader`, a reader the caller holds (C's reader
  lives on the stack of each query, `coords.c:1522`; its iterator's stack
  is a fixed array, `piece.h:134-142`): `grapheme_next_boundary_with`,
  `text_cluster_next_with`, `off_to_ccol_with`, `ccol_to_off_with`; the
  fresh-reader forms stay for every other caller. `text.piece`: the
  iterator's stack emptied in place on a seek.
- `util.intern`: `intern_bytes`, the lookup by bytes C's `yew_intern`
  makes (`intern.c:21-50`), through a hash index, so a cluster over 8 bytes
  (an emoji ZWJ sequence, an Indic conjunct) costs no `str` per put.
- `term.grid`: `control_expansion` answers what C writes into `out[4]`
  (`grid.c:272-297`) and `put_ascii_expansion` spells it; the fill's
  template check reads the cell's bytes into the grid's `fill` buffer (C
  reads `c.utf8`, `grid.c:520-535`); long clusters interned by bytes.
- `term.render`: `decimal` in place (`render.c:113-124`); the SGR delta's
  three tables a `match` (C's `static const` arrays, `render.c:433-438`);
  the out-of-band queue emptied in place (`render.c:57`).
- `text.clipboard`: an empty reap list is not rebuilt after every frame
  (C's in-place pass, `clipboard.c:534-551`).
- `edit.drawbufs` (new, `Ed.dbuf`): the storage a frame draws into — the
  cluster bytes (`draw.c:879`'s `local[64]`), the held reader, a gutter
  number (`gutter.c:338`), the statusline's text, segments and pool
  (`statusline.c:362-400`), the clipped path, the message row, the menu's
  label and footer (`menu.c:505-506`), the prompt's line and ghost; and
  `push_dec`, digits in place.
- `edit.draw`: document rows through `ed.dbuf`; the cursor overlay's
  signature compared and recorded in place (`draw.c:149-185`); border
  glyphs through the cluster bytes; the drawn tab marks compared and
  recorded in place (`ed.c:2593-2618`, C's byte buffer).
- `edit.gutter`: `gutter_number_into` (C's `yew_gutter_number(dst, cap,
  ...)`); signs read in place.
- `edit.statusline`, `edit.message`: `statusline_build_into` (C's
  caller-owned `StatuslineText *out`); `statusline_build` is its copy for
  the tests; the job badge (the jobs fork's slot 8) written in place.
- `edit.viewport`, `edit.edit_cmds`: `vp_follow_with` through the held
  reader (a motion's and the render's follow).
- `edit.cmdline`, `edit.cmdline_comp`, `edit.menu`: the prompt row's
  clusters, columns, message and ghost (`cmdline_ghost_into`) and the
  menu's labels, details and footer through `ed.dbuf`.
- `edit.cmdparse`: `cmd_bang_body` parsed in a `copy region` (MAP §1's
  form for a per-keystroke rebuild; the ghost asks every frame).
- `edit.tabs` (kept small, as the lane asked — the groups fork was in
  flight there and has since merged cleanly over it): `strip_render`'s two
  chevrons and the new-tab control drawn through `ed.dbuf.foot` instead
  of a list each. Nothing else in `tabs.lu`; nothing in `strip.lu`.

## What remains, named

| per | bytes | what | why it stays |
|---|---:|---|---|
| full-damage frame | 832 | the tab strip's row-1 entries (each label interpolated, then copied twice) and the layout's spans (`tab_row1_entries`, `strip_layout`) | moving them into editor storage reshapes `strip_render`, which the groups fork rewrote while this fork ran: a follow-up over the merged file. No wolf feature is missing. |
| `:` key (menu) | ~15,000 | the completion menu's rows copied out of the filter's `copy region` and assigned (`cl_refilter_as`) | **a wolf gap at this pin**: refilling the menu's existing rows from inside the region is E1010 (`witness/rebuild-copyin/`: `copyin.lu` refused, `replace.lu` holds ~4 KB a rebuild); the in-place form needs s255's outer-write and `List.reset`/`reserve` (wolf 0.2.35) |
| `:` key | 1,232-2,956 | the refilter's parse (`cmd_parse_point`: the matches list, the ambiguous or unknown-command message), growing with the line | port work, not a wolf gap: `copy region` over the pure parse needs `cmd_parse_point` split at its bang path (it takes `mut ed` only there) |
| `:` key | 112-667 | the line copied for the refilter (`cmdline_text`) | the same: a held line buffer threaded through the refilter |
| typed key | 1,252 | the edit itself (the undo record, the journal append) | the edit path, not a draw path |
| typed key | 624 | the grapheme index's replay after an edit (`text.coords`, `off_to_gcol` from the statusline) | the index's builder in place (the `s255-witness` branch's shape) is text-module work beyond this deliverable |
| read | 64 | the terminal read: `fs.read_chunk` answers a fresh list (`term.tty_read`) | **a wolf-std gap**: no read into a caller's buffer at this pin |
| line move | 473 | the key's own dispatch (the motion and its bookkeeping); the render after it allocates 0 | not a draw path; not split further |

## Findings about wolf 0.2.34 (for the guide and the lane)

- **An empty `List[T]()` costs 48 ledger bytes on the native tier** even
  when nothing is pushed (`runs/probe-prim3.txt`, `elist`, at the fork's
  sources): a sentinel `return List[byte]()` on a per-frame path is an
  allocation a frame.
- **`s.bytes()` handed to a call materializes a list** (64 B for a
  one-byte `str`, `blit`/`bheap`/`bparam` in `runs/probe-prim3.txt`):
  a literal, a built `str` and a `str` parameter alike. The guide's "a
  zero-copy view ... passed to a function that only reads it" does not hold
  for these; iterating (`for b in s.bytes()`) and inline indexing do not
  allocate.
- **`fs.read_chunk` answers a fresh list per read** (64 B for one byte,
  `fread`): the terminal's read allocates every turn that reads, and
  wolf-std has no read into a caller's buffer at this pin.
- **A region's ledger is an exact allocation gate on the shipped tiers**:
  build the value inside `region r { }`, read `region_bytes(r)` around the
  work, assert the delta is 0 — no E1010, since nothing leaves the region
  but an `int`.
- **The checked machine's ledger charges a reused buffer's pushes**
  (`runs/checked-ledger.txt`, `runs/checked-ledger-job.sh`, under `wolf
  test`): ten push-and-pop pairs into a list with room charge 10; the
  gutter's 30 draws 1,020, the statusline's 3,330, an idle frame 30, the
  cursor 0, a `grid_fill` 0. It models each element's allocation, not the
  allocator's: "nothing allocated" is not a question it answers, so the
  test file's zero-ledger cases SKIP by name there (`ledger_charges_reuse`
  decides; the draw still runs for its UB rows) and the native lane gates
  the property. The first per-case checked run at `dbf6129` saw three of
  them fail for this (`gate/percase-dbf6129.log`); `d4c3896` is that
  revision, and its per-case run is 8 checked-pass, 3 unsupported (the step
  budget), 0 fail (`gate/percase-d4c3896.log`).

## The gates at the branch head `0d8fc52` (`gate/`, run f2c, 2026-10-22T20:13Z)

| gate | release | native |
|---|---|---|
| campaign 03 by name (`c03-cases.txt`) | 62/62 | 62/62 |
| campaign 04 by name (`c04-cases.txt`) | 104/104 | 104/104 |
| s22's 11 (`c05-s22-cases.txt`) | 11/11 | 11/11 |
| the tabs fork's 8 (`c05-tabs-cases.txt`) | 7/8: `startup_multiple_files`, the tabs fork's STOP (`notes/yw05-evidence/tabs/README.md`) | 7/8, the same |
| s24's 4 (`c05-s24-cases.txt`) | 4/4 | 4/4 |
| `tools/check-test --native` | exit 0, **101 files `[native] ok`**, 68 SKIP lines (the lane's 100 files after the groups merge and `edit_drawbufs_test`; every SKIP a named one, `gate/check-native-final2.log`) | |
| `tools/check-test` (the checked machine) | exit 0, **`wolf test: 101 passed; 0 failed; 0 rejected; 0 unsupported`** (`gate/check-checked-final2.log`) | |
| `percase.py` over `src/edit_drawbufs_test.lu` (G29: the file falls back to `[native]` whole) | 11 cases: **8 checked-pass, 0 fail, 3 unsupported** (the step budget: the document rows' 30 draws, the prompt row's four seeds, the ghost; each rests on the native run, which runs them all; `gate/percase-final2.log`) | |

The same gate at the fork's own head `dbf6129` (run f2, `gate/gate-f2.log`,
`gate/sweep-final-*.txt`): 03 62/62, 04 104/104, s22 11/11, tabs 7/8 on
both tiers; `check-test --native` exit 0, 97 files `[native] ok`, 60 SKIP
lines (the tabs fork's 96 files and `edit_drawbufs_test`); the checked
machine `wolf test: 97 passed; 0 failed; 0 rejected; 0 unsupported`
(`gate/check-checked-dbf6129.log`). At `d4c3896`
(`gate/d4c3896-native-percase-plant.log`): native exit 0, 97 ok, 60 SKIP;
the revised file `wolf test: 1 passed`; per case 8 pass, 3 unsupported.

## The plant (P1/P2: the measurement sees a regression)

`plant/job-p1.sh`, `plant/p1.log` (at `dbf6129`); `plant/job-p2.sh`,
`plant/p2.log` (at `0d8fc52`, the same line): in a worktree
(`target/hot/plantsrc`), ONE line of `draw_span` put back to the shape this
deliverable removed — the cluster bytes replaced by a fresh list for every
cluster instead of emptied in place (`ed.dbuf.cluster = List[byte]()` for
`clear_bytes(mut ed.dbuf.cluster)`, the G33 shape). Seen red, twice:

- `edit_drawbufs_test`: **rc 134**, `draw 0 x30: 1089600 ledger bytes`
  (36,320 B a document draw: 48 B a cluster), the assert at
  `t_document_rows_allocate_nothing` (`plant/edit_drawbufs_test-red.txt`,
  `-red-p2.txt`; also seen at `d4c3896`, the revised file).
- the PTY driver, N=1000, C beside the head and the plant from one run,
  P2: `lines40` C 82, head 1,794, **plant 43,827 B/key**; `prompt-menu`
  C 356, head 22,966, **plant 90,915 B/key** (P1: 1,671 → 41,701 and
  23,003 → 90,817); the head's and the plant's output byte-identical
  (`out_sha`) in both.

The worktree's file was restored after each (`git checkout -- src/edit/
draw.lu`, `git status` clean); nothing of the plant is committed.
