# yw04-prompt: s57_25_help_negative's keys by hand, the raw output after each.
# usage: s5725.py BINARY WORKDIR
import os, pty, sys, time, select, signal, fcntl, termios, struct, re
binary, work = sys.argv[1], sys.argv[2]
os.makedirs(work + "/bin", exist_ok=True)
open(work + "/bin/usage", "w").write("#!/bin/sh\necho 'usage: usage [-abc] file ...'\n")
os.chmod(work + "/bin/usage", 0o755)
open(work + "/notes.txt", "w").write("notes\n")
open(work + "/help.txt", "w").write("help fixture\n")
env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", YEW_TTY_PROBE="0",
           LANG="C.UTF-8", LC_ALL="C.UTF-8", PATH=work + "/bin:" + os.environ["PATH"])
pid, fd = pty.fork()
if pid == 0:
    os.chdir(work)
    os.execve(binary, [binary, "help.txt"], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
def drain(t, quiet=0.15):
    out = b""; end = time.time() + t; last = time.time()
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.005)
        if r:
            try:
                b = os.read(fd, 65536)
            except OSError:
                break
            if not b:
                break
            out += b; last = time.time()
        elif out and time.time() - last > quiet:
            break
    return out
def show(tag, b):
    s = b.decode("utf-8", "replace")
    s = re.sub(r"\x1b\[[0-9;:?<>=]*[A-Za-z~]", lambda m: "" if m.group(0)[-1] in "m" else "{" + m.group(0)[2:] + "}", s)
    s = s.replace("\x1b", "^[").replace("\r", "").replace("\n", "|")
    print(f"== {tag}: {len(b)} bytes: {s[:700]}")
drain(2.0)
for tag, k, wait in [(":", b":", 1.0), ("!usage no", b"!usage no", 1.0), ("tab1", b"\t", 1.5), ("idle", b"", 1.0), ("tab2", b"\t", 1.5)]:
    if k:
        os.write(fd, k)
    show(tag, drain(wait, 0.3))
os.write(fd, b"\x1b\x1b[27u:q!\r"); time.sleep(0.5)
try:
    os.kill(pid, signal.SIGKILL)
except ProcessLookupError:
    pass
os.waitpid(pid, 0)
