#!/usr/bin/env python3
"""measure.py -- cold start -> first paint and keypress -> paint for a
demo_paint binary (C yew's or the port's), driven in a PTY the way
sagitta's harness drives it.

  measure.py --bin PATH [--label L] [--starts N] [--keys K] [--state DIR]

The child gets the pinned environment of tests/pty/harness.c (TERM,
YEW_TTY_PROBE=1, the 500 ms probe deadline, the 25 ms escape deadline,
a scratch XDG_STATE_HOME); the driver answers the three probe queries
the way the harness's VT does in the modern profile (kitty 0, sync
supported, DA) so the demo paints as it does under the goldens.

Cold start: from the fork to the end of the first synchronized frame
(ESC [ ? 2026 l) of the `basic` scene.  Keypress -> paint: in the
`damage` scene, from the write of one key to the first bytes the demo
answers with (the damage frame is one small raw write, below the
renderer's 32-byte envelope gate, so there is no frame marker to wait
for; the same rule measures both binaries).  Prints one line per
metric with the p50 and p99 in nanoseconds; exits 2 on a harness fault.
"""
import argparse
import fcntl
import os
import select
import signal
import struct
import sys
import termios
import time

QUERIES = b"\x1b[?u\x1b[?2026$p\x1b[c"
REPLY = b"\x1b[?0u\x1b[?2026;2$y\x1b[?62;22c"
FRAME_END = b"\x1b[?2026l"
ROWS, COLS = 24, 80


def child_env(state):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("YEW_") and k not in ("NO_COLOR", "COLORTERM")}
    env.update({
        "TERM": "xterm-256color",
        "COLORTERM": "truecolor",
        "LC_ALL": "C.UTF-8",
        "HOME": state,
        "XDG_STATE_HOME": state,
        "YEW_TTY_PROBE": "1",
        "YEW_PROBE_TIMEOUT_MS": "500",
        "YEW_ESC_TIMEOUT_MS": "25",
        "YEW_LOG_LEVEL": "error",
    })
    return env


def spawn(binary, scene, env):
    master, slave = os.openpty()
    winsz = struct.pack("HHHH", ROWS, COLS, 0, 0)
    fcntl.ioctl(slave, termios.TIOCSWINSZ, winsz)
    started = time.monotonic_ns()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(master)
            os.setsid()
            fcntl.ioctl(slave, termios.TIOCSCTTY, 0)
            os.dup2(slave, 0)
            os.dup2(slave, 1)
            os.dup2(slave, 2)
            if slave > 2:
                os.close(slave)
            os.execve(binary, [binary, "--scene", scene], env)
        finally:
            os._exit(126)
    os.close(slave)
    return master, pid, started


def read_until(master, needle, deadline_ns, buf):
    """Append master's output to buf until needle appears; answer the
    probe queries the moment they are complete.  Returns the time the
    needle's last byte was read, or None on the deadline."""
    answered = QUERIES in buf
    while True:
        at = buf.find(needle)
        if at >= 0:
            return time.monotonic_ns()
        now = time.monotonic_ns()
        if now >= deadline_ns:
            return None
        r, _, _ = select.select([master], [], [], (deadline_ns - now) / 1e9)
        if not r:
            return None
        try:
            chunk = os.read(master, 65536)
        except OSError:
            return None
        if not chunk:
            return None
        buf += chunk
        if not answered and QUERIES in buf:
            os.write(master, REPLY)
            answered = True


def stop(master, pid):
    try:
        os.write(master, b"q")
    except OSError:
        pass
    deadline = time.monotonic_ns() + 2_000_000_000
    while time.monotonic_ns() < deadline:
        done, status = os.waitpid(pid, os.WNOHANG)
        if done == pid:
            os.close(master)
            return status
        time.sleep(0.005)
    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)
    os.close(master)
    return -1


def one_start(binary, env):
    master, pid, started = spawn(binary, "basic", env)
    buf = bytearray()
    painted = read_until(master, FRAME_END, started + 3_000_000_000, buf)
    stop(master, pid)
    if painted is None:
        raise RuntimeError("no first frame within 3 s (got %d bytes)" % len(buf))
    return painted - started


def keypresses(binary, env, keys):
    master, pid, started = spawn(binary, "damage", env)
    buf = bytearray()
    # The damage scene runs without the synchronized envelope; its first
    # paint ends with the cursor-show that closes an unsynchronized frame.
    if read_until(master, b"\x1b[?25h", started + 3_000_000_000, buf) is None:
        stop(master, pid)
        raise RuntimeError("damage scene did not paint")
    time.sleep(0.05)
    samples = []
    for _ in range(keys):
        # Drain anything pending so the next read is the answer to this key.
        while select.select([master], [], [], 0)[0]:
            os.read(master, 65536)
        t0 = time.monotonic_ns()
        os.write(master, b"a")
        r, _, _ = select.select([master], [], [], 1.0)
        if not r:
            stop(master, pid)
            raise RuntimeError("no paint within 1 s of a key")
        os.read(master, 65536)
        samples.append(time.monotonic_ns() - t0)
    stop(master, pid)
    return samples


def pct(samples, p):
    s = sorted(samples)
    return s[min(len(s) - 1, int(round((len(s) - 1) * p)))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--label", default="demo")
    ap.add_argument("--starts", type=int, default=20)
    ap.add_argument("--keys", type=int, default=300)
    ap.add_argument("--state", required=True)
    a = ap.parse_args()
    os.makedirs(a.state, exist_ok=True)
    env = child_env(a.state)
    try:
        starts = [one_start(a.bin, env) for _ in range(a.starts)]
        keys = keypresses(a.bin, env, a.keys)
    except RuntimeError as e:
        print("measure: %s: %s" % (a.label, e), file=sys.stderr)
        return 2
    print("startup.first_paint.%s p50_ns=%d p99_ns=%d n=%d"
          % (a.label, pct(starts, 0.5), pct(starts, 0.99), len(starts)))
    print("keypress_to_paint.%s p50_ns=%d p99_ns=%d n=%d"
          % (a.label, pct(keys, 0.5), pct(keys, 0.99), len(keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
