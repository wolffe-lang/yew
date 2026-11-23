# Copied harness: the read after the reap (yew#124)

Three gated PTY cases signal the editor from outside with a signal that runs
none of its code: `restore_bus` (SIGBUS), `notepad_restore_segv` (SIGSEGV) and
`notepad_restore_kill` (SIGKILL). C yew restores the terminal in its fatal
handler before it dies, except for SIGKILL, where its guardian sibling restores
after the death. The port cannot run code on any of the three, so its guard
sibling, which still holds the terminal, writes the restore bytes after the
death (`src/term/tty.lu`, the guard notes).

The pinned harness waits for the reap, reads once more, and then searches the
capture for the restore bytes (`tests/pty/harness.c`, `wait_for_exit` and
`ptc_expect_output`). Bytes the guard writes after that one read are missed,
and the case fails though the terminal was restored. That is yew#124, seen on
hosted Linux runners and the reason the three cases are advisory on macOS.

`restore-after-reap.json` changes `ptc_expect_output` alone. When the expected
bytes are not in the capture and the child has been reaped while the terminal
is still open, it reads on until the bytes arrive, the terminal's last holder
closes it (EOF), or 2000 ms pass, whichever comes first. A capture that
already holds the bytes, or a child not yet reaped, reads nothing more. A
failure keeps its message and says why the wait ended: ` after the terminal
closed` or ` after a 2000 ms wait past the reap`.

What the check then holds the port to: the restore bytes reach the terminal
before its last holder releases it, not before the editor's death. For an
outside SIGSEGV or SIGBUS the port's restore lands after the death, as C's
does for SIGKILL, so a shell prompt can come before it.

`tools/oracle-vt.py` applies this specification with the test VT's, under the
same rules: the original blob is pinned by revision and SHA256, the literal
context must match once, no other oracle file may change, and the result is
saved in `target/oracle/harness.sha256` for the build rigs to pin. The C editor,
the cases in `tests/pty/registry.c` and every golden are unchanged.

```sh
tools/oracle --prepare-only --jobs 2
python3 -I tools/oracle-vt-test.py
```
