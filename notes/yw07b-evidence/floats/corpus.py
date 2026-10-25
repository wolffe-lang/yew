#!/usr/bin/env python3
# Inputs only; no Python output is treated as the reference conversion.
import math, pathlib, random, struct, sys
out = pathlib.Path(sys.argv[1])
rng = random.Random(1)
bits = [0, 1, 2, (1<<52)-1, 1<<52, (1<<52)+1,
        0x7fefffffffffffff, 0x7ff0000000000000, 0x7ff8000000000000,
        0x7ff0000000000001, 0x7fffffffffffffff]
bits += [x | (1<<63) for x in bits]
for e in range(-1074, 1024):
    value = math.ldexp(1.0,e)
    n = struct.unpack('>Q',struct.pack('>d',value))[0]
    bits.extend([max(0,n-1),n,n+1,n|(1<<63)])
for e in range(-323,309):
    value = float('1e'+str(e))
    n = struct.unpack('>Q',struct.pack('>d',value))[0]
    bits.extend([max(0,n-1),n,n+1,n|(1<<63)])
for x in (0.5,1.5,2.5,3.5,1.25,1.125,1.015625):
    n=struct.unpack('>Q',struct.pack('>d',x))[0]
    bits.extend([n-1,n,n+1])
bits += [rng.getrandbits(64) for _ in range(100000)]
parse=['', ' ', '+', '-', '.5', '1.', '1.e2', '1_2.3', '1.2_3',
       '1e', '1e+', '1e-99999', '-1e-99999', '1e99999', '  +3.25x',
       'inf','INFINITY','-inf','nan','-nan','nan(123)','nan(payload)',
       'nan()','nan(+1)','0x1p2','0X.8P+1','0x','0x.','0x1p',
       '0x1p-1074','0x1p-1075','0x1.0000000000001p-1075',
       '0x1.fffffffffffffp1023','0x1.fffffffffffff8p1023']
with out.open('w') as f:
    for n in bits:
        signed = n if n < (1<<63) else n-(1<<64)
        f.write(f'B {signed}\n')
    for s in parse: f.write('P '+s+'\n')
    for n in bits:
        x=struct.unpack('>d',struct.pack('>Q',n))[0]
        f.write('P '+repr(x)+'\n')
        if math.isfinite(x): f.write('P '+x.hex()+'\n')
print('binary_rows',len(bits),'parse_specials',len(parse))
