#!/usr/bin/env python3
import os,pathlib,shutil,subprocess,sys
root=pathlib.Path('/home/mfwolffe/lanes/yw07b/core')
stage=root/'target/checked-core';stage.mkdir(exist_ok=True)
for name in ['fl','unicode','util']:
    shutil.copytree(root/'src'/name,stage/name,dirs_exist_ok=True)
source=(root/'src/fl_compile_test.lu').read_text();source=source[:source.rindex('fn main(')]
cases=['fl_compile_synthetic_opcodes_execute', 'fl_compile_synthetic_opcodes_disassemble', 'fl_compile_every_opcode_is_covered', 'fl_compile_rejects_bad_scopes', 'fl_compile_dedupes_constants', 'fl_compile_small_ints_avoid_the_constant_pool', 'fl_compile_tracks_max_stack', 'fl_compile_lines_are_recorded_for_every_op', 'fl_compile_operand_lengths_match_the_emitter', 'fl_compile_is_deterministic_across_instances', 'fl_compile_profile_markers_are_explicit_and_executed']
rows=[];failed=0
tag=os.environ.get("CASE_TAG","")
prefix="compile"+("-"+tag if tag else "")
for i,name in enumerate(cases):
    file=stage/'case_test.lu';file.write_text(source+'fn main() { '+name+'() }\n')
    p=subprocess.run(['/home/mfwolffe/lanes/yw07b/yew/.wolf-bin/wolf','test','--deny-warnings','--nocapture','--no-native-fallback',str(file)],capture_output=True,text=True)
    (root/f'notes/yw07b-evidence/core/{prefix}-case-{i:02d}.log').write_text(p.stdout+p.stderr)
    ok=p.returncode==0 and '1 passed; 0 failed; 0 rejected; 0 unsupported' in p.stdout+p.stderr
    failed+=not ok
    row=f'{i}\t{name}\t{"PASS" if ok else "FAIL"}\texit={p.returncode}'
    print(row,flush=True);rows.append(row)
(root/('notes/yw07b-evidence/core/'+prefix+'-cases.tsv')).write_text('\n'.join(rows)+'\n')
sys.exit(bool(failed))
