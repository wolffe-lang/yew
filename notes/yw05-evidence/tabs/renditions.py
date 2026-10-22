#!/usr/bin/env python3
# yw05-tabs: s57.8's renditions (DoD 2: the tab roles degrade
# deterministically through every rendition), witnessed against C yew's own
# goldens. For each case named, run it through tools/goldens with
# YEW_PTY_DIFF=full and compare: a green case is the whole screen equal; a
# red one (its document rows are a later lane's: syntax colours, yw10) is
# compared on the STRIP ROW alone — row 1's text, and each cell's resolved
# style (the class letter looked up in the legend) — so the line printed
# says whether the tab strip is C's cell for cell in that rendition.
# Run in the container from the repository root (RULES §5):
#   python3 notes/yw05-evidence/tabs/renditions.py BIN CASE...
import os, subprocess, sys

def blocks(text):
    # The full diff: "--- want\n<golden>--- got\n<snapshot>" (snapshot.c).
    w = text.split("--- want\n", 1)[1]
    want, got = w.split("--- got\n", 1)
    return want, got

def parse(golden):
    lines = golden.splitlines()
    t = lines.index("--- text")
    s = lines.index("--- style")
    g = lines.index("--- legend")
    text = lines[t + 1:s]
    style = lines[s + 1:g]
    legend = {}
    for l in lines[g + 1:]:
        if len(l) > 2 and l[1] == " ":
            legend[l[0]] = l[2:]
        else:
            break
    return text, style, legend

def row_cells(style_row, legend):
    return [legend.get(ch, "?" + ch) for ch in style_row]

binary = sys.argv[1]
status = 0
for case in sys.argv[2:]:
    env = dict(os.environ, YEW_PTY_DIFF="full")
    subprocess.run(["tools/goldens", "--yew", binary, "--demo", "target/tools/demo_paint",
                    "--suite", "pty", "--case", case], env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = open("target/oracle/goldens/pty.log").read()
    if f"pty: {case}: ok" in log.splitlines():
        print(f"renditions: {case}: ok (the whole screen is C's)")
        continue
    if "--- want\n" not in log:
        print(f"renditions: {case}: RED with no diff to compare: {log.strip()[:300]}")
        status = 1
        continue
    want, got = blocks(log)
    wt, ws, wl = parse(want)
    gt, gs, gl = parse(got)
    same_text = wt[0] == gt[0]
    same_style = row_cells(ws[0], wl) == row_cells(gs[0], gl)
    first = next((i for i in range(min(len(wt), len(gt))) if wt[i] != gt[i] or
                  row_cells(ws[i], wl) != row_cells(gs[i], gl)), None)
    verdict = "the strip row is C's" if same_text and same_style else "the strip row DIFFERS"
    print(f"renditions: {case}: RED; {verdict} (text {'=' if same_text else '!='}, "
          f"style {'=' if same_style else '!='}); first differing row {None if first is None else first + 1}")
    print(f"renditions:   want row 1: {wt[0]!r}")
    print(f"renditions:   got  row 1: {gt[0]!r}")
    if not (same_text and same_style):
        status = 1
sys.exit(status)
