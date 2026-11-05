# yw11a — the LSP client core and diagnostics (sagitta s45, s46)

_yew's LSP client, its transport and its diagnostics, ported from sagitta's
`src/mod/lsp/` at `sagitta.pin` (`9ace98c2`), so that `wolf lsp` works in
the editor. The features (completion, hover, goto, references, rename,
highlight, symbols) are yw11b's._

## Prediction

Written before the first change (2026-11-05, base trunk `1218169e`, wolf
0.2.36 / lupin 0.1.58 / std `78b9d3cb`).

### The map

sagitta's `src/mod/lsp/` is 21 files and 11,283 lines. Each file, its wolf
unit, and which half of campaign 09 takes it:

| sagitta | lines | wolf unit | yw11a | yw11b |
|---|---|---|---|---|
| `json.c`, `json.h` | 1,184 | `lsp.json` (`src/lsp/json.lu`) | all: the parser, the accessors, the writer | — |
| `jsonrpc.c`, `jsonrpc.h` | 906 | `lsp.jsonrpc` (`src/lsp/jsonrpc.lu`) | all: framing, classification, the pending table, calls, notifications, replies, cancel, sweep, deadlines | — |
| `client.c`, `client.h` | 1,631 | `lsp.client` (pure half: the default table, roots, URIs, capabilities, `initialize`'s params, the lifecycle transitions) and `edit.lsp_client` (the half that takes the `Ed`: config from `init.fl`, the child as a framed job, the handshake, dispatch, `publishDiagnostics`, server requests, crash and restart, stop, the editor's shutdown wait) | all | the shadow request fields stay zero |
| `sync.c`, `sync.h` | 581 | `lsp.sync` (the document, positions, didOpen/didChange/didSave/didClose bodies) and `edit.lsp_sync` (the editor hooks) | all | — |
| `diag.c`, `diag.h` | 901 | `edit.lsp_diag` | all: the store on marks, the gutter signs, the underline attributes, the cursor hint, the picker, the jump | — |
| `lsp.c`, `lsp.h` | 567 | `edit.lsp` | the boundary: info, log, start (restart), stop, diagnostics, diag_step, attached, the status badge, pump, free, buffer open/save/close | complete, hover, signature, the gotos, references, rename, symbols, the signature auto-trigger: they keep refusing by name (Sprint 47, yw11b) |
| `shim.c` | 230 | none | the disabled-module stub; the port is always the full build (ruling #93 R4), so it is not ported | — |
| `features.c`, `.h` | 2,450 | — | — | all |
| `rename.c`, `.h` | 1,581 | — | — | all |
| `pickers.c`, `.h` | 744 | — | — | all |
| `highlight.c`, `.h` | 508 | — | `yew_lsp_highlight_buffer_clear`'s two calls are no-ops until yw11b, named where they stand | all |

Outside `src/mod/lsp/`, yw11a ports the call sites the client and the
diagnostics need: `src/edit/lsp_cmds.c`'s info, log, restart, stop,
diagnostics and diag_next/prev (the rest refuse by name, yw11b);
`src/edit/notify.c:44,57` (the edit hooks); `src/edit/loop.c:614` (the
pump); `src/edit/ed.c:277,482,490,862,2061,2141-2147` and
`src/edit/file_cmds.c:367` (open, save, close, free);
`src/edit/batch_test.c:633,638-660` (`t.pump`, `t.job_stderr`);
`src/edit/job.c`'s framed writer (`job_write_framed`, `:1726-1755`) and
the framed deadline and tick (`:1893-1900`, `:1948-1950`);
`src/ui/draw.c:715-740` (the diagnostic underline) and `:1063` (the
cursor hint); `src/ui/statusline.c:554-588` (segment 12, the LSP and
diagnostic badge); `src/ui/ctxrows.c:408` (the document menu's LSP
section, through `lsp_attached`); and the demo's `s46_diag_*` scenes
(`tests/pty/demo_paint.c:586-690, 829-832, 935-938`).

The unit tests follow their units: `test_json.c`, `test_json_num.c`,
`test_jsonw.c`, `test_jsonrpc.c`, `test_jsonrpc_frame.c`,
`test_lsp_uri.c`, `test_lsp_caps.c`, `test_lsp_config.c`,
`test_lsp_sync.c`, `test_lsp_diag.c`, `test_lsp_transport.c` and
`test_lsp_life.c`'s lifecycle, root, table, stale-drop and fakelsp
session cases are yw11a's. `test_lsp_life.c`'s feature cases (completion,
hover, signature, definition, references, symbols, highlight),
`test_lsp_gate.c`, `test_lsp_completion.c`, `test_lsp_nav.c`,
`test_lsp_rename.c`, `test_lsp_snippet.c`, `test_lsp_symbols.c` and
`test_lsp_highlight.c` are yw11b's.

**What the client needs from units not yet ported.**
- **yw10's `syn`: the buffer's language.** C sets `Buffer.lang` from
  `yew_syn_lang_for_scored` (`ed.c:183-232`), and the client starts a
  server only for a buffer with a language (`client.c:1133`, `lsp.c:446`).
  The port has no language detection. yw11a ports the minimum: the
  builtin detection index's path half (extensions and file names,
  `syn/defs.c:3614-3622`'s `path_language`), with no shebang, no first
  line, no Fortran scoring and no user definitions; those stay yw10's,
  and a buffer they would name has no language, as now. That is
  **R-yw11-1**.
- **yw11b's highlight, shadow and symbol index:** the sync hook clears
  the document highlight (`sync.c:430-431`), close cancels the shadow
  request (`client.c:1186-1192`), and `ed.lsp.symbols` falls back to the
  index. None of it is reachable before yw11b: the calls are named no-ops
  or keep their refusals.
- **yw12's ai and yw14's plug:** nothing.

**JSON: sagitta's, ported, not `std.json`.** The bytes on the wire are
the writer's, and C's writer fixes them: keys in call order; `\"`, `\\`,
`\b`, `\f`, `\n`, `\r`, `\t` and `\u00XX` (lower-case hex) for the other
controls, `/` never escaped; a U+DC80–U+DCFF escape in the editor's
decoded stream written back as `\uDCXX` (a raw byte, round-tripped); an
integer as `%" PRId64 "`; a real as `%.17g` with `.0` added. The parser
keeps member order, keeps the first position of a duplicate key with the
last value and flags it, flags a lossy number, reads `\uDCXX` back to the
raw byte, and refuses at depth 128, at 64 MiB and at 4,194,304 nodes,
each with C's message and line and column. A `std.json` that agreed on
every one of those would still be a second implementation to hold to C's
tests; the port of C's is held to them directly. `std.json`'s source is
not read (the clean room covers JSON libraries).

### What the rows should show

- The JSON, writer and JSON-RPC unit files port one for one and are red
  first against stubs, then green on the checked machine and natively;
  the 4,194,304-node case is the one I expect past the checked machine's
  budget, so it runs natively and case by case.
- The eight `lsp_diag_*` PTY goldens (the demo's `s46_diag_*` scenes) go
  green against the port's demo; the first I expect to disagree is
  `lsp_diag_visual_truecolor` (undercurl `4:3` with the underline colour
  of `diag.error`), the first golden with a coloured underline the port
  has drawn.
- `tests/script/lsp_sync.fl` (fakelsp `session-sync`) moves from the
  deferred list to the gate: initialize, initialized, didOpen,
  didChange, didSave, didClose, in that order.
- The oracle rows: C yew and the port each open the same `.lu` files
  against the same `wolf lsp` (wolf at the pin) and their screens match
  cell for cell, attributes included: a clean file (no signs, the badge
  `wolf`), a lexer error, a type error, two diagnostics on one line
  (`(+1 more)`), the list, the jump, an edit that fixes the error (the
  sign goes), undo (it comes back). `wolf lsp` advertises full sync
  (`change: 1`), so the incremental path is proven by fakelsp
  (`change: 2`) and by unit rows that apply the sent changes to a copy
  and compare it with the buffer after edits, undo and a multi-cursor
  insert.
- The error paths, against a deterministic fake: a crash (the `restarted`
  messages and the backoff), a malformed frame (the transport dies, the
  server is restarted), an initialize that never answers (the named
  timeout, the child killed, never a hung editor), a reply after its
  deadline (dropped).
- The static x86-64 binary builds and starts `wolf lsp` in a container
  holding only it and the musl static `wolf`.
- What I expect to go wrong: the position conversion at a CRLF line end
  and at a non-BMP character (UTF-16), and the shutdown wait's 500 ms on
  the checked machine, which has no real pipes for a child.
