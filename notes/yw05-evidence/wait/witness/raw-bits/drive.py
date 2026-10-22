#!/usr/bin/env python3
"""yw05-wait: run raw-bits' witness under a pty for each mode int; report
the CR it reads and whether its written LF reached the master as LF or CRLF."""
import os, pty, select, sys, time
def run(binary, mode):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv(binary, [binary, str(mode)])
    buf = b""
    t = time.time() + 10
    while b"READY" not in buf and time.time() < t:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            buf += os.read(fd, 4096)
    time.sleep(0.2)
    os.write(fd, b"\r")
    t = time.time() + 5
    while buf.count(b"|") < 2 and time.time() < t:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                d = os.read(fd, 4096)
            except OSError:
                break
            if not d:
                break
            buf += d
    os.waitpid(pid, 0)
    os.close(fd)
    i = buf.index(b"READY")
    seg = buf[i:]
    lf = "CRLF (OPOST on)" if b"A\r\nB" in seg else ("LF alone (OPOST off)" if b"A\nB" in seg else repr(seg[:12]))
    line = seg.split(b"|")[1].decode(errors="replace")
    print("raw-bits: %-30s written LF reached the master as %-22s %s" % ("mode %d" % mode, lf, line))
for m in (32 + 64 + 256, 256, 64 + 256, 32 + 256):
    run(sys.argv[1], m)
