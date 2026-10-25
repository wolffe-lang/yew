#!/usr/bin/env python3
import os,pathlib,re,shutil,subprocess,sys
root=pathlib.Path('/home/mfwolffe/lanes/yw07b/core')
stage=root/'target/checked-vm';stage.mkdir(exist_ok=True)
for name in ['fl','unicode','util']:shutil.copytree(root/'src'/name,stage/name,dirs_exist_ok=True)
source=(root/'src/fl_vm_test.lu').read_text()
names=re.findall(r'^fn (t_\w+)\(\)',source,re.M);assert len(names)==30
rows=[];failed=0
for i,name in enumerate(names):
    for tier in sys.argv[1:]:
        for stress in [False,True]:
            mode='stress' if stress else 'normal'
            env=dict(os.environ)
            env.pop('YEW_FL_GC_STRESS',None);env.pop('FL_GC_STRESS',None)
            if stress:env['YEW_FL_GC_STRESS']='1'
            if tier=='checked':
                file=stage/'case_test.lu'
                file.write_text(re.sub(r'fn main\(\) \{.*?\n\}',f'fn main() {{ {name}() }}',source,flags=re.S))
                cmd=['/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf','test','--deny-warnings','--nocapture','--no-native-fallback',str(file)]
            else:cmd=[str(root/f'target/vm30-{tier}'),str(i)]
            p=subprocess.run(cmd,env=env,capture_output=True,text=True)
            output=p.stdout+p.stderr
            (root/f'notes/yw07b-evidence/core/vm30-{i:02d}-{tier}-{mode}.log').write_text(output)
            verdict='PASS' if p.returncode==0 else 'UNSUPPORTED' if 'unsupported (' in output else 'FAIL'
            failed+=verdict!='PASS'
            row=f'{i}\t{name}\t{tier}\t{mode}\t{verdict}\texit={p.returncode}'
            rows.append(row);print(row,flush=True)
(root/('notes/yw07b-evidence/core/vm30-'+'-'.join(sys.argv[1:])+'.tsv')).write_text('\n'.join(rows)+'\n')
sys.exit(bool(failed))
