# yw04 — execute and search

**Opus 5.5, crawl 54, 2026-10-20.** Contract: planning repo
`sprints/yew/04-execute-and-search/yw04-execute-and-search.md` at
`f2fed84` (drafted by yw03 as this repo's
`notes/contracts/yw04-execute-and-search.md`, adopted). Ports sagitta
campaign 04 (`s18`, `s18_5`, `s19`, `s20`, `s21` at `sagitta.pin`) with
the prompt and shell rows of campaign 13 that build on it (`s57_17`,
`s57_18`, `s57_21`, `s57_23`–`s57_32`): the `:` prompt in full (its
history, grammar, ranges, completion engine, ranked menu, fuzzy scorer,
pager, readline keys, selection and clipboard), shell jobs and the shell
completion engine, the regex engine (Thompson NFA, Pike VM, lazy DFA,
literal prefilter), search, replace and the jump lists, and the
live-editor torture lane.

## The toolchain at the lane's start

`gh release list -R wolffe-lang/wolf-lang` at **2026-10-20T22:00:21Z**:
the latest release is **v0.2.33** (2026-10-19T18:37:53Z);
`gh release list -R wolffe-lang/wolf-interp`: **lupin 0.1.54**
(2026-10-17T16:48:34Z). r39 (lupin 0.1.55, then wolf 0.2.34) is in
flight and unreleased. The pin yw03 left stands — wolf 0.2.33
`85dab5d7`, lupin 0.1.54, wolf-std `cceda63`, staged by digest through
`tools/fetch-toolchain` on kasumi — so deliverable 1's bump is not this
lane's first commit. The release list is read again before deliverable
3 (R-yw04-1, below); if v0.2.34 is out then, the bump is a commit of its
own with its prediction.

**Deliverable 3 was reached before 0.2.34 existed.** The shell fork read
the release list when it started `job.c`'s model, at
**2026-10-20T23:19:20Z** (and again at 2026-10-21T03:00:51Z and
12:50:04Z): v0.2.33 every time (`notes/yw04-evidence/shell/
toolchain-at-job-model.txt`). **v0.2.34 was published at
2026-10-21T12:58:10Z** (created 12:49:57Z), after deliverable 3's code had
landed at 0.2.33 with R-yw04-1's stops. So, as R-yw04-1 rules, the lane
finishes at 0.2.33 and **the bump is yw05's** first commit
(`notes/contracts/yw05-panes-tabs-groups.md` deliverable 1), which turns
the job half's stops into calls.

## Rulings taken at launch (the orchestrator's, recorded)

- **R-yw04-1 = A.** The job half — deliverable 3's streaming, filter and
  session — STOPs by name until `os_signal_wait_fds` (G2, wolf-lang#795)
  is pinned; the prompt, regex and search halves land. If v0.2.34 is
  released before deliverable 3 is reached, the bump is a commit of its
  own with its prediction and the job half is taken as the contract says
  (yw02's and yw03's KNOWN-RED and SKIP cases that the new calls serve
  turn green); if it lands after, the lane finishes at 0.2.33 and leaves
  the bump to yw05, saying so.
- **R-yw04-2 = A.** The narrow region registry s18.5 §8 assumes
  (`yew_region_frame_begin`/`add`/`hit`, last-added-wins, the menu's rows
  only) and the loop's mouse route; yw05 widens it with panes, yw06 with
  drag and scroll.
- **R-yw04-3 = A.** The filter's write side is a STOP by name until
  wolf-lang#818 (a non-blocking pipe write and a write-ready wait, G30).
- **R-yw04-4 = A.** The 25 completion specs (`runtime/completions/*.fl`,
  copied verbatim) are read with yw03's literal reader `edit.fldata`,
  extended; a statement it cannot take is refused by line and column
  naming yw07.
- **R-yw03-6 = B.** A paste key that reaches the clipboard STOP (G30)
  refuses the paste with C's deferred status and a message naming G30,
  and keeps the session; yew#18 (in-band invalid UTF-8 in a paste) is
  taken if it falls in the lane's path.
- **wolf-lang#806/#807** are fixed on branch s251 (PR #823), unreleased:
  yw03's registry shape (a handler kind and one `match` on literal
  implementation ids) is kept; its retirement is yew#17's, at the pin
  that carries s251.

## Prediction (written 2026-10-20, before the first port line)

**The contract's**, kept: the regex ports with no backtracking, the 188
golden rows and the differential fuzz green and the pathological table
inside its bounds; the prompt's 47 cases and search's 17 go green
without a golden edited and without one of campaign 03's 62 changing as
the narrow `:` is replaced; the job half's 40 cases are green only on a
pin with `os_signal_wait_fds` (G2) — at 0.2.33 they reach R-yw04-1 and
the filter's interleave reaches G30; `--category`/`--case` regenerate
byte-identical to sagitta's arrays; keypress → paint in the prompt and
the search session within 2× of C yew, regex throughput within 2×, and
`perf_jobstream`'s streamed 50 MiB holding keypress p99 within 2× where
the job half runs.

**The lane's own**, from sagitta's sources and PTY registry before any
code:

1. **R-yw04-1 reaches further than streaming, filter and session.**
   Every surface that reads a child's pipe while the loop keeps
   painting is a job in C: the completion generators (`compgen.c`,
   `s57_24_generator_pending`, the `make` targets), `--help` parsing
   (`comphelp.c`, the three `s57_25_*`), the fish oracle (`compfish.c`,
   `s57_26_fish_stub_rows`), `:r !` (`s19_read_at_cursor`) and cd-aware
   completion (the session's cwd, `s57_32_*`). At 0.2.33 the
   deliverable-3 goldens that can be green are the ones that complete,
   lex or refuse without a child's pipe: `s57_18_*` (3), `s57_23_*` (6),
   the static-spec rows of `s57_24_*`, the history rows of `s57_26_*`
   and `s19_term_is_not_a_feature`. Predicted: **at most 16 of the 40**
   green at 0.2.33, each red one named by R-yw04-1 or R-yw04-3.
2. **`A-e` needs a second tab.** `s57_31_edit_in_buffer_open` and
   `_roundtrip` open `*command-line*` in a NEW tab and close it on
   accept (`cmdedit.c:341-364`), past yw03's one-tab strip (R-yw03-3).
   Predicted: a narrow extension of `edit.tabs` (open, switch, close, the
   strip for a few tabs with no overflow) or both cases red naming yw05
   — asked as **R-yw04-5** when the prompt reaches it.
3. **The module seam.** `src/search/`'s `parse`, `compile`, `pike`,
   `dfa`, `literal`, `pack`, `regex`, `search` and `replace` take no
   `Ed` (their includes stop at `text`, `unicode` and `util`) and form
   the `search` module below `edit`; `overlay.c` and `searchui.c`
   include `edit/ed.h` and live in `edit` with sagitta's names (yw03's
   module rule, E0303), as do `cmdline`, `cmdcomp`, `cmdparse`,
   `cmdhist`, `cmdedit`, `menu`, `shctx`, `comp*`, `shell*`, `job`,
   `jumplist`, `search_cmds` and `readline_cmds`; `fuzzy.c` takes only
   `util/sort.h` and opens the `ws` module at s26's path.
4. **Function pointers become kinds.** C's completion sources
   (`YewCompSource` with a `collect` callback, s18.5 §3), the menu's host
   (`YewMenuHost` callbacks), job consumers and generators all cross
   files as function pointers; each becomes a kind matched in one place
   (G19/G20), as yw03's registry did. No function value crosses a module
   boundary.
5. **Campaign 03's 62 stay green.** Every one types `:ed.quit` (or
   `ed.quit_force`, `ed.suspend`) at its teardown after its snapshot,
   except the dirty-prompt cases that snapshot after `:ed.quit enter`;
   the full prompt draws its line, ghost text and menu on the same
   footer row, so predicted green unchanged — the risk is the ghost/hint
   painting a frame the old narrow `:` never drew before an Enter.
6. **The live torture lane is reachable on the first day**: the driver
   types `:ed.quit_force\r` with a raw CR, which G34's interim reads as
   Enter (R-yw03-4); predicted green but for G3's red by its exact line.
7. **G33 grows a new hot path.** The prompt rebuilds its candidate list,
   its menu rows and its ghost on every keystroke inside the
   session-long `Ed`; a `List` replaced there is held to the session's
   end (G33), so predicted: a measurable resident growth per prompt
   keystroke unless the rebuilds reuse storage in place (yw02's spare
   pair shape) — measured, R-yw03-7's row.

Hits and misses are recorded in §3 as they are measured.

## The plan

The contract is the directive; this is the order. The leaf units run as
forks of the lane on their own branches (`yw04-<fork>`), each with its
own worktree on nomad-1 and its own tree on kasumi, merged into `yw04`
with a merge commit naming what landed (yw03's shape); the lane itself
holds the toolchain, the torture lane, the integration, the gates and
the note.

1. **The toolchain** (deliverable 1): read at the start (above) and
   again before deliverable 3.
2. **Forks, in parallel** (each ports its C with `file:line` headers,
   its unit suites one for one, its fuzzers and perf harnesses, and
   records its evidence under `notes/yw04-evidence/<fork>/`):
   - `regex` — deliverable 4 whole: `src/search/` (`parse`, `compile`,
     `pike`, `dfa`, `literal`, `pack`, `regex`, `search`), the generator's
     `--category` and `unicode.category`/`tables_cat`; `test_re_*`,
     `re_golden.h` as data, `fuzz_re_diff` over the ported `re_ref`,
     `fuzz_re_compile`, `fuzz_re_quote`, `perf_re_pathological`,
     `perf_re_throughput`.
   - `grammar` — `cmdparse` (tokens, the 9-row expansion table, the
     three quoting forms, ranges with the six `range_policy` rows, the
     13 errors) and `cmdhist`; `test_cmdparse`, `test_cmdrange`,
     `test_cmdhist`, `fuzz_cmdparse`.
   - `comp` — `cmdcomp` (sources as kinds, the LCP, quoting, live
     filtering), `menu` with the narrow region registry (R-yw04-2),
     `ws.fuzzy`; `test_cmdcomp`, `test_menu`, `test_fuzzy`, `fuzz_fuzzy`,
     `perf_cmdcomp`.
   - `prompt` — `cmdline` in full replacing yw03's narrow `:`, `cmdedit`
     (`A-e`), `readline_cmds`, the pager, the selection and clipboard,
     R-yw03-6; `test_cmdline`, `test_prompt_keys`, `test_readline_keys`;
     the 47 prompt goldens as the grammar and comp forks land.
   - `shell` — `shell_quote`, `shctx`, `compspec` over `edit.fldata`
     (R-yw04-4) with the 25 specs, `compgen`, `comphelp`, `compfish`,
     `shell`, `shell_cmds`, `job` and `shsession` as far as R-yw04-1 and
     R-yw04-3 let them; the unit suites, `fuzz_shctx`, `fuzz_comphelp`,
     the `/bin/sh` round trip; the 40 goldens as far as the rulings
     reach.
   - `search` — `jumplist`, `replace`, `overlay`, `searchui`,
     `search_cmds`; `test_jumplist`, `test_overlay`, `test_replace`,
     `test_search_smartcase`, `test_searchui`, `fuzz_search`,
     `perf_search_latency`; the 17 `s21_*` goldens on the regex and
     prompt forks' merges.
3. **The live-editor torture lane** (deliverable 6), the lane's own.
4. **The gates** (deliverable 7): both `check-test` lanes with the
   per-case checked run for every `[native]` fallback, the 104 campaign-04
   goldens gated by name in CI beside campaign 03's 62 (the red ones
   recorded by owner), the 2× gates on kasumi under `taskset -c 0-3` in
   a container.
5. **The note and the map** (deliverable 8), yw05's contract, the PR.

## Slips, as they happened (RULES §5; the coordinator's reports)

- **2026-10-20T22:22:36–22:22:43Z**: the regex fork ran a recursion-depth
  probe (`~/lanes/yw04-regex/yw04-regex-probe/rec/`, `nat` and `rel`, the
  native and release builds of one program) on kasumi's HOST; it overflowed
  its stack and systemd-coredump stored ten cores (uid 1000, pids
  632790–632988), which the coordinator removed. Only the probe's own
  processes were involved. From then on every fork runs anything that can
  trap or fault inside the lane's container, which also gained
  `--ulimit core=0` (`notes/yw04-evidence/gates/ctr.sh`).
- The regex fork, reported by itself: it piped its own host-side `perf
  record` through `head` (SIGPIPE to its own profiler, a process it
  started), and stopped two of its own stale campaign containers — one by
  its recorded container id, and one picked out by its `8-11` CPU set after
  checking it was only the fork's (a selection by pattern, which RULES §4
  forbids even when it hits only one's own). After the cores, a re-run of
  its stack-overflow witness inside the container left systemd-coredump
  journal entries at 2026-10-20T23:23:27Z with `COREFILE none` — no core
  stored, the `--ulimit core=0` working.
- **The usage limit** (2026-10-21, before 01:50Z): the lane and three
  forks (prompt, shell, search) were cut off mid-turn; on the reset the lane
  re-checked its branch, worktrees, uncommitted edits, kasumi jobs and
  containers by recorded pid (none live) and CI on `yw04`, then resumed the
  forks from their saved state.
