#!/usr/bin/python3
"""ptyrelay.py LOG BIN ARGS...: run BIN on a fresh pty, relaying the caller's
terminal both ways byte for byte, and log every chunk with a timestamp
(ms since start): `O <ms> <repr>` for the editor's output, `I <ms> <repr>`
for input. The window size is copied from the caller's terminal."""
import fcntl, os, pty, select, struct, sys, termios, time, tty
log = open(sys.argv[1], "w", buffering=1)
argv = sys.argv[2:]
t0 = time.monotonic()
log.write(f"T0 {time.time():.6f}\n")
def ms(): return int((time.monotonic() - t0) * 1000)
ws = fcntl.ioctl(0, termios.TIOCGWINSZ, b"\0" * 8)
pid, fd = pty.fork()
if pid == 0:
    os.execv(argv[0], argv)
fcntl.ioctl(fd, termios.TIOCSWINSZ, ws)
try:
    old = termios.tcgetattr(0)
    tty.setraw(0)
except termios.error:
    old = None
try:
    while True:
        r, _, _ = select.select([0, fd], [], [])
        if fd in r:
            try:
                b = os.read(fd, 65536)
            except OSError:
                break
            if not b:
                break
            log.write(f"O {ms()} {b!r}\n")
            os.write(1, b)
        if 0 in r:
            b = os.read(0, 65536)
            if not b:
                break
            log.write(f"I {ms()} {b!r}\n")
            os.write(fd, b)
finally:
    if old is not None:
        termios.tcsetattr(0, termios.TCSANOW, old)
    _, st = os.waitpid(pid, 0)
    log.write(f"X {ms()} status={st}\n")
    sys.exit(os.waitstatus_to_exitcode(st) if hasattr(os, "waitstatus_to_exitcode") else 0)
