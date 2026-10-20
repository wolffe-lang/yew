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

Hits and misses are recorded below as they are measured.

## 1. Forbidden / inputs

(filled as the lane runs)

## 2. The five sections

(filled as the modules land)

## 3. What yw02 measured

(filled as the gates run)

## 4. Rulings asked

(filled)

## 5. Issues to file

(filled)
