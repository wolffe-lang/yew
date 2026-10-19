# yew

yew — the maintainer's modal terminal editor ("tmux and vim had a baby":
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
sagitta change is made here. Fletch stays Fletch: its scripts, data
files and recorder output run on both editors.

C yew's numeric quality gates (keypress to paint p99 <= 5 ms, cold start
<= 20 ms, a 100 MB file <= 150 ms, binary <= 2,310,144 B, memory <= 1.6x
the file) are the port's targets: every lane records the wolf/C ratio
for the gates its subsystem touches, measured on one host beside C yew's
number from the same run, and a 2x gate holds from the first paint.

## Status

Campaign 00 of sagitta's fifteen (yw00): the repo, the harness, `util`
(strmap, intern, buf, sort) and `unicode` (UTF-8 with the lossless
invalid-byte policy, UAX #29 grapheme clusters, UAX #11 and emoji
widths) with a wolf generator over `ucd/16.0.0/` producing tables
identical to sagitta's, and sagitta's unit tests ported one for one.
`yew --version` prints what C yew prints; every other path hard-errors
naming its sagitta sprint and the port lane that lands it. The map of
every sagitta directory and sprint to a port lane, and of every wolf
gap the port has met, is [`docs/MAP.md`](docs/MAP.md).

## Build and test

```sh
tools/fetch-toolchain            # wolf, lupin and std by digest, into .wolf-bin/
tools/build                      # target/native/yew and target/release/yew
tools/check-test                 # the unit tests, warnings denied
tools/check-tables               # tables.lu is the generator's, and sagitta's
tools/oracle --unit              # C yew at the pin, gcc and clang, its unit suite
tools/goldens --yew target/release/yew
```

Builds and tests run on linux x86-64 and macOS arm64; on linux aarch64
wolf 0.2.32 builds no tier (wolf-lang#614) and CI asserts the refusal
by name, as pelt does. The oracle builds everywhere.

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
