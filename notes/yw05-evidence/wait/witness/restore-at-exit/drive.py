#!/usr/bin/env python3
"""yw05-wait: drive restore-at-exit's witness under a pty, one death a run.

Usage: drive.py BINARY. For each case, fork the binary on a fresh pty, wait
for READY, deliver the death (an outside signal, or a byte that picks an
exit path), read everything it writes until EOF, reap it, and report
whether `RESTORED` reached the terminal and whether ICANON is back on.
"""
import os, pty, select, signal, sys, termios, time

def run(binary, kind, arg):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv(binary, [binary])
    buf = b""
    deadline = time.time() + 10
    while b"READY" not in buf and time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                buf += os.read(fd, 4096)
            except OSError:
                break
    time.sleep(0.1)
    if kind == "signal":
        os.kill(pid, arg)
    else:
        os.write(fd, arg)
    out = b""
    deadline = time.time() + 5
    while time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                d = os.read(fd, 4096)
            except OSError:
                break
            if not d:
                break
            out += d
        else:
            try:
                p, st = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                p = pid
            if p == pid:
                break
    try:
        lflag = termios.tcgetattr(fd)[3]
        canon = bool(lflag & termios.ICANON)
    except termios.error as e:
        canon = "unreadable(%s)" % e
    try:
        _, st = os.waitpid(pid, 0)
    except ChildProcessError:
        st = None
    os.close(fd)
    how = ("signal %d" % os.WTERMSIG(st)) if st is not None and os.WIFSIGNALED(st) else ("exit %s" % (os.WEXITSTATUS(st) if st is not None else "?"))
    return how, b"RESTORED" in out, canon, out

cases = [
    ("outside SIGSEGV", "signal", signal.SIGSEGV),
    ("outside SIGBUS", "signal", signal.SIGBUS),
    ("outside SIGABRT (not listened)", "signal", signal.SIGABRT),
    ("outside SIGTERM (not listened)", "signal", signal.SIGTERM),
    ("outside SIGKILL", "signal", signal.SIGKILL),
    ("a trap (index past the end)", "byte", b"t"),
    ("os_exit(3)", "byte", b"q"),
    ("os_exit_signal(TERMINATE)", "byte", b"e"),
    ("a return from main", "byte", b"r"),
]
for name, kind, arg in cases:
    how, restored, canon, out = run(sys.argv[1], kind, arg)
    print("restore-at-exit: %-32s -> %-10s RESTORED written: %-5s ICANON back: %s" % (name, how, restored, canon))
