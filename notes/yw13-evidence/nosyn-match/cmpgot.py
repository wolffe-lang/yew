#!/usr/bin/env python3
"""cmpgot.py PORTDIR CDIR CASE...: for each case, the `--- got` block of the
port's pty log against the C oracle's highlighting-off (nosyn) got block,
byte for byte. A case equal on both is "port == C without highlighting"."""
import sys, os, difflib
port, cdir, cases = sys.argv[1], sys.argv[2], sys.argv[3:]
def got(path):
    try:
        t = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return None, None
    first = t.splitlines()[0] if t else ""
    if "--- got" not in t:
        return first, None
    g = t[t.index("--- got"):]
    # the got block ends at the next case line or end of file
    end = g.find("\npty: ", 1)
    g = g if end < 0 else g[:end]
    # The runner's preserved-state temp directories differ run to run.
    g = "\n".join(l for l in g.splitlines() if not l.startswith("pty state preserved: "))
    return first, g
same = 0
for c in cases:
    pf, pg = got(os.path.join(port, c + ".pty.log"))
    cf, cg = got(os.path.join(cdir, c + ".pty.log"))
    if pg is not None and cg is not None and pg == cg and pf == cf:
        same += 1
        print(f"SAME {c}: {pf}")
    else:
        print(f"DIFF {c}: port[{pf}] c[{cf}]")
        if pg and cg:
            d = list(difflib.unified_diff(cg.splitlines(), pg.splitlines(), "c-nosyn", "port", n=0, lineterm=""))
            for line in d[:16]:
                print("    " + line)
print(f"cmpgot: same={same} of {len(cases)}")
