#!/usr/bin/env python3
"""yew#33's row: `G` then `o` on the empty line after a final newline.

    final-newline-pty.py --yew BIN --runtime DIR --root DIR [--want HEX]

Opens a file of `alpha\\nbeta\\ngamma\\n` in BIN under a PTY with fresh
home, config, state, cache and data trees below --root (yew#99), types
`G`, `o`, `delta`, Escape, `s` (save) and quits through the command line,
then prints the saved file's bytes as hex and as a Python literal. With
--want, exits 1 unless the bytes are that hex. Run it once against C yew
(the oracle) and once against the port: the two lines must be equal.
"""
import argparse
import errno
import fcntl
import os
from pathlib import Path
import select
import shutil
import struct
import sys
import termios
import time

p = argparse.ArgumentParser()
p.add_argument("--yew", required=True)
p.add_argument("--runtime", required=True)
p.add_argument("--root", required=True)
p.add_argument("--want")
a = p.parse_args()
root = Path(a.root).resolve()
root.mkdir(parents=True, exist_ok=True)
for part in ("home", "config", "state", "cache", "data", "work"):
    if (root / part).exists():
        shutil.rmtree(root / part)
    (root / part).mkdir()
file = root / "work/final.txt"
file.write_bytes(b"alpha\nbeta\ngamma\n")
env = {"PATH": "/usr/bin:/bin", "HOME": str(root / "home"), "XDG_CONFIG_HOME": str(root / "config"),
       "XDG_STATE_HOME": str(root / "state"), "XDG_CACHE_HOME": str(root / "cache"),
       "XDG_DATA_HOME": str(root / "data"), "YEW_RUNTIME_DIR": str(Path(a.runtime).resolve()),
       "TERM": "xterm-256color", "LC_ALL": "C", "YEW_NO_OSC52": "1",
       "YEW_LOG": str(root / "editor.log")}
binary = str(Path(a.yew).resolve())
pid, fd = os.forkpty()
if pid == 0:
    os.chdir(root / "work")
    os.execve(binary, [binary, "--no-workspace-config", str(file)], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))


def drain(seconds):
    until = time.monotonic() + seconds
    while time.monotonic() < until:
        if not select.select([fd], [], [], max(0.0, min(0.1, until - time.monotonic())))[0]:
            continue
        try:
            data = os.read(fd, 65536)
        except OSError as e:
            if e.errno == errno.EIO:
                return
            raise
        if not data:
            return


def send(data):
    os.write(fd, data)
    drain(0.3)


exited = False
try:
    drain(1.0)
    for keys in (b"G", b"o", b"delta", b"\x1b[27u", b"s", b"e", b"ed.quit_force\r"):
        send(keys)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        got, status = os.waitpid(pid, os.WNOHANG)
        if got == pid:
            exited = True
            break
        drain(0.1)
finally:
    os.close(fd)
    if not exited:
        # Closing the PTY hangs the child up; never a signal to a group.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            got, _ = os.waitpid(pid, os.WNOHANG)
            if got == pid:
                break
            time.sleep(0.05)
saved = file.read_bytes()
print(f"final-newline: exited={exited} bytes={saved.hex()} text={saved!r}")
if a.want is not None and saved.hex() != a.want:
    print(f"FAIL final_newline_after_G_o: saved {saved.hex()}, want {a.want}")
    sys.exit(1)
sys.exit(0 if exited else 1)
