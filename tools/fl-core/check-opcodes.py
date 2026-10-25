#!/usr/bin/env python3
"""Compare the single Wolf opcode table and discriminants with pinned C."""
import pathlib,re,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[2]
oracle=pathlib.Path(sys.argv[1])
pin='9ace98c2adfeb9d63e7da4bdb4fd6e29ae5c3e4a'
c=subprocess.check_output(['git','-C',str(oracle),'show',pin+':src/fl/opcodes.def'],text=True)
rows=re.findall(r'^FL_OP\((\w+),\s*"([bsw]*)",\s*([+\-0-9]+|FL_EFF_VAR),',c,re.M)
w=(root/'src/fl/opcodes.lu').read_text()
actual=re.findall(r'(\d+) => FlOpcode\s*\{\s*name: "(\w+)",\s*operands: "([bsw]*)",\s*effect: ([\-0-9]+|FL_EFF_VAR)',w)
expected=[(str(i),n,o,str(int(e)) if e!='FL_EFF_VAR' else e) for i,(n,o,e) in enumerate(rows)]
assert len(rows)==60 and len(rows)<=240
assert actual==expected,(actual,expected)
for i,(name,_,_) in enumerate(rows):
    assert re.search(r'pub const FL_OP_'+name+r': int = '+str(i)+r'\b',w)
print('PASS all 60 opcode discriminants/operands/effects match pinned C')
