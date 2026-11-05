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
| `shim.c` | 230 | none | the disabled-module stub; the port is always the full build, so it is not ported | — |
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
  and a buffer they would name has no language, as now (decided
  below).
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

## Forbidden

- No merge, label, tag or release, and no issue closed. No attribution
  trailer.
- Clean room: sagitta at the pin was read and is cited `file:line`; no
  other editor's source, no JSON, JSON-RPC or LSP library's source
  (`std.json`'s included), no fackr crate. `wolf lsp` was run as a black
  box and read on the wire; its source was not read.
  `tools/lsp-rows/fakeserver.py` is written from the LSP specification
  for these rows alone.
- No golden is edited and no sagitta file changed: the oracle rows are
  this repository's own runner over sagitta's PTY harness objects, as
  `tools/trials/` is, and keep their screens outside the oracle tree.
  `sagitta.pin` and the wolf pin are unchanged.
- PR#102–#106 and #110 are untouched. #110 also changes `ci.yml`,
  `docs/MAP.md`, `README.md` and `CHANGELOG.md`; the hunks are apart.
- No perf row.

## Inputs verified

- **Base:** #110's head `2eb9cb9b` (yw14), trunk's next state as a
  fast-forward of trunk `1218169e` (r41q's record); the branch was
  rebased onto it before the final records. Only `CHANGELOG.md`
  conflicted (both entries kept, newest first); `ci.yml`, `edit.job`,
  `MAP.md` and the README merged with both sides' lines intact.
- **Toolchain:** wolf 0.2.36 (`5adf3d91`), lupin 0.1.58, std
  `78b9d3cb`, from the pinned archives (`tools/fetch-toolchain`).
- **C yew:** `sagitta.pin` (`9ace98c2`), built by `tools/oracle` (clang
  on macOS, gcc in the Linux image) with `fakelsp` beside it.
- **The server:** the pinned `wolf lsp` answers `initialize` with full
  sync (`textDocumentSync.change` 1), `positionEncoding` utf-8 and
  `save.includeText` false, and publishes one diagnostic per error with
  a multi-line message, a `code` and `relatedInformation`. With full
  sync on the wire, the incremental path is the fake server's
  (`change` 2, UTF-16) and the unit rows'.
- **The PTY harness** writes every PTY session a user `init.fl` of
  `let lsp = {servers: {}}` (`tests/pty/runner.c:201-236`), so no
  existing golden starts a server; the port honours the empty table (a
  table that exists replaces the defaults, `client.c:312-341`).
- **PAX's compiler:** `tools/mkwolf` builds wolf-lang `v0.2.36` for
  `x86_64-unknown-linux-musl` (`+crt-static`, `relocation-model=static`,
  stripped, no build-id; `user/wolf.pin`); PAX's `user/wolf.sums`
  records `wolf` `2df1fb76…` (16,257,584 bytes).

| host | role |
|---|---|
| Apple M-series Mac, macOS arm64 | builds, the macOS rows (C yew built with clang) |
| x86-64 Linux, rootless podman, a 6-CPU block | the gauntlet in `ubuntu:24.04` with the runner's tools, the musl wolf in a Rust 1.97.1 image, the static binary and the scratch container |

## Evidence index

Commits, in order:

- `50ef9dd` the prediction.
- `354d52d` `lsp_json_test`, red (no `lsp.json`); `9cd40a2` `lsp.json`.
- `13b4d33` `lsp_jsonrpc_test`, red; `99eec83` `lsp.jsonrpc`.
- `0ce0987` `lsp_client_test` and `lsp_sync_test`, red (no
  `lsp_uri_of_path`, no `lsp.sync`); `27dd56f` `lsp.client`; `753b819`
  `lsp.sync`.
- `4d5cb49` `edit_lsp_diag_test` and `de97d8a` `edit_lsp_config_test`,
  each red at its commit (no `edit.diag_replace`, no `lsp_client_cfg`).
- The oracle rows, red against the trunk port: `a049ebb` the fake
  server, `ddf02e5` the runner's cases, `5e9abf6` the comparison,
  `a3d4736` `tools/run-lsp-rows`.
- The client: `623abb2` `lsp.sync` replays a logged edit; `bc67f30`
  `text.edit` logs each edit at the choke point (C's notify hooks,
  `notify.c:44,57`); `95ebaf8` `edit.syn_paths` and `79c421a`
  `tools/check-syn-paths`; `d4e5f60` `edit.lsp_client`;
  `71ecf93` `edit.lsp_diag`; `9af2ebf` `edit.lsp`; `0873751` the framed
  sink in `edit.job`; `0d7b757`, `8b215ab`, `0ad5746` the `Ed`, the
  close and free paths and the commands; `e73803b` the server table
  read against a running script's VM.
- The drawing: `8536908` the underline and the hint, `0acea03` the
  statusline badge, `ac75dcd` the picker host.
- `b149354` `lsp` staged for the tools that build the editor;
  `d25253f` the demo's `s46_diag_*` scenes; `df31080` CI's gate;
  `595e199` the four files over the checked machine's budget one case at
  a time (G29); `a8fa142` `wolf fmt`.

**The rows, and what each showed.**

- **JSON and JSON-RPC** (`lsp_json_test`, 13 cases, 407 assertions;
  `lsp_jsonrpc_test`, 14 cases, 245,125 assertions): red at their
  commits, green natively; on the checked machine one case at a time
  (`tools/check-test-cases`), where eight of the 38 cases across the four
  over-budget files are still past a budget alone and carry `allow`
  rows: JSON's depth case (call depth), its size and node limits, its
  writer-bug children (self-exec), the frame split at every byte, the
  16,385-entry store, the thousand edits and the two config loads. The writer's corpus (`tests/fixtures/lsp/writer-corpus.json`)
  is C's, byte for byte.
- **URIs, capabilities, the lifecycle and sync** (`lsp_client_test`, 12
  cases; `lsp_sync_test`, 4 cases and one port case): green on the
  checked machine whole. The port case applies every incremental change
  the document sends to a copy, in UTF-8 and UTF-16, through edits, undo
  and a two-cursor insert, and holds the copy to the buffer.
- **Diagnostics and config** (`edit_lsp_diag_test`, 6 cases;
  `edit_lsp_config_test`, 5): red at their commits; green. The config
  file caught one divergence: the port read a buffer's binary flag only
  for a file-backed buffer, where C reads `meta.binary` always
  (`lsp_client.lu` now does).
- **The eight `lsp_diag_*` PTY goldens**: red against the trunk demo
  (`demo_paint: error: not yet ported: scene s46_diag_*`), then green
  by name against the port's demo; no golden moved.
- **`tests/script/lsp_sync.fl`**: green by name. On the way it showed
  that a running batch script holds the Fletch VM out of the `Ed`, so
  the server table read from `t.pump` found no `lsp` binding and the
  pump started clangd; `t.pump` now reads the table against the
  script's own VM (`e73803b`).
- **The oracle rows** (`tools/run-lsp-rows`, nine cases, seventeen
  screens), C yew and the port against the same pinned `wolf lsp` and
  the same fake server, each case twice per editor:
  - against `wolf lsp`: a type error opened (the gutter's ✗, the
    undercurl, `E:1`), `ed.lsp.diag_next` (the cursor on line 2 and
    the hint), `ed.lsp.diagnostics` (the list); an insert that breaks
    the file brings `E:1` and undo takes it away; one insert at two
    cursors brings `E:2` and undo mends both;
  - against the fake: incremental sync through a non-BMP line, a
    deletion across a line join, two cursors and undo, the server's
    copy then held to the saved file (`view matches disk`); a crash on
    save, the restart at the editor's next turn and the second
    server's diagnostic; a header that is not a length, the transport
    dropped and the server restarted; an `initialize` answered 1.5 s
    late while the editor takes keys; one never answered (the 1,000 ms
    deadline: the server killed, the badge's ellipsis gone, no
    message); a server that answers neither `shutdown` nor `exit`
    (the quit is bounded by the 500 ms wait).
  - Red against the trunk port: every case `FAIL` by name (the
    trunk port has no client: no badge, no sign, no list, no saved view
    answered).
  - Green on macOS: all seventeen screens `same`, both runs of both
    editors stable.
- **Static for PAX:** `tools/build --static` in the Linux image gives
  an `ET_EXEC` with no `PT_INTERP` (the gauntlet's `static` step prints
  its digest twice and its size). PAX's musl-static `wolf`, rebuilt here
  from the `v0.2.36` tag by PAX's recipe (Rust 1.97.1,
  `x86_64-unknown-linux-musl`, the three packages, 2 min 15 s), is
  `2df1fb7660ce27dd6bd0d8c7395abec74bb399824842f89b8a407060be80ab59`,
  16,257,584 bytes, read twice: the bytes PAX's `user/wolf.sums` records
  (its `wolf-cimport-worker` and `libwolf_rt.a` agree too). A `FROM
  scratch` image holds `/yew`, `/bin/wolf` and the pin's std beside it,
  nothing else (no shell, no libc). In it, `yew --batch --test` opens
  `src/main.lu` of a wolf package with a type error, pumps the jobs,
  runs `ed.lsp.diag_next` and asserts the cursor stands on `wolf lsp`'s
  E0401, line 2, column 17: `YEWTEST 3 0 0`, exit 0. The control, the
  same run with no `wolf` on `PATH`, fails the two cursor assertions
  (the gauntlet's `pax-container` step).
- **The gauntlet** at the final head, in the Linux image, and **the
  plant** (`yw11a-plant-*`: one hunk in `src/lsp/sync.lu`, every
  incremental change's end one character late), red by name at
  `lspf_mirror_sync`: both records are the PR's.

**What the rows taught the comparison**: C's syntax engine
colours `.lu` (yw10's, not ported) and paints frames of its own as it
settles (`ed.c:1383-1389`), so the comparison leaves out the document
area's foreground, bold and italic and the header's frame count; every
glyph, the cursor, the modes, the background and the underline,
undercurl, strike, dim and reverse attributes are compared everywhere.
C's shadow (ghost text) repaints once a server is ready (`ed.c:2690`);
it is yw11b's, and the rows' config turns it off in both editors. The
diagnostic list labels a row by the buffer's whole path (`diag.c:639-643`,
`ed.c:333-340`), so both editors open the same fixed path.

### Decided

- **The language before yw10.** C starts a server only for a buffer
  with a language (`client.c:1133`), and the language is syn's. The
  port has the builtin detection index's path half only, generated from
  the pin (`tools/gen-syn-paths`, checked by `tools/check-syn-paths`):
  extensions, exact names and globs; no shebang, no first line, no
  Fortran scoring, no user definitions. Every `.lu`, `.c`, `.py` and the
  rest name their language as C's do; a file only a shebang or a user
  definition would name has none until yw10. Waiting for yw10 was the
  alternative.
- **The hung `initialize` says nothing, as C.** C has the deadline (the
  server's `init_timeout_ms`, 60 s by default) and kills the server, but
  draws no message: the badge loses its ellipsis (`client.c:833-844`).
  The port matches, and the silent-initialize row holds it to C's
  screen. A named message such as `wolf: initialize timed out` was the
  alternative: a divergence from C's screen that sagitta never draws.
- **What the oracle rows compare** (above): every cell but the document
  area's syntax colouring and the header's frame count, the shadow off
  in both editors, until yw10 lands; then whole snapshots, and
  `compare.py` loses two lines.
- **`lsp_sync.fl`'s list.** It stays in `tools/scripts-deferred.txt`
  (yw09's partition of the pin's 94 holds at 69 + 25), and yw11a's own
  CI step gates it by name.
- **`test_lsp_transport` and `test_lsp_life` wait for yw11b.** Their C
  fixtures hand the job layer an ops table for a test owner; the port's
  framed owner is a server id the job layer matches by kind, so they
  have no seam to port onto as written. Here `lsp_sync.fl` and the
  rows' crash, malformed frame, slow and silent initialize and deaf
  shutdown cover those paths; yw11b ports the files through a real
  `LspServer` fixture.

## Done-when

- [x] The map, with what waits for yw11b and what syn gives.
- [x] sagitta's JSON and JSON-RPC, ported, their unit files red first.
- [x] The client and the child: configs, roots, the job on pipes, the
  handshake, shutdown and exit, a crash, a malformed frame, a hang with
  its deadline (silent, as C's), through the existing wait (G2).
- [x] Sync: didOpen, incremental didChange, didSave, didClose, with the
  server's view held to the buffer after edits, undo and two cursors.
- [x] Diagnostics drawn as C draws them: gutter, underline, statusline,
  hint, list, jumps; the eight goldens.
- [x] The oracle rows, each red before its code, green on macOS; the
  Linux gauntlet's record is the PR's.
- [x] Static for PAX: the binary's digest, and the client starting
  `wolf lsp` in a container holding only it and PAX's musl wolf (the
  gauntlet's `static` and `pax-container` steps; the record is the
  PR's).
- **wolf yew opening a `.lu` file shows `wolf lsp`'s diagnostics
  exactly as C yew shows them, on the same server:** the `lspw_*` rows'
  screens, cell for cell, syntax colouring aside.
