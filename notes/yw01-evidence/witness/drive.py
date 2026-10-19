#!/usr/bin/env python3
# drive.py — a PTY driver for the mode-bit witness.
#
#   drive.py enter  BIN      raw, master writes CR, reports the byte BIN read
#   drive.py opost  BIN      raw, BIN writes one LF, reports the bytes on the wire
#
# Opens a pseudo-terminal, forks, and execs BIN with the slave as its
# 0/1/2 after setsid(), exactly as sagitta's harness does (tests/pty/
# harness.c §1) so the child's raw-mode behaviour is observed from the
# master side. No editor, regex, VT or libc source is read: openpty is
# the OS's, os.read/os.write are the driver's.
import os, pty, select, sys, time

def run(mode, binpath):
    pid, master = pty.fork()
    if pid == 0:
        try:
            os.execv(binpath, [binpath, "--enter" if mode == "enter" else "--opost"])
        except Exception:
            os._exit(127)
    if mode == "enter":
        time.sleep(0.2)            # let the child reach its raw read
        os.write(master, b"\x0d")  # a carriage return
    out = b""
    deadline = time.time() + 3.0
    while time.time() < deadline:
        r, _, _ = select.select([master], [], [], 0.2)
        if master in r:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            out += chunk
        try:
            wpid, _ = os.waitpid(pid, os.WNOHANG)
            if wpid == pid and not (select.select([master], [], [], 0)[0]):
                break
        except ChildProcessError:
            break
    try:
        os.close(master)
    except OSError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass
    return out

if __name__ == "__main__":
    mode, binpath = sys.argv[1], sys.argv[2]
    out = run(mode, binpath)
    if mode == "enter":
        # the child prints the decimal value it read, under cooked mode
        txt = out.decode("latin1").strip()
        print(f"enter {binpath}: read={txt!r}")
    else:
        # the bytes the master saw for the single LF the child wrote
        print(f"opost {binpath}: wire={out.hex()}")
