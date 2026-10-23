#!/usr/bin/env python3
"""yw05 (lane): a black-box driver of the job stream's lost frame.

Replays sagitta's perf_jobstream shape against an editor binary (24x80, a
200-line fixture, `:!yes ... | head -c N`, then Up/Down alternately, each
waiting for a synchronized-update frame, 2 s each) and, at the first key
that reaches no frame, keeps watching: how long until a frame comes (a
stall) or none (a hang), what the editor's process and its children are
doing (/proc), and whether one more key wakes it. Inside ctr only.

    js-driver.py BINARY RUNS [BYTES] OUTDIR
"""
import fcntl
import os
import pty
import select
import struct
import sys
import tempfile
import termios
import time

BIN = sys.argv[1]
RUNS = int(sys.argv[2])
BYTES = int(sys.argv[3]) if len(sys.argv) > 4 else 52428800
OUT = sys.argv[-1]
os.makedirs(OUT, exist_ok=True)


class Pty:
    def __init__(self, binary, path, state):
        pid, fd = pty.fork()
        if pid == 0:
            fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
            env = dict(os.environ)
            env.update({
                "TERM": "xterm-256color", "COLORTERM": "truecolor",
                "YEW_COLORS": "truecolor", "YEW_TTY_PROBE": "1",
                "YEW_PROBE_TIMEOUT_MS": "500", "YEW_ESC_TIMEOUT_MS": "25",
                "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
                "XDG_STATE_HOME": state, "YEW_LOG": "/dev/null",
            })
            os.execve(binary, [binary, path], env)
        self.pid, self.fd = pid, fd
        self.frames = 0
        self.in_sync = False
        self.tail = b""
        self.log = bytearray()
        self.replied = set()

    def pump(self, timeout):
        r, _, _ = select.select([self.fd], [], [], max(0.0, timeout))
        if not r:
            return False
        try:
            data = os.read(self.fd, 65536)
        except OSError:
            return None
        if not data:
            return None
        self.log += data
        if len(self.log) > 1 << 20:
            del self.log[: len(self.log) - (1 << 20)]
        replies = b""
        for b in data:
            self.tail = (self.tail + bytes([b]))[-16:]
            t = self.tail
            if "sync" not in self.replied and t.endswith(b"\x1b[?2026$p"):
                self.replied.add("sync"); replies += b"\x1b[?2026;2$y"
            if "da" not in self.replied and t.endswith(b"\x1b[c"):
                self.replied.add("da"); replies += b"\x1b[?62;22c"
            if t.endswith(b"\x1b[?2026h"):
                self.in_sync = True
            if self.frames == 0 and not self.in_sync and t.endswith(b"\x1b[?25h"):
                self.frames += 1
            if t.endswith(b"\x1b[?2026l"):
                self.frames += 1
                self.in_sync = False
        if replies:
            os.write(self.fd, replies)
        return True

    def wait_frame(self, after, secs):
        end = time.monotonic() + secs
        while self.frames <= after:
            left = end - time.monotonic()
            if left <= 0:
                return False
            if self.pump(left) is None:
                return False
        return True


def proc_view(pid):
    lines = []
    def stat(p):
        try:
            with open(f"/proc/{p}/stat") as f:
                s = f.read()
            comm = s[s.index("(") + 1 : s.rindex(")")]
            rest = s[s.rindex(")") + 2 :].split()
            return comm, rest[0], int(rest[1])
        except OSError:
            return None
    def wchan(p):
        try:
            with open(f"/proc/{p}/wchan") as f:
                return f.read().strip()
        except OSError:
            return "?"
    def syscall(p):
        try:
            with open(f"/proc/{p}/syscall") as f:
                return f.read().strip()
        except OSError:
            return "?"
    s = stat(pid)
    lines.append(f"editor {pid}: {s} wchan={wchan(pid)} syscall={syscall(pid)}")
    try:
        for t in sorted(os.listdir(f"/proc/{pid}/task")):
            ts = stat(f"{pid}/task/{t}")
            lines.append(f"  task {t}: {ts} wchan={wchan(f'{pid}/task/{t}')}")
    except OSError:
        pass
    try:
        for fd in sorted(os.listdir(f"/proc/{pid}/fd"), key=int):
            try:
                lines.append(f"  fd {fd} -> {os.readlink(f'/proc/{pid}/fd/{fd}')}")
            except OSError:
                pass
    except OSError:
        pass
    kids = []
    for p in os.listdir("/proc"):
        if p.isdigit():
            st = stat(p)
            if st and st[2] == pid:
                kids.append((p, st))
    lines.append(f"  children: {kids}")
    for kp, _ in kids:
        for gp in os.listdir("/proc"):
            if gp.isdigit():
                st = stat(gp)
                if st and st[2] == int(kp):
                    lines.append(f"    grandchild of {kp}: {gp} {st} wchan={wchan(gp)} syscall={syscall(gp)}")
    # The poll's own array (struct pollfd: int fd, short events, short revents).
    try:
        sc = syscall(pid).split()
        if sc and sc[0] == "7":
            addr, nfds = int(sc[1], 16), int(sc[2], 16)
            with open(f"/proc/{pid}/mem", "rb") as m:
                m.seek(addr)
                raw = m.read(8 * nfds)
            pf = [struct.unpack("ihh", raw[8 * k : 8 * k + 8]) for k in range(nfds)]
            lines.append(f"  poll fds (fd, events, revents): {pf}")
    except Exception as e:
        lines.append(f"  poll fds: unreadable ({e})")
    # What the terminal holds unread (FIONREAD on the editor's own slave).
    try:
        fd = os.open(f"/proc/{pid}/fd/0", os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY)
        n = struct.unpack("i", fcntl.ioctl(fd, termios.FIONREAD, b"\0\0\0\0"))[0]
        os.close(fd)
        lines.append(f"  the terminal's unread input: {n} bytes")
    except Exception as e:
        lines.append(f"  the terminal's unread input: unknown ({e})")
    for fdn in ("10", "12", "13", "14"):
        try:
            with open(f"/proc/{pid}/fdinfo/{fdn}") as f:
                lines.append(f"  fdinfo {fdn}: " + " ".join(f.read().split()))
        except OSError:
            pass
    return "\n".join(lines)


def one(run):
    root = tempfile.mkdtemp(prefix="yw05-js-")
    path = os.path.join(root, "fixture.txt")
    state = os.path.join(root, "state")
    os.mkdir(state, 0o700)
    with open(path, "w") as f:
        f.write("streaming fixture line\n" * 200)
    p = Pty(BIN, path, state)
    if not p.wait_frame(0, 5):
        return f"run {run}: no first paint"
    cmd = (":!yes 0123456789abcdefghijklmnopqrstuvwxyz"
           f"0123456789abcdefghijklmn | head -c {BYTES}\r").encode()
    os.write(p.fd, cmd)
    t0 = time.monotonic()
    result = f"run {run}: ok"
    for i in range(2000):
        key = b"\x1b[B" if i & 1 else b"\x1b[A"
        before = p.frames
        os.write(p.fd, key)
        if p.wait_frame(before, 2.0):
            continue
        at = time.monotonic() - t0
        view = proc_view(p.pid)
        waited = p.wait_frame(before, 15.0)
        late = time.monotonic() - t0 - at
        view2 = proc_view(p.pid)
        f2 = p.frames
        os.write(p.fd, b"\x1b[B")
        woke = p.wait_frame(f2, 3.0)
        with open(os.path.join(OUT, f"run{run}-key{i + 1}.txt"), "w") as f:
            f.write(f"key {i + 1} ({key!r}) reached no frame in 2 s at {at:.3f}s; frames={before}\n")
            f.write(f"then: {'a frame after ' + format(late + 2.0, '.3f') + ' s' if waited else 'no frame in 15 s more'}\n")
            f.write(f"one more Down: {'woke (frame)' if woke else 'no frame in 3 s'}\n")
            f.write("--- /proc at the timeout\n" + view + "\n")
            f.write("--- /proc 15 s later\n" + view2 + "\n")
            f.write("--- the last 4096 bytes of output\n")
            f.write(repr(bytes(p.log[-4096:])) + "\n")
        result = (f"run {run}: key {i + 1} lost at {at:.3f}s; "
                  f"{'frame after %.3f s' % (late + 2.0) if waited else 'HANG (15 s)'}; "
                  f"next key {'woke' if woke else 'no frame'}")
        break
    os.write(p.fd, b"\x1b[27u:q!\r")
    end = time.monotonic() + 5
    while time.monotonic() < end:
        if p.pump(0.2) is None:
            break
    try:
        os.kill(p.pid, 9)
    except OSError:
        pass
    try:
        os.waitpid(p.pid, 0)
    except OSError:
        pass
    os.close(p.fd)
    return result


fails = 0
for r in range(1, RUNS + 1):
    line = one(r)
    if "lost" in line or "no first" in line:
        fails += 1
        print(line, flush=True)
    if fails >= 3:
        break
print(f"js-driver: {r} runs, {fails} lost", flush=True)
