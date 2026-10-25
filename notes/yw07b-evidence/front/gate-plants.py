#!/usr/bin/env python3
"""Negative controls for differential/spec drift checkers; originals untouched."""
import os
from pathlib import Path
import shutil
import subprocess
root=Path(__file__).resolve().parents[3]
stage=root/'target/front/gate-plants';stage.mkdir(exist_ok=True)
wrapper=stage/'wrong-driver'
wrapper.write_text('#!/bin/bash\n"'+str(root/'target/tools/fl-front')+'" "$@"\ns=$?\ncase "$2" in */tests/fletch/01-lexical.fl) printf "PLANTED-DUMP-DRIFT\\n";; esac\nexit "$s"\n')
wrapper.chmod(0o755)
out=root/'notes/yw07b-evidence/front'
run=subprocess.run(['python3','-I',str(root/'tools/check-fl-front'),'--oracle-tree',os.environ['SAGITTA_TREE'],'--oracle-driver',str(root/'target/front/oracle-front'),'--driver',str(wrapper),'--output',str(stage/'diff')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/'plant-differential.log').write_bytes(run.stdout+b'\nexit='+str(run.returncode).encode()+b'\n')
assert run.returncode==1 and b'89 files; 88 pass' in run.stdout
specroot=stage/'spec';(specroot/'tools').mkdir(parents=True,exist_ok=True);(specroot/'docs').mkdir(exist_ok=True)
shutil.copy2(root/'tools/check-fletch-spec',specroot/'tools/check-fletch-spec')
shutil.copy2(root/'sagitta.pin',specroot/'sagitta.pin')
(specroot/'docs/fletch-spec.md').write_bytes((root/'docs/fletch-spec.md').read_bytes()+b'PLANTED-SPEC-DRIFT\n')
run=subprocess.run([str(specroot/'tools/check-fletch-spec'),os.environ['SAGITTA_TREE']],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/'plant-spec.log').write_bytes(run.stdout+b'\nexit='+str(run.returncode).encode()+b'\n')
assert run.returncode==1
print('PASS differential/spec plants: each rejected planted drift with exit1')
