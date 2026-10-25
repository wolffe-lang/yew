"""compare.py CASES PORT C: per case, identical or the two answers."""
import sys
cases = [l.rstrip("\n") for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
port = open(sys.argv[2]).read().split("\n")
c = open(sys.argv[3]).read().split("\n")
same = 0
for i, body in enumerate(cases):
    a, b = bytes.fromhex(port[i]), bytes.fromhex(c[i])
    if a == b:
        same += 1
    else:
        print(f"DIFF {i}: {body}\n  port: {a!r}\n  C:    {b!r}")
print(f"{same} of {len(cases)} identical")
