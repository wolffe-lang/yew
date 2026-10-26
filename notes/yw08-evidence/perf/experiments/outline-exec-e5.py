#!/usr/bin/env python3
"""yw08 experiment E5 (E4 with INDEX/FIELD kept hot): move fl_vm_exec's cold opcode arms (CLOSURE..TRACE_LINE
and the unknown-opcode bug) and its FL_VM_CHECKS block into two functions, so
the hot loop compiles smaller. Pure code motion. vm.lu in, overlay out."""
import sys
src = open(sys.argv[1]).read()

def one(s, needle):
    assert s.count(needle) == 1, (needle[:60], s.count(needle))
    return s.index(needle)

# 1. The checks block: from `if checks {` (after the opcode read) to the line
#    before `if vm.tracing`.
cstart = one(src, '            if checks {\n                if op >= FL_OP_COUNT')
cend = one(src, '            if vm.tracing { (mut vm.trace).push(op as byte) }\n')
checks = src[cstart:cend]
assert checks.rstrip().endswith('}')
inner = checks[len('            if checks {\n'):checks.rstrip().rindex('}')]
src = src[:cstart] + '            if checks { fl_exec_checks(mut vm, fnidx, ci, framebase, pc, op) }\n' + src[cend:]

# 2. The cold arms: from CLOSURE to the unknown-opcode default, inclusive.
astart = one(src, '                39 => { // CLOSURE\n')
dflt = '                _ => fl_vm_bug(mut vm, fnidx, pc, op, "fl vm: unknown opcode"),\n'
aend = one(src, dflt) + len(dflt)
arms = src[astart:aend]
hs = arms.index('                42 | 43 => { // INDEX_GET / INDEX_SET\n')
he = arms.index('                46 => { // ITER_NEW\n')
hot = arms[hs:he]
arms = arms[:hs] + arms[he:]
src = src[:astart] + hot + src[astart:]
astart += len(hot); aend += len(hot)
cont = '                        if bound.t != 0 { fl_push(mut vm, bound); continue }\n'
assert cont in hot and 'return' not in arms and 'continue' not in arms
src = src[:astart] + '                _ => fl_exec_cold(mut vm, op, fi, fnidx, ci, framebase, pc),\n' + src[aend:]

def dedent(text, n):
    return ''.join(l[n:] if l.startswith(' ' * n) else l for l in text.splitlines(True))

new = ('\n/// FL_VM_CHECKS\' per-instruction invariants (s32 §9), out of the hot loop\n'
       '/// (yw08, yew#77): fl_vm_exec stays smaller; called only when checks is on.\n'
       'fn fl_exec_checks(mut vm: FlVm, fnidx: int, ci: int, framebase: int, pc: int, op: int) {\n'
       + dedent(inner, 12) +
       '}\n\n'
       '/// The dispatch loop\'s cold opcodes, CLOSURE..TRACE_LINE but INDEX/FIELD, and the unknown\n'
       '/// opcode, out of fl_vm_exec (yw08, yew#77) so its hot arms compile as a\n'
       '/// smaller function. Pure code motion; no arm returns from the loop.\n'
       'fn fl_exec_cold(mut vm: FlVm, op: int, fi: int, fnidx: int, ci: int, framebase: int, pc: int) {\n'
       '    match op {\n' + dedent(arms, 8) + '    }\n}\n')
anchor = one(src, '\n/// Execute a compiled top-level chunk, resetting transient VM state on exit.')
src = src[:anchor] + '\n' + new + src[anchor:]
open(sys.argv[2], 'w').write(src)
print('checks lines', inner.count('\n'), 'cold arm lines', arms.count('\n'))
