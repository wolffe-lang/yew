#!/usr/bin/env python3
"""yw09b's runtime-skew PTY row, isolated HOME/XDG/runtime fixtures only."""
import argparse
import errno
import fcntl
import os
from pathlib import Path
import re
import select
import shutil
import struct
import sys
import termios
import time

p = argparse.ArgumentParser()
p.add_argument("--yew", required=True)
p.add_argument("--root", required=True)
p.add_argument("--runtime", required=True)
p.add_argument("--expect-locked", action="store_true")
p.add_argument("--prefix", action="store_true", help="test a fixture mounted at the install prefix in a container")
p.add_argument("--fixture-only", action="store_true", help="prepare an owned runtime for a container mount")
a = p.parse_args()
root = Path(a.root).resolve()
root.mkdir(parents=True, exist_ok=True)
for part in ("home", "config", "state", "cache", "data", "work"):
    (root / part).mkdir(exist_ok=True)
runtime = root / "runtime"
if runtime.exists(): shutil.rmtree(runtime)
shutil.copytree(a.runtime, runtime)
with (runtime / "init.fl").open("a") as out:
    out.write('\nbind("L", "t h", "ed.theme.pick")\nbind("L", "Z", "ed.quit_force")\n')
if a.fixture_only: sys.exit(0)
file = root / "work/proof.txt"
file.write_bytes(b"first\nsecond\n")
log = root / "editor.log"
if log.exists(): log.unlink()
env = dict(os.environ, HOME=str(root / "home"), XDG_CONFIG_HOME=str(root / "config"),
           XDG_STATE_HOME=str(root / "state"), XDG_CACHE_HOME=str(root / "cache"),
           XDG_DATA_HOME=str(root / "data"), YEW_RUNTIME_DIR=str(runtime),
           TERM="xterm-256color", LC_ALL="C", YEW_NO_OSC52="1", YEW_LOG=str(root / "editor.log"))
if a.prefix: env.pop("YEW_RUNTIME_DIR", None)
binary = str(Path(a.yew).resolve())
pid, fd = os.forkpty()
if pid == 0:
    os.chdir(root / "work")
    os.execve(binary, [binary, "--no-workspace-config", str(file)], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 240, 0, 0))
wire = bytearray()

def drain(seconds):
    until = time.monotonic() + seconds
    while time.monotonic() < until:
        if not select.select([fd], [], [], min(0.1, until-time.monotonic()))[0]: continue
        try:
            data = os.read(fd, 65536)
        except OSError as e:
            if e.errno == errno.EIO: return
            raise
        if not data: return
        wire.extend(data)

def send(data):
    os.write(fd, data)
    drain(0.25)

try:
    drain(1.0)
    startup = bytes(wire)
    send(b"\x1b[B")
    send(b"i")
    send(b"proof")
    send(b"\x1b[27u")
    send(b"s")
    if a.prefix:
        send(b"e")
        send(b"ed.config.reload\r")
        send(b"e")
        send(b"ed.quit_force\r")
    else:
        send(b"Z")
    drain(0.5)
    got, status = os.waitpid(pid, os.WNOHANG)
    exited = got == pid
    moved = file.read_bytes() == b"first\nproofsecond\n"
    plain = re.sub(rb"\x1b\[[0-?]*[ -/]*[@-~]", b"", startup)
    (root / "wire.bin").write_bytes(wire)
    (root / "startup.txt").write_bytes(plain)
    row = "runtime_prefix_skew" if a.prefix else "runtime_locked_mode"
    print(f"{row}: exited={exited} motion_and_insert={moved}", flush=True)
    print(plain.decode("utf-8", "replace"), flush=True)
    if a.expect_locked:
        assert not exited and not moved, "baseline did not reproduce the locked mode"
        assert b"config runtime error:" in plain, "baseline did not report config failure"
        print("runtime_locked_mode: reproduced at 3133476", flush=True)
    else:
        if a.prefix:
            assert b"runtime at /usr/local/share/yew/runtime is not this build's" in plain, "runtime_prefix_skew: no warning"
            assert b"using the built-in runtime" in plain, "runtime_prefix_skew: no fallback notice"
            assert b"unknown command" not in plain, "runtime_prefix_skew: mismatched runtime was executed"
            assert log.read_text().count("is not this build's") == 1, "runtime_prefix_warn_once: warning repeated on reload"
        else:
            assert b"unknown command 'ed.theme.pick'" in plain, "refused command not named"
            assert b"init.fl:" in plain, "refused file/line not named"
        assert exited and os.waitstatus_to_exitcode(status) == 0, f"{row}: quit binding did not answer"
        assert moved, f"{row}: motion, Insert and save did not answer"
        print("runtime_prefix_skew: ok; runtime_prefix_warn_once: ok" if a.prefix else "runtime_locked_mode: ok", flush=True)
finally:
    os.close(fd)
    if not locals().get("exited", False):
        # Closing our PTY sends its hangup; no host/process-group signals.
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            got, status = os.waitpid(pid, os.WNOHANG)
            if got == pid: break
            time.sleep(0.05)
        else:
            raise RuntimeError(f"PTY child {pid} did not reap after close")
