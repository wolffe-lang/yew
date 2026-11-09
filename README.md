# yew

yew — a modal terminal editor ("tmux and vim had a baby":
C11 + POSIX, zero dependencies, 218 KLOC at
[tenseleyFlow/sagitta](https://github.com/tenseleyFlow/sagitta), with
its scripting language Fletch) — ported to wolf, **byte-identical**, so
that [PAX](https://github.com/wolffe-lang/pax)'s console has an editor
built in its own language and wolf has its largest real program. Track
12 of the planning repo (`sprints/yew/index.md`, ruling #89).

## The oracle

C yew built from the commit in `sagitta.pin` is the oracle. The wolf
binary is held to C yew's own tests, unchanged: its PTY goldens
(`tests/pty/runner --yew <binary>`), script, Fletch, syntax and torture
suites. `tools/oracle` fetches and builds it; `tools/goldens --yew
<binary>` runs its suites against any binary and prints one
`pass/fail/skip` line per suite with a diff per failure. A golden that
disagrees with the port is a STOP and a ruling, never a golden edit; no
sagitta change is made here. Explicitly approved differences are listed in
`tools/goldens-divergences.txt`: each names the port's expected snapshot and
pins the unchanged C golden's SHA-256. The harness prints each divergence
by name; a changed C golden requires re-evaluation. Fletch stays Fletch: its scripts, data
files and recorder output run on both editors.

C yew's numeric quality gates (keypress to paint p99 <= 5 ms, cold start
<= 20 ms, a 100 MB file <= 150 ms, binary <= 2,310,144 B, memory <= 1.6x
the file) are the port's targets: every lane records the wolf/C ratio
for the gates its subsystem touches, measured on one host beside C yew's
number from the same run, and a 2x gate holds from the first paint.

## Status

Campaigns 00 to 07 of sagitta's fifteen (yw00 to yw09), campaign 09's
language server client (yw11) and campaign 11's git layer and F mode
(yw13), at wolf
0.2.36 (lupin 0.1.58): `util` and `unicode` (tables generated from `ucd/16.0.0/`,
identical to sagitta's); the terminal (raw mode, the input decoder, the
cell grid and damage renderer, the restore on every exit path); the text
engine (piece tree, byte-exact load, the atomic and synced save, the
crash journal, undo); the modal core (modes, keymaps, dispatch,
selection, multi-cursor); the `:` prompt with its completion engine, the
regex engine, search and replace, and shell jobs (`:!`, the stream, the
region filter, `:r !`, the persistent session); and the workspace: the
pane tree, tabs with the strip and its overflow, tab groups, the
workspace key and its saved session (resumed on the next launch,
byte-identical to C yew's state file), the startup plan, the fuzzy
finder over the workspace walk and `.gitignore` with the buffer, undo
and command pickers, and the mouse: click, wheel, drag and drop with
the strip's previews, drag-to-spawn and the context menus; and Fletch,
the editor's scripting language, as `yew fl`: the lexer, parser,
compiler and VM with its collector and standard modules, the
interactive prompt, and the structured report a broken VM invariant
exits with (campaign 06's 39 conformance units, its coverage ledger and
three fuzzers against C's drivers). Fletch also runs inside the editor:
origin-owned bindings and hooks, live `init.fl`, recording and replay with
the recorder/Fletch round-trip, the macro browser and library, workspace
config trust, and headless `--batch` editing (campaign 07). The language
server client's first half (campaign 09): a server started for each
language and workspace root as a job on pipes, its handshake, shutdown,
crash restart and deadlines, document sync (incremental when the server
asks for it), and diagnostics in the gutter, under the text, on the
statusline, as the cursor's hint and in a list with jumps, so `wolf lsp`
works in the editor; and its features: hover and signature help in a
floating panel, the four gotos, references, document symbols, document
highlight and rename. Completion follows. FUSS, the git layer and F mode
(campaign 11, s51 and s52): git as a subprocess through a fixed verb
table, its environment pinned and its `status --porcelain=v2` grammar
parsed byte for byte, a status cache on the wall clock; F mode's tree and
drawer, depth navigation, type-to-jump, the verbs with their typed
confirmations, the commit editor, the pickers, the actions palette and the
diff viewer; s53's hunks, blame and diff view are yw13b's.
Each campaign's reachable PTY goldens are gated by name against C yew's
(the cases that draw source text in syntax colours, campaign 05's four
and campaign 11's 24, are recorded until yw10 lands highlighting); every path
not yet ported hard-errors naming its sagitta sprint and the port lane
that lands it. The map of every sagitta
directory and sprint to a port lane, and of every wolf gap the port has
met, is [`docs/MAP.md`](docs/MAP.md); `CHANGELOG.md` has each lane.

The 0.2.35 adoption restores read-only callbacks and shared stable sorting,
uses the standard terminal wrappers and non-blocking clipboard writes, and
reuses menu and tab-frame storage. Mutable callbacks and some
allocation/filesystem work remain open in the map. The start-up and tab-switch
rows meet the 2× gate again (yew#55); first Backspace stays named under
yew#53. Eleven of Fletch's thirteen release
bench rows are over 2× and named under yew#77, and its native tier is a
named backend MISS. Of the five gated editor rows, four are named under
yew#89 and `macrolib_scan_200`, which sits on the 2× line, under yew#77;
every row is also held to its own regression baseline, re-measured at trunk
on the current lane host. Other host/metric rows keep the 2× gate.

## Build and test

```sh
tools/fetch-toolchain            # wolf, lupin and std by digest, into .wolf-bin/
tools/build                      # target/native/yew and target/release/yew
tools/check-test                 # output/refusals visible; native fallback counted
tools/check-test --native        # all unit files built and run natively
tools/check-test --no-native-fallback # strict checked-only run (refusals fail)
tools/check-test-cases           # the checked machine one case at a time (files past its budget)
tools/build-fakeclip             # C's fake clipboard tool alone, for the clipboard rows
tools/check-test --fakeclip-ran  # after both lanes: no clipboard row skipped for want of it
tools/check-tables               # tables.lu is the generator's, and sagitta's
tools/oracle --unit              # C yew at the pin, gcc and clang, its unit suite
tools/goldens --yew target/release/yew
tools/check-fletch-goldens target/release/yew   # Fletch: 39 units, stressed and twice
tools/check-fletch-coverage target/release/yew  # the coverage gate and its ledger
```

Builds and tests run on linux x86-64 and macOS arm64; on linux aarch64
wolf builds no tier at the pin (wolf-lang#614) and CI asserts the refusal
by name, as pelt does. The oracle builds everywhere.

## Runtime and completion

`YEW_RUNTIME_DIR` explicitly selects a runtime directory. Otherwise the
install prefix `/usr/local/share/yew/runtime` is used only when its
`init.fl` is byte-identical to this build's embedded copy. A mismatched
install warns once and uses the built-in runtime, not the current
working directory. With no installed runtime, `./runtime` precedes the
embedded fallback.

A refused built-in binding reports the command and its source location,
skips that row, and keeps the other bindings. A failing user or workspace
config stops at its raise and removes that source's registrations; the
built-in bindings remain. Once Tab enters a completion table, Up moves to
the row above and wraps at the top to the true last row, beyond the visible
page if necessary. Up before entering the table still walks history.
Down at the bottom still returns focus to the command line, keeping the
last candidate.

## Keys

`A-?` (Alt and `?`; a kitty-protocol terminal reports the same keys as
`A-S-/`, and both are bound) opens the keys help, `:ed.keys`: every
mode's bindings in one list, each row the mode, the keys, the command
and its one-line help, and `(unsupported: sagitta Sprint N, ywNN)` on a
binding the port still refuses, naming the sagitta sprint and the lane
that land it. Type to filter; Enter shows the row whole on the message
line; Esc closes. The keys help is yew's own (sagitta's nearest is
`ed.map`, the current mode's configured bindings), and an `init.fl`
binding of the same key wins over it.

The language-server keys: in L mode `K` hover, `g d` definition, `g D`
declaration, `g y` type definition, `g i` implementation, `g r`
references, `g R` rename and `g s` document symbols; in I mode `A-k`
signature help. For a `.lu` file yew starts `wolf lsp` from `PATH` with
no configuration (sagitta's default server table), rooted at the
nearest directory up to the workspace that holds `wolf.pkg` or `.git`,
else at the workspace root: the startup directory, or `--workspace DIR`.

## The rules in brief

Reading sagitta is allowed and expected (every commit on it is the
maintainer's); every wolf unit cites what it ports. Clean-room for
everything else: never another editor's source, never fackr's crates,
never a regex, JSON, HTTP or VT library's source. No dependencies but
wolf-std. Unicode tables are generated from `ucd/` by a wolf program,
checked in, with a drift check. Every wolf, std or lupin gap is filed
upstream with a witness and listed in the map; the port never works
around a compiler bug silently. `CLAUDE.md` has the rest.

## Licence

GPL-3.0-only (`LICENSE`), with the wolf Training Data Permission
(`LICENSE-TRAINING-DATA`), as pax and boreutils. `ucd/` is Unicode,
Inc.'s data under the Unicode licence (`ucd/LICENSE`).
