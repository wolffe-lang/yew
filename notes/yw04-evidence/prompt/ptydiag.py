# yw04-prompt: per-key response at a real window size: bytes and time until
# the output goes quiet (or 0.5 s). usage: ptydiag.py BINARY FILE ROWSxCOLS
import os, pty, sys, time, select, signal, fcntl, termios, struct
binary, path, size = sys.argv[1], sys.argv[2], sys.argv[3]
r, c = (int(x) for x in size.split("x"))
env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", YEW_TTY_PROBE="1",
           YEW_PROBE_TIMEOUT_MS="500", LANG="C.UTF-8", LC_ALL="C.UTF-8")
pid, fd = pty.fork()
if pid == 0:
    os.execve(binary, [binary, path], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", r, c, 0, 0))
def drain(t, quiet=0.02):
    got = 0; end = time.time() + t; last = time.time()
    while time.time() < end:
        rr, _, _ = select.select([fd], [], [], 0.002)
        if rr:
            try:
                b = os.read(fd, 65536)
            except OSError:
                return got, "eof"
            if not b:
                return got, "eof"
            got += len(b); last = time.time()
        elif got and time.time() - last > quiet:
            return got, "quiet"
    return got, "timeout"
def rss():
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except OSError:
        pass
    return -1
t0 = time.time(); print("startup", drain(3.0), round(time.time() - t0, 3), "rss", rss())
for k in [b":", b"f", b"\x7f", b"f", b"\x7f", b"a", b"b"]:
    t0 = time.time(); g = drain(0.0)
    os.write(fd, k)
    res = drain(2.0)
    print(repr(k), res, round(time.time() - t0, 3), "rss", rss())
os.write(fd, b"\x1b\x1b[27u:q!\r")
time.sleep(1)
wp, st = os.waitpid(pid, os.WNOHANG)
if wp != pid:
    os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0); print("killed")
else:
    print("exit", st)
