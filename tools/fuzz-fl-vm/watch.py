#!/usr/bin/env python3
"""fuzz_fl_vm's per-input watchdog (C: alarm(5) in fuzz_fl_vm.c:92-94 and the
ITIMER_PROF timer of fuzzlib.c:1125-1209), with no signal handler in the VM.

The child gets the write end of a pipe as YEW_FL_FUZZ_WATCH_FD and writes one
'.' before each input; 30 s may pass before the first, 5 s between any two.
On a stall it prints the input's index and returns 124 (C's _Exit(124)),
terminating only the child this call started, by its recorded pid.
"""
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time


def run(command, pid_file, timeout=5.0, startup=30.0, say=True):
    read_fd, write_fd = os.pipe()
    env = dict(os.environ, YEW_FL_FUZZ_WATCH_FD=str(write_fd))
    proc = subprocess.Popen(command, env=env, pass_fds=(write_fd,))
    Path(pid_file).write_text(str(proc.pid) + '\n')
    os.close(write_fd)
    deadline = time.monotonic() + startup
    inputs = 0
    timed_out = False
    try:
        while proc.poll() is None:
            left = deadline - time.monotonic()
            if left <= 0:
                timed_out = True
                break
            if select.select([read_fd], [], [], left)[0]:
                data = os.read(read_fd, 65536)
                if not data:
                    # EOF must be followed by exit, never an unbounded wait.
                    try:
                        proc.wait(timeout=max(0.01, deadline - time.monotonic()))
                    except subprocess.TimeoutExpired:
                        timed_out = True
                    break
                if any(b != ord('.') for b in data):
                    raise ValueError('invalid input-progress record')
                inputs += len(data)
                deadline = time.monotonic() + timeout
        if timed_out:
            if say:
                print(f'fuzz_fl_vm: watchdog expired after input {inputs - 1}; argv={command!r}',
                      file=sys.stderr, flush=True)
            return 124
        code = proc.wait()
        return code if code >= 0 else 128 - code
    finally:
        os.close(read_fd)
        if proc.poll() is None:
            proc.terminate()  # recorded, directly-owned pid only; never a group
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


def selftest():
    with tempfile.TemporaryDirectory(prefix='yew-vm-watch-') as d:
        def child(code):
            return [sys.executable, '-I', '-c', 'import os,time; fd=int(os.environ["YEW_FL_FUZZ_WATCH_FD"]); '+code]
        assert run(child('os.write(fd,b"."); raise SystemExit(0)'), Path(d)/'ok.pid', timeout=.1) == 0
        assert run(child('os.write(fd,b"."); raise SystemExit(7)'), Path(d)/'fail.pid', timeout=.1) == 7
        assert run(child('os.write(fd,b"."); time.sleep(10)'), Path(d)/'stall.pid', timeout=.1, say=False) == 124
        assert run(child('os.close(fd); time.sleep(10)'), Path(d)/'eof.pid', timeout=.1, startup=.2,
                   say=False) == 124
    print('fuzz_fl_vm watchdog: success, failure, stalled input, early EOF controls PASS')


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        selftest()
    elif len(sys.argv) >= 3:
        raise SystemExit(run(sys.argv[2:], sys.argv[1]))
    else:
        raise SystemExit('usage: watch.py PID_FILE BINARY [ARGS...] | --selftest')
