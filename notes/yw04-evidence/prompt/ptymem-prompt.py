# yw04-prompt: resident memory of an editor across N keystrokes IN THE `:`
# PROMPT, in a PTY (yw03's ptymem.py, the prompt's phases). Run inside the
# container (it SIGKILLs a child that will not quit).
#   phase "menu":  `f` then Backspace, N/2 times: the live table rebuilt
#                  every keystroke (the filter, the menu rows, the ghost,
#                  the hint)
#   phase "type":  N printable keys into one long line: the prompt's
#                  TextBuf and its draw
# usage: ptymem-prompt.py BINARY FILE N PHASE
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
os.write(fd, b":")
drain(0.5)
before = rss()
marks = []
for i in range(n):
    if phase == "menu":
        k = b"f" if i % 2 == 0 else b"\x7f"
    else:
        k = b"a" if i % 2 else b"b"
    os.write(fd, k)
    drain(0.5)
    if (i + 1) % (n // 4) == 0:
        marks.append(rss())
after = rss()
print(f"{os.path.basename(binary)} prompt-{phase}: n={n} rss_kb before={before} after={after} delta={after-before} kb ({(after-before)*1024/n:.1f} B/key) quarters={marks}")
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
