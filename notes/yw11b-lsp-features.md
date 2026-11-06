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

## Forbidden

- No merge, label, tag or release, and no issue closed. No attribution
  trailer.
- Clean room: sagitta at the pin was read and is cited `file:line`; no
  other editor's source and no JSON, JSON-RPC or LSP library's source.
  `wolf lsp` was run as a black box and read on the wire (its
  `initialize` reply, probed with the pinned binary); its source was not
  read. The fake server's feature modes are written from the LSP
  specification for these rows alone.
- No golden is edited and no sagitta file changed. `sagitta.pin` and the
  wolf pin are unchanged.
- PR#102–#106 and #110 are untouched. No perf row.

## Inputs verified

- **Base:** trunk `7009fb2a` (yew#111, yw11a).
- **Toolchain:** wolf 0.2.36 (`5adf3d91`), lupin 0.1.58, std
  `78b9d3cb`, from the pinned archives (`tools/fetch-toolchain`).
- **C yew:** `sagitta.pin` (`9ace98c2`), built by `tools/oracle` (clang
  on macOS, gcc in the Linux image), `fakelsp` with it.
- **The server:** the pinned `wolf lsp` advertises definition,
  references, document symbols, hover (markdown), signature help
  (triggers `(` and `,`), rename (with `prepareProvider`, which C never
  sends) and completion; not declaration, type definition,
  implementation or document highlight. Full sync, utf-8.
- **PAX's compiler:** the musl static `wolf` at `v0.2.36` by PAX's
  recipe, `2df1fb76…` (16,257,584 bytes), the bytes PAX's
  `user/wolf.sums` records and yw11a's note cites; copied by value from
  yw11a's build and checked by digest.

| host | role |
|---|---|
| Apple M-series Mac, macOS arm64 | builds, the macOS take (units, goldens, rows; C yew built with clang) |
| x86-64 Linux, rootless podman, a 6-CPU block | the gauntlet in `ubuntu:24.04` with the runner's tools, the static binary and the scratch container |

## Evidence index

Commits, in order (the prediction first, every row red before its code):

- `b22ff1d` note: yw11b's prediction: the map, the split, the capabilities and the rows
- `4b68be0` lsp_features_test: the location, symbol, highlight, hover and signature parsers' cases (red: no lsp.features)
- `3a96318` edit_panel_test: test_panel.c's eighteen cases (red: no edit.panel)
- `90af81a` edit_lsp_rename_test: test_lsp_rename.c's twenty-six cases (red: no edit.lsp_rename)
- `65374a5` edit_lsp_nav_test: the jumps and the symbol picker (red: no lsp.features, no edit.lsp_pickers)
- `a4ea713` edit_lsp_gate_test: test_lsp_gate.c over fakelsp (red: no job-turn seam, no features)
- `a2d069e` edit_lsp_transport_test: test_lsp_transport.c through a real server (red: no framed-turn seam)
- `818c76e` edit_lsp_life_test: test_lsp_life.c's remaining thirty-six cases (red: no seams, no features)
- `ce8ff70` lsp-rows: the fake server's feature modes
- `5e89480` lsp-rows: yw11b's rows over wolf lsp, the fake server and C's rename sessions (red against trunk's port)
- `f43e565` lsp.features: the location, symbol, highlight, hover and signature parsers
- `2e99eb0` edit.panel: the floating panel: placement, wrap, keys, draw, the document mark
- `39a84ee` edit.win: the panel, the request records and the highlight state in the window
- `830ed82` edit.ed: the picker and rename state; a shown buffer keeps the window's records
- `14b9539` edit.lsp_client: the features' pending kinds
- `a8443a9` edit.lsp_features: hover, signature, navigation and symbol requests and callbacks
- `723636c` edit.lsp_pickers: the location and symbol pickers, the jump, the preview
- `27943e9` edit_lsp_nav_test: finish the picker's sliced pass before counting, as the loop does
- `39f89a4` edit.lsp_highlight: the idle request and the read and write overlays
- `e790e03` edit.lsp_rename: preflight, apply, rollback, the summary, the diff, the prompt
- `b1df8c4` edit.lsp: the feature entry points, the capability gate, the commands
- `43a8fc2` edit.impl: dispatch the feature commands and the panel's move
- `f19575d` draw: the panel last, the hover mark and the highlight overlays
- `3878cf5` input: the panel and rename keys, the signature auto-trigger
- `296fd65` layout: resize the focused window's panel
- `9790e1d` mouse: a click inside the panel, outside it closes
- `c4e8844` ctxrows: the document menu's LSP section and the rename panel's answers
- `555f2cc` mods: the LSP module is the port's
- `8b8b3f6` edit.batchtest: the LSP unit rows' seams: one job turn, the fake server's path
- `fe6dc72` tools/build-fakelsp: C's fake language server, alone
- `7ef1cb1` tools/check-test --fakelsp-ran: no LSP row skipped for want of the fake server
- `f2109bd` check-test-cases: the five cases past the checked machine's budget
- `1913a69` CI: build fakelsp for the unit lanes; yw11b's rename goldens by name
- `3588af9` CHANGELOG, MAP: yw11b2
- `91716ee` lsp-rows: wait on the highlights' cells and on each close, not a quiet gap
- `84164ec` lsp-rows: hover waits on the panel's corner, not the typed command's word
- `50939dc` lsp-rows: the fake's silent answers carry a receipt; stale and late answers on a condition, not a clock
- `d71abca` lsp-rows: error, stale and deadline rows wait on the fake's receipts and marker, not a quiet gap
- `11a13bf` CHANGELOG: the rename row crosses a file not yet open; silent answers have receipts

**The red witnesses** (each test file built at its own commit, before
any code, on the Linux block in yew CI's image): every one fails to
compile on the items its code brings, `E0301` naming them —
`lsp.LspLoc` and `lsp.lsp_locations_parse` (`lsp_features_test`),
`edit.PanelSpec` (`edit_panel_test`), `edit.RenamePlan` and
`edit.lsp_rename_preflight` (`edit_lsp_rename_test`), `lsp.LspLoc` and
`edit.lsp_location_jump` (`edit_lsp_nav_test`), `edit.ed_pump_jobs_once`
(`edit_lsp_gate_test`), `edit.ed_pump_framed_once`
(`edit_lsp_transport_test`), and `edit.ed_pump_jobs_once`,
`edit.lsp_hover` and `edit.PANEL_BELOW` (`edit_lsp_life_test`).

**The rows** (`tools/run-lsp-rows`, the Linux block, C yew built with
gcc): 27 rows, each run twice over C yew and twice over the port,
47 kept screens stable and the same in both editors (syntax
colouring aside); yw11a's nine and the eighteen new (`lspw_goto_def`,
`_goto_def_file`, `_goto_unsupported`, `_references`, `_symbols`,
`_hover`, `_rename`; `lspf_null`, `_error`, `_stale`, `_deadline`,
`_partial`, `_highlight`, `_signature`, `_rename_files`; and
`lspg_rename_summary`, `_apply`, `_unknown_key`). Red first: at
`5e89480`, the rows' commit before any feature code, C yew passed all
27 and trunk's port failed fourteen by name (`lspw_goto_def`,
`_goto_def_file`, `_goto_unsupported`, `_references`, `_symbols`,
`_rename`; `lspf_null`, `_stale`, `_partial`, `_signature`,
`_rename_files`; the three `lspg_*`), and the other four new rows'
screens differed from C's (`lspw_hover`'s panel, `lspf_error`'s two,
`lspf_deadline`'s pending screen, `lspf_highlight`'s two); all five
rename goldens failed. The four rows made stricter after the first macOS take
(`lspw_hover`, `lspf_error`, `_stale` and `_deadline`, below) were run
again at their commit against the same trunk port: C passed each, and
the port failed each by name (`the hover panel never opened`, `the
hover's error reply never came`, `the edit did not land` with the
refused hover's line still open, and `the definition request never
reached the fake`).

**C's rename goldens**: `lsp_feat_rename_diff` and `_refusal` pass by
name; `_summary`, `_apply` and `_unknown_key` first differ at the typed
`!` (below). The gauntlet's record and the macOS take are the PR's.

### What the work found

- **A request is queued, not written.** The first port wrote each
  request at once; C leaves it in the connection's queue for the loop's
  write turn (POLLOUT), and `test_lsp_life.c`'s idle-highlight case
  reads it there. The requests now wait for `job_pump`'s framed writers.
- **The LSP module was off.** `edit.mods` answered for a module-less
  build, so `lsp.open_in`, the one option the LSP module owns, refused
  every write ("this build has no lsp module"); the jump case could not
  set it. LSP is the port's now; AI, FUSS and plugins still refuse.
- **The rename answers through the dispatcher.** C's dispatcher opens a
  `TXN_TYPE` transaction around any command that changes a buffer
  (`yew_ed_invoke`, `ed.c:1699-1820`), and `ed.lsp.rename.apply` is
  one; the apply then opens `TXN_LSP` on the same buffer, and
  `yew_undo_begin` stops on the reason mismatch (`undo.c:434-452`). The
  port's dispatcher is C's, and it stopped the same way when the unit
  test went through it; C's test calls the handler itself (`rename_run`,
  `test_lsp_rename.c:1038-1049`) and so does the port's. Enter on the
  summary panel applies without the dispatcher, as C's goldens do; the
  panel menu's Apply row reaches the stop in both editors (R-yw11b-4,
  below).
- **Three rename goldens hold syntax colouring.** C's s47 sessions make
  `alpha.c` dirty by typing `!` (`registry.c:9897-9902`), and C draws it
  in its operator colour (`#56b6c2`); the port has no highlighting
  before yw10, so `lsp_feat_rename_summary`, `_apply` and `_unknown_key`
  first differ at that cell (line 31 of the snapshot, the style row).
  `_diff` and `_refusal` (no dirty file) pass. The three are recorded as
  campaign 05's two highlighting goldens are, and the `lspg_*` rows
  replay the same sessions and hold every other cell to C's (R-yw11b-5).
- **The transport's capture is the server's reader.** The port releases
  the reader with the connection when the job settles, where C's capture
  outlives its owner, so the transport cases read it once the child's
  stdout has ended and before the drain.
- **A row's walk waits on each step.** The first rows walked the cursor
  with arrow keys, and in L mode `<right>` moves by the mode's unit, a
  line, to its end (`runtime/init.fl:53`): `lspw_goto_def` stood at
  `6:14`, past the call, and asked for nothing. Seven rows failed that
  way in both editors, on the Linux block and on the Mac alike. They
  failed in their first run, and the runner skips a row's second run
  once the first fails, so "the two runs kept different screens" was
  the listing of the failed rows' missing second runs; no kept screen
  moved between runs. The rows now walk with `ed.move.char.right`, one
  command at a time, each waited for on the statusline's position.
- **Silence needs a receipt.** The error, stale and deadline rows hold an
  answer the editor shows nothing for, and held it over a quiet gap,
  which a slow host can outlast. The fake now follows each such answer
  with a receipt, one more warning on line 1, which both editors read
  after the answer on the same pipe, and the rows wait for its badge
  (`W:1`, `W:2`). The stale answer waits for the document's `didChange`
  instead of a second's sleep, so it is stale on any host; the deadline
  mode marks the request's arrival and answers 12 s later, past the
  10 s deadline (`jsonrpc.h:20`), and the row holds that the late answer
  is ignored (the sweep has already called the request back,
  `jsonrpc.c:682-718`). The hover row waits on the panel's corner, since
  the typed `:ed.lsp.hover` holds the bare word, and the highlight row
  on the two overlays' cells.

### Decided

- **R-yw11b-1 = A** (the shadow and the index): the shadow framework
  (Sprint 43's registry, debounce, staleness, draw and accept commands)
  comes with yw11b1, the LSP provider registered and the index and AI
  providers refusing by name (yw10, yw12); the index, its completion
  source and `ed.lsp.symbols`' fallback refuse by name until a lane
  after yw10 ports `ws/sym*` on settled syntax. yw11b2 ships the
  fallback's refusal: `not yet ported: the symbol index: sagitta Sprint
  44 (yw10)`.
- **R-yw11b-2 = A** (M-YW9's replay): the replay needs a wolf-lsp lane
  that adds a `yew` capability profile and an editor-side `lspconf
  serve`. **M-YW9 stays open until it lands**; the rows here hold wolf
  yew to C yew on the same `wolf lsp`, and they are not counted as
  M-YW9.
- **R-yw11b-3** (the split): yw11b2 first, as implemented; this is
  yw11b2, and yw11b1 (completion) follows as its own change.
- **R-yw11b-4 = A** (the rename panel's Apply row): the port stays C's,
  so the menu row reaches the same stop. The finding, exactly: C's
  dispatcher, `yew_ed_invoke` (`ed.c:1699-1820`), opens a `TXN_TYPE`
  transaction on the command window's buffer around any command flagged
  `YEW_CMD_CHANGES_BUFFER`, and `ed.lsp.rename.apply` is one
  (`cmd.c:1167-1168`); the context menu runs its rows through that
  dispatcher (`invoke_desc`, `mouse.c:1006-1030`); the apply then opens
  `TXN_LSP` on the same buffer through an edit context over it
  (`rename.c:700-706`), and `yew_undo_begin` (`undo.c:434-452`) stops
  on the nested reason mismatch (`undo: nested transaction reason
  mismatch`). Enter on the summary panel applies without the dispatcher
  (`rename.c`'s key route), the path C's goldens take. The finding is
  sagitta's to decide; the port follows the pin when it moves.
- **R-yw11b-5** (the three coloured goldens): **A (implemented)**: gate
  `lsp_feat_rename_diff` and `_refusal` by name, record `_summary`,
  `_apply` and `_unknown_key` (a `continue-on-error` step that announces
  them, as campaign 05 records its highlighting goldens) until yw10, and
  hold the rest of their screens to C's with the `lspg_*` rows. **B**:
  hold all five until yw10.
- **The fake server's path is fixed, as the clipboard tool's is.** The
  LSP rows that spawn C's `fakelsp` find the oracle's build at
  `target/oracle/sagitta/build/tests/helpers/fakelsp` (the prediction
  said `YEW_FAKELSP`) and SKIP by name without it; `tools/build-fakelsp`
  builds it alone for the unit jobs and `tools/check-test
  --fakelsp-ran` refuses a lane log holding such a SKIP, as yew#42's
  fakeclip pair does.
- **The transport through a real server.** Each case places a server in
  the client by hand (its connection live, no handshake sent) and spawns
  `fakelsp` with `spawn_server`'s framed spec. C's echoed body is a
  request; the port's server answers a request it does not know, and
  that answer's write to an exited child would fail the transport, so
  the port's body is the same object without its id (a notification).
- **RED by name.** `test_lsp_life.c`'s two completion cases are
  yw11b1's: each asserts `ed.lsp.complete`'s refusal and prints RED. The
  language-change case needs `ed.syn.set` (Sprint 39, yw10): it asserts
  that refusal, then runs the LSP half C's handler runs
  (`yew_lsp_buffer_close`) and its transcript, and prints RED.
- **The rows** differ from the prediction's list where the fake server
  could show more: `lspf_error` holds an error reply silent (hover and
  references), `lspf_deadline` holds the late answer ignored as well as
  the silence, `lspf_rename_files` renames across the open file and one
  not open; `lspf_stale` holds the dropped answer off the screen, and
  the drop's count is `test_lsp_life.c`'s delayed-response case
  (`edit_lsp_life_test`); the stale-version refusal is
  `test_lsp_rename.c`'s (`edit_lsp_rename_test`), the resource-operation
  refusal `lsp_feat_rename_refusal`'s.
- **The rename seam.** C edits a buffer through an `EditCtx` over it
  (`yew_ed_edit_ctx_buffer`); the port's edit seam is a window that
  shows the buffer, which the rename has (every file it touches is
  hydrated into a tab).

## Done-when

- [x] The map, the split, the capabilities, the rows (the prediction).
- [x] The panel; hover and signature help with the auto-trigger; the
  four gotos; references; document symbols (the index refusing by name);
  document highlight; rename with its summary, diff and rollback; each
  gated on its capability by name.
- [x] The C tests ported: the parsers, the panel, navigation, rename,
  the gate, and `test_lsp_transport.c` and `test_lsp_life.c` through a
  real `LspServer` over `fakelsp` (the completion and language-change
  cases red by name).
- [x] C's `lsp_feat_rename_diff` and `_refusal` goldens by name; CI
  gates them. `_summary`, `_apply` and `_unknown_key` are recorded until
  yw10 (their style rows hold the C buffer's syntax colouring), the rest
  of each screen held to C's by the `lspg_*` rows.
- [x] The oracle rows over `wolf lsp` and the fake server's error paths.
- [ ] M-YW9's replay: open until a wolf-lsp lane adds the `yew` profile
  and `lspconf serve` (R-yw11b-2 = A); not counted on the rows.
- [x] Static for PAX: the digest, and the client going to a definition
  through `wolf lsp` in a `FROM scratch` container with only the static
  yew and PAX's musl wolf; the control without `wolf` fails (the
  gauntlet's `static` and `pax-container` steps; the record is the
  PR's).
- [ ] yw11b1 (completion, the menu, resolve, snippets, and the shadow
  framework per R-yw11b-1 = A): its own change.
