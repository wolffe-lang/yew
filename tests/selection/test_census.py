#!/usr/bin/env python3
"""Drive the actual census process on a PTY, including macOS script(1)."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import pty
import select
import subprocess
import sys
import termios
import time

HERE = Path(__file__).resolve().parent


def run_case(root, via_script=False, control_c=False):
    root.mkdir(parents=True, exist_ok=False)
    master, slave = pty.openpty()
    before = termios.tcgetattr(slave)
    cmd = [sys.executable, '-I', str(HERE/'mouse-census.py'), '--terminal', 'automated-pty']
    if via_script:
        cmd = ['/usr/bin/script', '-q', str(root/'script.typescript')] + cmd
    def controlling_tty():
        os.setsid()
        fcntl.ioctl(slave, termios.TIOCSCTTY, 0)
    proc = subprocess.Popen(cmd, stdin=slave, stdout=slave, stderr=slave,
                            pass_fds=(slave,), preexec_fn=controlling_tty,
                            cwd=root, env={'PATH':'/usr/bin:/bin','HOME':str(root),
                                           'SHELL':'/bin/sh','TERM':'xterm-256color'})
    raw = bytearray()
    def wait_for(needle, seconds=8):
        deadline = time.monotonic()+seconds
        while needle not in raw:
            if time.monotonic()>deadline:
                raise AssertionError(f'timed out awaiting {needle!r}; {bytes(raw)!r}')
            ready,_,_=select.select([master],[],[],.1)
            if ready:
                data=os.read(master,65536)
                if not data:raise AssertionError('unexpected EOF')
                raw.extend(data)
    try:
        wait_for(b'press q when done')
        assert b'\x1b[?1000h\x1b[?1002h\x1b[?1006h' in raw
        current=termios.tcgetattr(slave)
        assert not (current[3] & termios.ICANON), 'not raw: ICANON'
        assert not (current[3] & termios.ECHO), 'not raw: ECHO'
        for cb in (0,16,20,8,4,2):
            for suffix in ('M','m'):
                event=f'\x1b[<{cb};10;5{suffix}'.encode()
                # Split the CSI across writes; no Space or timer handshake.
                os.write(master,event[:4]);os.write(master,event[4:])
                wait_for(('raw='+event.hex()).encode())
        os.write(master,b'\x03' if control_c else b'q')
        wait_for(b'MOUSE-CENSUS-JSON ')
        # The JSON is line framed; wait for its completed line, not just prefix.
        while b'\n' not in raw.split(b'MOUSE-CENSUS-JSON ',1)[1]:
            ready,_,_=select.select([master],[],[],2)
            if not ready:raise AssertionError('incomplete JSON line')
            raw.extend(os.read(master,65536))
        proc.wait(timeout=8)
        assert proc.returncode==0, proc.returncode
        payload=json.loads(raw.split(b'MOUSE-CENSUS-JSON ',1)[1].splitlines()[0])
        mouse=[x for x in payload['events'] if x['kind'] in ('press','release')]
        assert len(mouse)==12, payload
        assert [x['mods'] for x in mouse[::2]]==[0,16,20,8,4,0], payload
        assert [x['button'] for x in mouse[::2]]==[0,0,0,0,0,2], payload
        assert all(x['x']==10 and x['y']==5 for x in mouse)
        assert [x['release'] for x in mouse]==[False,True]*6
        assert payload['exit_reason']==('ctrl-c' if control_c else 'q'), payload
        assert b'\x1b[?1000l\x1b[?1002l\x1b[?1006l' in raw
        assert termios.tcgetattr(slave)==before, 'terminal settings not restored exactly'
        (root/'result.json').write_text(json.dumps(payload,indent=2))
    finally:
        (root/'raw.bin').write_bytes(raw)
        os.close(master)
        os.close(slave)
        if proc.poll() is None:
            proc.wait(timeout=8)  # controlling-tty EOF; no process scan or group signal
    print('PASS '+root.name+' live events, raw mode, decoded JSON and exact tty restore',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    a.output=a.output.resolve()
    a.output.mkdir(parents=True,exist_ok=True)
    run_case(a.output/'direct-q')
    run_case(a.output/'direct-ctrl-c',control_c=True)
    if sys.platform=='darwin':
        run_case(a.output/'mac-script-q',via_script=True)
    else:
        print('SKIP mac-script-q reason=macos-specific-script-cli')
