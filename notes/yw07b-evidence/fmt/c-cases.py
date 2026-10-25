"""fmt black-box differential, C's half: each line of cases.txt as a script
run by C yew at the pin (black box), printing its body's value with io.print
or the raise as `!kind: msg` (flfix's rendering); one line of hex per case.
Usage: python3 -I c-cases.py YEW CASES (inside the lane container)."""
import os, subprocess, sys, tempfile
yew, cases = sys.argv[1], sys.argv[2]
prelude = "import fmt\nimport math\nimport map\nimport list\nimport str\nimport io\n"
with open(cases, encoding="utf-8") as fh:
    lines = [l.rstrip("\n") for l in fh if l.strip()]
d = tempfile.mkdtemp()
for i, body in enumerate(lines):
    p = os.path.join(d, f"c{i}.fl")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(prelude + "fn case_body() {\n" + body + "\n}\n"
                 + "try { io.print(case_body()) } catch e { io.print(fmt.f(\"!{}: {}\", e.kind, e.msg)) }\n")
    r = subprocess.run([yew, "fl", p], capture_output=True)
    out = r.stdout
    if out.endswith(b"\n"):
        out = out[:-1]
    if r.returncode != 0 or r.stderr:
        out = b"<C exit %d: " % r.returncode + r.stderr.strip() + b">"
    print(out.hex())
