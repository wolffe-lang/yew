#!/usr/bin/env python3
"""Owner-operated raw mouse census. No network, clipboard or preference access.
Run in each terminal: python3 -I mouse-census.py --terminal 'name and version'
Six 8-second windows; click only the plain target shown. q aborts. Paste back JSON.
"""
import argparse
import json
import os
from pathlib import Path
import select
import sys
import termios
import time
import tty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terminal import sgr_events

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--terminal', required=True, help='terminal name/version from its About panel')
a = p.parse_args()
fd = os.open('/dev/tty', os.O_RDWR)
old = termios.tcgetattr(fd)
rows = []
try:
    tty.setraw(fd)
    os.write(fd, b'\x1b[?1049h\x1b[?1002h\x1b[?1006h')
    for label in ('plain-left', 'ctrl-left', 'ctrl-shift-left', 'alt-left', 'shift-left', 'right'):
        os.write(fd, ('\x1b[2J\x1b[HMouse census: ' + label + '\r\n'
                      'Release all keys first. Press SPACE when ready; q aborts.\r\n'
                      'Then perform that gesture once on TARGET within 8 seconds.\r\n'
                      'Click plain text, not a URL: [ TARGET ]\r\n').encode())
        while True:
            b = os.read(fd, 256)
            if b'q' in b or b'\x03' in b:
                raise KeyboardInterrupt
            if b' ' in b:
                break
        end = time.monotonic() + 8
        raw = bytearray()
        while time.monotonic() < end:
            ready, _, _ = select.select([fd], [], [], min(.1, max(0, end-time.monotonic())))
            if ready:
                b = os.read(fd, 4096)
                if b'q' in b or b'\x03' in b:
                    raise KeyboardInterrupt
                raw.extend(b)
                if len(raw) > 65536:
                    raise RuntimeError('input limit exceeded')
        events = sgr_events(bytes(raw))
        rows.append({'gesture': label, 'raw_hex': raw.hex(), 'events': events,
                     'delivery': 'received' if events else 'not-received'})
finally:
    os.write(fd, b'\x1b[?1002l\x1b[?1006l\x1b[?1049l')
    termios.tcsetattr(fd, termios.TCSANOW, old)
    os.close(fd)
print(json.dumps({'terminal': a.terminal, 'TERM': os.getenv('TERM'),
                  'TERM_PROGRAM': os.getenv('TERM_PROGRAM'),
                  'TERM_PROGRAM_VERSION': os.getenv('TERM_PROGRAM_VERSION'),
                  'target': 'plain text (not link)', 'rows': rows}, indent=2))
