"""yw13 inventory classifier: for each YEW_PTY_DIFF=full log in DIR, split
the want and got snapshots into text rows, style rows and legend, and
report whether the text grid is identical and which cells' resolved
styles differ (row, column span, and the golden's text on that row).

  python3 -I inv-classify.py FULL_DIR GOLDEN_DIR
"""
import os
import re
import sys


def sections(snap):
    out = {}
    cur = "head"
    out[cur] = []
    for line in snap.split("\n"):
        m = re.match(r"^--- (\w+)$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        out[cur].append(line)
    return out


def legend(lines):
    leg = {}
    for line in lines:
        m = re.match(r"^(\S) (.*)$", line)
        if m:
            leg[m.group(1)] = m.group(2)
    return leg


def split_full(text):
    a = text.find("--- want\n")
    b = text.find("\n--- got\n")
    if a < 0 or b < 0:
        return None, None
    want = text[a + len("--- want\n"):b]
    got = text[b + len("\n--- got\n"):]
    return want, got


def classify(want, got):
    ws, gs = sections(want), sections(got)
    head_eq = ws.get("head") == gs.get("head")
    text_eq = ws.get("text") == gs.get("text")
    wl, gl = legend(ws.get("legend", [])), legend(gs.get("legend", []))
    rows = {}
    wst, gst = ws.get("style", []), gs.get("style", [])
    for r in range(max(len(wst), len(gst))):
        a = wst[r] if r < len(wst) else ""
        b = gst[r] if r < len(gst) else ""
        for c in range(max(len(a), len(b))):
            x = wl.get(a[c], "?") if c < len(a) else "<none>"
            y = gl.get(b[c], "?") if c < len(b) else "<none>"
            if x != y:
                rows.setdefault(r, []).append((c, x, y))
    other = sorted(k for k in set(ws) | set(gs)
                   if k not in ("head", "text", "style", "legend") and ws.get(k) != gs.get(k))
    return head_eq, text_eq, rows, ws.get("text", []), other


def spans(cols):
    out = []
    for c in cols:
        if out and c == out[-1][1] + 1:
            out[-1][1] = c
        else:
            out.append([c, c])
    return ",".join(f"{a}-{b}" if a != b else str(a) for a, b in out)


def main():
    full_dir = sys.argv[1]
    for name in sorted(os.listdir(full_dir)):
        if not name.endswith(".pty.log"):
            continue
        case = name[: -len(".pty.log")]
        text = open(os.path.join(full_dir, name), encoding="utf-8", errors="replace").read()
        want, got = split_full(text)
        if want is None:
            print(f"CASE {case} NODIFF (no full diff in log: {text[:120]!r})")
            continue
        head_eq, text_eq, rows, wtext, other = classify(want, got)
        ncell = sum(len(v) for v in rows.values())
        wantfg = sorted({x.split()[0] for v in rows.values() for (_, x, _) in v})
        print(f"CASE {case} head_eq={head_eq} text_eq={text_eq} style_cells={ncell} "
              f"rows={len(rows)} other_sections_differ={other} want_fgs={wantfg}")
        for r in sorted(rows):
            cols = [c for (c, _, _) in rows[r]]
            row_text = wtext[r] if r < len(wtext) else ""
            print(f"  row {r}: cols {spans(cols)} | {row_text.rstrip()}")


main()
