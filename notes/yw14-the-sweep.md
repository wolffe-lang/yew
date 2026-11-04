# yw14 — the sweep: the red nightly and the correctness backlog

_yew's backlog sweep at wolf 0.2.36 / lupin 0.1.58: the red CI first, then the correctness bugs with a row
each, the `.gitignore` complexity case, and the retirements the pin allows. The perf rows and perf issues
are out of scope (they need the perf host's baseline), and so are yw13's open PRs._

## Prediction

Written before the first change and committed first (`6997469`, `notes/yw14-evidence/prediction.txt`).
What it said, and what the rows showed:

- **#49 and #90 are one red** — confirmed. Every scheduled run from 10-22 to 10-28 is red only in
  `port (macos-latest, true)`, and every one from 10-29 is cancelled there at the job's 240 minutes. The
  push run #90 calls green had no macOS port leg (PRs and trunk pushes leave it to the nightly), so the
  comphelp trap was never a flake: it trapped every night. Both predicted causes held, and the cap was a
  third red:
  - comphelp: the fixture logs `os_exe()`, which on macOS keeps the symlinked directory of the exec'd
    path, and the test expected `fs_realpath(bin)`. The tool's actual log, reproduced on macOS arm64
    under a symlinked TMPDIR, was `<link>/yew-comphelp-<pid>-5/bin/tool --help stdin=eof`; the test
    wanted the resolved `<real>/…` spelling. It was the realpath, not a settle race.
  - runtime_skew: `refusal_names_file_line` on the checked machine. The workspace unit is read through
    the trust check's resolved workspace, so its refusal names the canonical path, and the runner's
    TMPDIR sits under `/var/folders` (`/private/var/folders`) with a trailing slash.
  - The cap: the checked lane alone took 152 and 200 minutes on the last two nights.
- **#42** — confirmed: the clipboard rows SKIP in every job that has not built C's fakeclip.
- **#78** — confirmed not reproduced: of the 19 red unit jobs since 10-25, none is cmdcomp_shell; the two
  traps are 10-25's, at the 0.2.35 pin, before yw08's conform-run print.
- **Today's nightly** (41877566157): its `fuzz (macOS arm64, against-c-2)` is red too (read at the hand-back).
- **#33** — confirmed: C yew saves `alpha\nbeta\ngamma\n\ndelta`, the same bytes as the port.
- **#18** — wrong: it was fixed at `a7be446` (yw04) and the issue was left open; the row is green at trunk.
- **#32** — not predicted: already fixed at `f60a2a0` (CmdRange carries `tok_lo`/`tok_hi`).
- **#93** — half right: B's inner refusal *is* the caller's principal. The witness printed only the outer
  `ed.run`'s status.
- **#100** — partly wrong. `*\` is linear in the port, and C's driver is ASan- and UBSan-clean on the
  campaign. But the scaling row found a real superlinear case, an unanchored crossing star, and it is
  fixed.
- **#98** — more than predicted: the G50 witness exits 139 natively at the pin without the copy.

## Forbidden

- No merge, label, tag, release, and no issue closed. No attribution trailer.
- No perf row and no perf issue (#30 #31 #38 #40 #45 #53 #54 #55 #77 #89).
- yw13's PR#102–#105 and PR#106 are untouched.
- Clean room: C yew is run as a black box, never read. One exception, disclosed: while looking for a harness
  over C's matcher, the lane opened `notes/yw06-evidence/pick/gitignore/gi_answers.c`. That file is a
  verbatim copy of sagitta's fuzz driver. The lane read its header comment, stopped there and did not use
  it. No other editor's source was read.
- No golden is edited. `sagitta.pin` and the wolf pin are unchanged. No test is disabled, and no
  assertion is weakened.

## Inputs verified

- **Base:** yew trunk `1218169e` (r41q's record). The pin is wolf 0.2.36 (`5adf3d91`), lupin 0.1.58 and
  std `78b9d3cb`. 0.2.36 is still the latest wolf release.
- **C yew** comes from `sagitta.pin` (`9ace98c2`), built with clang on macOS and gcc in the Linux image.
- **The newer wolf** for #98 is a wolf-lang build at `8989074`, 190 commits past `a246580b` (#998, the fix
  for #948).
- **The CI history** was read from the run API: the macOS port job of 13 scheduled runs, the 39 red runs
  since 10-25, and each red unit job's log.
- **The retirements at 0.2.36:**
  - #17 and #27 keep their remainder: the mutable registries (G48) need wolf-lang#917, and the bound
    calls (G47) need #916. Both are open, so no released wolf has them.
  - #23 keeps G32's two rows: a write-only open of an existing file, and the journal's POSIX record
    lock. No wolf release through 0.2.36 has them, and no wolf-lang issue names them (R-yw14-4).
  - Retired here: `env_arg0` (s261, available since 0.2.36) replaces the comphelp fixture's `os_exe()`.
- **README** read against the change. It gains the fake clipboard tool's two commands (`db1d1ab`, README
  only); everything else in it is current.

## Evidence index

Commits, in order:

- `6997469` the prediction.
- **#90**
  - `983fe33` comphelp's fixture trees under TMPDIR. This keeps the Mac run out of `/tmp`, and it is what
    makes the red reproducible there.
  - `e16c027` the help fixture names itself by `argv[0]`.
- **#49**
  - `1aea4be` runtime_skew expects the workspace refusal's canonical path.
  - `4913f8b` the CI proofs (`ci/legs-test.py`, `ci/macos-split-test.py`) want `macos-unit`, the fake tool
    and the clipboard check. They are red at that commit (5 FAILs, `macos-split-test` AssertionError).
  - `4cfb068` the workflow: the macOS unit lanes as four `macos-unit` shards, where the port's macOS leg
    runs. From 11-02's per-file times, each shard's checked lane is 34–42 minutes. The proofs are green
    here.
  - `4ff4928` the planner's docstring.
- **#42**
  - `c298a9e` `tools/build-fakeclip`.
  - `169725a` `tools/check-test` keeps the native lane's log and gains `--fakeclip-ran`.
  - `4cfb068` (above) adds both steps to `unit` and `macos-unit`.
- **#33** `c75f974` the PTY row: C's bytes are the oracle, and the port must equal them.
- **#99** `a118c99` the row (red with the trunk script: run 2 in one root, "motion, Insert and save did
  not answer"), then `3f84601` the fix (green twice in the red run's own root).
- **#93** `d1b1dc3` witness B prints and asserts its inner refusal:
  `capability: fs.read denied to the workspace config`. The outer "ed.run is not valid in the current
  state" is `ed.fl.eval`'s answer when the chunk it ran failed.
- **#100**
  - `be6fb00` the scaling row, `tools/run-fuzz-gitignore --native --scale`. It is red there, by name:
    `a**b**c**d**e` takes 226 µs, 20.3 ms and 1.64 s at 481, 4,810 and 48,100 bytes of ten-byte
    components, and 395 µs, 35.5 ms and 3.54 s over `abcd/` components.
  - `669ad3b` the fix: the walk memoises the star states it has proven false. The same row then gives
    28, 279 and 2,755 µs; all 35 shapes × 3 paths are linear; the answer fold is still C's matcher's
    `ade5cd1e3574db76`.
- **#98**
  - `7b4679a` the repair.
  - `8135320` the row. Trunk's form exits 139 natively under the pinned wolf and is refused with E1010
    under `8989074`; the copy builds and runs on both.
- **#18** `b85e085` the row. It is green as committed, and red at `edit_paste_bytes_test.lu:38` when the
  paste is carried as a `str` again.
- **Docs**
  - `c4bc2a1` MAP's G50 and G23 rows.
  - `db1d1ab` README only.
  - `db6d591` CHANGELOG.

The macOS rows, on macOS arm64 with TMPDIR through a symlink and a trailing slash:

| row | state | result |
|---|---|---|
| comphelp | before `e16c027` (tree-equal to `983fe33`) | red at `:710` |
| comphelp | at `e16c027` | `21 C cases pass, 0 SKIP; 4 port cases pass` |
| runtime_skew | before `1aea4be` | `runtime_config_0/1` pass, then a trap at `:83` |
| runtime_skew | at `1aea4be` | all four pass |

The gauntlet runs at the final head, under the recorder, in yew CI's own image (`ubuntu:24.04` with the
hosted runner's tools) on six pinned Linux x86-64 CPUs. It holds:

- the port job step for step: fmt, scratch homes, the divergence controls, both tiers, `--version`, the
  tables, the walk listings, the 283 Fletch cases, the dispatch and the choke point;
- the CI proofs;
- C's build and the fake tool;
- every row above: comphelp and runtime_skew under a symlinked TMPDIR (runtime_skew on both machines),
  the nested witness, the paste row, the clipboard rows with their control, the final-newline PTY pair,
  runtime-pty twice, the scaling row, the fuzz row against C's driver with the answer fold, and the G50
  row;
- cmdcomp_shell's whole-file checked run three times (#78).

Its END lines and the plant's record are in the PR body.

**The plant**, `yw14-plant-memo`, is one hunk off the green head. The memoised walk forgets the states a
backtrack enters, and `gitignore_scales_linearly` goes red by name.

**Triage of every other open issue:**

| issue | state |
|---|---|
| #32 | already fixed, `f60a2a0`; `cmdline_catalogue_errors_preserve_live_prompt` asserts the range caret (`5,3d`, `900d`) |
| #18 | already fixed, `a7be446`; row `b85e085` |
| #33 | the oracle's behaviour; row `c75f974` (R-yw14-1) |
| #78 | still open: not reproduced since 10-25; the trap never printed its message; three checked runs in the gauntlet |
| #79 | an oracle question (the feeder is the oracle's driver, which the clean room leaves unread). A second torture-live red exists: trunk push 40448806681 (10-27), the replica's determinism lane, run 0's fault-shim log with an extra leading `close`. Same step, same shape (an fs operation on either side of the arm). |
| #43 | a watch; the macOS oracle's pty goldens were green on 11-03's nightly |
| #109 | not started: it renames `ed.<field>` across files PR#102 also changes (R-yw14-3) |
| #17, #27 | blocked on wolf-lang#916 and #917 |
| #23 | blocked on a wolf with a record lock and a write-only open (R-yw14-4) |
| #30 #31 #38 #40 #45 #53 #54 #55 #77 #89 | perf: blocked on the perf host's baseline, out of scope |

**Rulings:**

- **R-yw14-1 (#33).** C yew keeps no final newline after `G` `o` on the empty last line, and the port is
  C's. Options: (A) close as the oracle's behaviour; (B) file a sagitta change if vim's model is
  wanted. Recommended and implemented: A. The row holds the port to C.
- **R-yw14-2 (the macOS unit lanes).** Options: (A) four `macos-unit` shards on the nightly; (B) raise the
  port job's cap. B cannot fit: about 300 minutes of unit lanes plus the fuzzers is past GitHub's 360.
  Recommended and implemented: A. PRs and trunk pushes still run no macOS unit leg (tl30), so only a
  nightly or a dispatch proves it.
- **R-yw14-3 (#109).** Options: (A) after PR#102 merges, one mechanical lane; (B) now, conflicting with
  #102 in every editor file it touches. Recommended: A. Not done here.
- **R-yw14-4 (#23).** Options: (A) file one wolf-lang gap issue for the record lock and the write-only
  open; (B) leave G32's text as the only record. Recommended: A. Filing is not this lane's.

## Done-when

- [x] Every change has its row, seen red before green (macOS rows, the CI proofs, #99, #100, #18; #98's
  row carries its red form in itself).
- [x] The gauntlet is green at the final head under the recorder, and the plant is red by name (records in
  the PR body).
- [ ] CI at the head (cross-cutting: `.github/`, `ci/`). The macOS `macos-unit` legs run only on a nightly
  or a dispatch.
- [ ] To close: #90, #42, #18, #32, #33, #93, #98, #99 and #100 at the merge, and #49 at the first
  green nightly.
