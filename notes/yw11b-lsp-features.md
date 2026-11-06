# yw11b — the LSP client's features (sagitta s47; s43 and s44 decided)

_yew's language-server features, ported from sagitta's `src/mod/lsp/`
(`features.c`, `pickers.c`, `highlight.c`, `rename.c`, `lsp.c`'s
entry points) and `src/ui/panel.c` at `sagitta.pin` (`9ace98c2`), so
that `wolf lsp`'s navigation, references, symbols, hover, signature
help and rename work in the editor as C yew shows them. yw11a (yew#111,
`7009fb2a`) built the client core and diagnostics._

## Prediction

Written before the first change (2026-11-06, base trunk `7009fb2a`, wolf
0.2.36 / lupin 0.1.58 / std `78b9d3cb`, `sagitta.pin` `9ace98c2`).

### The split (R-yw11b-3)

The features are about 5,200 lines of C (`features.c` 2,372,
`rename.c` 1,476, `pickers.c` 722, `highlight.c` 472, `panel.c` 635)
and their tests about 4,800 (`test_lsp_life.c`'s 36 remaining cases,
`test_lsp_rename.c` 1,261, `test_panel.c` 668 and six more files).
Completion adds the menu (`ui/complmenu.c`, 992, Sprint 44), the shadow
(`edit/shadow.c`, `ui/shadowdraw.c`, `edit/shadow_cmds.c`, 1,609,
Sprint 43) and the symbol index (`ws/symidx.c`, `symwalk.c`,
`symshadow.c`, `symrank.c`, 2,852, Sprint 44). That is more than one
reviewable PR, so the lane is two:

- **yw11b2, first: the panel and the picker's features.** The floating
  panel (`ui/panel.c`, s47 §3, core), hover and signature help (with the
  auto-trigger), definition, declaration, type definition,
  implementation, references, document symbols (the index fallback
  refusing by name, below), document highlight, and rename. It needs
  nothing from s43 or s44 but the completion-kind vocabulary (eleven
  glyphs, `complmenu.c:56-63`), which comes forward.
- **yw11b1, second: completion.** The menu (`ui/complmenu.c`), the LSP
  source with `completionItem/resolve`, the snippet downgrade, accept
  with its additional edits, and whatever R-yw11b-1 rules for the shadow
  and the index.

The contract's split had hover and signature with completion. They move
to yw11b2 because what they need is the panel, which rename's
confirmation brings, and none of s43 or s44; yw11b1 is then exactly the
work R-yw11b-1 decides, and yw11b2 starts without waiting for it. The
contract's other choice, b1 first, would hold both halves on the ruling.
Each half gets its own records, plant and PR. Items 9 (M-YW9) and 10
(PAX) land in yw11b2: a definition is yw11b2's.

### The map

| sagitta | wolf unit | half |
|---|---|---|
| `ui/panel.c` (all), `panel.h` | `edit.panel` (`src/edit/panel.lu`): placement, wrap, keys (`ed.ui.panel.move`), draw, the document mark | b2 |
| `features.c:298-345` (exact positions and ranges) | `lsp.features` (`src/lsp/features.lu`) | b2 |
| `features.c:347-511` (hover and signature parsers) | `lsp.features` | b2 |
| `features.c:513-633` (locations) | `lsp.features` | b2 |
| `features.c:635-885` (document symbols, the kind map) | `lsp.features`, with `complmenu.c:56-63`'s glyph table and `complmenu.h:29-40`'s kinds | b2 |
| `features.c:1316-1999` (the panel, navigation and symbol requests and their callbacks) | `edit.lsp_features` (`src/edit/lsp_features.lu`); a pending request's callback is a kind (`LSP_PK_*`) in `lsp_pending_done`, its context a record in `ed.lsp` | b2 |
| `features.c:1-222` (snippets), `:224-1314` (completion items, resolve, accept), `:2001-2372` (the shadow provider, the menu source) | `lsp.features` and `edit.lsp_features` | b1 |
| `pickers.c` (all) | `edit.lsp_pickers` (`src/edit/lsp_pickers.lu`): the location and symbol picker hosts (`PICK_HOST_LSP`), the jump, the preview; `yew_lsp_symbol_index_open` (`:642-722`) refuses by name until the index (R-yw11b-1) | b2 |
| `highlight.c` (all) | `lsp.features` (the parser) and `edit.lsp_highlight` (the idle timer, the request, the two overlays, clear, buffer clear, shutdown); `draw.c:604-655` in `edit.draw` | b2 |
| `rename.c` (all) | `edit.lsp_rename` (`src/edit/lsp_rename.lu`): preflight, apply and rollback, the summary panel, the diff scratch, the prompt, the key route and the three answers | b2 |
| `lsp.c:84-95` (`feat_require`), `:215-371` (the entry points), `:440-466` (shutdown and buffer close) | `edit.lsp` | b2, with `yew_lsp_complete` b1's |
| `edit/lsp_cmds.c:61-171` | `edit.lsp` | b2 (complete b1) |
| `ed.c:2367-2377, 2417` (rename and panel keys, the auto-trigger), `:2768` (the panel drawn last), `:296-301, 623-624, 1149-1203` (the window's highlight and panel lifetimes) | `edit.input`, `edit.ed`, `edit.win` | b2 |
| `loop.c:660` (the highlight idle hook) | `edit.loop` | b2 |
| `layout.c:662` (resize), `mouse.c:985` (a click closes the panel) | `edit.layout`, `edit.mouse` | b2 |
| `sync.c:419`, `lsp.c:465` (yw11a's named no-ops) | `edit.lsp_highlight`'s buffer clear | b2 |
| `ctxrows.c`'s PANEL rows for the rename answers | `edit.ctxrows` | b2 |

yw11a's named no-ops go: `yew_lsp_highlight_buffer_clear`'s two calls
become the real clear; the shadow request fields stay zero until
yw11b1; `ed.lsp.symbols`' fallback refuses by name (R-yw11b-1).

### What each feature asks of `wolf lsp`, and C's answer when it lacks it

`wolf lsp` 0.2.36 answers `initialize` (probed 2026-11-06 with the
pinned binary) with `definitionProvider`, `referencesProvider`,
`documentSymbolProvider`, `hoverProvider`, `signatureHelpProvider`
(triggers `(` and `,`), `renameProvider` (with `prepareProvider`),
`completionProvider` (trigger `.`), formatting, code actions, inlay
hints and semantic tokens, `positionEncoding` utf-8 and full sync. It
does not advertise declaration, type definition, implementation or
document highlight, and answers them `-32601`.

| feature | command, key | capability | without it (C) |
|---|---|---|---|
| definition | `ed.lsp.goto_def`, `g d` | `definitionProvider` | `feat_require` (`lsp.c:84-95`): `<id> does not support definition`, once per server and capability; no request |
| declaration | `ed.lsp.goto_decl`, `g D` | `declarationProvider` | `… does not support declaration` (wolf: always) |
| type definition | `ed.lsp.goto_type`, `g y` | `typeDefinitionProvider` | `… does not support type definition` (wolf: always) |
| implementation | `ed.lsp.goto_impl`, `g i` | `implementationProvider` | `… does not support implementation` (wolf: always) |
| references | `ed.lsp.references`, `g r` | `referencesProvider` | `… does not support references` |
| document symbols | `ed.lsp.symbols`, `g s` | `documentSymbolProvider` | `… does not support document symbols`; with no ready server, C opens the index picker (`lsp.c:333-339`) |
| document highlight | idle 300 ms after the cursor stops (`highlight.c:17`) | `documentHighlightProvider` | silent: nothing is requested and any overlay clears (`highlight.c:412-419`) (wolf: always) |
| hover | `ed.lsp.hover`, `K` | `hoverProvider` | `… does not support hover` |
| signature help | `ed.lsp.signature`, `A-k` in I; auto on a trigger character | `signatureHelpProvider` | `… does not support signature help`; the auto-trigger is silent |
| rename | `ed.lsp.rename`, `g R` | `renameProvider` | `… does not support rename`; `prepareRename` is never sent (s47 §8) |

Every feature with no ready server says `no ready LSP server for <lang>`
(`lsp.c:242-261`). A `-32601` reply clears the capability bit silently,
so the next invocation gives the `does not support` sentence without a
round trip (`features.c:1630-1634`, `:1804-1808`, `:1925-1929`,
`highlight.c:272-277`, `rename.c:971-978`). Any other error reply is
silent, the bit kept, except rename's: every error reply to a rename
says `rename request failed` (`rename.c:971-977`). A
`null` or empty result says `<id>: no <what> found` for the gotos and
references (`features.c:1813-1817`), `<id>: no document symbols found`,
`no hover information here` for hover, nothing for signature help, and
`no rename available here` for rename.

### The shadow and the symbol index (R-yw11b-1)

Neither is `src/mod/lsp/`'s. The shadow is Sprint 43's
(`edit/shadow.c`, `ui/shadowdraw.c`, `edit/shadow_cmds.c`): a provider
registry, debounce timers, staleness, the ghost-text draw and the accept
commands. `features.c:2012-2233` is only the LSP provider that registers
into it. The symbol index is Sprint 44's (`ws/symidx.c` and its
siblings), and it is built from settled syntax: `symidx.c:977` reads
`yew_syn_spans`, and `symwalk.c:18` the syntax definitions, both yw10's.
The index's shadow provider (`symshadow.c`) and the AI provider
(`mod/ai/shadow_ai.c`, yw12) feed the same registry.

What yw11b needs from them: `ed.lsp.symbols` with no ready server opens
the index picker (`pickers.c:677-722`); `ed.lsp.complete` with no ready
server opens the index completion source (`lsp.c:242-246`); the LSP
shadow provider needs the registry.

- **A (recommended): the shadow framework comes with yw11b1, the index
  waits for yw10.** yw11b1 ports s43's registry, debounce, staleness,
  draw and accept commands with the LSP provider registered, the index
  and AI providers refusing by name (yw10, yw12); its rows and
  `s43_shadow_lsp_*` goldens run with the shadow on. The index, its
  completion source and `ed.lsp.symbols`' fallback refuse by name
  (`not yet ported: the symbol index: sagitta Sprint 44 (yw10)`) until a
  lane after yw10 ports `ws/sym*` on settled syntax. yw11b2 ships the
  fallback's refusal now.
- **B: both wait.** yw11b1 ports the menu and the LSP source only; the
  shadow, its LSP provider and the index go to a lane after yw10, and
  the rows keep the shadow off as yw11a's do.
- **C: both now.** The index without syntax would need a second,
  syntax-free symbol scanner, which C does not have.

I implement A's yw11b2 part (the fallback's named refusal) and stop
there for the ruling before yw11b1.

### The wolf-lsp harness (R-yw11b-2)

`lspconf` (wolf-lsp `c54e375`) is a client: `replay` drives recorded
sessions against `wolf lsp`, playing each transcript's client side and
matching the server's answers record by record. Nothing in it plays a
server to an editor, so there is no editor-side replay to point at wolf
yew, and campaign 09's "the wolf-lsp harness replays against wolf yew"
cannot run as written. What it would take, in wolf-lsp:

1. a `yew` capability profile (`profiles/`), from what wolf yew sends
   (`lsp.client`'s `initialize` parameters);
2. an editor-side mode, say `lspconf serve <t.jsonl>`: stdio framing to
   a client, answering each request from the transcript's server records
   and matching the client's own records (method, params under the
   transcript normalization) in order;
3. a driver that makes the editor send each transcript's requests: a
   `yew --batch --test` script per transcript (open, move, `ed.lsp.*`,
   `t.pump`), since the transcripts are written from a client script's
   point of view.

That is a wolf-lsp lane (the harness is its code) with a yew-side script
set. My recommendation: **A**, a wolf-lsp lane adds the `yew` profile
and `serve`; yw11b's rows already hold wolf yew to C yew on the same
`wolf lsp`, which is the comparison M-YW9's first half asks for. **B**:
count M-YW9 met on the rows and the ported conformance runs, and retire
the replay clause. I do not invent a replay here.

### What the rows should show

All red first: each new row is committed and seen failing before the
code that turns it green.

- **The unit files, ported one for one** (the per-case selector and the
  checked machine's budget as yw11a's):
  - `src/edit_panel_test.lu` ← `test_panel.c` (18 cases);
  - `src/lsp_features_test.lu` ← `test_lsp_nav.c`'s five parser cases,
    `test_lsp_symbols.c`'s seven, `test_lsp_highlight.c`'s six and
    `test_lsp_completion.c`'s four hover and signature cases;
  - `src/edit_lsp_nav_test.lu` ← `test_lsp_nav.c`'s two jumps and
    `test_lsp_symbols.c`'s index case (which refuses by name until the
    index: the one C case that stays red by ruling, listed);
  - `src/edit_lsp_rename_test.lu` ← `test_lsp_rename.c` (26);
  - `src/edit_lsp_gate_test.lu` ← `test_lsp_gate.c` (2), over C's
    `fakelsp` (`tests/helpers/fakelsp.c`, built by `tools/oracle`);
  - `src/edit_lsp_life_test.lu` ← `test_lsp_life.c`'s 36 remaining
    cases: the stale drops, the feature cases (hover and signature
    panels, the gotos, references, symbols, the seven highlight cases),
    and the fakelsp sessions yw11a left (handshake, encodings, missing
    sync, the initialize timeout, repeated sessions, open-edit-save-close,
    a language change, a delayed response, the graceful free, the
    diagnostic versions, the restart, stop's escalation, server
    requests, the document menu's LSP section). The two completion
    cases are yw11b1's;
  - `src/edit_lsp_transport_test.lu` ← `test_lsp_transport.c` (4).
  The fakelsp files run as black boxes with the helper's path in
  `YEW_FAKELSP`, through the port's real `LspServer` and job (the seam
  yw11a's note asked for), and skip loudly without it.
- **C's goldens**: `lsp_feat_rename_summary`, `_diff`, `_apply`,
  `_unknown_key` and `_refusal`, by name, red now (`ed.lsp.rename`
  refuses).
- **The oracle rows** (`tools/run-lsp-rows`), C yew and wolf yew against
  the same pinned `wolf lsp`, screen by screen:
  - `lspw_goto_def`: `g d` on a use of a function jumps to its
    definition; `C-o` comes back;
  - `lspw_goto_def_file`: a definition in a file not open opens it
    (`lsp.open_in` `here`) at the converted position;
  - `lspw_goto_unsupported`: `g D`, `g y`, `g i` say `wolf does not
    support …` once each, and nothing the second time;
  - `lspw_references`: `g r` opens the location picker (path relative to
    the root, 1-based line and column, the line's text); Enter jumps;
  - `lspw_symbols`: `g s` opens the symbol picker with the kind glyphs
    and `Point › x` breadcrumbs; typing filters by leaf; Enter jumps;
  - `lspw_hover`: `K` on a definition opens the hover panel (`fn add`,
    the markdown fence lines dropped) with the range marked; the next key
    closes it and is dispatched;
  - `lspw_rename`: `g R`, a new name, the summary panel, Enter: `renamed
    2 occurrences in 1 files (unsaved — :wa to write)`; one undo restores
    both.
- **The fake server's error paths** (`tools/lsp-rows/fakeserver.py`
  grows modes; the fake advertises what each row needs):
  - `lspf_highlight`: read and write overlays after the idle, cleared by
    an edit;
  - `lspf_signature`: the auto-trigger on `(` opens the panel above the
    cursor with the active parameter bold;
  - `lspf_null`: a `null` definition and an empty references result give
    `fake: no definition found` and `fake: no references found`;
  - `lspf_error`: a `-32601` reply is silent and the next `g d` says
    `fake does not support definition`; a `-32603` reply is silent and
    keeps the bit;
  - `lspf_stale`: a reply after the document changed is dropped (no
    jump; `:ed.lsp.info` counts it in `stale drops`);
  - `lspf_deadline`: a definition reply past the 10 s request deadline
    (`RPC_TIMEOUT_MS`) is answered by the timeout error: nothing moves,
    nothing is said, the late reply is ignored;
  - `lspf_partial`: a server with only `definitionProvider` refuses the
    other eight features with their sentences;
  - `lspf_rename_files`: a rename across the open file and a file not
    yet open (hydrated into a tab), one undo node per buffer, a stale
    `documentChanges` version refused with `rename is stale; the buffer
    changed. try again`.
- **M-YW9**: R-yw11b-2 above.
- **Static for PAX**: the static x86-64 binary's digest, and `yew --batch
  --test` in a `FROM scratch` image with only it, PAX's musl `wolf` and
  the pinned std going to a definition through `wolf lsp` (the cursor
  lands on the definition's line and column); the control without
  `wolf` fails that assertion.

**What I expect to go wrong**: the panel's wrap and width at a tab and at
a wide or combining cluster; the hover body's fence lines; the location
label's root-relative path (C's `yew_ws_root` against the port's
workspace, and macOS's `/tmp` symlink under C's `realpath` in rename's
workspace check); the symbol picker's separator glyph under the `dumb`
profile; the highlight's 300 ms idle against the port's timer heap; the
rename summary's `%-40s %5llu` columns; and the rollback's undo-node
checks against the port's undo tree.
