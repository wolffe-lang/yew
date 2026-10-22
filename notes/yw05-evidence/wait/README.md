# yw05 — the `wait` fork's evidence

The loop half of deliverable 1 at wolf 0.2.34: G2 (`os_signal_wait_fds`,
wolf-lang#795), G34 (the mode int's bits 5-7, #802), G1
(`os_term_restore_at_exit`, #794) and yew#28's macOS burst gates. kasumi
(Linux 7.2.8, 16 cpus), every run in `~/lanes/yw05/bin/ctr` on CPUs 4-7.

- `witness/restore-at-exit/` — which deaths the runtime's restore covers
  (`main.lu`, `drive.py`, `run.txt`, native and release): a trap,
  `os_exit`, `os_exit_signal` and a return from `main` restore; an outside
  `SIGSEGV`, `SIGBUS`, `SIGKILL`, and an unlistened `SIGABRT` or
  `SIGTERM` restore nothing. So yw01's guard sibling stays for the
  harness's outside `SEGV`/`BUS`/`KILL`, and the editor listens for
  `ABORT` (C's handler table, `tty.c:381-384`) to restore before that
  death in process.
- `witness/raw-bits/` — under a pty, the port's `rawios` (352) reads a
  typed CR as 13 and writes a LF alone; 0.2.33's raw mode (256, no bit 5
  or 6) reads it as 10 (the `ICRNL` red) and writes CRLF.
- `plant-raw-cr.txt` — `RAW_CR` planted off with the LF interim gone:
  campaign 03 stays 62/62 (the modern profile sends Enter as CSI u), the
  live-editor kill9 lane goes RED (its driver types `:ed.quit_force\r`
  raw: "feeder failed at quit hangup"); the fork's own editor: GREEN but
  G3.
- `percase.py`, `percase-term-input.log` — `term_input_test` falls back
  to `[native]` under `wolf test` (G29); per case on the checked machine:
  17 cases, 10 pass, 7 over the step budget, 0 fail (the two OSC 52 cases
  take the log path and rest on the native run).
- `sweeps/` — campaign 01 (18), 03 (62) and 04 (104) by name on both
  tiers, at `85b9a61` and at the final head `a137225` (`a137225-*`, built
  2026-10-22T02:46Z, release `1de838134f30`): 18/18, 62/62 and 83/104 on
  both tiers (the 21 red are the job half's and the clipboard writer's,
  owned by the `jobs` and `sync` forks); the burst pair 20× on the release
  tier, 20/20 and 20/20; `check-test --native` exit 0 (89 files) and the
  checked lane "89 passed; 0 failed" (`a137225-final-f1.txt`).
- `sweeps/dispatch-39713224005-macos-oracle.txt` — the fork's
  `workflow_dispatch` (run 39713224005, every leg) at `a137225`: the macOS
  oracle gates campaign 03's 60 by name, the burst pair among them (yew#28
  re-gated), and campaign 04's 83. That run is red on one step only: the
  macOS PORT leg's `wolf test` (nightly-only since tl30), where
  `edit_shctx_test` traps — `t_shctx_cwd_tilde_user` reads the current
  user from `/etc/passwd` (G37), and macOS keeps its users in Directory
  Services (uid 501 has no row there): yw04's test, never run on a macOS
  port leg before this dispatch, not this fork's change.
- `torture-live.txt` — `tools/torture-live` over the fork's release editor
  (GREEN but G3's determinism order, which the `sync` fork retires) and
  over the RAW_CR plant (RED: "feeder failed at quit hangup").
