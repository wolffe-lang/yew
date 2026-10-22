# yw05 — panes, tabs and groups

**Opus 5.5, crawl 54, 2026-10-22.** Contract: planning repo
`sprints/yew/05-panes-tabs-groups/yw05-panes-tabs-groups.md` at
`d702963`, which adopts yw04's draft (this repo's
`notes/contracts/yw05-panes-tabs-groups.md` at `5889a8b`) whole. Ports
sagitta campaign 05's first half (`s22`, `s23`, `s24` and `s57_8` at
`sagitta.pin`): the pane tree in cells, the clickable-region registry in
full, tabs with the strip and its overflow, facsimile's group model,
several startup files and the allocation-free hot paths; and, first, the
bump to wolf 0.2.34 with yw04's job half.

## The toolchain at the lane's start

`gh release list -R wolffe-lang/wolf-lang` at **2026-10-22T01:08:09Z**:

    v0.2.34  Latest  v0.2.34  2026-10-21T12:58:10Z
    v0.2.33          v0.2.33  2026-10-19T18:37:53Z

`gh release list -R wolffe-lang/wolf-interp`:

    lupin 0.1.55  Latest  v0.1.55  2026-10-20T22:11:27Z
    lupin 0.1.54          v0.1.54  2026-10-17T16:48:34Z

`v0.2.34` names commit `9da7bdcf2aea9adf48df6570bedc58e16e9ef853` (tag
object `38ab81cb`); `v0.1.55` names `e642f2630ad4c7f53740428d5cca705f2e0d295b`
(tag object `047184fb`). The archive digests, read twice from the
release API (`gh release view --json assets`, two passes, identical):

| archive | sha256 |
|---|---|
| `wolf-0.2.34-x86_64-unknown-linux-gnu.tar.gz` | `88a9dd3da1c9a0e38c08eb6e2de9c1ef04d1ed93dcf51024d8dbbb76890c1821` |
| `wolf-0.2.34-aarch64-apple-darwin.tar.gz` | `29c8331f5d188b00c4580bc7677b1238891c5734d00b0512df10c60eab236ee3` |
| `wolf-0.2.34-aarch64-unknown-linux-gnu.tar.gz` | `ca5cadf936dc0d4396e92733fc65e953d549f3b61f0aa354e7be2e78ea8c3ad0` |
| `lupin-0.1.55-x86_64-unknown-linux-gnu.tar.gz` | `1152abc0bef65d334b94bc881a26463fac345919cc2ca07a291796e6048a8a38` |
| `lupin-0.1.55-aarch64-apple-darwin.tar.gz` | `2eac1cccdc8a5bec5831787604098982a7ac42e41561a037c3b5ccf0ac21741a` |
| `lupin-0.1.55-aarch64-unknown-linux-gnu.tar.gz` | `5854ab268a835bb75749bce7601441858ac342351906a0838e8602e4edbd45d7` |

The bundled std is wolf-std **`e036bec`** (the release notes'
"`STD-PIN` moves to wolf-std `e036bec`"; read again from the staged
archive's `std/STD-REV` at the bump). sc69's wrappers (`term.Mode`'s
three fields, `signal.wait_fds`, `term.restore_at_exit`, wolf-std `3bacc5f`)
are the NEXT std pin and not available here: the port calls the prelude
names directly and yew#24 stays the 0.2.35 pin's.

What 0.2.34 brings the port (its release notes, read in full): `os_fork`
(s247: `busy` while a task is live, `unsupported` on the checked machine),
`os_term_restore_at_exit` (G1, #794), `os_signal_wait_fds` (G2, #795),
`fs_sync`/`fs_sync_dir` (G3, #796), `fs_realpath` (G4, #797),
`os_clock_ns` (G8, #798), the mode int's bits 5–7 (G34, #802: `RAW_CR` 32,
`RAW_OUTPUT` 64, `STRIP8` 128; a mode WITHOUT them now writes the usual
setting where 0.2.33 left each as found), and `wolf test` running a test
file's own `test_*` (G10, #799). Not this pin: s251 (yew#17, yew#27: the
closures across modules) and s255 (wolf-lang#859, the per-turn region and
`List.reset`/`reserve`) are 0.2.35's; s255's `s255-witness` branch here is
read-only evidence, never merged.

## Rulings taken at launch (the maintainer's, 2026-10-22, recorded)

- **R-yw04-5 = A** (the narrow `A-e` tab), replaced here by the full model.
- **R-yw04-6 = B**, retiring unasked when `os_fork` makes the clipboard
  writer C's (yew#29 closes then).
- **R-yw04-7 = A** (`:set` over `Opts` until yw09).
- **R-yw05-1 = A**: s57.13–s57.15 and s57.22 (17 PTY cases,
  `test_ctxmenu`, `test_ctxrows`) move to yw06, after Sprint 27's router.
- **R-yw05-2 = A**: the bump and yw04's job half inside this lane.
- **R-yw05-3** as the draft recommends: R-yw03-7 (A) is deliverable 6.
- **R-yw05-4 = A**: a deferred tab's residency is its buffer's piece tree
  being built, the read counted by a test hook in `text.file`.
- **yew#28**: `notepad_burst_keys` and `_paste` re-gated on macOS here,
  with what was measured. **yew#27** (s251's retirements) is 0.2.35's.

## Prediction (written 2026-10-22, before the first change)

**The contract's**, kept: the pane tree, tabs and groups port with no
golden edited and none of campaigns 03's and 04's changing as the one-tab
strip and the narrow registry are replaced; the campaign-05 cases of
deliverables 2–5 go green; the layout fuzz, the tab oracle and the
membership fuzz hold; s24 DoD 4's one read per group holds through
`text.file`'s hook; keypress → paint with two panes and the tab switch
within 2× of C yew; the job half's red goldens go green without a golden
edited and every G2/G3/G4/G30/G34 interim retires with its test turned
green.

**The lane's own**, from the release notes, sagitta's sources and the PTY
registry before any code:

1. **The pin commit changes no source.** No `.lu` file declares one of the
   seven new prelude names (the release notes searched yew's trunk); the
   port names no `test_*` in a test file (`cmdcomp.lu`'s
   `test_stub_enumerate` is a module function, not a test file's), so
   #799 changes no test run; a mode int without bits 5–7 WRITES `ICRNL`
   and `OPOST` on, which is what the PTY harness's usual terminal already
   has. Predicted: both tiers build with warnings denied, `check-test`
   green on both lanes, campaign 03 62/62 and campaign 04 83/104
   unchanged at the pin commit, before any gap is adopted.
2. **The deliverable's count is 23, not 30.** sagitta's registry holds
   `s22_*` 11, `s23_*` 6, `s24_*` 4, `s57_8_*` 1 and
   `startup_multiple_files`: 23 cases; the draft's "30" is a miscount.
   Predicted: 23 of 23 green by name on both tiers.
3. **G2 retires the whole interim.** One `os_signal_wait_fds` over the tty
   (and, with the job half, the jobs' pipes) with the signal set and the
   timer heap's deadline replaces `term.tty_wait`'s three shapes (parked,
   the `VTIME` tick, the fine wait), the drain mode (a zero-deadline poll
   is the typeahead query) and `edit.loop`'s deadline-first turn; the
   termios mode is set once at raw entry and never switched in the wait.
   With no `tcsetattr(TCSADRAIN)` left in the wait, `notepad_burst_keys`
   and `_paste` pass on macOS: **re-gated, green in the PR's macOS oracle
   leg.**
4. **G34 retires the LF-as-Enter interim** (R-yw03-4): `rawios` sets
   `RAW_CR | RAW_OUTPUT` (C's `cfmakeraw` set, `tty.c:521-543`), Enter
   arrives as CR, `term.input_set_lf_enter` and `tty_icrnl_stuck` go;
   no golden changes (the renderer writes no LF; the handover gives the
   child the saved cooked mode).
5. **G1 does not retire the guard.** `os_term_restore_at_exit` covers the
   exits the runtime owns (a return, `os_exit`, a trap, the stack guard,
   `os_exit_signal`); the harness's `restore_bus`, `restore_abrt`,
   `notepad_restore_segv` and `notepad_restore_kill` kill the editor from
   OUTSIDE with a signal nobody listens for, which "restores nothing"
   (the release notes). Predicted: the registration replaces the
   in-process `tty_fatal` restore on a trap, yw01's guard sibling stays
   for outside fatal signals, and those four macOS cases stay advisory
   under R-yw01-1, renamed to say why.
6. **G3 turns every sync red green**: `save_fault_shim_contract`, the
   replica's determinism order, `tools/torture-live`'s determinism lane
   and `test_multicursor`'s two sync-count cases (R-yw03-5); the
   acceptances and CI's KNOWN-RED branches are deleted.
7. **G4**: `fs_realpath` replaces `text.file_realpath`'s component walk
   with every existing answer unchanged.
8. **G30's fork half**: the clipboard writer forks as C's does (twice,
   the grandchild writing), so `s57_29_prompt_select_and_copy` goes green,
   R-yw04-6 retires and `test_prompt_keys`' writer SKIPs run; the reader
   gets its deadline from `os_signal_wait_fds`. The filter's WRITE side
   (R-yw04-3, wolf-lang#818) is served the same way — a forked writer
   child feeding the filter's stdin — so its three goldens go green too;
   if that shape is refused, they stay red under a new name.
9. **The job half: 19 of yw04's 20 job goldens go green** (the stream,
   the footers, the badge, `:r !`, the generator, `--help` ×3, fish, the
   session ×4 and the filter ×3); `s19_jobs_table` needs the `*jobs*`
   scratch buffer, which full tabs make reachable — green if its table
   needs no workspace state (s25), else red naming yw06. Every SKIP-by-
   name of yw04's job suites (80 cases) runs.
10. **Deliverable 6 cuts the `:` keystroke's ~210 KB by 10× or more**
    (the document rows' full repaint written into storage the `Ed` owns)
    but does not reach C's 0.3–0.5 KB: a turn's other temporaries stay
    until a per-turn region compiles (G18/G33, s255, 0.2.35).
11. **The pane tree's ratio is a C `float`**: the cell split is computed
    in single precision (`layout.c`); the port must round as C does or a
    resize golden differs by a cell. Predicted: wolf's `f32` reproduces it
    exactly; if it has none, the ratio is held as C's float bits.
12. **Merging is the risk, not the porting**: every campaign-05 unit
    takes the `Ed` (yw03's module rule), so the forks meet in `ed.lu`,
    `draw.lu`, `loop.lu` and the registry's `match`; predicted no golden
    of campaigns 03 and 04 changes at any merge.

Hits and misses are recorded in §3 as they are measured.

## The plan

The contract is the directive; this is the order. The leaf work runs as
forks of the lane on their own branches (`yw05-<fork>`), each with its
own tree on kasumi and its own CPU set, merged into `yw05` with a merge
commit naming what landed (yw03's and yw04's shape).

1. **The pin** (deliverable 1's first commit), then a baseline of the
   gates at the pin before any gap is adopted.
2. **Forks**:
   - `wait` — G2's wait over descriptors, G34's bits, G1's registration;
     the interims retired; yew#28's macOS gates.
   - `sync` — G3's syncs, G4's realpath, G30's forked clipboard writer
     (yew#29) and R-yw03-5.
   - `jobs` — yw04's job half on the `wait` fork's wait: `job.c`'s table
     and consumers, the stream, the filter, `:r !`, the session, the
     generators, `--help`, fish.
   - `layout` — s22: the pane tree, the region registry in full,
     `pane_cmds`, borders and dim-inactive, click-to-focus and the
     border drag, the layout fuzz.
   - `tabs` — s23 and s57.8: tabs in full, the strip engine, glyphs, the
     close prompt, several startup files, the tab oracle.
   - `groups` — s24, on the `tabs` fork's model: groups, groupnav, the
     picker, from-dir, the membership fuzz.
3. **The hot paths** (deliverable 6), after the merges.
4. **The gates** (deliverable 7) on kasumi in a container under
   `taskset -c 0-3`; the note, the map and yw06's contract; the PR.

## 1. Forbidden

The seven standing rules and `sprints/RULES.md`, as the brief gave them:
sagitta read freely and cited (`layout*`, `region*`, `tabs*`, `strip*`,
`groups*`, `groupnav*`, `grouppicker*`, `groupfromdir*`, `glyphs*`,
`draw.c`, `pane_cmds.c`, and for the bump `job.c`, `shsession.c`,
`shell*.c`, `compgen.c`, `comphelp.c`, `compfish.c`, `clipboard.c`,
`tty.c`, `loop.c`); facsimile's model only as sagitta's C states it; no
other editor's or multiplexer's source; no dependency but wolf-std; no
golden edited. Builds, runs, signals, children and every golden on kasumi
in a container (`notes/yw05-evidence/lane/ctr.sh`: `archlinux:base-devel`
under podman, the host's `/usr` read-only for its compilers, `taskset`
per fork, `ulimit -c 0`, an 8 GB cap, no network), never on nomad-1; git
work in the lane's and the forks' worktrees on nomad-1; no merge, tag,
issue filed or closed; no trailer.

## 2. Inputs, verified

| input | re-derived (2026-10-22) | drift from the draft |
|---|---|---|
| the sprint files | `s22` 279, `s23` 249, `s24` 366 (894), `s57_8` 279 lines | none |
| the C | the header's twenty files: 7,535 lines; `draw.c` 1,348 (its border half is s22 §7's) | none |
| the unit files | 10 files, 194 tests, every one in `tests/unit/registry.c` (layout 45, region 7, draw 4, tabs 34, strip 14, glyphs 8, groups 23, groupnav 35, grouppicker 19, groupfromdir 5) | none |
| the PTY cases | `s22_*` 11, `s23_*` 6, `s24_*` 4, `s57_8_*` 1, `startup_multiple_files`: **23** | the draft's "30" is a miscount |
| the fuzz lanes | `tests/fuzz/fuzz_panes.c`, `fuzz_tabs.c`, `fuzz_groups.c` | named here |
| the budgets | `budgets.txt` has no pane or tab-switch row; `startup.first_paint.workspace50` and `mem.workspace50` are s25's deferred tabs (yw06) | the 2× gates here are the port/C ratio from the same run |
| the oracle | C yew at `9ace98c2`, gcc: 3,047 unit tests, 0 failures in the lane's container once `YEW_LOG` is unset (one failure under it, the variable's, `notes/yw05-evidence/lane/pin-baseline.txt`) | none |
| the yew trunk | `5889a8b` (yw04's merge) | none |
