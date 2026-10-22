# yw05 — the `sync` fork's evidence (G3, G4, G30's fork half)

kasumi, wolf 0.2.34 / lupin 0.1.55 / wolf-std `e036bec`, in `ctr`'s
container (archlinux:base-devel, the host's `/usr` read-only, `ulimit -c
0`, an 8 GiB cap) on CPUs 8-11, the fork tree `~/lanes/yw05-sync/yew`
(its oracle copy's PTY runner rebuilt for the tree's paths).

## G3 — the syncs (`fs_sync`, `fs_sync_dir`)

- `pin/` — the pin commit `e6d3f04`, before anything: `save_paths_test`
  "9 cases pass, save_fault_shim_contract known-red" (the driver red at
  `torture: injected inplace write did not fail`); the replica GREEN for
  port-child/C-checker and C-child/port-checker, RED port/port at the
  determinism order — the port's shim log `write, fchown, close, rename,
  close` against C's `write, fsync-file, fchown, close, rename, fsync-dir,
  close, fsync-dir, close, close`.
- `red-acceptance-gone/` — the acceptances deleted (`9981fe5`, `ff2e34c`,
  `660667d`, `ebb43d3`), the save still unsynced: `save_paths_test` traps
  at its `status == 0` assert (exit 134), `tools/torture-live` RED
  (`driver: torture: determinism run failed`, the replica's order `NO
  (fchown where fsync-file is wanted)`), `multicursor_test` traps in the
  shim half. That multicursor red was partly the test's own bug (the
  child's `journaled_done` removed the root holding the shim's log), fixed
  in `3f9c680`; `redmc/` is the honest red of the fixed test against the
  PRE-G3 text module (`file.lu`, `journal.lu` at `e6d3f04`): the trap at
  the `fsyncs == 1` assert, the shim log counting 0 `fsync-file pass`.
- `g3-syncs/` — at `452128f` (the syncs): `save_paths_test: 10 cases pass`
  (the driver exits 0 through every lane: the in-place EIO boundaries,
  EINTR, ENOSPC, determinism); the replica GREEN three ways, the port's log
  now `write, fsync-file, close, fchown, close, rename, fsync-dir, close,
  fsync-dir, close, close` — C's order with one more `close` after the
  sync (the compiled tiers sync a duplicate of the handle,
  `[os.fs.sync]`), which `atomic_log_order` accepts; `tools/torture-live`
  GREEN with no acceptance — the driver over the LIVE editor green through
  every lane, `determinism seed=424242 ok` and `external-sigkill
  iterations=500 attempts=500 ok` included; the replica's 500 SIGKILLs
  old=500 new=0; the per-run-state determinism GREEN. The shared-state
  replica run still differs by the global `:` history append (yw06's
  workspace state), which the tool prints as its KNOWN-RED note and does
  not gate. (`g3-syncs/mc.out` is the buggy-log test's trap, above.)

## G4 — `fs_realpath`

`f249cbb`: `text.file_realpath` is `fs_realpath`; `tests/native-text_file_test.out`
"17 cases pass (+1 port)" — the port case `l/..` resolving to the link
target's parent; `text_save_paths_test`'s realpath-keyed backup case
unchanged.

## G30's fork half — the clipboard writer and reader

`c2535bf`, `093e2e8`, `b6a8a62`, `0ea8c32`: natively every clipboard case
runs whole — `clipboard_test` 15 cases, 0 SKIP; `prompt_keys_test` 56
cases, 0 SKIP (the four clipboard-file halves and both C-v pastes);
`sel_actions_test` 30 cases, 0 SKIP (the three pastes). On the checked
machine (`wolf conform-run --json --checked`, whose record carries the
program's stdout; `wolf test` shows none) `clipboard_test` exits 0 with 10
SKIPs, each "os_fork answers unsupported here (the checked machine, ruling
#95 R4 C)"; `text_file_test` and `text_save_paths_test` exit 0 with none.

## The per-case checked runs (G29)

`percase.txt` (yw02's `percase.py`): `sel_actions_test` 27 pass, 3 `fail
exit(1)`; `multicursor_test` 25 pass, 4 `fail exit(1)`, 2 over the step
budget. Every `fail exit(1)` is a case of the `fn t_x() -> int` shape
returning its SKIP count (1): the three paste cases and the multicursor
shim halves and bug guards SKIP on the checked machine (no fork, `os_exe()`
is `wolf`), and `multicursor_batches_symbol_rebuild_and_damage` always
returns its yw10/yw11 SKIP — none is an assertion (a trap). `percase-pk.txt`
(the same tool renaming `prompt_keys_*`): `prompt_keys_test` 45 pass, 0
fail, 11 over the step budget (yw04: 44 and 12).

## The fork's final gate (`final/`)

At `7367985` (the sources built 2026-10-22T02:40Z, release `895f205fae8f`),
in the container on CPUs 8-11 (`final.log`): every tier built; campaign 03
62/62 on both tiers; campaign 04 **84/104** on both tiers — the 20 red are
the job half's alone (`s57_29_prompt_select_and_copy` green: the forked
writer); `check-test --native` exit 0 (89 files, 216 SKIP lines) and the
checked lane "89 passed; 0 failed"; the replica GREEN three ways;
`tools/torture-live` GREEN with no acceptance; `save_paths_test` 10 cases
pass.
