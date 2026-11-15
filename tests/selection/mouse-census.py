#!/usr/bin/env python3
"""Free, live mouse capture; no steps, Space prompts, timers or preferences.
Run in each terminal and paste back the JSON printed after q or Ctrl+C.
"""
import argparse
import json
import os
from pathlib import Path
import re
import signal
import sys
import termios
import tty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terminal import sgr_events

ENABLE = b'\x1b[?1000h\x1b[?1002h\x1b[?1006h'
DISABLE = b'\x1b[?1000l\x1b[?1002l\x1b[?1006l'
PROMPT = b'click with: none, Ctrl, Ctrl+Shift, Alt, Shift, right; press q when done\r\n'


def split_event(buf):
    """Return one complete byte event and the remainder, or None for a prefix."""
    if not buf:
        return None
    if buf.startswith(b'\x1b['):
        m = re.match(rb'\x1b\[[0-?]*[ -/]*[@-~]', buf)
        if m:
            return buf[:m.end()], buf[m.end():]
        # A valid CSI prefix may be split across arbitrary reads.
        if re.fullmatch(rb'\x1b\[[0-?]*[ -/]*', buf) and len(buf) <= 128:
            return None
    elif buf == b'\x1b':
        return None
    return buf[:1], buf[1:]


def interrupted(signum, frame):
    raise KeyboardInterrupt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--terminal', default=os.getenv('TERM_PROGRAM', 'unknown'),
                   help='terminal name and version, when known')
    a = p.parse_args()
    fd = os.open('/dev/tty', os.O_RDWR)
    old = termios.tcgetattr(fd)
    events, pending, reason = [], b'', 'q'
    previous = {}
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        previous[sig] = signal.signal(sig, interrupted)
    try:
        tty.setraw(fd)
        os.write(fd, ENABLE + PROMPT)
        done = False
        while not done:
            chunk = os.read(fd, 4096)
            if not chunk:
                reason = 'eof'
                break
            pending += chunk
            while True:
                item = split_event(pending)
                if item is None:
                    break
                raw, pending = item
                decoded = sgr_events(raw)
                if decoded:
                    e = decoded[0]
                    base = e['button']
                    button = {0:'left', 1:'middle', 2:'right', 64:'wheel-up', 65:'wheel-down'}.get(base, str(base))
                    kind = 'release' if e['release'] else 'motion' if 32 <= base <= 35 else 'press'
                    e.update(kind=kind, button_name=button, shift=bool(e['mods'] & 4),
                             alt=bool(e['mods'] & 8), ctrl=bool(e['mods'] & 16))
                    line = (f"{kind} button={button} Shift={int(e['shift'])} Alt={int(e['alt'])} "
                            f"Ctrl={int(e['ctrl'])} x;y={e['x']};{e['y']} raw={raw.hex()} bytes={raw!r}\r\n")
                else:
                    e = {'kind':'input', 'raw':raw.hex()}
                    line = f'input raw={raw.hex()} bytes={raw!r}\r\n'
                events.append(e)
                os.write(fd, line.encode())
                if raw in (b'q', b'\x03'):
                    reason = 'q' if raw == b'q' else 'ctrl-c'
                    done = True
                    break
                if len(events) > 10000:
                    reason = 'event-limit'
                    done = True
                    break
    except KeyboardInterrupt:
        reason = 'signal'
    finally:
        # Restore even if writing the final escape sequence fails on a closed tty.
        try:
            os.write(fd, DISABLE + b'\r\n')
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSANOW, old)
            finally:
                os.close(fd)
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
    print('MOUSE-CENSUS-JSON ' + json.dumps({'terminal':a.terminal,
          'TERM':os.getenv('TERM'), 'TERM_PROGRAM':os.getenv('TERM_PROGRAM'),
          'TERM_PROGRAM_VERSION':os.getenv('TERM_PROGRAM_VERSION'),
          'exit_reason':reason, 'pending_hex':pending.hex(), 'events':events}), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
