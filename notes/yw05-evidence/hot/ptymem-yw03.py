# yw03 scratch: resident memory of an editor across N keystrokes, in a
# PTY. Run inside the container (it SIGKILLs a child that will not quit).
import os, pty, sys, time, select, signal
binary, path, n, phase = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", YEW_TTY_PROBE="1",
           YEW_PROBE_TIMEOUT_MS="500", LANG="C.UTF-8", LC_ALL="C.UTF-8")
pid, fd = pty.fork()
if pid == 0:
    os.execve(binary, [binary, path], env)
def drain(t):
    got = 0
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.002)
        if not r:
            if got:
                return got
            continue
        try:
            b = os.read(fd, 65536)
        except OSError:
            return -1
        if not b:
            return -1
        got += len(b)
    return got
def rss():
    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    return -1
drain(1.0)
time.sleep(0.6)
drain(0.2)
if phase == "type":
    os.write(fd, b"i")
    drain(0.5)
before = rss()
marks = []
for i in range(n):
    if phase == "type":
        k = b"a" if i % 2 else b"b"
    elif phase == "arrows":
        k = b"\x1b[B" if (i // 500) % 2 == 0 else b"\x1b[A"
    else:
        k = b"\x1b[C" if (i // 40) % 2 == 0 else b"\x1b[D"
    os.write(fd, k)
    drain(0.5)
    if (i + 1) % (n // 4) == 0:
        marks.append(rss())
after = rss()
print(f"{os.path.basename(binary)} {phase}: n={n} rss_kb before={before} after={after} delta={after-before} kb ({(after-before)*1024/n:.1f} B/key) quarters={marks}")
os.write(fd, b"\x1b[27u:q!\r")
end = time.time() + 3
while time.time() < end:
    wp, st = os.waitpid(pid, os.WNOHANG)
    if wp == pid:
        break
    drain(0.05)
else:
    os.kill(pid, signal.SIGKILL)
    os.waitpid(pid, 0)
    print("killed")
