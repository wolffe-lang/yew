# yw15 — the keys help, and wolf's language server by default

_A yew addition, not in sagitta: `ed.keys`, a list of every mode's key
bindings with each command's help and, for a command the port has not
reached yet, the sagitta sprint and the yew lane that own it. And a
check, with rows, that yew starts `wolf lsp` for wolf files with no
setup, as PAX needs._

## Prediction

Written before the first change (2026-11-07, base trunk `8967813`, wolf
0.2.36 / lupin 0.1.58 / std `78b9d3cb`, `sagitta.pin` `9ace98c2`).

### What sagitta has, and what it lacks

C's `ed.map` (`bind.c:475-522`, the port's `bind_cmd_map`) lists the
**current** mode's **configured** layer only (`ed->bind_keys[mode]`), as
one message, with no help text and no word on what is not ported. Nothing
in C lists every mode, and nothing says what a key will refuse until it
is pressed. sagitta has no startup line and no `:help` command (`main.c`,
`ed.c`: no message at start; the registry has no help command); `--help`
is C's bytes (`main.c:25-86`), which a goldens row holds the port to.

### The shape (R-yw15-1 to R-yw15-8, each implemented as recommended)

- **R-yw15-1, the surface.** **A (recommended): yew's picker**, a new
  host (`PICK_HOST_KEYS`). sagitta's own rule is that "every future list
  in this program is an instance of this widget" (`picker.h:7-11`); it
  brings the filter line (typed text), the scroll, the `shown/total`
  footer, the mouse rows and the three laws, so the modal searches and
  scrolls as the file finder and the palette do. B: the floating panel
  (`edit.panel`): it scrolls but has no filter. C: a new full-screen
  modal: a second list widget, which `picker.h` exists to prevent.
- **R-yw15-2, the key.** **A (recommended): `A-?`**, with `A-S-/` beside
  it. sagitta's key for "list the keys" is `?` with a modifier: F mode's
  `C-S-/`, `C-?` and `C-_` all open `ed.git.actions`, "List effective
  F-mode actions by key" (`keys_default.c:81-83`), three spellings of one
  key because terminals report it three ways. The Control form cannot be
  ours: a legacy terminal (PAX's console, the `dumb` profile) sends
  Control-/ as 0x1F, which is `C-_`, undo in I and E (`runtime/init.fl`),
  and F binds all three. The Alt form is free in every mode's default
  keymap (the floors, every H table, the 389 config rows): a legacy
  terminal sends Alt-? as `ESC ?`, which decodes as `A-?` (the same path
  `A-b` and `A-f` take, `runtime/init.fl`'s readline comment), and a
  kitty-protocol terminal reports the unshifted key with Shift, `A-S-/`
  (`keymap.lu`'s `keyid` drops Shift only when the key carried text,
  and an Alt chord carries none) — so both are bound, as F binds `C-?`
  and `C-S-/`. B: `C-S-/`/`C-?` (sagitta's exact key, but undo on PAX).
  C: `<f1>` (no sagitta convention, and PAX's console F-key bytes are
  not known here).
- **R-yw15-3, where the key lives.** **A (recommended): the user layer**
  (`ed->user_keys`): C builds it empty and puts it in every mode's stack
  between the mode's floor and the config layer (`keys_default.c:107-111`;
  the port's `km_user()`), so a key there reaches every mode, and any
  `bind()` of the same key in an `init.fl` wins (the config layer is
  above it). `runtime/` stays sagitta's byte for byte (`tools/check-
  runtime`), and C's frozen counts hold (`test_runtime_defaults.c`'s 389
  config rows and 60 floor rows, `test_flconf.c`'s per-origin counts).
  B: lines appended to the built-in unit (moves `test_flconf.c`'s counts,
  which run a test runtime). C: `runtime/init.fl` (refused by
  `check-runtime` and the frozen test).
- **R-yw15-4, the command.** `ed.keys` is the first yew row of the
  registry, registered after C's 408 (`src/edit/cmdtab_yew.lu`, not
  generated), so every C command keeps C's id. Its flags are C's
  `ed.macro.list`'s, 0: a picker opener C does not mark as prompting, so
  sagitta's `29_interactive_refusal.fl` (every PROMPTS command must name a
  batch alternative) and the other `ed.commands()` scripts do not move.
  `tools/check-cmd-dispatch`'s fourth rule ("every mapped handler names a
  row of cmdtab.lu") learns yew's rows file.
- **R-yw15-5, pointing users at it.** yew has no startup line and no
  `:help` (neither has C), and a startup message would move every PTY
  golden's first frame; `--help` is C's bytes under a goldens row. **A
  (recommended):** the pointer goes where yew already lists commands: the
  palette (`ed.find.command`) shows `ed.keys` with its help, the E-mode
  completion offers `:ed.keys`, and the README's keys section and
  `docs/MAP.md` name it and the key. B: a yew-only startup message
  (moves goldens: refused by the contract). C: a line in `--help` (moves
  the help row).
- **R-yw15-6, Enter on a row.** **A (recommended):** the picker closes
  and the row's whole line goes to the message row (`C-g` expands it), so
  a row a narrow terminal clipped can be read whole. B: run the command,
  as the palette does (most rows belong to another mode than the one the
  editor is in). C: nothing.
- **R-yw15-7, what "unsupported" means.** **A (recommended):** a row is
  labelled `(unsupported: sagitta Sprint N, ywNN)` exactly when invoking
  its binding answers the deferred status (`CMD_ERR_DEFERRED`) before
  anything runs, and the label is read from the same functions the
  refusals are written from: an unported handler (`impl_id ==
  IMPL_UNPORTED`, its owner `cmd_entry_owner`, the source of
  `cmd_unported_message`), C's own deferral (`CMD_DEFERRED`; no built-in
  carries it at the pin), a plugin command (yw14's refusal), and a
  binding whose argument names a mode the port refuses (`ed.mode.enter
  F`, `mode.lu`'s refusal, which moves into a function both read). A
  refusal that depends on the editor's state (the symbol index with no
  server, a FUSS row of a context menu) is not a label: the command
  itself runs. N is the sprint's number (`cmd_owner`'s first word). B:
  per command only (`f`, `ed.mode.enter F`, would show as supported and
  refuse).
- **R-yw15-8, which rows.** The dispatcher's own rule decides what a key
  does: the first key picks the top layer that knows it, and the rest of
  the chord is read in that layer only (`dispatch.c:278-291`, the port's
  `dispatch_key`). So a mode's rows are each layer's rows (config, user,
  floor) that the dispatcher would reach; a floor row whose first key the
  config layer owns is not listed (L's `q !`, under the config layer's
  `q`). H's motions are rebuilt for the unit it is entered from
  (`keys_highlight.c`): a row the same in all four units is listed once
  as `H`, the others per unit (`H/L`, `H/W`, `H/B`, `H/I`). Modes in the
  registry's order, L W B H I E F; rows in key order within a mode.

### Item 4: `wolf lsp` by default

yew already does it, as C does (`client.c:89`): `src/lsp/client.lu:135`
(`cfg("wolf", "wolf", "wolf", ["lsp"], ["wolf.pkg", ".git"])`), read
through `lsp_client_cfg` (`src/edit/lsp_client.lu:346-359`) whenever no
`init.fl` sets `lsp.servers`; `lsp_pump` (`src/edit/lsp.lu:455-475`)
starts it for every buffer with a path and a language, and `.lu` is
`wolf` by the generated path index (`src/edit/syn_paths.lu`, `lu 20`).

**The root with no `wolf.pkg` and no `.git`.** `lsp_resolve_root`
(`src/lsp/client.lu:189-224`, C's `client.c:391-433`) walks from the
file's directory up to the workspace root, stopping at the first that
holds `wolf.pkg` or `.git`; with neither it answers the workspace root
itself, and a file outside the workspace gets the workspace root too.
The workspace root is the startup cwd unless `--workspace` or one
positional directory names another (`edit.driver`, s56.5 §1). So on PAX,
`yew /home/me/a.lu` started from `/` gives `wolf lsp` the root `/`.
Probed black-box with the pinned `wolf lsp` (2026-11-07): with `rootUri`
`file:///` and a file in a directory without `wolf.pkg`, hover answers
`fn add` and definition answers the definition's range at once; the
server does not walk the root.

### What the rows should show

All red first where there is code to come: each row committed and seen
failing before the code that turns it green.

- **`src/edit_keys_help_test.lu`** (yew's own, new), one case at a time
  by `YEW_EDIT_KEYS_HELP_CASE`:
  - `keys_rows_list_every_mode`: with `runtime/init.fl` loaded, rows for
    L, W, B, H (and its unit rows), I, E and F; every row's command is
    what the dispatcher resolves its sequence to in that mode; L's `q !`
    is not listed; `A-?` and `A-S-/` are `ed.keys` in every mode;
  - `keys_status_agrees_with_invoke`: **the status row.** For every row,
    the binding invoked as a key would invoke it, in a fresh editor:
    the row is labelled iff the status is `CMD_ERR_DEFERRED` with a "not
    yet ported" message, and the label names the message's sprint and
    lane. One command is not invoked, `ed.suspend`, which stops the
    process it runs in (`tty.lu`'s `stop_self` raises SIGTSTP on itself,
    and no row signals a process on the host's own table); the row
    holds it ported by its implementation id instead, and
    `check-cmd-dispatch`'s second rule gives that id its arm;
  - `keys_status_names_sprint_and_lane`: `f` in L reads `(unsupported:
    sagitta Sprint 51, yw13)`, `A-<up>` (`ed.git.hunk.prev`) the same,
    `C-<space>` in I (`ed.compl.complete`) `(unsupported: sagitta Sprint
    44, yw11)`, `K` none;
  - `keys_help_key_opens_the_picker`: `ESC ?` and kitty's `CSI 47;4u`,
    decoded by `term.input` and dispatched, open the keys picker in L, W,
    B, H, I and E; an open prompt is closed first;
  - `keys_picker_draws_and_filters`: the picker drawn at 80 and 160
    columns: a row's key, command and label in the cells (the label never
    clipped before the help); typing `goto` leaves the four gotos; Enter
    puts the row's whole line on the message row and closes the picker;
  - `keys_init_binding_wins`: an `init.fl` `bind("L", "A-?", "ed.nop")`
    takes the key in L, and the picker lists `ed.nop` there.
- **The LSP rows** (`tools/lsp-rows/lsprows.c`, over C yew and the port):
  - `lspw_keys_default`: no `--config` at all (the harness's own
    `XDG_CONFIG_HOME`, so no user `init.fl`): the real keys `K` (the hover
    panel over `add`) and `g d` (from the call to the definition's line);
  - `lspw_keys_bare`: a lone `notes/bare.lu`, no `wolf.pkg` and no `.git`
    in the workspace: `K` and `g d` the same, and `:ed.lsp.info` names
    the workspace root;
  - `lspw_keys_help` (the port's half only; C's half holds C has no such
    key, `unbound: A-?`): `ESC ?` opens the keys picker; typing `goto`
    shows `g d` over `ed.lsp.goto_def`; esc closes it.
  These are green against trunk's port for the LSP half (yew already
  starts `wolf lsp`); `lspw_keys_help` is red against trunk.
- **Unchanged:** every gated PTY golden, the script and Fletch suites,
  and the units whose code moves (`edit_cmdreg_test`, `edit_keymap_test`,
  `edit_bind_test`, `edit_runtime_defaults_test`, `edit_modes_test`,
  `edit_picker_test`, `edit_pickers_test`, `edit_record_test`,
  `fl_marshal_test`, `edit_flconf_test`, `edit_cmdline_test`,
  `edit_batch_test`).
- **The plant:** one hunk in the status function shows the `ed.git.*`
  family as ported; red by name at `keys_status_agrees_with_invoke`.

**What I expect to go wrong:** a ported command that refuses deferred in
a fresh editor for a reason of state (the row will name it, and R-yw15-7
decides it); the picker's filter line meeting an open E prompt; a C
golden that lists command names by completion (`:ed.k`, `:k`) moving
with a 409th command; the kitty spelling of Alt-? decoding as something
other than `A-S-/`; and the hover row's panel under the default shadow
(the existing rows turn it off; these two cannot).

## Forbidden

- No merge, label, tag or release, and no issue filed or closed. No
  attribution trailer.
- Clean room: sagitta at the pin was read and is cited `file:line`
  (`bind.c`, `keys_default.c`, `dispatch.c`, `cmd.c`, `message.c`,
  `mode.c`, `picker.h`, `main.c`, `mod/lsp/client.c`,
  `test_runtime_defaults.c`, `test_flconf.c`, `test_keyseq.c`,
  `tests/script/29_interactive_refusal.fl`); no other editor's source.
  `wolf lsp` was run as a black box (its hover and definition replies to
  a probe), its source not read.
- No golden edited and no sagitta file changed; `runtime/` is sagitta's
  byte for byte (`tools/check-runtime`). `sagitta.pin` and the wolf pin
  are unchanged.
- No other open PR touched.

## Inputs verified

- **Base:** trunk `8967813` (yew#112, yw11b2), still trunk's head. yew#113
  (the CI caps and the goldens selftest's quiet scale, open at
  `bc37e6c`) touches `.github/workflows/ci.yml`, `ci/macos-split-test.py`
  and `tools/goldens-selftest`, none of this branch's files.
- **Toolchain:** wolf 0.2.36 (`5adf3d91`), lupin 0.1.58, std `78b9d3cb`,
  from the pinned archives (`tools/fetch-toolchain`).
- **C yew:** `sagitta.pin` (`9ace98c2`), built by `tools/oracle` (clang on
  macOS, gcc in the Linux image).
- **The server:** the pinned `wolf lsp`. Probed black-box (2026-11-07,
  macOS): over a directory with no `wolf.pkg`, with `rootUri`
  `file://<dir>` and with `file:///`, `textDocument/hover` on `add`
  answers the markdown `fn add` and `textDocument/definition` on the call
  answers the definition's range, at once both times.
- **PAX's compiler:** the musl static `wolf` at `v0.2.36` by PAX's
  recipe, `2df1fb76…` (16,257,584 bytes), copied by value from the
  previous lane's build and checked by digest.

| host | role |
|---|---|
| Apple M-series Mac, macOS arm64 | builds, the unit files natively, the checked machine's per-case runs, the macOS take (C yew built with clang) |
| x86-64 Linux, rootless podman, a 6-CPU block and its light CPUs | the gauntlet in yew CI's image, the static binary and the scratch container |

## Evidence index

Commits, in order (the prediction first, every row red before its code):

- `a6e8f6f` note: yw15's prediction: the keys help's shape, the key, the status, wolf lsp by default
- `3309be8` edit_keys_help_test: every mode's rows, the status row, the key, the picker (red: no ed.keys)
- `6085d43` lsp-rows: the fake's root mode writes initialize's rootUri to its marker
- `a5d8c4d` lsp-rows: wolf lsp with no setup through K and g d, a bare file's root, the keys help (red: no keys help)
- `91005a2` edit_keys_help_test: wolf fmt
- `fe92af1` edit.cmd: yew's own rows after C's; the plugin refusal's owner and C's deferral sprint by name
- `93a0619` edit.cmdtab_yew: ed.keys, yew's first registry row
- `85ffd3e` edit.mode: the unported mode's owner, read by the refusal and the keys help
- `0010365` edit.invoke: the plugin refusal names cmd_plugin_owner's sprint and lane
- `9e070b5` edit.keyshelp: every mode's rows by the dispatcher's rule, the status from the refusals' owners, the picker
- `988c245` edit.picker: the keys host: the wide box, the label whole before the help, no split
- `93520c1` edit.impl: dispatch ed.keys
- `cec6739` edit.ed: the user layer carries the keys help's key in every mode
- `fe0f43b` check-cmd-dispatch: yew's own rows file names handlers too
- `e440132` note: the suspend exclusion in plain words
- `da6264a` edit_keys_help_test: copy the row the label is read from
- `8450f6f` edit.cmd: keys, yew's own application verb, so ed.keys is a valid name
- `6cc5219` edit_keys_help_test: the label's mode column, and kitty's report with the alternate key
- `37d2472` check-test-cases: the keys help's six cases one at a time
- `1fe70c7` README: the keys section (ed.keys, the LSP keys, wolf lsp by default); the LSP features shipped
- `824bcbf` MAP: section 9, yew's own additions: ed.keys
- `9a44e0d` CHANGELOG: yw15
- `ffd573f` edit.keyshelp: Enter's line replaces whatever the message row held
- `85d098c` edit_keys_help_test: the message row's line named when it differs
- `06a3acd` edit_keys_help_test: Enter shows the selected row, the filter's first
- `505038f` edit_keys_help_test: the status row prints the unsupported rows by owner
- `cc9d8de` lsp-rows: C's half of the keys help row: ESC ? opens nothing, :ed.keys is unknown; the port's :ed.keys too
- `f8bdaba` edit.keyshelp: H's row counts by map index, which the checked machine runs (map.get dispatches Eq on str)
- `a73f060` edit_keys_help_test: the mode counts by map index
- `dcfdbd8` check-test-cases: the keys help's four cases past the checked machine's budget
- `5a325a5` edit_keys_help_test: the key route and the init.fl case boot without the shipped runtime
- `8cba7b1` check-test-cases: the key route's allowance says what it runs
- `3c126e1` note: yw15's forbidden, inputs, evidence, findings, decisions and done-when
- `080fa1e` lsp-rows: the keys help row waits on the picker's footer; the command line's hint covers its title

### What the work found

- **`ed.keys` is not a name C's registry admits.** `command_name_valid`
  (`cmd.c:1504-1671`, the port's `cmd_name_valid`) takes `ed.<verb>` for
  seven application verbs only (`quit`, `quit_force`, `suspend`, `redraw`,
  `repeat`, `nop`, `map`), so the first build exited with `invalid command
  name: ed.keys` at registration. `keys` is yew's own application verb
  (`yew_app_verbs`), beside C's seven (R-yw15-9).
- **The rows at the pin's `runtime/init.fl`: 526.** L 121, W 58, B 55, H 58
  shared and 34 by unit (H/L 10, H/W 10, H/B 8, H/I 6), I 75, E 70, F 55.
  82 are labelled unsupported: 57 `(unsupported: sagitta Sprint 51,
  yw13)` (F mode's own keys, the hunk jumps `A-<up>` and `A-<down>` in L,
  W and B, and `f`, `ed.mode.enter F`, in the three unit modes), 24
  `(unsupported: sagitta Sprint 43, yw11)` (the shadow's accept, next and
  previous keys) and 1 `(unsupported: sagitta Sprint 44, yw11)` (I's
  `C-<space>`, `ed.compl.complete`). The test prints the count per label.
- **The status row agrees on every binding it invokes.** 525 bindings
  invoked, each in a fresh editor as its key would invoke it (a binding
  that captures the next key handed `a`, as the dispatcher hands the
  key's text); 82 answer the deferred status with the label's own sprint
  and lane, the other 443 do not, and 0 disagree. The 526th, `C-z`
  (`ed.suspend`), stops the process it runs in; it is held ported by its
  implementation id, which `tools/check-cmd-dispatch`'s second rule ties
  to its `run_impl` arm. State-dependent refusals are not labels
  (R-yw15-7): with no server, `g s` refuses the symbol index by name
  (`not yet ported: the symbol index`, `CMD_ERR_STATE`), and with one it
  lists the document's symbols.
- **An error on the message row kept Enter's line off it.** C's rule
  (`message.c`, the port's `message_may_replace`): an INFO message does not
  replace an active ERROR. The row was asked for, so the keys help clears
  the message row first.
- **The filter ranks equal matches by the scorer's order, not the list's.**
  `hunk.prev` matches L's, W's and B's `A-<up>` equally, and B's comes
  first. The Enter row follows the selection.
- **The checked machine refuses `map.get` on a `str` key.** Every case
  first answered `unsupported — trait dispatch on a non-nominal receiver`
  at `std://map/map.lu:243` (`cmp.Eq.eq(pair.0, k)`, the method form of
  `Map.get`); the map index form (`m[k] else d`, `m[k] = v`) runs there.
  With it, the label and line case and the `init.fl` case run whole on the
  checked machine (`exit(0)`, the second after it stopped booting the
  shipped runtime it does not need); the other four exhaust its step
  budget (the rows over `runtime/init.fl` held to the dispatcher, the 525
  editors of the status row, the key route's 18, the picker's three) and
  are listed by name in `tools/check-test-cases.txt`, the native lane
  covering them.
- **C has no message for an unbound Alt key in the `dumb` profile.** The
  prediction had C's half of `lspw_keys_help` reading `unbound: A-?`; C
  (and trunk's port) show nothing after `ESC ?`. C's half now holds that
  nothing opens and that `:ed.keys` is an unknown command.
- **The keys help's title is not a detector when `:` opens it.** The first
  macOS take at `3c126e1` passed every unit file, the release build and
  30 of the 31 rows, and failed `lspw_keys_help` in the port at its second
  open (`:ed.keys did not open the keys help`) with the picker open on the
  screen (`526/526`, its footer and L's rows). The command line's hint for
  the typed name, `ed.keys → keys` (`cmdline.c:810-857`, the port's
  `cl_hint_value`), is drawn over the picker's title row, as the
  diagnostic list's title is in `lspw_open_diag`. The row now waits on the
  keys help's footer (`enter show the row`) for every open and close, and
  holds the title only where the key opened it.
- **A filtered row run keeps no screens and compares RED.** `run-lsp-rows
  --filter bare_root` passed in both editors and printed `lsp-rows: RED`
  for `no screens kept` (`compare.py`): the new rows hold their own
  assertions and keep no screens, and the full run has the other rows'.
- **The red witnesses.** `edit_keys_help_test` at its commit (`3309be8`)
  fails to compile on the items its code brings (`E0301`: `KeysRow`,
  `keys_rows`, `keys_row_line`, `keys_row_label`, `keys_seq_width`,
  `keys_cmd_open`, `PICK_HOST_KEYS`). The rows at their commit (`a5d8c4d`,
  macOS, trunk's port built at it): `lspw_keys_default`, `lspw_keys_bare`
  and `lspf_bare_root` pass in both editors (yew already starts `wolf lsp`
  and resolves the root as C does); `lspw_keys_help` fails in the port by
  name (`ESC ? did not open the keys help`); that runner's C half was the
  wrong one (above). With the runner at `3c126e1` against the same trunk
  port, C's half passes and the port's fails by name as before. `tools/
  check-cmd-dispatch` at trunk refuses the new handler (`map:
  yew_keys_cmd_open names no row of cmdtab.lu`).

### Decided

Each as recommended in the prediction, implemented:

- **R-yw15-1 = A** (the surface): yew's picker, `PICK_HOST_KEYS`. The
  host's rows draw their label (mode, keys, command, status) whole before
  the help, which takes the room the label leaves (at least 12 cells),
  right-aligned as the picker's detail column is; it gets the wide box
  (`PICKER_PREVIEW_MAX_W`, 160) a preview picker gets; Ctrl-V and Ctrl-S
  accept as Enter (nothing to split for). At 80 columns the help gives
  way on the longer rows; at PAX's 160 every row has its help.
- **R-yw15-2 = A** (the key): `A-?`, with `A-S-/` beside it.
- **R-yw15-3 = A** (where the key lives): the user layer.
- **R-yw15-4** (the command): `ed.keys`, yew's first registry row
  (`src/edit/cmdtab_yew.lu`, after C's 408), flags 0, help "List every
  mode's key bindings, marking what is not ported yet (yew's own)".
- **R-yw15-5 = A** (pointing users at it): the palette, the command
  line, the README's keys section and `docs/MAP.md`; no startup line and
  no `--help` line.
- **R-yw15-6 = A** (Enter): the row's whole line on the message row,
  replacing whatever the row held.
- **R-yw15-7 = A** (what "unsupported" means): the deferred status before
  anything runs, read from the refusals' own owner functions.
- **R-yw15-8** (which rows): the dispatcher's rule; H shared and per unit.
- **R-yw15-9 = A** (the name): `keys` is yew's own application verb
  (`yew_app_verbs`), so the contract's `ed.keys` registers under C's naming
  rule. B: `ed.ui.keys.list`, a name C's vocabulary already admits
  (`:ui.keys.list` to type). C: `ed.map` with an argument (changes C's
  command).
- **R-yw15-10 = A** (`--clean`): the key stays under `--clean`, which
  keeps the floor and the user layer and drops the configuration
  (`flconf.c:375-386`, the port's `cfg_source_enabled`): the help is panic-safe and `:ed.keys` works
  either way. B: no user rows under `--clean`, as C's empty layer.

## Done-when

- [x] The prediction: the shape, the key, the status, item 4 (`a6e8f6f`).
- [x] `ed.keys`, yew's own (named so in `docs/MAP.md` §9, in its help text
  and in `edit.keyshelp`'s header): the picker over every mode's
  bindings, each row its mode, keys, command, help and status, the status
  read from the refusals' own owner functions.
- [x] The status row: every bound command invoked, and the modal and the
  invocation agree (525 of 526; `ed.suspend` held by its id).
- [x] Search and scroll as the other pickers: the filter by typed text,
  the arrows, the pages, the footer's count.
- [x] The key: `A-?` and `A-S-/`, free in every mode's default keymap,
  sagitta's `?`-lists-the-keys convention; `:ed.keys`; the
  README's keys section; no startup line or `:help` exists to point from
  (R-yw15-5).
- [x] `wolf lsp` by default: already yew's (`src/lsp/client.lu:135`); rows
  through `K` and `g d` with no setup, over a package and a lone file, the
  lone file's root the workspace root; the static yew in a `FROM scratch`
  container with PAX's musl wolf, the same over both (the gauntlet's
  `lsp-rows`, `static` and `pax-container` steps; the record is the PR's).
- [x] No golden moved: every gated PTY golden, the script and Fletch
  suites, by name, and `runtime/` byte for byte (the gauntlet's
  `pty-ci-gates`, `script-yw09-gate`, `fletch-goldens` and
  `check-runtime` steps; the record is the PR's).
- [x] CHANGELOG under Unreleased; README read and refreshed (the keys
  section, and the Status paragraph's LSP sentence, which still said
  hover, navigation and rename were to follow).
- [ ] The Linux gauntlet, the plant and the macOS take at the head: the
  PR's.
