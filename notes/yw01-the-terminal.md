# yw01 — the terminal and the first paint

**Fable 5.1, crawl 54, 2026-10-19.** Contract: planning repo
`sprints/yew/01-the-terminal/yw01-the-terminal.md` at `ae47814`. Ports
sagitta campaign 01 (`s03`–`s06`) `src/term/*`, the driver (`main`,
`args`), `log`, `xdg`, `base64`, `tests/pty/demo_paint.c`. Ruling #93's
interim shapes: R1 = C with **B** (the supervisor) shipped meanwhile; R2
= A (`os_signal_wait_fds`, s248) with VTIME polling meanwhile. This lane
sets the idiom every later terminal lane copies.

## Prediction (written 2026-10-19, before the first port line)

The mode int (`os_term_set_mode`, `[os.term.mode]`) reaches
`ICANON`/`ECHO`/`ISIG`/`IXON`/`IEXTEN`/`VMIN`/`VTIME` and **not**
`ICRNL`/`OPOST`/`ISTRIP`/`BRKINT`/`PARMRK`/`INPCK`/`CS8`: the Enter
witness will show LF (CR not distinguished from `^J` because `ICRNL`
still translates CR→LF on input), the `\n` witness will show CRLF
(`OPOST`/`ONLCR` still rewrites `\n`→`\r\n` on output), and **both are
filed before the first PTY golden is attempted**. sagitta's goldens
assume both bits cleared, so campaign-01's `input_keys_*` and every
paint case will be red until the widening lands or the maintainer rules
an interim. Cold start of the port within 2× of C's (yw00's stub was
0.84×); keypress → paint for `demo_paint`'s `damage` scene within 2×.
Nothing in campaign 01 allocates per keystroke after warm-up except
`Key.text`, which the port keeps as a reused `List[byte]`.

Hits and misses are recorded in §4 as they are measured.

## 1. Forbidden / inputs

The track's seven standing rules and `sprints/RULES.md` held: sagitta's
`src/term/*.c` read and cited `file:line` in every unit; no other
editor's terminal code and no VT library's source; no dependency but
wolf-std; no golden edited (a disagreeing golden is a STOP with the
diff); every gap filed with a witness; no attribution trailer; builds
and tests on kasumi under a checkout path under 40 characters
(`~/lanes/yw01/yew`); `setsid`/`nohup` with a pid file for long jobs,
killed by recorded pid only; the maintainer's sagitta checkout read-only
(cloned to `~/lanes/yw01/sagitta`).

Inputs, verified: wolf 0.2.33 `v0.2.33` → `85dab5d7e5…` (tag object
`56110e4f`), lupin 0.1.54 → `0e536e8f…` (unchanged), wolf-std
`cceda631…` as the 0.2.33 archive bundles it; the six archive digests
read twice from the release API, identical both passes (§ pin); the
spec's `[os.term.*]`, `[os.signal.*]` clauses and `spec/prelude.json`
at `85dab5d7`; std's `term`, `signal`, `process`, `fs`, `time` at the
pin; sagitta `9ace98c2` `src/term/*`, `src/main.c`, `src/args.c`,
`src/util/log.c`, `xdg.c`, `base64.c`, `src/mod/mods.c`,
`tests/pty/{harness,runner,vt,snapshot,registry,demo_paint}.c`,
`tests/perf/{perf_latency,perf_startup,budgets.txt}`.

## 2. The pin bump

wolf 0.2.32 → 0.2.33, wolf-std `d37c911` → `cceda63`, lupin 0.1.54
unchanged. What 0.2.33 brings this lane: the five s246 calls
(`os_signal_ignore_one`, `os_signal_default_one`, `os_exit_signal`,
`os_wait_status_core`, `os_wait_poll_core`) and `os_signal_text(0)`
answering the host's words. `os_exit_signal` is #93 R1's interim-B death
path (the supervisor ends itself with the child's signal), and the full
signal table is what the restore's listen + re-raise needs. The pin
bump is this lane's first commit, with the prediction above committed in
the same commit and before any port code.

## 3. The five sections (filled as the modules land)

- **`term.tty`** — LANDED (`src/term/tty.lu`, `src/term_tty_test.lu`,
  13 cases): the raw-mode mapping (`rawios` builds a `std_term.Mode`
  with the five reachable bits off and `VMIN=1`, clearing `signals` too —
  Ctrl-C is a key), the restore blob byte-pinned against C (with the
  1003-motion variant), the capability probe state machine (kitty /
  DECRQM 2026 / DA1 / OSC 11, the ambiguous-prefix flush, the deadline,
  chunk-safe), truecolor detection (12 vectors), the probe config, and
  the I/O surface: `tty_open` (the not-a-terminal and broken-pipe
  diagnostics), `tty_raw`/`tty_restore` through `os_term_set_mode`,
  `tty_winsize`, `tty_altscreen`, `tty_suspend` (restore, reset the
  handler, raise, listen again; re-raw on `CONTINUED`), `tty_wait` over
  `os_signal_wait_fd` with the `VTIME` interim (#93 R2), `tty_read`,
  `tty_on_signal` (WINCH/CONT/CHLD/SUSPENDED), mouse motion. **The
  restore guarantee, ruling #93 R1 interim B**, as the guard sibling of
  sagitta `tty.c:243-349`: the editor spawns `os_exe() --guard <saved
  mode>` with a pipe at fd 3 and feeds it `R`/`C`/`M`/`S` bytes; on EOF
  (the editor dead, however it died) the guard writes the restore blob,
  puts the saved mode back and prints `yew: fatal signal, terminal
  restored` if the editor was still raw. `TERMINATE`/`RELOAD`/`QUIT` are
  listened for and end in `os_exit_signal`; `SIGSEGV`/`SIGBUS`/`SIGABRT`
  reach the guard through the pipe's EOF. Proven by sagitta's own
  `restore_quit`, `restore_crash`, `restore_bus`, `restore_abrt` and
  `restore_suspend` cases (§4).
- **`term.input`** — LANDED (`src/term/input.lu`, `src/term_input_test.lu`,
  18 cases, the 131 legacy vectors): the escape state machine with the 25
  ms lone-ESC deadline, CSI/SS3/kitty (`CSI u` with every modifier,
  release/repeat events, the text payload), bracketed paste streamed in
  4096-byte chunks with the 8192 string cap and the drop/retain counts
  (a 5 MiB paste in the test), SGR mouse and focus, the unsolicited OSC
  52 reply quarantined to the log; the enable/disable blobs with the
  `YEW_MOUSE` gate.
- **`term.grid` / `term.render` / `osc52`** — LANDED (`grid.lu` 20 cases,
  `render.lu` 21, `osc52.lu` 4, `util/base64.lu` 3): `Cell` as 13 ints
  (eight inline bytes packed in two, the intern id, fg/bg, attrs, width,
  flags), the front/back pair with per-row damage spans, the three
  wide-glyph rules and `break_pair`, overlays and the cursor; the
  renderer appends to a `List[byte]` and does no I/O: the cursor-motion
  cost model, erase-to-EOL on the default background only, SGR runs
  with the shared-reset trap (all 16 bold/dim transitions), the frame
  envelope with mode 2026 as one balanced pair and the ≤ 32-byte raw
  gate, the three colour tiers with `rgb_to_256`/`rgb_to_16` and their
  tie rules, every golden byte string of `test_render.c`, the six
  invalid-cell scenarios as exit-4 self-spawns; OSC 52 with the tmux and
  screen wrappings and the size cap.
- **`demo_paint` + the driver** — LANDED: `tools/demo-paint/main.lu` (the
  six scenes, `--crash`, `--guard`; `tools/build-demo` stages it beside
  the port's modules, D32) and `src/yew.lu` with `args` (20 cases),
  `util.log` (3), `util.xdg`, `util.base64`; `--help` byte for byte (a
  `tools/goldens` row), the not-a-terminal diagnostic, every later
  surface hard-erroring by sprint and lane. **M-YW1 met**: the first
  paint through the whole stack under sagitta's harness, 2026-10-19 on
  kasumi (§4).
- **The gates** — `tools/goldens` green on every campaign-01 case (§4),
  `tools/goldens-selftest` red on both plants, the 2× step in CI
  (`tools/run-perf-latency`, advisory on the hosted runner) and the
  ratios on kasumi (§4).

## 4. What yw01 measured

All on kasumi (16 cpus, load 0.25 at the run), the release tier of
wolf 0.2.33, C yew at `9ace98c2` built with gcc, the checkout under
`~/lanes/yw01/yew` (29 characters).

**The campaign-01 goldens** (`tools/goldens --yew target/release/yew
--demo target/tools/demo_paint --suite pty --filter <case>`, each case
by name, 2026-10-19): `probe_modern`, `probe_dumb`, `paint_basic`,
`paint_wide`, `paint_colors_truecolor`, `paint_colors_256`,
`paint_colors_16`, `paint_damage`, `paint_resize`, `restore_quit`,
`restore_crash`, `restore_bus`, `restore_abrt`, `restore_suspend`,
`input_keys_modern`, `input_keys_legacy` — the sixteen the contract's
prefixes name (`registry.c:13083-13100`; there is no `demo_` case at the
pin) — and `osc52_reply`, every one `ok`; `version` and `help` green
against `target/release/yew`. By profile: `modern` fourteen, `nokitty`
one (`input_keys_legacy`), `dumb` one (`probe_dumb`); **no campaign-01
case carries the `nosync` profile at the pin** (the registry assigns it
to no case in these lines), so "four profiles" is three for campaign 01
and the fourth is the `damage` scene's own sync-off path, which
`paint_damage` covers. `osc52_frame` drives the demo's `osc52` scene,
which needs the registers and the clipboard (sprint 12, yw02); the
scene hard-errors naming yw02. `tools/goldens-selftest`: ok — green on
the oracle, red on both plants.

**The restore, proven by sagitta's cases**: `restore_quit` (the tail is
the restore blob, termios unchanged), `restore_crash` (`--crash` raises
SIGSEGV through `os_exit_signal`; the tail is the crash blob and `yew:
fatal signal, terminal restored`, written by the guard), `restore_bus`
and `restore_abrt` (the harness signals the demo; the restore blob
follows, the terminal is back), `restore_suspend` (SIGTSTP/SIGCONT; the
alternate screen re-entered).

**The 2× gate** (`tools/run-perf-latency --cpus 0-3`, C first, the
port, C again; 20 cold starts and 300 keys each, `target/perf/`):

| metric | C p50 | wolf p50 | wolf/C | C again (drift) |
|---|---|---|---|---|
| cold start → first paint (`basic`, ESC [?2026 l) | 4,620 us | 6,973 us | **1.51** | 4,599 us (1.00) |
| keypress → paint (`damage`, one key to the first bytes back) | 7.5 us | 7.7 us | **1.03** | 8.0 us (1.06) |

p99: starts C 14.4 ms (one outlier; the second C run 5.0 ms) / wolf 7.2
ms; keys C 285 us / wolf 268 us. Both within 2.0; the step is in CI as
an announced advisory (the hosted runner is unpinned). sagitta's own
`perf_latency.c`/`perf_startup.c` drive the editor (`--workspace`,
`--config`, a file) and so cannot measure the port before yw03; the
same two points are measured over the demo by
`tools/perf-demo/measure.py`, the probe answered as the harness's VT
answers it.

**The unit wolf/C ratios** (20 runs each under `taskset -c 0-3`, the
whole process, release tier vs `unit_tests --filter`): `test_input`'s
chunking test (`input_chunking_independence` / `--case chunking`) C
1,019 us, wolf 922 us, **0.91**; `test_render`'s full repaint
(`render_resize_repaint_is_deterministic` / `--case resize_repaint`) C
1,052 us, wolf 1,261 us, **1.20**.

**Sizes.** `Cell` is 13 ints = 104 bytes against C's 20 (5.2×: wolf has
no `u8`/`u16` fields in a struct, D-idiom §1; the eight inline bytes ride
in two ints). `Key` is 7 ints plus the reused `List[byte]` text (C: see
the sagitta `Key`). Nothing in campaign 01 allocates per keystroke after
warm-up but `Key.text`, kept as one reused list (the prediction held).

**`unsafe` census**: one block in the repository, yw00's
`unicode.width.ambiguous_wide`; yw01 adds none.

**The test runs**: `tools/check-test --native` every suite green (19
files); `wolf test src` on the checked machine 19 passed, 0 failed, 9.5
s — with the six invalid-cell scenarios and the bug-report scenario
SKIPPED LOUDLY there (`os_exe()` under `wolf test` is `wolf` itself, so
a self-spawn would read the wrong program's exit; the native run covers
them). Formatting: `wolf fmt` converges on the second pass over
`src/term_render_test.lu` (the first pass's output is not a fixed
point); the repo is formatted at the head.

## 5. The two witnesses (the terminal gaps)

Both written and run on kasumi before the first PTY golden
(`notes/yw01-evidence/witness/`).

**W1 — the mode bits.** `os_term_set_mode`'s mode int reaches
`ICANON`/`ECHO`/`ISIG`/`IXON`/`IEXTEN`/`VMIN`/`VTIME` and leaves every
other termios field as found (`[os.term.mode]`), so `ICRNL`, `OPOST`,
`ISTRIP`, `BRKINT`, `PARMRK`, `INPCK` and the `CS8` set are unreachable.
Measured under a PTY (`run.txt`): the master writes CR and C yew reads
**13** (CR, `ICRNL` cleared) while the port reads **10** (LF); the child
writes one LF and C yew puts **0a** on the wire (`OPOST` cleared) while
the port puts **0d0a** (CRLF). Both prediction clauses HIT. **Not a yw01
blocker:** no campaign-01 golden sends CR as input nor emits a bare LF in
paint output (the renderer is pure CSI/UTF-8, the quit key is `q`, the
input cases press `ctrl+a`), so the divergence does not reach a
campaign-01 golden; it bites yw03 (Enter in the editor). A STOP by the
contract's letter (a bit the mode int cannot clear), filed; never worked
around with a dumber terminal.

**W2 — the timed multi-descriptor wait** (`wait-fds.md`). `os_signal_wait_fd`
takes one fd and no deadline; there is no wait over the tty + signals +
job pipes with a timer, so the editor's loop cannot be written as sagitta
writes it (witness by construction). Interim (#93 R2): `VTIME` polling
(`Mode.time = 1`, 100 ms), which rounds the 25 ms lone-ESC deadline to
100 ms in the `nokitty` profile only — a documented timing, never byte,
divergence. Not a yw01 blocker (the cases settle on quiet periods and
press `ctrl+a`, not a lone ESC). Filed as `os_signal_wait_fds` (#795).

## Issues to file (listed, not filed by the lane; track rule 4)

- **wolf-lang** — `[os.term.mode]` **widening** (W1, `run.txt`,
  `witness/enter/`, `witness/opost/`): `os_term_set_mode`'s mode int
  cannot clear `ICRNL`, `OPOST` or `ISTRIP`, which an editor's raw mode
  needs (sagitta `src/term/tty.c:521-543`). Measured under a PTY: with
  the port's raw mode a carriage return read is LF 0x0A, not CR 0x0D
  (Enter = Ctrl-J), and a written LF reaches the wire as CRLF, not LF.
  Proposed: three more mode bits — `CR_NL` (ICRNL), `OUTPUT_POST`
  (OPOST/ONLCR), `STRIP8` (ISTRIP) — or an editor-raw flag that clears
  the `cfmakeraw(3)` set. Needed in full by yw03 (Enter); yw01 ships
  without it because campaign 01 does not press Enter.
- **wolf-lang** — `os_signal_wait_fds(fds, set, deadline_ms)` (W2,
  `wait-fds.md`): the widening of `os_signal_wait_fd` to several
  descriptors and a deadline, ruling #93 R2 = A, s248/0.2.34. Already
  filed as **wolf-lang#795** by the orchestrator at yw00; yw01 confirms
  the shape and the VTIME interim.
- The first is the same `[os.term.mode]` surface yw00's G1 names;
  **wolf-lang#794** (restore at exit, #93 R1) is the sibling and stands.

- **wolf-lang** — **the release tier refuses a closure made in one
  object and called in another** ("cannot compile this yet — a vtable
  slot `@main.cls0` outside this object's subset"): an entry file's
  closure passed to a module's function (witness `e`: `main.lu` passes
  `fn(k: str) lookup(k)` to `lib.tier`, red on `--release`, green on the
  native tier and in a single file), and the twin where the inliner
  moves the closure's making across the partition (the demo's
  `term.render_new_env` — one line, inlined into `main` — refused as
  `@term.render_new_env.cls0`; `--codegen-report` lists the slot under
  `fn main`'s calls). The port now passes the environment as a VALUE
  (`term.Env`) and no fn value crosses a module boundary; every
  lookup-taking API of sagitta's (`getenv` injected) is `Env` in the
  port. Witness programs: the lane's `~/lanes/yw01/cls/{a..g}` on
  kasumi, to be committed to `notes/yw01-evidence/witness/closure/` if
  the maintainer wants them in the issue.
- **wolf-lang** — **a module-level function used as a function value is
  refused once its module has more than one file** (G19, "a vtable slot
  `@term.env_getv.fv` outside this object's subset"; yew `7acaa89` red
  by name, the closure form green on the native tier). Subsumed by the
  `Env` change in the port; stands as a finding.
- **wolf-lang** — **`clock_ms()` on the release tier in a multi-module
  program**: `wolf build --release` of the demo answered "calls outside
  the resolved surface @1638..1648", the span being `clock_ms()` inside
  `fn now_ms() -> int`; `time_now_ms()` in the same place builds. A
  ledger row to name.
- **wolf-lang** — **`wolf fmt` is not idempotent** on
  `src/term_render_test.lu` at 0.2.33: the first pass's output changes
  again on the second, which converges. `tools/check-fmt` would fail a
  once-formatted file.
- **wolf-lang** — **`os_exe()` under `wolf test` is `wolf`**: a test that
  re-executes itself (sagitta's child-role tests) spawns the compiler on
  the checked machine. The port's tests hand-shake first (`--self-check`
  exits 7) and skip loudly; a `wolf test` facility for child roles (or
  `--nocapture`, which 0.2.33's `wolf test` does not take) would let them
  run there.
- **sagitta** (the maintainer's) — `tests/pty/registry.c` assigns no
  campaign-01 case the `nosync` profile; the contract's "four profiles"
  counts three at `9ace98c2`.

## Done-when

- [x] the pin bump with the prediction (`bf12b30`), verified clean
      against campaign 00 under 0.2.33 (fmt, tables, 11 unit files green)
- [x] the two witnesses written and run before any golden, with bytes
      and issue texts (`bb1bbbd`; both mode-bit predictions HIT)
- [x] yw02's contract drafted (`4997881`)
- [x] `term.tty` with its I/O surface and the restore guarantee (interim
      B, the guard sibling); `term.input`; `term.grid`/`term.render`;
      `osc52`; `demo_paint`; the driver — each with its tests, green on
      the checked machine and natively
- [x] every campaign-01 PTY case green by name against the port's demo
      (§4); `version` and `help` green; `tools/goldens-selftest` red on
      the plants; the restore proven by `restore_quit`, `restore_crash`
      and `restore_suspend` (and `_bus`, `_abrt`)
- [x] the 2× ratios recorded on kasumi under `taskset -c 0-3` beside C
      yew's from the same run (1.51 / 1.03); the CI step in place
      (advisory on the hosted runner); the unit ratios (0.91 / 1.20)
- [x] `docs/MAP.md` §4–§5 updated (the mode-bit gap, the closure gaps,
      the `Env` idiom, the root-level test layout)
- [ ] CI green; PR open with the five sections; the plant seen red;
      `lane-audit.sh yew yw01 <PR>` clean but for the final run

