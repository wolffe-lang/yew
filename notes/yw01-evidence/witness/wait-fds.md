# The timed multi-descriptor wait (G2) — witness by construction

sagitta's event loop is one `poll(2)` over the tty, the signal self-pipe
and (from Sprint 19) per-job pipes, with a timer as the timeout: the
25 ms lone-ESC deadline (`src/term/input.c` `YEW_ESC_TIMEOUT_MS`), the
50 ms capability-probe deadline (`src/term/tty.c` `YEW_TTY_PROBE_DEFAULT_MS`),
`tests/pty/demo_paint.c:744-784` (`poll(fds, 2, timeout)` over
`tty.rfd` and `yew_tty_signal_fd`).

**What wolf 0.2.33 has** (`spec/prelude.json` at `85dab5d7`, `[os.signal.wait.fd]`):

    os_signal_wait_fd(fd: int, set: int) -> int ! {io, unsupported}

ONE descriptor and a signal set; it answers the meaning, or 0 when the
descriptor is readable, and **it has no deadline** (the spec says so by
name: "It has no deadline: on a terminal, VMIN and VTIME time the read
that follows"). There is no wait over several descriptors, and no
timeout on the wait of any shape — `net_wait` is the socket reactor and
takes net handles, not fs ones. So the editor's loop, which must wake on
a key, a signal (RESIZE, CONTINUE, a child), **and** a deadline at once,
cannot be written as sagitta writes it: no program can express it.

**Interim (ruling #93 R2 = A, `os_signal_wait_fds`, s248, 0.2.34).**
Until the pin has it, the port times its waits with `VTIME`: a raw
`Mode.time` of 1 (100 ms granularity, `std.term`'s `min`/`time`) makes a
read return after at most 100 ms with no byte, which the loop treats as a
deadline tick. The 25 ms lone-ESC deadline therefore becomes **100 ms in
the `nokitty` profile only** (under `modern`/kitty the ESC timeout is
never armed, s04 §5), a documented *timing* divergence, never a byte
divergence; a golden whose bytes depend on the 25-vs-100 ms difference is
a STOP. The capability probe's 50 ms deadline likewise rounds up to the
VTIME tick, and the harness pins `YEW_PROBE_TIMEOUT_MS=500`, generous
enough that VTIME polling answers inside it.

**Not a yw01 blocker.** Campaign-01's cases wait for the probe to reach
DONE and settle on quiet periods, and the input cases press `ctrl+a`,
not a lone ESC; none asserts bytes that depend on sub-100 ms ESC timing.
The gap is filed (`os_signal_wait_fds`, wolf-lang#795); the port keeps
its one call site (`term.tty`'s wait helper) so the 0.2.34 pin swaps it.
