# Copied test-VT extension

The editor emits XTSHIFTESCAPE to request Shift mouse reports. The pinned
reference test VT predates that non-visual protocol, so its copied test
implementation is adapted before running the original golden suite. The C
editor and all original goldens are unchanged.

`shift-capture.json` pins the reference revision and SHA256 of both original
files. Each literal context must match once. `tools/oracle-vt.py` permits only
`tests/pty/vt.c` and `tests/pty/vt.h` beneath this checkout's copied oracle,
refuses other tracked edits, unexpected bytes and symlinked paths, and supports
idempotent installation and verification. It derives the expected patched
bytes from the pinned git blobs and checked-in edits, not from an arbitrary
working copy.

```sh
tools/oracle --prepare-only --jobs 2
python3 -I tools/oracle-vt-test.py
```

Preparation does not compile. It saves the exact resulting file digests in
`target/oracle/vt.sha256`; build rigs must pin **both resulting files** by those
digests before compiling, as well as pinning the checked-in edit specification.
A deliberate acceptance-drop plant has a different derived C-file digest and
must have its own rig pin. Do not relax the production pin to run a plant.

The same tool applies a second specification, the harness's read after the
reap (`tests/oracle-harness/`, yew#124), to `tests/pty/harness.c` alone. It
saves that file's digest in `target/oracle/harness.sha256`; this file's pins
in `vt.sha256` do not change.

## Protocol and state

Exactly `CSI > 0 s` and `CSI > 1 s` are accepted. They do not alter cells,
cursor, colors or the existing mouse-mode bits. Other parameter spellings or
values still reach `unknown()`, including omitted, repeated, colon-form and
intermediate-space parameters.

The state records whether Shift capture is active, request/reset counts,
mouse-mode bits at active transitions, and counts of requests before mouse
setup or active resets after mouse teardown. Repeated resets after capture
was already disabled are idempotent. These fields are not added to golden
snapshots.

## Executable rows

On an approved build slot:

```sh
python3 -I tools/oracle-vt-check.py --cc clang
python3 -I tools/oracle-vt-check.py --cc clang --capture /path/to/editor-full.bin
```

The checker compiles only the small test-VT program and its dependencies.
Rows check startup/reset acceptance, unchanged visual state, detection of bad
setup/restore order, and twelve rejected forms. Inputs are split at every byte.
`--capture` additionally feeds a real editor output transcript and requires
requests and resets, correct ordering, no parser errors and capture disabled
at the end. Use raw editor output, not an input census. A capture is bounded
at 16 MiB.

`tools/oracle` runs these rows before building the reference programs. A
one-hunk acceptance-drop plant must fail `startup-shift-capture-and-restore`
and, when given a real capture, `startup-restore-capture`; a compile error or
pin refusal is not a successful plant witness. No relay filters the editor's
output, and no test-only option suppresses its protocol requests.
