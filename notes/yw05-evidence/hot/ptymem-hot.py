# yw05-hot (deliverable 6): resident memory of an editor across N keys in a
# PTY, C yew and the port under the same driver. yw03's ptymem.py and
# yw04's ptymem-prompt.py (copied beside this file, unchanged) with three
# changes: the window is set to 24x80 in the child before exec (both of
# theirs left it 0x0), the phases are theirs plus a two-pane session
# (`ctrl+w s` first, in one write), and the bytes the editor writes during the measured
# keys are counted and hashed, so two runs (C and the port, or the port
# before and after a change) can be compared byte for byte.
# Run inside the container (it SIGKILLs a child that will not quit).
#   prompt-menu  `:` then `f`/Backspace, N/2 times (yw04's worst row)
#   prompt-type  `:` then N printable keys into one long line (yw04)
#   type         `i` then N printable keys (yw03)
#   arrows       N line moves, 500 down then 500 up (yw03)
#   lines40      N line moves, 40 down then 40 up (a short file's moves)
#   pane-*       `ctrl+w s`, then the phase after the dash
# usage: ptymem-hot.py BINARY FILE N PHASE
import os, pty, sys, time, select, signal, termios, struct, fcntl, hashlib
binary, path, n, phase = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", YEW_TTY_PROBE="1",
           YEW_PROBE_TIMEOUT_MS="500", LANG="C.UTF-8", LC_ALL="C.UTF-8")
pid, fd = pty.fork()
if pid == 0:
    fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
    os.execve(binary, [binary, path], env)
h = hashlib.sha256()
total = [0]
def drain(t, keep=False):
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
        if keep:
            h.update(b)
            total[0] += len(b)
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
base = phase
if phase.startswith("pane-"):
    # One write: the chord completes in one read, never racing its timeout.
    os.write(fd, b"\x17s")
    drain(0.5)
    base = phase[5:]
if base.startswith("prompt-"):
    os.write(fd, b":")
    drain(0.5)
elif base == "type":
    os.write(fd, b"i")
    drain(0.5)
time.sleep(0.3)
drain(0.2)
before = rss()
marks = []
t0 = time.time()
for i in range(n):
    if base == "prompt-menu":
        k = b"f" if i % 2 == 0 else b"\x7f"
    elif base in ("prompt-type", "type"):
        k = b"a" if i % 2 else b"b"
    elif base == "arrows":
        k = b"\x1b[B" if (i // 500) % 2 == 0 else b"\x1b[A"
    elif base == "lines40":
        k = b"\x1b[B" if (i // 40) % 2 == 0 else b"\x1b[A"
    else:
        k = b"\x1b[C" if (i // 40) % 2 == 0 else b"\x1b[D"
    os.write(fd, k)
    drain(0.5, True)
    if (i + 1) % (n // 4) == 0:
        marks.append(rss())
drain(0.3, True)
dt = time.time() - t0
after = rss()
print(f"{os.path.basename(binary)} {phase}: n={n} rss_kb before={before} after={after} delta={after-before} kb ({(after-before)*1024/n:.1f} B/key) quarters={marks} out={total[0]} B ({total[0]/n:.0f} B/key) out_sha={h.hexdigest()[:16]} {dt/n*1000:.1f} ms/key")
os.write(fd, b"\x1b\x1b[27u:q!\r")
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
