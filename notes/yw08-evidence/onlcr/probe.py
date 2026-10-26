#!/usr/bin/env python3
"""Own-child PTYs only: compare REPL output with ONLCR initially cleared."""
import os
import pathlib
import pty
import select
import sys
import termios
import time

out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
for label, binary in zip(('C', 'wolf'), sys.argv[2:]):
    pid, fd = pty.fork()
    if pid == 0:
        attrs = termios.tcgetattr(0)
        attrs[1] &= ~termios.ONLCR
        termios.tcsetattr(0, termios.TCSANOW, attrs)
        os.execv(binary, [binary, 'fl'])
    (out / (label + '.pid')).write_text(str(pid) + '\n')
    data = bytearray()
    sent = False
    deadline = time.monotonic() + 15
    try:
        while time.monotonic() < deadline:
            if not select.select([fd], [], [], 0.1)[0]:
                continue
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            data.extend(chunk)
            if not sent and b'fl> ' in data:
                os.write(fd, b'import io\rio.print("ONLCR-A\\nONLCR-B")\r:quit\r')
                sent = True
    finally:
        os.close(fd)
    _, status = os.waitpid(pid, 0)
    (out / (label + '.bytes')).write_bytes(data)
    code = os.waitstatus_to_exitcode(status)
    crlf = b'ONLCR-A\r\nONLCR-B' in data
    lf = b'ONLCR-A\nONLCR-B' in data
    print(f'{label}: exit={code} sent={sent} CRLF={crlf} bare_LF={lf}', flush=True)
    assert sent and code == 0
    assert crlf or lf
