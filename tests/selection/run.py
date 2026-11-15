#!/usr/bin/env python3
"""Executable selection contracts; intentionally red until the redesign lands.

These rows are held outside the default unit suite. Exit 0 means every selected
contract passed, 1 a behavior mismatch, 2 an infrastructure/control failure.
There is no xfail conversion. --self-test judges the observer, not the editor.
Use the repository runtime and a binary built from its unchanged source tree.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import pty
import select
import signal
import struct
import subprocess
import sys
import termios
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terminal import VT, sgr_events

SEED = 'alpha beta gamma\nsecond line\nthird line\n'
ESC = b'\x1b'
SHIFT_RIGHT = b'\x1b[1;2C'
CA_UP, CA_DOWN = b'\x1b[1;7A', b'\x1b[1;7B'
CASES = [
    'escape-origin-I', 'escape-origin-W', 'escape-origin-B',
    'selection-visible-256', 'selection-visible-truecolor', 'selection-visible-16',
    'copy-retains-selection', 'copy-internal-paste', 'cut-internal-paste',
    'cut-origin-I', 'replace-typing-origin-I', 'h-selects-current-line',
    'alt-click-add-cursor', 'ctrl-alt-down-I', 'ctrl-alt-up-I',
    'ctrl-alt-repeat-frontier', 'keyboard-definition-control',
    'ctrl-click-definition', 'ctrl-shift-click-menu', 'right-click-menu',
    'ctrl-shift-duplicate-menu',
]

class Infra(Exception):
    pass

class Session:
    def __init__(self, binary, runtime, root, colors='256', lsp=False):
        self.root = root
        root.mkdir(parents=True, exist_ok=False)
        (root/'home').mkdir()
        (root/'bin').mkdir()
        self.file = root/('source.lu' if lsp else 'source.txt')
        self.file.write_text(SEED)
        env = {'PATH': str(root/'bin')+':/usr/bin:/bin', 'HOME': str(root/'home'),
               'XDG_CONFIG_HOME': str(root/'home'/'config'),
               'XDG_STATE_HOME': str(root/'home'/'state'), 'SHELL': '/bin/sh',
               'TERM': 'xterm-256color', 'LANG': 'C.UTF-8',
               'YEW_COLORS': colors, 'YEW_RUNTIME_DIR': str(runtime),
               'YEW_CLIPBOARD': 'none', 'YEW_OSC52': 'off'}
        if lsp:
            target = root/'target.txt'
            target.write_text('DEFINITION_TARGET\n')
            wrapper = root/'bin'/'wolf'
            wrapper.write_text('#!'+sys.executable+' -I\n'+(HERE/'fake-lsp.py').read_text())
            wrapper.chmod(0o755)
            env['SELECTION_LSP_LOG'] = str(root/'lsp.jsonl')
            env['SELECTION_LSP_TARGET'] = target.as_uri()
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.chdir(root)
            os.execve(str(binary), [str(binary), '--no-workspace-config', str(self.file)], env)
        (root/'pid').write_text(str(self.pid)+'\n')
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack('HHHH',24,80,0,0))
        self.vt, self.raw, self.counter = VT(), bytearray(), 0
        self.eof = False
        self.rss_peak = 0
        self.last_rss = 0
        self.status = None
        self.take('startup', seconds=2)
        try:
            hits = [(y,r.index('alpha beta gamma')) for y,r in enumerate(self.vt.rows()) if 'alpha beta gamma' in r]
            if len(hits) != 1 or not self.mode('L'):
                raise Infra('startup/fixture control missing')
            self.y, self.x = hits[0]
        except BaseException:
            self.close()
            raise

    def mode(self, mode):
        return self.vt.rows()[23].startswith(' '+mode+('·' if mode=='H' else ' '))

    def body(self, row=0):
        return self.vt.rows()[self.y+row][self.x:].rstrip()

    def rss(self):
        now = time.monotonic()
        if now-self.last_rss < .1:
            return
        self.last_rss = now
        if sys.platform.startswith('linux'):
            try:
                value = int(Path('/proc',str(self.pid),'statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')//1024
            except (OSError, IndexError):
                return
        else:
            q = subprocess.run(['/bin/ps','-o','rss=','-p',str(self.pid)],capture_output=True,text=True,check=False)
            if not q.stdout.strip():
                return
            value = int(q.stdout.strip())
        self.rss_peak = max(self.rss_peak,value)
        if value > 2*1024*1024:
            # Only this recorded child; never a process group or a process scan.
            os.kill(self.pid, signal.SIGKILL)
            raise Infra('own child exceeded 2 GiB RSS')

    def take(self, label, data=None, seconds=.3):
        if data is not None:
            if self.eof:
                raise Infra('child ended before '+label)
            os.write(self.fd,data)
        until = time.monotonic()+seconds
        part = bytearray()
        while time.monotonic()<until:
            self.rss()
            ready,_,_ = select.select([self.fd],[],[],min(.05,max(0,until-time.monotonic())))
            if ready:
                try:
                    b=os.read(self.fd,65536)
                except OSError:
                    self.eof=True
                    break
                if not b:
                    self.eof=True
                    break
                part.extend(b)
        self.raw.extend(part)
        (self.root/f'{self.counter:02d}-{label}.bin').write_bytes(part)
        self.counter+=1
        try:
            self.vt.feed(bytes(part))
        except (ValueError,IndexError) as error:
            raise Infra('unsupported/truncated VT output: '+str(error)) from error
        return bytes(part)

    def click(self, cb, line=0, col=0):
        x,y=self.x+col+1,self.y+line+1
        self.take('click',f'\x1b[<{cb};{x};{y}M\x1b[<{cb};{x};{y}m'.encode(),.5)

    def selected(self):
        self.take('insert',b'i')
        if not self.mode('I'):
            raise Infra('insert mode control missing')
        self.take('select',SHIFT_RIGHT*5)
        if not self.mode('H') or '1:6' not in self.vt.rows()[23]:
            raise Infra('selection state control missing')

    def normalize_insert(self):
        self.take('escape-one',ESC,.35)
        self.take('escape-two',ESC,.35)
        if not self.mode('L'):
            raise Infra('cannot normalize to line mode')
        self.take('insert-again',b'i')

    def lsp_requests(self):
        path=self.root/'lsp.jsonl'
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

    def close(self):
        if self.status is not None:
            return
        # Quit through the PTY, including from a context menu or insert selection.
        if not self.eof:
            for n in range(3):
                self.take('quit-escape',ESC,.2)
                if self.eof:
                    break
            if not self.eof:
                self.take('quit',b':q!\r',.7)
        os.close(self.fd)
        _,status,usage=os.wait4(self.pid,0)
        self.status=status
        (self.root/'full.bin').write_bytes(self.raw)
        (self.root/'metrics.json').write_text(json.dumps({'pid':self.pid,'status':status,
            'rss_peak_kib':self.rss_peak,'cpu_seconds':usage.ru_utime+usage.ru_stime},indent=2))
        if status:
            raise Infra('child exit status '+str(status))


def require(condition, detail):
    if not condition:
        raise AssertionError(detail)


def contract(name,s):
    if name.startswith('escape-origin-'):
        origin=name.rsplit('-',1)[1]
        s.take('origin',{'I':b'i','W':b'w','B':b'b'}[origin])
        if not s.mode(origin):raise Infra('origin control missing')
        s.take('highlight',b'\x1bh' if origin=='I' else b'h')
        if not s.mode('H'):raise Infra('highlight control missing')
        s.take('escape',ESC,.4)
        require(s.mode(origin),'Escape did not restore '+origin)
    elif name.startswith('selection-visible-'):
        before=[s.vt.cells[s.y,s.x+i] for i in range(6)]
        s.selected()
        after=[s.vt.cells[s.y,s.x+i] for i in range(6)]
        changed=sum(a!=b for a,b in zip(before[:5],after[:5]))
        require(changed==5,f'{changed}/5 selected cells visibly changed')
        require(before[5]==after[5],'unselected neighbor changed')
    elif name in ('copy-internal-paste','cut-internal-paste','copy-retains-selection','cut-origin-I','replace-typing-origin-I'):
        s.selected()
        if name=='replace-typing-origin-I':
            s.take('replacement',b'Q')
            require(s.body()=='Q beta gamma' and s.mode('I'),'typing did not replace selection in I')
        else:
            cut=name.startswith('cut-')
            s.take('cut' if cut else 'copy',b'\x18' if cut else b'\x03')
            if cut and s.body()!=' beta gamma':raise Infra('cut extent control missing')
            if name=='copy-retains-selection':
                require(s.mode('H') and s.body()==SEED.splitlines()[0],'copy lost selection or changed text')
            elif name=='cut-origin-I':
                require(s.mode('I'),'cut did not restore I')
            else:
                s.normalize_insert()
                if not cut:s.take('end-of-line',b'\x05')
                s.take('internal-paste',b'\x16')
                expected=SEED.splitlines()[0] if cut else SEED.splitlines()[0]+'alpha'
                require(s.body()==expected,'Ctrl-V did not paste internal register without backend')
    elif name=='h-selects-current-line':
        s.take('highlight',b'h')
        if not s.mode('H'):raise Infra('H control missing')
        s.take('delete-current-selection',b'd')
        require(s.body()=='second line','explicit h did not select current line')
    elif name in ('alt-click-add-cursor','ctrl-alt-down-I','ctrl-alt-up-I','ctrl-alt-repeat-frontier'):
        s.take('insert',b'i')
        if name=='alt-click-add-cursor':s.click(8,line=1)
        elif name=='ctrl-alt-up-I':
            s.take('down',b'\x1b[B');s.take('add-above',CA_UP)
        elif name=='ctrl-alt-down-I':s.take('add-below',CA_DOWN)
        else:
            s.take('H',b'\x1bh');s.take('add-below-one',CA_DOWN);s.take('add-below-two',CA_DOWN);s.take('change',b'c')
        s.take('type-at-cursors',b'Z')
        require(s.body()=='Zalpha beta gamma' and s.body(1)=='Zsecond line','edit did not reach both independent carets')
        if name=='ctrl-alt-repeat-frontier':require(s.body(2)=='Zthird line','repeated add did not grow to third line')
    elif name=='ctrl-shift-duplicate-menu':
        s.selected()
        x,y=s.x+1,s.y+1
        press=f'\x1b[<20;{x};{y}M'.encode()
        release=f'\x1b[<20;{x};{y}m'.encode()
        s.take('first-press',press)
        if not all(k in '\n'.join(s.vt.rows()) for k in ('Cut','Copy','Paste')):
            raise Infra('first context press control missing')
        s.take('duplicate-press',press)
        still_open=all(k in '\n'.join(s.vt.rows()) for k in ('Cut','Copy','Paste'))
        s.take('release',release)
        require(still_open and all(k in '\n'.join(s.vt.rows()) for k in ('Cut','Copy','Paste')),
                'identical repeated press toggled or invoked the menu')
    else:
        if name=='keyboard-definition-control':s.take('definition-key',b'gd',.8)
        else:s.click({'ctrl-click-definition':16,'ctrl-shift-click-menu':20,'right-click-menu':2}[name],line=1,col=2)
        text='\n'.join(s.vt.rows())
        requests=[r for r in s.lsp_requests() if r.get('method')=='textDocument/definition']
        if name in ('ctrl-shift-click-menu','right-click-menu'):
            require(all(x in text for x in ('Cut','Copy','Paste')),'document context menu missing')
            require(not requests,'context gesture sent definition request')
        else:
            if not any(r.get('method')=='initialize' for r in s.lsp_requests()):raise Infra('fake LSP handshake absent')
            require(bool(requests) and 'DEFINITION_TARGET' in text,'definition request/jump missing')
            if name=='ctrl-click-definition':
                require(requests[-1]['params']['position']=={'line':1,'character':2},'definition used old caret, not clicked position')


def self_test():
    checks=[]
    v=VT();v.feed(b'\x1b[2;7H\x1b[37;40malpha \x1b[2;7H\x1b[7malpha\x1b[27m ')
    checks.append(('observer-reverse-cells', all(v.cells[1,x][1][2]==(7,) for x in range(6,11)) and v.cells[1,11][1][2]==()))
    e=sgr_events(b'\x1b[<20;7;2M\x1b[<20;7;2m')
    checks.append(('wire-ctrl-shift-retained', len(e)==2 and all(x['mods']==20 and x['button']==0 for x in e) and e[-1]['release']))
    checks.append(('wire-right-not-control', sgr_events(b'\x1b[<2;7;2M')[0]['button']==2 and sgr_events(b'\x1b[<16;7;2M')[0]['mods']==16))
    for name,ok in checks:print(('PASS ' if ok else 'FAIL ')+name)
    return 0 if all(ok for _,ok in checks) else 1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--self-test',action='store_true')
    p.add_argument('--binary',type=Path)
    p.add_argument('--runtime',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--case',choices=CASES,action='append')
    a=p.parse_args()
    if a.self_test:return self_test()
    if not all((a.binary,a.runtime,a.output)):p.error('--binary, --runtime and --output required')
    a.binary,a.runtime,a.output=a.binary.resolve(),a.runtime.resolve(),a.output.resolve()
    a.output.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    for name in a.case or CASES:
        s=None;kind='PASS';detail='contract holds'
        try:
            colors=name.rsplit('-',1)[1] if name.startswith('selection-visible-') else '256'
            lsp='definition' in name or 'click-menu' in name
            s=Session(a.binary,a.runtime,a.output/name,colors,lsp)
            contract(name,s)
        except AssertionError as error:kind,detail='FAIL',str(error)
        except (Infra,OSError,ValueError,IndexError) as error:kind,detail='ERROR',str(error)
        finally:
            if s is not None:
                try:s.close()
                except (Infra,OSError,ValueError,IndexError) as error:kind,detail='ERROR',str(error)
        print(f'{kind} {name} {detail}',flush=True)
        outcomes.append({'name':name,'verdict':kind,'detail':detail})
    (a.output/'outcomes.json').write_text(json.dumps(outcomes,indent=2))
    if any(x['verdict']=='ERROR' for x in outcomes):return 2
    return 1 if any(x['verdict']=='FAIL' for x in outcomes) else 0

if __name__=='__main__':
    sys.exit(main())
