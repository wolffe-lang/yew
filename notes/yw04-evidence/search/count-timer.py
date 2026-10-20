#!/usr/bin/env python3
# yw04-search: how long after `*` does the idle count's `[n/m]` badge reach
# the terminal? s21_search_word_under_cursor settles 60 ms after the key
# (registry.c, "the bounded count is intentionally deferred by one idle
# timer"); C's timer is 16 ms out and its poll(2) wakes for it. Usage
# (in the container, RULES 5): count-timer.py BIN [BIN...]
import os, pty, re, select, sys, time, tempfile

def drain(fd, t):
    out = b""
    end = time.monotonic() + t
    while True:
        left = end - time.monotonic()
        if left <= 0:
            return out
        r, _, _ = select.select([fd], [], [], left)
        if fd in r:
            try:
                b = os.read(fd, 65536)
            except OSError:
                return out
            if not b:
                return out
            out += b

def run(binary, reps=5):
    d = tempfile.mkdtemp()
    path = os.path.join(d, "doc.txt")
    open(path, "w").write("alpha needle one\nbeta two\ngamma needle three\ndelta four\nepsilon five\nzeta needle six\n")
    res = []
    for _ in range(reps):
        pid, fd = pty.fork()
        if pid == 0:
            env = dict(os.environ, TERM="xterm-256color", HOME=d, XDG_CONFIG_HOME=d, XDG_STATE_HOME=d, YEW_LOG="/dev/null")
            os.execve(binary, [binary, path], env)
        drain(fd, 1.0)
        for k in [b"\x1b[C"] * 6:
            os.write(fd, k)
            drain(fd, 0.05)
        t0 = time.monotonic()
        os.write(fd, b"*")
        got = b""
        seen = None
        while time.monotonic() - t0 < 1.0:
            got += drain(fd, 0.005)
            if seen is None and re.search(rb"\[\d+/\d+\+?\]", got):
                seen = (time.monotonic() - t0) * 1000.0
                break
        res.append(seen)
        os.write(fd, b"\x1b:q!\r")
        drain(fd, 0.3)
        try:
            os.kill(pid, 9)
        except ProcessLookupError:
            pass
        os.waitpid(pid, 0)
    return res

for b in sys.argv[1:]:
    r = run(b)
    print("%s: badge after `*` in ms: %s" % (b, ", ".join("none" if x is None else "%.1f" % x for x in r)))
