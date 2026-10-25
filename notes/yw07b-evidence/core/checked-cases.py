#!/usr/bin/env python3
import pathlib,shutil,subprocess,sys
root=pathlib.Path('/home/mfwolffe/lanes/yw07b/core')
stage=root/'target/checked-core';stage.mkdir(exist_ok=True)
for name in ['fl','unicode','util']:
    shutil.copytree(root/'src'/name,stage/name,dirs_exist_ok=True)
source=(root/'src/fl_compile_test.lu').read_text();source=source[:source.rindex('fn main(')]
cases=['t_synthetic_execute','t_synthetic_disassemble','t_opcode_coverage','t_scopes','t_constants','t_small_ints','t_stack','t_lines','t_lengths','t_determinism','t_profile']
rows=[];failed=0
for i,name in enumerate(cases):
    file=stage/'case_test.lu';file.write_text(source+'fn main() { '+name+'() }\n')
    p=subprocess.run(['/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf','test','--deny-warnings','--nocapture','--no-native-fallback',str(file)],capture_output=True,text=True)
    (root/f'notes/yw07b-evidence/core/compile-case-{i:02d}.log').write_text(p.stdout+p.stderr)
    ok=p.returncode==0 and '1 passed; 0 failed; 0 rejected; 0 unsupported' in p.stdout+p.stderr
    failed+=not ok
    row=f'{i}\t{name}\t{"PASS" if ok else "FAIL"}\texit={p.returncode}'
    print(row,flush=True);rows.append(row)
(root/'notes/yw07b-evidence/core/compile-cases.tsv').write_text('\n'.join(rows)+'\n')
sys.exit(bool(failed))
