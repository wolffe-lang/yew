#!/usr/bin/env python3
"""gen-cmdtab — the command registry's descriptor table, as data.

Reads sagitta's `src/edit/cmd.c` at `sagitta.pin` (the `builtins[]`
descriptor table and the `builtin_meta[]` E-mode grammar rows) and emits
`src/edit/cmdtab.lu`: one `str` constant of rows, one per command in C's
registration order (so a command's id is C's id), and nothing else —
the table is data, the lookups are hand-written (`edit.cmd`). A row is
seven fields separated by 0x1f:

    name, impl, arity, flags, help, word, meta

`impl` is C's handler NAME (`yew_edit_cmd_insert_at`): two descriptors
with one handler are an alias pair (the registry test compares them), and
`edit.cmd` maps the handler names it implements onto its `match`; `meta`
is `argspec^range_policy^abbrev` when `builtin_meta[]` names the command,
else empty. C's flag and arity enumerators are spelled out as numbers
(`cmd.h:84-126`).

Usage: gen.py SAGITTA_TREE OUT   (tools/check-cmdtab regenerates and diffs)
"""
import re
import sys

ARITY = {"YEW_ARITY_NONE": 0, "YEW_ARITY_INT": 1, "YEW_ARITY_STR": 2,
         "YEW_ARITY_OPT_INT": 3, "YEW_ARITY_OPT_STR": 4}
FLAGS = {"YEW_CMD_REPEATABLE": 1 << 0, "YEW_CMD_TAKES_COUNT": 1 << 1,
         "YEW_CMD_RECORDABLE": 1 << 2, "YEW_CMD_NEEDS_WIN": 1 << 3,
         "YEW_CMD_CHANGES_BUFFER": 1 << 4, "YEW_CMD_PROMPTS": 1 << 5,
         "YEW_CMD_DEFERRED": 1 << 6, "YEW_CMD_MULTI_AGGREGATE": 1 << 7,
         "YEW_CMD_CAPTURES_TEXT": 1 << 8, "YEW_CMD_INTERNAL": 1 << 9,
         "YEW_CMD_INTERACTIVE": 1 << 10}
RP = {"YEW_RP_FORBID": 0, "YEW_RP_OPT": 1, "YEW_RP_LINE": 2,
      "YEW_RP_BUFFER": 3, "YEW_RP_REQUIRED": 4}

TOKEN = re.compile(r'\s+|/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|[A-Za-z_][A-Za-z0-9_]*|0[xX][0-9a-fA-F]+[uU]?|[0-9]+[uU]?|<<|.', re.S)


def tokens(text):
    for m in TOKEN.finditer(text):
        t = m.group(0)
        if t.isspace() or t.startswith("/*") or t.startswith("//"):
            continue
        yield t


def unquote(t):
    body = t[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            n = body[i + 1]
            simple = {"n": 10, "t": 9, "\\": 92, '"': 34, "'": 39, "0": 0}
            if n in simple:
                out.append(simple[n])
                i += 2
                continue
            if n == "x":
                j = i + 2
                while j < len(body) and body[j] in "0123456789abcdefABCDEF":
                    j += 1
                out.append(int(body[i + 2:j], 16))
                i = j
                continue
            raise SystemExit(f"gen-cmdtab: unknown escape \\{n}")
        out += c.encode("utf-8")
        i += 1
    return out.decode("utf-8")


def table(text, start_marker):
    at = text.index(start_marker)
    at = text.index("{", at + len(start_marker))
    toks = list(tokens(text[at:]))
    rows, depth, field, fields, i = [], 0, [], [], 0
    while i < len(toks):
        t = toks[i]
        i += 1
        if t == "{":
            depth += 1
            if depth == 2:
                fields, field = [], []
            continue
        if t == "}":
            depth -= 1
            if depth == 1:
                fields.append(field)
                rows.append(fields)
            if depth == 0:
                break
            continue
        if depth == 2:
            if t == ",":
                fields.append(field)
                field = []
            else:
                field.append(t)
    return rows


def value(field, enum):
    total = 0
    for t in field:
        if t == "|":
            continue
        if t in enum:
            total |= enum[t]
        elif t.rstrip("uU").isdigit():
            total |= int(t.rstrip("uU"))
        elif t in ("(", ")"):
            continue
        else:
            raise SystemExit(f"gen-cmdtab: unknown flag token {t}")
    return total


def text_of(field):
    if field == ["NULL"]:
        return None
    return "".join(unquote(t) for t in field)


def main():
    tree, out = sys.argv[1], sys.argv[2]
    src = open(f"{tree}/src/edit/cmd.c", encoding="utf-8").read()
    builtins = table(src, "static const CmdDesc builtins[] =")
    meta = {}
    for row in table(src, "static const BuiltinMeta builtin_meta[] ="):
        name = text_of(row[0])
        meta[name] = "{}^{}^{}".format(text_of(row[1]), value(row[2], RP),
                                       text_of(row[3]) or "")
    lines = []
    for row in builtins:
        if len(row) not in (5, 6):
            raise SystemExit(f"gen-cmdtab: a descriptor with {len(row)} fields")
        name = text_of(row[0])
        impl = "".join(row[1])
        arity = value(row[2], ARITY)
        flags = value(row[3], FLAGS)
        help_ = text_of(row[4])
        word = text_of(row[5]) if len(row) == 6 else None
        for s in (name, help_, word or "", meta.get(name, "")):
            if "\x1f" in s or "\n" in s or '"' in s or "\\" in s:
                raise SystemExit(f"gen-cmdtab: an unencodable byte in {name}")
        lines.append("\x1f".join([name, impl, str(arity), str(flags), help_,
                                  word or "", meta.get(name, "")]))
    missing = sorted(set(meta) - {l.split("\x1f")[0] for l in lines})
    if missing:
        raise SystemExit(f"gen-cmdtab: builtin_meta names unknown commands: {missing}")
    with open(out, "w", encoding="utf-8") as f:
        f.write("//! edit.cmdtab — GENERATED by tools/gen-cmdtab from sagitta\n")
        f.write("//! `src/edit/cmd.c` at `sagitta.pin` (`builtins[]`, `builtin_meta[]`);\n")
        f.write("//! do not edit. `tools/check-cmdtab` regenerates it and diffs. One row\n")
        f.write("//! per command in C's registration order (a row's index + 1 is C's\n")
        f.write("//! `CmdId`), seven fields separated by 0x1f: name, C handler, arity,\n")
        f.write("//! flags, help, recorder word, E-mode meta (`argspec^range^abbrev`).\n\n")
        f.write("/// The number of descriptor rows in `CMDTAB`.\n")
        f.write(f"pub const CMDTAB_ROWS: int = {len(lines)}\n\n")
        f.write("/// The descriptor rows, one per line, fields separated by 0x1f.\n")
        f.write('pub const CMDTAB: str = """\n')
        for l in lines:
            enc = l.replace("{", "{{").replace("}", "}}").replace("\x1f", "\\x1f")
            f.write(enc + "\n")
        f.write('"""\n')


main()
