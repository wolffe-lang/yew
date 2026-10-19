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

- **`term.tty`** — raw mode, the restore guarantee (interim B), the
  alternate screen, window size, the capability probe, truecolor: PENDING.
- **`term.input`** — the escape state machine, kitty, paste, mouse,
  focus: PENDING.
- **`term.grid` / `term.render`** — the double buffer, damage, wide
  glyphs, the diff, colour tiers, `osc52`: PENDING.
- **`demo_paint` + the driver** (`main`, `args`, `log`, `xdg`,
  `base64`): PENDING.
- **The gates** — four golden profiles, the 2× CI step, the ratios:
  PENDING.

## 4. What yw01 measured

PENDING. The wolf/C ratios for keypress → paint and cold start, the
`Key`/`Cell` struct sizes and their ratio to C, the `unsafe` census.

## 5. The two witnesses (the terminal gaps)

PENDING — the mode bits (`[os.term.mode]` cannot reach `ICRNL`/`OPOST`/
`ISTRIP`), and the multi-descriptor timed wait (`os_signal_wait_fds`,
G2). Issue texts in §Issues.

## Issues to file (listed, not filed)

PENDING.

## Done-when

- [ ] the pin bump with the prediction (this commit)
- [ ] the two witnesses written before the first golden
- [ ] `term.tty`, the restore guarantee (interim B), `term.input`,
      `term.grid`/`term.render`, `osc52`, `demo_paint`, the driver
- [ ] the four golden profiles green; `tools/goldens-selftest` red on
      the plants; the restore proven
- [ ] the 2× ratios recorded on kasumi under `taskset -c 0-3`
- [ ] `docs/MAP.md` updated; yw02's contract drafted
- [ ] CI green; PR open; `lane-audit.sh yew yw01 <PR>` clean but for the
      final run
