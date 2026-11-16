# Selection contracts

These tests describe the selection redesign. They are **held contract rows**,
not a green feature gate: the current editor is expected to fail several rows.
Do not add them to the default passing suite or treat a failure as an expected
success. Each implementation stage can adopt its rows when it fixes them.

Run from any directory with an explicit binary, matching runtime, and a new
output directory:

```sh
python3 -I tests/selection/run.py --self-test
python3 -I tests/selection/run.py --binary /path/to/yew \
  --runtime /path/to/runtime --output /path/to/new-output
```

`--case NAME` selects one row and can be repeated. Exit **0** means every
selected contract passed, **1** means a behavioral failure, and **2** means a
control or infrastructure failure. The JSON result, raw terminal bytes and
child metrics remain in the output directory. A process exit of zero alone is
not a contract pass. No real clipboard backend or network server is used.

The 23 rows cover mode restoration from Insert/Word/Block, 16/256/truecolor
selection visibility, copy/cut and internal paste without a system clipboard,
insert-origin replacement, initial line selection, Alt-click cursors,
Ctrl+Alt+Up/Down and repeated vertical additions, keyboard and Ctrl-click
navigation, empty-selection boundaries confined to the active pane,
duplicate-press idempotence, and context
menus on Ctrl+Shift+click and right-click. Existing
correct behavior is a positive control, not a manufactured failure. The fake
language server records requested positions and returns a local target file.

The child starts with a fresh HOME, explicit `/bin/sh`, no workspace config,
and the provided runtime. **Do not use `--clean`: it loads only the panic
keymap.** The fixture must enter I and H before a selection is judged. Ordinary
Shift-selection does not necessarily display its anchor in the current
statusline; do not require an `@anchor` suffix as proof of a selection.

The small VT reader handles the escape families these one-cell fixtures emit;
it is not a general-purpose emulator or Unicode geometry test. The existing
Unicode, rectangle, undo and multi-cursor unit suites remain necessary.
Unsupported/truncated output is an infrastructure error, never a feature red.
The parent samples only its own recorded child's RSS and stops that child if
it exceeds 2 GiB. Run on an otherwise approved test host with sufficient free
memory; run only one copy of this suite at a time.

## Physical mouse census

In each terminal, run:

```sh
python3 -I tests/selection/mouse-census.py --terminal 'NAME VERSION'
```

Capture is free-form: no steps, Space prompts or timers. Click with no
modifier, Ctrl, Ctrl+Shift, Alt, Shift, and the right button, in any order.
Each complete input event prints immediately with button, modifier bits,
press/release, coordinates and its raw bytes. Press `q` or Ctrl+C when done;
the script restores raw mode/reporting and prints all events as JSON. Paste
that JSON with terminal name/version and settings that affect reporting.
It changes no terminal preferences or clipboard. Add `--shift-escape` to request
Shift reports with `CSI > 1 s`; the restore path sends `CSI > 0 s`. A terminal
configured to forbid Shift capture can ignore the request. The JSON states
whether it was requested.

The transport regression runs the actual census process in a PTY, injects all
six press/release pairs (including split escape sequences), checks live output
and the final JSON, and compares terminal settings before and after `q` and
Ctrl+C. On macOS it also runs through `/usr/bin/script`:

```sh
python3 -I tests/selection/test_census.py --output /path/to/new-census-test
```

A missing report is **not received**, not proof of why it was intercepted. A
secondary-click report for physical Ctrl-click is different from a Ctrl-modified
left report. URL gestures may behave differently from the plain target; for
example, kitty's default Ctrl+Shift-click link action can consume the click.
Terminal-generated selection bypasses and macOS secondary-click translation
must be reported as observations, never assumed from an injected SGR sequence.

The editor contract is Ctrl-click for definition, Ctrl+Shift+click for its
context menu, and right-click for the same menu. SGR modifiers are Shift=4,
Alt/Meta=8 and Ctrl=16; Ctrl+Shift is 20. Standard SGR mouse has no Command/Super
bit. Keyboard navigation remains the fallback when a terminal owns a gesture.
