# yw04: per-key output bytes and RSS of an editor typing in I mode in a PTY
# (yw03's ptymem.py's setup, a short drain); run inside the container.
import os, pty, sys, time, select, signal, termios, struct, fcntl
binary, path, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
pid, fd = pty.fork()
if pid == 0:
    os.environ["TERM"] = "xterm-256color"
    os.execv(binary, [binary, path])
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
def drain(t):
    got = 0
    end = time.time() + t
    while True:
        r, _, _ = select.select([fd], [], [], max(0.0, end - time.time()))
        if not r:
            return got
        try:
            b = os.read(fd, 65536)
        except OSError:
            return got
        got += len(b)
        end = time.time() + t
def rss():
    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    return -1
drain(1.0); time.sleep(0.5); drain(0.2)
os.write(fd, b"i"); drain(0.3)
r0 = rss(); outs = []
for i in range(n):
    os.write(fd, b"a" if i % 2 else b"b")
    outs.append(drain(0.15))
r1 = rss()
print(f"{os.path.basename(binary)}: n={n} out_bytes/key avg={sum(outs)/n:.0f} first={outs[:5]} rss {r0}->{r1} kb ({(r1-r0)*1024/n:.0f} B/key)")
os.write(fd, b"\x1b[27u:q!\r")
end = time.time() + 3
while time.time() < end:
    wp, st = os.waitpid(pid, os.WNOHANG)
    if wp == pid:
        break
    drain(0.05)
else:
    os.kill(pid, signal.SIGKILL); os.waitpid(pid, 0); print("killed")
