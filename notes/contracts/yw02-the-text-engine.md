# yw02 — The text engine

**Opus 5.5 (#89 R4: Fable for yw00–yw01, then Opus). Crawl 54+. Drafted by
yw01 from `docs/MAP.md` §7 and sagitta campaign 02.** Ruling #89
(`sprints/yew/index.md`); the track's seven standing rules; `docs/MAP.md`
(the idiom §1 as yw01 extended it, the gaps §5, the rulings §6);
`sprints/RULES.md`. Ports sagitta campaign 02 (`s07-piece-tree.md`,
`s08-file-io-and-save.md`, `s09-coords-and-cursor.md`,
`s10-undo-and-marks.md`, `s11-registers-and-clipboard.md`,
`s12-textbuf-fuzz.md` at `sagitta.pin`): `src/text/` (11,688 C lines) and
`src/unicode/coords.c`, `u16.c`. The port inherits the idiom yw01 set
(regions/`List`/`Map`, `str` tables, `(s, at, end)` byte conventions,
`copy` on lent getters, the one `unsafe` module var per `[mem.static.2]`,
no bound `.bytes()` in a hot loop).

## Deliverables

1. **`text.piece`** (s07): the piece tree with a byte count and a line
   count in every subtree node (`piece.c`), balanced on insert and
   delete, `O(log n)` offset→(node, local) and line→offset; the original
   and add buffers as `List[byte]` (never mmap, invariant 1); the line
   index the tree carries, not a side array. `test_piece` ported one for
   one, and the tree invariants (subtree counts equal the sum of their
   children, no empty piece but the root of an empty document) asserted
   after every edit in the port's own checker.
2. **`text.file`** (s08 load): byte-exact load with binary / CRLF / BOM
   detection (`file.c`), no normalization, invalid UTF-8 preserved
   verbatim (the escape policy is the decoder's, storage is bytes);
   `FileMeta` (eol, had_bom, binary, had_invalid_utf8) as `demo_paint`'s
   `s15_metadata_*` scenes read it. `test_file*` ported.
3. **The atomic save and the crash journal** (s08 save, `journal.c`): the
   save decision table (temp in the same directory, `fsync`, `rename`,
   `fsync` the directory; the symlink / hard-link fallback that writes
   through the link's target), and the append-and-sync journal that
   recovers an interrupted save. **Gap G3** (`fsync` of a file and of a
   directory, create-exclusive, rename-without-replace) is not in wolf
   0.2.33's `std.fs`: until it lands (**wolf-lang#796**, s248/0.2.34) the
   save is write-temp + `rename` **without the syncs**, and says so by
   name in the code and the note; a `kill -9` mid-save then loses the
   sync guarantee but never corrupts (the rename is atomic), which the
   torture lane measures. The port files the gap with its witness and
   never claims the sync it does not make.
4. **`unicode.coords` and the cursor** (s09, `coords.c`, `cursor.c`,
   `u16.c`): typed coordinates (`ByteOff`, `LineNo`, `CCol` as
   `distinct int`), byte↔column with wide glyphs and tabs, the cursor
   engine with the mark-bias rules, UTF-16 offsets for the LSP (`u16.c`).
   `test_coords`, `test_cursor`, `test_u16*` ported.
5. **`text.undo` and `text.mark`** (s10, `undo.c`, `mark.c`): the undo
   tree with transactions, grouping, and its serialization; marks with
   their gravity and the transaction that moves them as one. `test_undo*`,
   `test_mark` ported.
6. **`text.register` and the clipboard** (s11, `register.c`,
   `clipboard.c`, `yankstack.c`): the register file, the yank stack, and
   the OSC 52 clipboard with its subprocess fallbacks (`osc52` is yw01's;
   the subprocess backends — `wl-copy`, `xclip`, `pbcopy`, `cmd:` — are
   yw02's, process groups available since 0.2.31). **Gap G5** (`xattr`,
   one use in a later save preset) is yw14's, not needed here.
   `test_register` ported.
7. **The differential fuzz** (s12, `fuzz_textbuf`): a bounded seeded
   driver (wolf has no `fuzz` verb, as `tools/fuzz-unicode`) running the
   piece tree against a naive `List[byte]` oracle over random
   insert/delete/undo/redo, asserting byte-equality and the line index
   after every op; the seed replays. Watch the memory note: four streams
   of this soak took nomad-1 to the OOM killer (`nomad-1-oom-yew-soak`),
   so the driver bounds its document and runs under a region per
   iteration.
8. **The gates**: `tools/check-test` and `--native` green; `tools/goldens
   --yew target/release/yew` with campaign 02's surface — `make torture`'s
   **batch-kill9** and **live-editor kill9** lanes against the wolf binary
   (M-YW2: the save-boundary and SIGKILL campaigns), the save never
   corrupting whatever G3's state; the `test_*` unit files ported one for
   one; the wolf/C ratios for `piece`'s insert/offset and `file`'s
   100 MB load recorded (the `open.100m_*` budgets are yw15's gate, yw02
   records the ratio). The 2× gate from yw01 holds.
9. **The note and the map**: `notes/yw02-the-text-engine.md` with the
   five sections, the ratios, the `unsafe` census delta, the save shape
   and why (G3 interim); `docs/MAP.md` §5 updated with G3/G5 as yw02 met
   them; yw03's contract drafted in full from §7.

## Forbidden / rules

The seven standing rules and `sprints/RULES.md`. Read sagitta's
`src/text/*.c` freely and cite `file:line`; **no other editor's buffer,
rope or piece-table source, ever**. No dependency but wolf-std. No golden
edited; a disagreeing golden is a STOP with the diff. Invariant 1 (no
data loss) outranks speed: the save's correctness is the gate, its speed
a ratio. The G3 gap is a STOP with a witness when the save is written,
never a silent claim of a sync that does not happen. Toolchains: the pin
yw01 left (wolf 0.2.33 / lupin 0.1.54 / wolf-std `cceda63`) unless s248's
0.2.34 has landed with G3's `fs_sync`/`fs_sync_dir`, in which case the
pin bump to 0.2.34 is yw02's first commit with the prediction.

## Inputs (re-derive)

sagitta at the pin: `s07`–`s12`, `src/text/*`, `src/unicode/coords.c`,
`u16.c`, `tests/unit/test_piece.c`, `test_file*.c`, `test_undo*.c`,
`test_cursor.c`, `test_mark.c`, `test_register.c`, `test_coords.c`,
`test_u16*.c`, `tests/torture/` (the kill9 harnesses), `tests/fuzz/
fuzz_textbuf.c`; the yew repo at yw01's merge (`src/term`, `src/unicode`,
`src/util`, the idiom in `docs/MAP.md`); wolf-std `std/fs`, `std/process`;
the spec `[os.fs.*]` (`[os.fs.rename]`, `[os.fs.stat]`, `[os.fs.symlink]`,
`[os.fs.link]`), and `[os.fs.sync]` if s248 has added it.

## Prediction (write before the first change)

G3's syncs are absent at 0.2.33, so the save is write-temp + atomic
`rename` without `fsync`/`fsync_dir`, and the torture SIGKILL campaign
shows no corruption (the rename is atomic) but the sync guarantee is only
as strong as the host's write-back — recorded, with the gap filed. The
piece tree ports without a compiler gap (a tree of indices into two
`List[byte]` buffers, no raw pointers); the differential fuzz holds
byte-equality over 200,000 ops at two seeds; the 100 MB load within 2× of
C's (the per-byte bounds checks are the cost). `test_undo`'s serialization
round-trips byte-for-byte.

## Done-when

Every deliverable with its tests; `tools/check-test` and `--native`
green; `make torture`'s batch and live kill9 lanes green against the wolf
binary (M-YW2); the unit files ported one for one; the save's no-corrupt
property shown and G3 filed with its witness; the ratios recorded on
kasumi under `taskset -c 0-3`; `docs/MAP.md` updated; yw03's contract
drafted; CI green; PR open with the five sections, shas as bullets, a
test checklist; `bash wolf/tools/lane-audit.sh yew yw02 <PR>` passing but
for the final run's green; hand back per RULES.md §6.
