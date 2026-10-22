#!/usr/bin/env python3
# yw05-hot: the measurements table (markdown) from a run-ptymem.sh output:
# one row a phase and file, B/key for each binary label in the run's order,
# the port/C ratio of the head, the before/after factor, and whether the
# port's output bytes during the measured keys were the same before and
# after (out_sha). usage: table.py ptymem-final.txt
import re, sys
rows = {}
labels = []
pat = re.compile(r"^(\S+) (R|K) (?:yw04-driver )?\S+ (\S+): n=(\d+) .*?\((-?[\d.]+) B/key\)(?: quarters=\[[^\]]*\] out=(\d+) B \(\d+ B/key\) out_sha=(\w+) ([\d.]+) ms/key)?")
for line in open(sys.argv[1]):
    m = pat.match(line)
    if not m:
        continue
    lb, f, ph, n, bkey, out, sha, ms = m.groups()
    if "yw04-driver" in line:
        ph = "yw04-driver " + ph
    if lb not in labels:
        labels.append(lb)
    rows.setdefault((ph, f), {})[lb] = (float(bkey), sha, out, ms)
print("| phase | file | " + " | ".join(f"{l} B/key" for l in labels) + " | head / C (release) | before / head (release, native) | port bytes same |")
print("|---|---|" + "---:|" * len(labels) + "---:|---:|---|")
for (ph, f), d in rows.items():
    cells = [f"{d[l][0]:,.0f}" if l in d else "" for l in labels]
    def b(l):
        return d[l][0] if l in d else None
    c, hr, hn, br, bn = b("C"), b("hot-release"), b("hot-native"), b("base-release"), b("base-native")
    ratio = f"{hr / c:,.0f}x" if c and hr is not None and c > 0 else "-"
    fr = f"{br / hr:,.1f}x" if hr and br is not None and hr > 0 else "-"
    fn = f"{bn / hn:,.1f}x" if hn and bn is not None and hn > 0 else "-"
    fac = f"{fr}, {fn}"
    same = ""
    shas = {l: d[l][1] for l in d if l != "C" and d[l][1]}
    if shas:
        same = "yes" if len(set(shas.values())) == 1 else "no: " + ", ".join(f"{l} {s[:8]}" for l, s in shas.items())
    print(f"| {ph} | {f} | " + " | ".join(cells) + f" | {ratio} | {fac} | {same} |")
