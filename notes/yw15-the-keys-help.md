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
    and the lane rules keep signals off a host's process table); the row
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
