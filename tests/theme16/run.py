#!/usr/bin/env python3
"""Judge unselected document cells, not escape substrings or terminal brightness.

The portable ASCII-fixture VT reader is shared with selection tests. No terminal
probe replies are synthesized. Output and the last live frame are kept verbatim.
Exit 1 is a semantic mismatch; exit 2 is infrastructure/document failure.
"""
import argparse
import errno
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pty
import select
import struct
import sys
import termios
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('selection_terminal', HERE.parent / 'selection' / 'terminal.py')
terminal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(terminal)
VT = terminal.VT
SAMPLE = (HERE / 'sample.lu').read_text()
LINES = SAMPLE.splitlines()
# line number (zero based), exact token, explicit logical ANSI index, attributes.
PENS = {
    'keyword': (6, 'if', 13, (1,)),
    'boolean': (6, 'true', 11, (1,)),
    'plain': (6, 'plain_word', 7, ()),
    'number': (4, '42', 11, ()),
    'string': (7, 'green', 10, ()),
    'function': (5, 'shade', 14, ()),
    'comment': (1, 'regular comment', 2, (3,)),
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def document(vt):
    rows = vt.rows()
    for first in range(1, len(rows) - len(LINES) - 1):
        offsets = []
        for n, line in enumerate(LINES):
            x = rows[first + n].find(line)
            if x < 0:
                break
            offsets.append(x)
        if len(offsets) == len(LINES):
            return first, offsets
    raise ValueError('complete current document absent from document rows')


def judge(raw, mode='indexed'):
    vt = VT()
    vt.feed(raw)
    first, offsets = document(vt)
    actual, matched = {}, {}
    for name, (n, token, pen, attrs) in PENS.items():
        x = offsets[n] + LINES[n].index(token)
        cells = [vt.cells[first + n, x + k] for k in range(len(token))]
        actual[name] = {'row': first + n, 'column': x, 'text': token,
                        'styles': [c[1] for c in cells]}
        if mode == 'dark16':
            pen = 8 if name in ('boolean', 'number', 'comment') else 7
        expected = (('index', pen), ('index', 0), attrs)
        if mode in ('mono', 'dumb'):
            expected = (('default',), ('default',), () if mode == 'dumb' else attrs)
        matched[name] = all(c[1] == expected for c in cells)
    results = {
        'syntax16-auto-keyword-pen': matched['keyword'] and matched['plain'],
        'syntax16-auto-boolean-pen': matched['boolean'] and matched['plain'],
        'syntax16-auto-palette': all(matched[k] for k in ('number', 'string', 'function', 'comment')),
    }
    if mode != 'indexed':
        results = {name.replace('auto', mode): ok for name, ok in results.items()}
    return results, actual, vt


def fake_frame():
    raw = bytearray(b'\x1b[2J')
    for n, line in enumerate(LINES):
        raw.extend(f'\x1b[{n+2};3H\x1b[0;37;40m'.encode() + line.encode())
    for n, token, pen, attrs in PENS.values():
        sgr = [0, 40, 90 + pen - 8 if pen >= 8 else 30 + pen, *attrs]
        raw.extend(f'\x1b[{n+2};{3+LINES[n].index(token)}H\x1b[{";".join(map(str,sgr))}m'.encode() + token.encode())
    return bytes(raw)


def self_test():
    good = fake_frame()
    assert all(judge(good)[0].values())
    cases = {
        'plain-only': b'\x1b[2J' + b''.join(f'\x1b[{n+2};3H\x1b[0;37;40m{line}'.encode() for n, line in enumerate(LINES)),
        'wrong-pen-with-bold': good + b'\x1b[8;7H\x1b[0;35;40;1mif',
        'statusline-only': b'\x1b[24;1H\x1b[95;1mif true { plain_word }',
        'osc-only': b'\x1b]0;' + good + b'\x07',
        'stale-erased-frame': good + b'\x1b[2J',
        'overwritten-frame': good + b'\x1b[8;7H\x1b[0;37;40mif true { plain_word }',
        'missing-document': b'\x1b[95;1mif\x1b[93m true',
    }
    for name, data in cases.items():
        try:
            rejected = not all(judge(data)[0].values())
        except (ValueError, KeyError, IndexError):
            rejected = True
        if not rejected:
            raise AssertionError('judge accepted ' + name)
        print('PASS judge-reject-' + name)
    print('PASS judge-accept-explicit-pens')


class Session:
    def __init__(self, binary, out, term, extra, theme=None, config=None, custom=False):
        self.out, self.raw = out, bytearray()
        self.cwd = out / 'scratch'
        self.cwd.mkdir()
        for p in ('home', 'config', 'state', 'cache', 'tmp'):
            (self.cwd / p).mkdir()
        fixture = self.cwd / 'sample.lu'
        fixture.write_text(SAMPLE)
        config_dir = self.cwd / 'config' / 'yew'
        if config or custom:
            config_dir.mkdir()
        if config:
            (config_dir / 'init.fl').write_text(f'set({{ theme: "{config}" }})\n')
        if custom:
            (config_dir / 'themes').mkdir()
            src = (HERE.parent.parent / 'runtime/themes/quiver-16.fl').read_text()
            assert src.count('name: "quiver-16"') == 1
            (config_dir / 'themes' / 'fixture-custom.fl').write_text(src.replace('name: "quiver-16"', 'name: "fixture-custom"'))
        env = os.environ.copy()
        for key in ('YEW_THEME', 'YEW_COLORS', 'NO_COLOR', 'YEW_RUNTIME_DIR', 'COLORTERM', 'TERM_PROGRAM'):
            env.pop(key, None)
        env.update(HOME=str(self.cwd / 'home'), XDG_CONFIG_HOME=str(self.cwd / 'config'),
                   XDG_STATE_HOME=str(self.cwd / 'state'), XDG_CACHE_HOME=str(self.cwd / 'cache'),
                   TMPDIR=str(self.cwd / 'tmp'), SHELL='/bin/sh', TERM=term,
                   PATH='/usr/bin:/bin', LANG='C.UTF-8',
                   YEW_LOG=str(out / 'yew.log'), YEW_CLIPBOARD='none', YEW_OSC52='off')
        env.update(extra)
        self.env = {k: env.get(k) for k in ('TERM', 'YEW_THEME', 'YEW_COLORS', 'NO_COLOR', 'YEW_RUNTIME_DIR')}
        self.pid, self.fd = pty.fork()
        if not self.pid:
            fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack('HHHH', 24, 80, 0, 0))
            os.chdir(self.cwd)
            argv = [binary, '--no-workspace-config']
            if theme:
                argv += ['--theme', theme]
            os.execve(binary, argv + [str(fixture)], env)
        (out / 'pid').write_text(str(self.pid) + '\n')
        os.set_blocking(self.fd, False)

    def pump(self, seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            ready, _, _ = select.select([self.fd], [], [], max(0, end - time.monotonic()))
            if not ready:
                break
            try:
                chunk = os.read(self.fd, 65536)
            except OSError as error:
                if error.errno == errno.EIO:
                    return
                raise
            if not chunk:
                return
            self.raw.extend(chunk)

    def finish(self):
        # A contiguous ESC-colon is an Alt-colon key, not Escape then a prompt.
        for _ in range(3):
            os.write(self.fd, b'\x1b')
            self.pump(.25)
        os.write(self.fd, b':q!\r')
        self.pump(1)
        pid, status = os.waitpid(self.pid, os.WNOHANG)
        deadline = time.monotonic() + 2
        while not pid and time.monotonic() < deadline:
            # EOF can precede process exit; still reap this exact recorded child.
            select.select([], [], [], .01)
            pid, status = os.waitpid(self.pid, os.WNOHANG)
        (self.out / 'session.raw').write_bytes(self.raw)
        os.close(self.fd)
        if not pid:
            raise RuntimeError('editor did not quit after normalized Escape and explicit quit')
        return os.waitstatus_to_exitcode(status)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--binary')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--term', default='linux')
    parser.add_argument('--env', action='append', default=[])
    parser.add_argument('--theme')
    parser.add_argument('--config-theme')
    parser.add_argument('--custom', action='store_true')
    parser.add_argument('--style-mode', choices=('indexed', 'dark16', 'mono', 'dumb', 'observe'), default='indexed')
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.binary or not args.out:
        parser.error('--binary and --out required')
    binary = str(Path(args.binary).resolve())
    if not Path(binary).is_file() or not os.access(binary, os.X_OK):
        print('INFRA binary is absent or not executable', flush=True)
        return 2
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    receipt = {'binary_sha256': digest(binary), 'sample_sha256': digest(HERE / 'sample.lu'),
               'judge_sha256': digest(__file__), 'platform': sys.platform, 'rows': 24, 'cols': 80,
               'probe_replies': False, 'loose_assets': bool(args.custom)}
    receipt['inputs'] = {'cli_theme': args.theme, 'config_theme': args.config_theme,
                         'custom': args.custom, 'style_mode': args.style_mode}
    session = Session(binary, out, args.term, dict(x.split('=', 1) for x in args.env),
                      args.theme, args.config_theme, args.custom)
    receipt['environment'] = session.env
    results = {}
    error = ''
    try:
        session.pump(1.5)
        frame = bytes(session.raw)
        (out / 'frame.raw').write_bytes(frame)
        results, actual, vt = judge(frame, args.style_mode)
        if args.style_mode == 'observe':
            results = {}
            print('OBSERVE explicit reference document (not an indexed-palette pass)', flush=True)
        if args.reference:
            ref = json.loads(args.reference.read_text())
            assert ref['document_verified'] and ref['editor_exit'] == 0
            assert ref['binary_sha256'] == receipt['binary_sha256']
            assert ref['sample_sha256'] == receipt['sample_sha256']
            assert ref['judge_sha256'] == receipt['judge_sha256']
            current = json.loads(json.dumps(actual))
            results = {'syntax16-rich-auto-matches-explicit-dark': current == ref['actual']}
            receipt['reference_sha256'] = digest(args.reference)
        receipt.update(document_verified=True, results=results, actual=actual,
                       frame_sha256=hashlib.sha256(frame).hexdigest(),
                       cells=[{'row': y, 'column': x, 'text': ch, 'style': style}
                              for (y, x), (ch, style) in sorted(vt.cells.items())])
        for name, passed in results.items():
            print(('PASS ' if passed else 'FAIL ') + name, flush=True)
        print('ACTUAL ' + json.dumps(actual, sort_keys=True), flush=True)
    except (ValueError, KeyError, IndexError, RuntimeError, AssertionError, OSError) as exc:
        error = str(exc)
        receipt.update(document_verified=False, error=error)
        print('INFRA ' + error, flush=True)
    finally:
        try:
            status = session.finish()
        except (RuntimeError, OSError) as exc:
            status = None
            error = str(exc)
            receipt['cleanup_error'] = error
            print('INFRA ' + error, flush=True)
        receipt['editor_exit'] = status
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    if error or status != 0:
        return 2
    return 0 if (results and all(results.values())) or (args.style_mode == 'observe' and not args.reference) else 1


if __name__ == '__main__':
    sys.exit(main())
