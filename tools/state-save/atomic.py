#!/usr/bin/env python3
"""test_ws_save.c:961-1189 through pinned faultshim, only inside lane ctr."""
import os, pathlib, subprocess, sys, tempfile
root=pathlib.Path.cwd()
exe=pathlib.Path(sys.argv[1]).resolve()
mode=sys.argv[2]
shim=root/'target/oracle/sagitta/build/tests/torture/faultshim.so'
if not shim.is_file(): raise SystemExit('FAIL missing pinned faultshim')
with tempfile.TemporaryDirectory(prefix='save-',dir=root/'target/state') as tmp:
    base=pathlib.Path(tmp); work=base/'work'; home=base/'home'
    work.mkdir(); home.mkdir(); log=base/'calls.log'
    env=os.environ.copy(); env.update(XDG_STATE_HOME=str(home),YEW_WS_TEST_WORK=str(work),LD_PRELOAD=str(shim),YEW_FAULT_ENABLE='0',YEW_LOG='/dev/null',YEW_FAULT_LOG=str(log))
    if mode=='order':
        subprocess.run([str(exe),'--atomic-child'],env=env,check=True)
        rows=log.read_text().splitlines()
        positions=[next(i for i,row in enumerate(rows) if needle in row) for needle in ('write','fsync-file','rename','fsync-dir')]
        assert positions==sorted(positions) and len(set(positions))==4,rows
        print('ws_save_write_is_atomic_in_order: '+','.join(map(str,positions)),flush=True)
    elif mode=='kill':
        killed=0
        for point in range(1,25):
            env['YEW_FAULT_AT']=str(point)
            result=subprocess.run([str(exe),'--torture-child'],env=env)
            assert result.returncode in (0,137),result.returncode
            killed+=result.returncode==137
            for state in home.glob('yew/workspaces/*/state.fl'):
                subprocess.run([str(exe),'--validate',str(state)],check=True)
        assert killed>0,'fault injection never fired'
        print(f'ws_save_survives_kill9_at_every_step: steps=24 killed={killed}',flush=True)
    else: raise SystemExit('bad mode')
