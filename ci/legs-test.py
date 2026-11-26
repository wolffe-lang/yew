#!/usr/bin/env python3
"""ci/legs-test.py — ci/legs.py's own proof (tl30). python3 and bash only.

    ci/legs-test.py

  L1  the legs by event: a pull request and a trunk push run `oracle` on
      every host and `port` on every host but macOS, and `macos-perf`; a
      trunk push also runs `macos-fuzz`, which a pull request leaves; the
      nightly and a dispatch run every leg and both macOS jobs; an event the
      planner does not know gets the pull request's legs (never more); no
      event is a usage error.
  L2  what the pull request leaves is exactly the macOS port, and the
      nightly runs it; the pull request keeps a macOS leg (the oracle's: its
      pty goldens caught wolf-lang#794 on macOS); every leg of every event
      is one of the legs before tl30. A pull request leaves `macos-fuzz`
      and a trunk push, the nightly and a dispatch run it: the one red only
      a macOS fuzz family caught (yew#100) came on a trunk push.
  L3  the hosts before tl30 (.github/workflows/ci.yml at trunk 9bd219c):
      the nightly's legs are exactly those, so no leg left the nightly.
  L4  the wiring of .github/workflows/ci.yml: `legs` is the first job and
      runs this file before ci/legs.py; `port` and `oracle` need it and
      take their hosts from it, read with a default, with no host list of
      their own; `unit` (the Linux unit lanes in eight shards, yw13s) and
      `fuzz` (the Linux fuzzers in seven families, yw13s) need it and run on
      ubuntu;
      `macos-unit` (yw14: the macOS unit lanes in eight shards, 180 minutes each) needs it and
      runs on macOS exactly where the port's macOS leg runs, the port job
      running neither lane; both unit jobs build C's fake clipboard tool first
      and prove no clipboard row SKIPped for it last (yew#42); and
      the port leaves those steps on Linux and macos-fuzz carries the seven
      oracle campaigns on macOS with their original commands; macos-perf
      carries the six oracle measurements, with no new host exclusion;
      `checked-cases` (yw06: the checked machine one case at a time) needs
      it too and runs on ubuntu only, the checked machine being the same
      on every host, in four shards of its run list (yw07b); `oracle-cmdcomp`
      (yw13: the linux oracle leg's perf_cmdcomp harness build and its 2x
      gate) needs it, runs on ubuntu, and only where the linux oracle leg
      runs; the outputs are declared; the trunk
      push, the pull request, the nightly and the dispatch are there; cancel-in-progress
      is for pull requests only and every other run has a group of its own
      run id; a red nightly, and only a red nightly, runs
      ci/nightly-red.sh with issues: write.
  L5  ci/nightly-red.sh against a stand-in `gh`: no open issue opens one,
      labelled, under the one title; an open one gets a comment and no new
      issue; a label that already exists is no failure.
  L8  a trunk push's macOS jobs already green at its commit, against a
      stand-in for the REST API and a scratch git repository: a completed,
      successful pull request or dispatch run of ci.yml at the commit, whose
      `legs` job tested the same tree and whose jobs of a macOS kind (the
      oracle's macOS leg, macos-fuzz, macos-perf) are each there once and
      green on macOS, lets the push leave that kind, and the plan names the
      run; anything less runs it: no such run, another event, another tree,
      no tree, a missing, duplicate, cancelled or non-macOS job, a jobs
      listing short of its count, an error, a timeout, a redirect, an odd
      answer, no token, a checkout that is not the pushed commit. Where
      macos-perf runs, the oracle's macOS leg runs (its artifact). No other
      event asks, and the token is never printed.

Exit 0 when every check passes, 1 otherwise.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "ci", "legs.py")
RED = os.path.join(ROOT, "ci", "nightly-red.sh")
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "ci.yml")
fails = 0


def say(ok, what):
    global fails
    print("legs-test: %s %s" % ("PASS" if ok else "FAIL", what))
    fails += not ok


def clean_env(**more):
    # The runner's own GITHUB_* and any token in the caller's environment stay
    # out: only the L8 rows give the planner a commit, an API and a token.
    drop = ("EVENT", "LEGS_TOKEN", "LEGS_API_TIMEOUT", "GH_TOKEN", "GITHUB_TOKEN", "GITHUB_SHA",
            "GITHUB_REPOSITORY", "GITHUB_API_URL", "GITHUB_SERVER_URL", "GITHUB_STEP_SUMMARY")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env.update(more)
    return env


def plan(event=None):
    args = [sys.executable, PLAN, "--json"] + (["--event", event] if event else [])
    r = subprocess.run(args, capture_output=True, text=True, env=clean_env())
    if r.returncode != 0:
        return {"ERROR": r.returncode}
    return json.loads(r.stdout)


# The hosts before tl30: .github/workflows/ci.yml at trunk 9bd219c.
U, M, A = "ubuntu-24.04", "macos-latest", "ubuntu-24.04-arm"
BEFORE = {
    "matrix_port": [{"os": U, "builds": True}, {"os": M, "builds": True}, {"os": A, "builds": False}],
    "matrix_oracle": [{"os": U, "ccs": "--cc clang --cc gcc", "port": True}, {"os": M, "ccs": "--cc clang", "port": True},
                      {"os": A, "ccs": "--cc clang --cc gcc", "port": False}],
}
# The macOS fuzz and perf jobs ran on every event before tl30. A pull
# request now leaves macos-fuzz; every other event runs both, unless a trunk
# push finds them green at its commit (L8).
BEFORE.update(macos_fuzz=True, macos_perf=True)
MERGE = {"matrix_port": [BEFORE["matrix_port"][0], BEFORE["matrix_port"][2]], "matrix_oracle": BEFORE["matrix_oracle"],
         "macos_fuzz": False, "macos_perf": True}
PUSH = dict(MERGE, macos_fuzz=True)
MOVED = {"matrix_port": [BEFORE["matrix_port"][1]], "matrix_oracle": []}


def matrices(m):
    return {k: v for k, v in m.items() if k.startswith("matrix_")}


# The macOS jobs a trunk push may leave, by the names GitHub gives them (L4
# reads them back from the workflow; L8 feeds them to the planner).
MAC_ORACLE = "oracle (macos-latest, --cc clang, true)"
MAC_FUZZ = ["fuzz (macOS arm64, against-c-%d)" % i for i in (1, 2, 3, 4)]
MAC_PERF = ["perf (macOS arm64, editor)", "perf (macOS arm64, components)"]
MAC_JOBS = [MAC_ORACLE] + MAC_FUZZ + MAC_PERF


def hosts(m):
    return {k: [l["os"] for l in v] for k, v in matrices(m).items()}


# --- L1 the legs by event ---------------------------------------------------------
for ev, want, fz in (("pull_request", MERGE, "no macos-fuzz"), ("push", PUSH, "macos-fuzz")):
    got = plan(ev)
    say(got == want, "L1 %s: oracle on every host, port on every host but macOS, macos-perf, %s (%s, macos_fuzz=%s)"
        % (ev, fz, json.dumps(hosts(got)) if "ERROR" not in got else got, got.get("macos_fuzz")))
for ev in ("schedule", "workflow_dispatch"):
    got = plan(ev)
    say(got == BEFORE, "L1 %s: both jobs on every host (%s)" % (ev, json.dumps(hosts(got)) if "ERROR" not in got else got))
got = plan("repository_dispatch")
say(got == MERGE, "L1 an event the planner does not know gets the pull request's legs, never more")
say(plan(None) == {"ERROR": 2}, "L1 no event is a usage error")

# --- L2 what the pull request leaves ---------------------------------------------
pr, night = plan("pull_request"), plan("schedule")
if "ERROR" not in pr and "ERROR" not in night:
    left = {k: [l for l in v if l not in pr.get(k, [])] for k, v in matrices(night).items()}
    say(left == MOVED, "L2 what a pull request leaves is exactly the macOS port: %s" % json.dumps({k: hosts({k: v})[k] for k, v in left.items() if v}))
    say(all(l in night[k] for k, v in matrices(pr).items() for l in v), "L2 every leg a pull request runs, the nightly runs too")
    say(any(l["os"] == M for l in pr["matrix_oracle"]), "L2 a pull request keeps a macOS leg: the oracle's (its pty goldens, wolf-lang#794)")
    say(all(m.get("macos_perf") is True for m in (pr, night)), "L2 a pull request and the nightly run macos-perf")
    fz = {e: plan(e).get("macos_fuzz") for e in ("pull_request", "push", "schedule", "workflow_dispatch")}
    say(fz == {"pull_request": False, "push": True, "schedule": True, "workflow_dispatch": True},
        "L2 a pull request leaves macos-fuzz; a trunk push, the nightly and a dispatch run it (yew#100 came on a trunk push): %s" % fz)
    every = [l for m in (plan(e) for e in ("pull_request", "push", "schedule", "workflow_dispatch")) for v in matrices(m).values() for l in v]
    say(all(any(l in v for v in BEFORE.values()) for l in every), "L2 every leg of every event is one of the legs before tl30")
else:
    say(False, "L2 the planner ran (%s, %s)" % (pr, night))

# --- L3 no leg left the nightly ----------------------------------------------------
say(night == BEFORE, "L3 the nightly runs exactly the legs every push ran before tl30 (9bd219c): %s" % json.dumps(hosts(BEFORE)))

# --- L4 the wiring -----------------------------------------------------------------
wf = open(WORKFLOW, encoding="utf-8").read()
JOBS = re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", wf[wf.index("\njobs:\n"):], re.M)
say(JOBS == ["legs", "port", "unit", "macos-unit", "fuzz", "checked-cases", "oracle", "oracle-cmdcomp", "macos-fuzz", "macos-perf", "nightly-red"], "L4 the jobs: %s" % " ".join(JOBS))
blocks = {}
for j in JOBS:
    m = re.search(r"^  %s:\s*\n(.*?)(?=^  [A-Za-z0-9_-]+:\s*$|\Z)" % re.escape(j), wf, re.M | re.S)
    blocks[j] = m.group(1) if m else ""
lg = blocks["legs"]
say("        run: python3 ci/legs-test.py\n" in lg and 'run: python3 ci/legs.py --github-output "$GITHUB_OUTPUT"\n' in lg
    and lg.index("ci/legs-test.py") < lg.index("ci/legs.py --github-output") and "EVENT: ${{ github.event_name }}" in lg
    and re.search(r"^    runs-on: ubuntu-24.04$", lg, re.M) is not None,
    "L4 the legs job runs this file, then plans from the event, on ubuntu")
say(all(("      %s: ${{ steps.legs.outputs.%s }}\n" % (k, k)) in lg for k in BEFORE), "L4 the legs job declares each matrix")
# The trunk push's lookup (L8): the legs job alone may read the actions API,
# names the tree it tests in a step's name (the jobs listing shows it), and
# hands the plan's step alone the workflow's own token.
say(re.search(r"^    permissions:\n      contents: read\n      actions: read\n(?!      \S)", lg, re.M) is not None,
    "L4 the legs job's token reads the repository and its runs, and nothing more")
TREE_NAME = "      - name: the tree under test is ${{ steps.tree.outputs.tree }}\n"
say("        id: tree\n" in lg and TREE_NAME in lg
    and lg.index("        id: tree\n") < lg.index(TREE_NAME) < lg.index("ci/legs.py --github-output")
    and "test \"$(git rev-parse 'HEAD^{tree}')\" = \"${{ steps.tree.outputs.tree }}\"" in lg,
    "L4 the legs job names the tree it tests in a step's name, checked, before the plan")
say(lg.count("github.token") == 1 and wf.count("LEGS_TOKEN") == 1
    and re.search(r"^        id: legs\n        env:\n(          .*\n)*          LEGS_TOKEN: \$\{\{ github\.token \}\}\n", lg, re.M) is not None,
    "L4 the plan's step, and no other, is given the workflow's token")
say("    if: ${{ needs.legs.outputs.macos_fuzz == 'true' }}\n" in blocks["macos-fuzz"]
    and "    if: ${{ needs.legs.outputs.macos_perf == 'true' }}\n" in blocks["macos-perf"],
    "L4 macos-fuzz and macos-perf run where the plan says")
# The names the lookup matches are the ones this workflow gives its macOS jobs.
rendered = []
for j in ("macos-fuzz", "macos-perf"):
    nm = re.search(r"^    name: (.*)$", blocks[j], re.M)
    fam = re.search(r"^        family: \[([^\]]+)\]$", blocks[j], re.M)
    rendered += [nm.group(1).replace("${{ matrix.family }}", f.strip()) for f in fam.group(1).split(",")] if nm and fam else []
mac_oracle = [l for l in plan("schedule").get("matrix_oracle", []) if l["os"] == M]
oracle_name = ["oracle (%s)" % ", ".join(str(v).lower() if isinstance(v, bool) else v for v in l.values()) for l in mac_oracle]
say(oracle_name == [MAC_ORACLE] and not re.search(r"^    name: ", blocks["oracle"], re.M) and rendered == MAC_FUZZ + MAC_PERF
    and all(re.search(r"^    runs-on: macos-latest$", blocks[j], re.M) for j in ("macos-fuzz", "macos-perf")),
    "L4 the macOS jobs a trunk push looks for are named as this workflow names them: %s" % (oracle_name + rendered))
for j in ("port", "oracle"):
    b = blocks[j]
    say("    needs: legs\n" in b and ("        include: ${{ fromJSON(needs.legs.outputs.matrix_%s || '[]') }}\n" % j) in b
        and "    runs-on: ${{ matrix.os }}\n" in b and not re.search(r"^          - os: ", b, re.M),
        "L4 %s needs the legs and takes its hosts from them, with a default, and no host list of its own" % j)
# yw13s: eight shards, as macOS has. The git layer and F mode made the
# editor's test builds heavier: run 42921677875 (yew#120 at 157841a) cut
# shard 4/6 at its 120-minute cap (wolf test 57 minutes, the native lane
# 63 when cut) and ran 5/6 in 114. At eight shards the slowest ran 111
# minutes (run 42996095311's shard 2/8; a hosted runner's speed varies by
# up to about 40 % from run to run), so the cap is 150 (L6). Since the
# syntax engine's tests the slowest is 124.1 (shard 8/8 in runs 45076451516
# and 45130155672), so the cap is 162.
UNIT_MEASURED_8 = 124.1
un = blocks["unit"]
ucap = re.search(r"^    timeout-minutes: (\d+)$", un, re.M)
say("    needs: legs\n" in un and re.search(r"^    runs-on: ubuntu-24.04$", un, re.M) is not None
    and "        shard: [1, 2, 3, 4, 5, 6, 7, 8]\n" in un and "run: tools/check-test --shard ${{ matrix.shard }}/8\n" in un
    and "run: tools/check-test --native --shard ${{ matrix.shard }}/8\n" in un
    and "    name: unit (linux x86-64, shard ${{ matrix.shard }}/8)\n" in un
    and ucap is not None and int(ucap.group(1)) >= 1.3 * UNIT_MEASURED_8,
    "L4 unit needs the legs and runs both unit lanes in eight shards on ubuntu, capped at least 30 % over the longest measured eight-way shard")
# yw14 (yew#49): the macOS unit lanes left the port job for macos-unit, eight
# round-robin shards on macOS (the partition the Linux unit job uses), run
# exactly where the port's macOS leg runs, each capped at 180 minutes: at
# least twice its measured time (run 41916949246's per-file times put the
# longest eight-way shard at about 78 minutes).
mu = blocks.get("macos-unit", "")
say("    needs: legs\n" in mu and re.search(r"^    runs-on: macos-latest$", mu, re.M) is not None
    and "    if: ${{ contains(needs.legs.outputs.matrix_port, 'macos-latest') }}\n" in mu
    and "        shard: [1, 2, 3, 4, 5, 6, 7, 8]\n" in mu and "run: tools/check-test --shard ${{ matrix.shard }}/8\n" in mu
    and "run: tools/check-test --native --shard ${{ matrix.shard }}/8\n" in mu
    and "    timeout-minutes: 180\n" in mu
    and not re.search(r"tools/check-test( --native)?$", blocks["port"], re.M),
    "L4 macos-unit needs the legs and runs both unit lanes in eight shards on macOS, capped at 180 minutes, where the port's macOS leg runs; the port job runs neither")
# yw14 (yew#42): every unit lane builds C's fake clipboard tool and then
# proves no clipboard row SKIPped for want of it.
say(all("run: tools/build-fakeclip --cc " in b and b.index("tools/build-fakeclip") < b.index("tools/check-test --shard")
        and "run: tools/check-test --fakeclip-ran\n" in b and b.index("--native --shard") < b.index("--fakeclip-ran")
        for b in (un, mu)),
    "L4 unit and macos-unit build the fake clipboard tool first and check no clipboard row SKIPped for it last")
fz = blocks["fuzz"]
say("    needs: legs\n" in fz and re.search(r"^    runs-on: ubuntu-24.04$", fz, re.M) is not None
    and "        family: [port, port-2, against-c-1, against-c-2, against-c-3, against-c-4, against-c-5]\n" in fz
    and "        if: matrix.family != 'port' && matrix.family != 'port-2'\n        run: tools/oracle --cc gcc --build-only\n" in fz,
    "L4 fuzz needs the legs and runs seven fuzzer families on ubuntu, C's drivers built for five")
# Every macOS campaign is still a Linux fuzz step. The oracle campaigns now
# live in macos-fuzz; the nightly port-only fuzzers and unit steps stay put.
moved = [m.group(1) for j in ("port", "oracle") for m in re.finditer(
    r"^      - name: (.*)\n        if: \$\{\{ (?:.*) && runner.os != 'Linux' \}\}$", blocks[j], re.M)]
moved += re.findall(r"^      - name: (fuzz_.*)$", blocks["macos-fuzz"], re.M)
fuzz_names = re.findall(r"^      - name: (.*)$", fz, re.M)
say(len(moved) == 13 and all(n in fuzz_names for n in moved),
    "L4 every step the port and oracle jobs leave on Linux is a fuzz step there (%d moved)" % len(moved))
cc = blocks["checked-cases"]
say("    needs: legs\n" in cc and re.search(r"^    runs-on: ubuntu-24.04$", cc, re.M) is not None
    and "        shard: [1, 2, 3, 4]\n" in cc and not re.search(r"^\s+(os|include):", cc, re.M)
    and "run: python3 -I tools/check-test-cases --shard ${{ matrix.shard }}/4\n" in cc,
    "L4 checked-cases needs the legs and runs tools/check-test-cases in four shards on ubuntu")
# yw11b (run 42346339007): the LSP unit files' cases spawn C's fake server
# and SKIP by name without it, which the one-case-at-a-time table reads as
# exit(0); the job builds it before the table runs.
fl = "run: tools/build-fakelsp --cc gcc\n"
say(fl in cc and cc.index(fl) < cc.index("run: python3 -I tools/check-test-cases --shard"),
    "L4 checked-cases builds C's fake language server before its cases run")
oc = blocks["oracle-cmdcomp"]
say("    needs: legs\n" in oc and re.search(r"^    runs-on: ubuntu-24.04$", oc, re.M) is not None
    and "    if: ${{ contains(needs.legs.outputs.matrix_oracle, 'ubuntu-24.04') }}\n" in oc
    and "          tools/run-perf-cmdcomp --build-only\n" in oc and "          PERF_PREBUILT=1 tools/run-perf-cmdcomp --trials 100\n" in oc,
    "L4 oracle-cmdcomp needs the legs and runs the linux oracle leg's perf_cmdcomp rows on ubuntu, where that leg runs")
say(re.search(r"^  push:\n    branches: \[trunk\]\n", wf, re.M) is not None and re.search(r"^  pull_request:\s*$", wf, re.M) is not None
    and re.search(r"^  schedule:\n(\s+#.*\n)*\s+- cron: ", wf, re.M) is not None and re.search(r"^  workflow_dispatch:\s*$", wf, re.M) is not None,
    "L4 the trunk push, the pull request, the nightly and the dispatch are there")
say("  cancel-in-progress: ${{ github.event_name == 'pull_request' }}\n" in wf, "L4 cancel-in-progress for pull requests only")
g = re.search(r"^concurrency:\n  group: (.*)$", wf, re.M)
g = g.group(1).rstrip() if g else ""
say(g.endswith("|| format('ci-{0}-{1}', github.event_name, github.run_id) }}") and "github.head_ref" in g,
    "L4 a pull request's runs share its branch's group; every other run has a group of its own run id")
n = blocks["nightly-red"]
say("    needs: [legs, port, unit, macos-unit, fuzz, checked-cases, oracle, oracle-cmdcomp, macos-fuzz, macos-perf]\n" in n and "    if: ${{ failure() && github.event_name == 'schedule' }}\n" in n
    and "      issues: write\n" in n and "        run: ci/nightly-red.sh\n" in n and "WORKFLOW: ${{ github.workflow }}" in n,
    "L4 a red nightly, and only a red nightly, runs ci/nightly-red.sh with issues: write")

# --- L5 the nightly's issue ------------------------------------------------------
FAKE_GH = r"""#!/usr/bin/env bash
printf '%s\n' "$*" >> "$FAKE_LOG"
case "$1 $2" in
  "label create") exit "${FAKE_LABEL_RC:-0}" ;;
  "issue list") printf '%s' "${FAKE_EXISTING:-}"; [ -n "${FAKE_EXISTING:-}" ] && echo; exit 0 ;;
esac
exit 0
"""


# L6 (yw13s): every job's cap is at least 30 % over the slowest time any
# of its legs, shards or families took in five runs: the nightly
# 42862922049 and the pull request runs 42921677875, 42922808966,
# 42996095311 and 42996771451. A job cut at its cap counts its cut, a lower
# bound. A family a split made counts the sum of its steps' slowest times
# there, and its setup. Minutes; a key is (job, the matrix value its cap
# depends on, or None).
SLOWEST = {
    ("legs", None): 1,
    ("port", "ubuntu-24.04"): 66, ("port", "ubuntu-24.04-arm"): 57,
    ("port", "macos-latest"): 219.8,  # the nightly 45048816590
    ("unit", None): 124.1,            # shard 8/8 in 45076451516 and 45130155672
    ("macos-unit", None): 102,
    ("fuzz", "port"): 147.0,          # 45130155672; cut on 42996771451 at 120, its one long step 115.2
    ("fuzz", "port-2"): 66,
    ("fuzz", "against-c-1"): 62.3,    # fuzz_cmdparse 61.3 and the C build
    ("fuzz", "against-c-2"): 67.7,    # fuzz_tabs 66.7 and the C build
    ("fuzz", "against-c-3"): 72,
    ("fuzz", "against-c-4"): 65,      # fuzz_panes
    ("fuzz", "against-c-5"): 56.1,    # fuzz_groups 55.1 (cut at 52.3 once) and the C build
    ("checked-cases", None): 60.2,    # shard 2/4 cut in 44996018243's first attempt and in 45129915974;
                                      # 43.1-58.1 in seven other runs; shard 4/4 57.3 in 44996018243
    # The oracle's two release builds of the whole program take 47-78 minutes each on Linux and
    # 52-68 on macOS since the syntax engine: 244.1 in 45075029709, 255.6 in 45129915974.
    ("oracle", "ubuntu-24.04"): 244.1, ("oracle", "ubuntu-24.04-arm"): 4, ("oracle", "macos-latest"): 255.6,
    ("oracle-cmdcomp", None): 63,
    ("macos-fuzz", "against-c-1"): 92.5,  # 45076451516
    ("macos-fuzz", "against-c-2"): 64.8,  # fuzz_tabs 57.1, fuzz_gitignore 6.9 and the C build
    ("macos-fuzz", "against-c-3"): 61,    # fuzz_panes
    ("macos-fuzz", "against-c-4"): 57.6,  # fuzz_groups 56.8 and the C build
    ("macos-perf", "editor"): 32, ("macos-perf", "components"): 7,
    ("nightly-red", None): 1,
}


def cap_for(block, value):
    m = re.search(r"^    timeout-minutes: (.+)$", block, re.M)
    if m is None:
        return None
    v = m.group(1).strip()
    if v.isdigit():
        return int(v)
    e = re.fullmatch(r"\$\{\{ matrix\.([a-z]+) == '([^']+)' && (\d+) \|\| (\d+) \}\}", v)
    if e is None:
        return None
    return int(e.group(3)) if value == e.group(2) else int(e.group(4))


short = []
for j in JOBS:
    b = blocks[j]
    fam = re.search(r"^        family: \[([^\]]+)\]$", b, re.M)
    values = [None]
    if fam:
        values = [x.strip() for x in fam.group(1).split(",")]
    elif j in ("port", "oracle"):
        values = ["ubuntu-24.04", "ubuntu-24.04-arm", "macos-latest"]
    for v in values:
        key = (j, v)
        if key not in SLOWEST:
            short.append("%s %s: no measured time" % key)
            continue
        c = cap_for(b, v)
        if c is None or c < 1.3 * SLOWEST[key]:
            short.append("%s %s: cap %s under 1.3 x %s" % (j, v, c, SLOWEST[key]))
say(not short, "L6 every job's cap is at least 30 % over its slowest measured time" + ("" if not short else ": " + "; ".join(short)))


def nightly_red(existing="", label_rc=0):
    d = tempfile.mkdtemp(prefix="legs-test-gh-")
    try:
        with open(os.path.join(d, "gh"), "w") as f:
            f.write(FAKE_GH)
        os.chmod(os.path.join(d, "gh"), 0o755)
        log = os.path.join(d, "log")
        env = dict(os.environ, PATH=d + os.pathsep + os.environ.get("PATH", ""), FAKE_LOG=log, FAKE_EXISTING=existing,
                   FAKE_LABEL_RC=str(label_rc), REPO="wolffe-lang/yew", WORKFLOW="ci",
                   RUN_URL="https://github.com/wolffe-lang/yew/actions/runs/1")
        r = subprocess.run(["bash", RED], capture_output=True, text=True, env=env)
        calls = open(log).read().splitlines() if os.path.exists(log) else []
        return r.returncode, calls
    finally:
        shutil.rmtree(d, ignore_errors=True)


TITLE = "nightly red: ci on trunk"
rc, calls = nightly_red()
creates = [c for c in calls if c.startswith("issue create")]
say(rc == 0 and len(creates) == 1 and "--title %s" % TITLE in creates[0] and "--label nightly-red" in creates[0]
    and not [c for c in calls if c.startswith("issue comment")],
    "L5 no open issue: one is opened, labelled nightly-red, titled '%s'" % TITLE)
lists = [c for c in calls if c.startswith("issue list")]
say(len(lists) == 1 and "--state open" in lists[0] and "--label nightly-red" in lists[0] and TITLE in lists[0],
    "L5 the dedupe asks for an open nightly-red issue under the title")
rc, calls = nightly_red(existing="41")
say(rc == 0 and [c for c in calls if c.startswith("issue comment 41 ")] and not [c for c in calls if c.startswith("issue create")],
    "L5 an open issue: a comment on it, no new issue")
rc, calls = nightly_red(label_rc=1)
say(rc == 0 and [c for c in calls if c.startswith("issue create")], "L5 a label that already exists is no failure")
r = subprocess.run(["bash", RED], capture_output=True, text=True, env=clean_env(PATH=os.environ.get("PATH", "")))
say(r.returncode != 0, "L5 the script refuses to run without REPO, WORKFLOW and RUN_URL")
say(re.search(r"^name: ci$", wf, re.M) is not None, "L5 the workflow's name is ci, the title's")

# L7: the hosted runner's image moves under "latest" (ubuntu-26.04, glibc 2.43, broke
# the oracle's docker trials, which run a host-built binary inside ubuntu:24.04).
# No workflow and no planner leg may say ubuntu-latest.
import glob
stale = []
for path in sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*")) + [os.path.join(ROOT, "ci", "legs.py")]):
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if "ubuntu-latest" in line:
            stale.append("%s:%d" % (os.path.relpath(path, ROOT), n))
say(not stale, "L7 no workflow or planner leg says ubuntu-latest, the runner image is pinned" + ("" if not stale else ": " + ", ".join(stale)))

# --- L8 a trunk push's macOS jobs already green at its commit ---------------------
# Merges are fast-forwards, so a trunk push runs the commit its pull request's
# run has just passed. The plan asks the REST API for this workflow's runs at
# the pushed commit and leaves a macOS kind only on positive evidence. These
# rows run the planner as the workflow does (EVENT, GITHUB_SHA,
# GITHUB_REPOSITORY, GITHUB_API_URL, LEGS_TOKEN) in a scratch git repository,
# against a stand-in API on 127.0.0.1.
import http.server
import threading
import time
import urllib.parse

REPO = "wolffe-lang/yew"
TOKEN = "legs-test-stand-in-token-7c1e"


class QuietServer(http.server.ThreadingHTTPServer):
    # A client that timed out leaves a handler writing to a closed socket.
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass


class FakeAPI:
    """The REST API's two answers the plan reads: the runs of ci.yml at a
    commit, and a run's jobs (paged). `fault` is (path prefix, kind)."""

    def __init__(self, runs=(), jobs=None, fault=None, page_cap=100, ignore_filter=False, totals=None):
        self.runs, self.jobs = list(runs), dict(jobs or {})
        self.fault, self.page_cap, self.ignore_filter = fault, page_cap, ignore_filter
        self.totals = dict(totals or {})
        self.requests = []
        self.redirect_to = None
        api = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                api.requests.append((self.path, self.headers.get("Authorization")))
                status, body, extra = api.answer(self.path)
                data = body if isinstance(body, bytes) else json.dumps(body).encode()
                self.send_response(status)
                for k, v in extra.items():
                    self.send_header(k, v)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = QuietServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def answer(self, path):
        u = urllib.parse.urlsplit(path)
        q = dict(urllib.parse.parse_qsl(u.query))
        if self.fault and u.path.startswith(self.fault[0]):
            kind = self.fault[1]
            if kind in (500, 403, 404):
                return kind, {"message": "stand-in error %d" % kind}, {}
            if kind == "html":
                return 200, b"<html>not json</html>", {}
            if kind == "keys":
                return 200, {"message": "an answer without the expected keys"}, {}
            if kind == "slow":
                time.sleep(4)
            if kind == "redirect":
                return 302, {}, {"Location": self.redirect_to + path}
        if u.path == "/repos/%s/actions/workflows/ci.yml/runs" % REPO:
            rs = [r for r in self.runs if self.ignore_filter or r["head_sha"] == q.get("head_sha")]
            return 200, {"total_count": len(rs), "workflow_runs": rs}, {}
        m = re.fullmatch(r"/repos/%s/actions/runs/(\d+)/jobs" % re.escape(REPO), u.path)
        if m:
            rid = int(m.group(1))
            js = self.jobs.get(rid, [])
            per = min(int(q.get("per_page", 30)), self.page_cap)
            page = int(q.get("page", 1))
            return 200, {"total_count": self.totals.get(rid, len(js)), "jobs": js[(page - 1) * per:page * per]}, {}
        return 404, {"message": "Not Found"}, {}


def scratch_repo():
    d = tempfile.mkdtemp(prefix="legs-test-repo-")
    g = ["git", "-C", d, "-c", "user.name=legs-test", "-c", "user.email=legs-test@invalid", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "-c", "init.defaultBranch=trunk", "init", "-q", d], check=True)
    with open(os.path.join(d, "f"), "w") as f:
        f.write("the pushed commit\n")
    subprocess.run(g + ["add", "f"], check=True)
    subprocess.run(g + ["commit", "-q", "-m", "the pushed commit"], check=True)
    rev = lambda r: subprocess.run(["git", "-C", d, "rev-parse", r], capture_output=True, text=True, check=True).stdout.strip()
    return d, rev("HEAD"), rev("HEAD^{tree}")


GITDIR, SHA, TREE = scratch_repo()
OTHER_TREE = "0" * 40


def wrun(rid, event="pull_request", conclusion="success", status="completed", sha=None, path=".github/workflows/ci.yml"):
    return {"id": rid, "event": event, "status": status, "conclusion": conclusion, "head_sha": sha or SHA, "path": path,
            "run_attempt": 1, "html_url": "https://github.com/%s/actions/runs/%d" % (REPO, rid)}


def wjob(name, conclusion="success", labels=None, steps=None):
    if labels is None:
        labels = ["macos-latest"] if name in MAC_JOBS else ["ubuntu-24.04"]
    return {"name": name, "status": "completed", "conclusion": conclusion, "labels": labels, "steps": steps or []}


def legs_job(tree=None, step=True):
    steps = [{"name": "Set up job", "conclusion": "success"}]
    if step:
        steps.append({"name": "the tree under test is %s" % (tree or TREE), "conclusion": "success"})
    return wjob("legs", steps=steps)


LINUX_JOBS = ["port (ubuntu-24.04, true)", "oracle (ubuntu-24.04, --cc clang --cc gcc, true)", "fuzz (linux x86-64, port)"]


def green(tree=None, step=True, drop=(), swap=None, extra=()):
    """A run's jobs: the legs job, three Linux jobs, every macOS job green,
    less `drop`, with `swap` {name: job} replacing some, plus `extra`."""
    swap = swap or {}
    js = [legs_job(tree, step)] + [wjob(n) for n in LINUX_JOBS]
    js += [swap.get(n, wjob(n)) for n in MAC_JOBS if n not in drop]
    return js + list(extra)


FULL = PUSH
NO_MAC = {"matrix_port": MERGE["matrix_port"], "matrix_oracle": [l for l in MERGE["matrix_oracle"] if l["os"] != M],
          "macos_fuzz": False, "macos_perf": False}
SEEN = []   # every plan's printed output, for the token check


def push_plan(api, event="push", sha=None, token=TOKEN, timeout=None, summary=None, cwd=None):
    env = clean_env(EVENT=event, GITHUB_SHA=sha or SHA, GITHUB_REPOSITORY=REPO, GITHUB_API_URL=api.url,
                    GITHUB_SERVER_URL="https://github.com")
    if token:
        env["LEGS_TOKEN"] = token
    if timeout:
        env["LEGS_API_TIMEOUT"] = str(timeout)
    if summary:
        env["GITHUB_STEP_SUMMARY"] = summary
    r = subprocess.run([sys.executable, PLAN, "--json"], capture_output=True, text=True, env=env, cwd=cwd or GITDIR, timeout=120)
    SEEN.append(r.stdout + r.stderr)
    got = {"ERROR": r.returncode}
    if r.returncode == 0:
        try:
            got = json.loads(r.stdout)
        except ValueError:
            got = {"ERROR": "not JSON: %r" % r.stdout[:80]}
    return got, r.stderr


def mac_kinds(p):
    if "ERROR" in p:
        return p
    return [k for k, on in (("oracle", any(l["os"] == M for l in p.get("matrix_oracle", []))),
                            ("fuzz", p.get("macos_fuzz")), ("perf", p.get("macos_perf"))) if on]


PLANS = []
VERDICT = re.compile(r"^legs: (skip|keep) (oracle-macos|macos-fuzz|macos-perf): (.*)$", re.M)


def row(what, api, want, **kw):
    got, err = push_plan(api, **kw)
    PLANS.append(got)
    verdicts = VERDICT.findall(err)
    kinds = sorted(k for _, k, _ in verdicts)
    say(got == want and kinds == ["macos-fuzz", "macos-perf", "oracle-macos"],
        "L8 %s: macOS %s, a verdict for each kind %s" % (what, mac_kinds(got), kinds))
    return got, err, verdicts


def skipped_by(verdicts):
    out = {}
    for v, k, why in verdicts:
        if v == "skip":
            m = re.match(r"green in (pull_request|workflow_dispatch) run (\d+) ", why)
            out[k] = (m.group(1), int(m.group(2))) if m else None
    return out


# A green pull request run at the commit and tree: the push runs no macOS job,
# and the plan names the run for each kind, in its log and its step summary.
summary = os.path.join(tempfile.mkdtemp(prefix="legs-test-summary-"), "summary.md")
api = FakeAPI([wrun(7001)], {7001: green()})
got, err, v = row("a green pull request run at the commit and tree leaves every macOS kind", api, NO_MAC, summary=summary)
say(skipped_by(v) == {k: ("pull_request", 7001) for k in ("oracle-macos", "macos-fuzz", "macos-perf")}
    and all(SHA in why and TREE in why for _, _, why in v),
    "L8 each skip names the run it relied on (pull_request run 7001), the commit and the tree")
text = open(summary).read() if os.path.exists(summary) else ""
say(text.count("7001") >= 3 and "macos-fuzz" in text, "L8 the step summary names the run for each skipped kind")
jobs_q = [urllib.parse.parse_qs(urllib.parse.urlsplit(p).query) for p, _ in api.requests if "/jobs" in p]
say(jobs_q and all(q.get("filter") == ["latest"] for q in jobs_q), "L8 a run's jobs are read at its latest attempt (filter=latest)")
say(api.requests and all(a == "Bearer " + TOKEN for _, a in api.requests), "L8 every request carries the workflow's token, to the API it was given")
api.close()

api = FakeAPI([wrun(7002, event="workflow_dispatch")], {7002: green()})
got, err, v = row("a green dispatch run at the commit counts", api, NO_MAC)
say(skipped_by(v) == {k: ("workflow_dispatch", 7002) for k in ("oracle-macos", "macos-fuzz", "macos-perf")}, "L8 the dispatch run is named")
api.close()

for ev in ("schedule", "push"):
    api = FakeAPI([wrun(7003, event=ev)], {7003: green()})
    row("a green %s run at the commit does not count" % ev, api, FULL)
    api.close()

api = FakeAPI([wrun(7004, conclusion="failure"), wrun(7005, conclusion="cancelled"), wrun(7006, status="in_progress", conclusion=None)],
              {7004: green(), 7005: green(), 7006: green()})
row("a failed, a cancelled and a running pull request run do not count", api, FULL)
api.close()

api = FakeAPI([wrun(7007)], {7007: green(tree=OTHER_TREE)})
row("a run that tested another tree (its base was not in the commit) does not count", api, FULL)
api.close()

api = FakeAPI([wrun(7008)], {7008: green(step=False)})
row("a run whose legs job names no tree does not count", api, FULL)
api.close()

api = FakeAPI([wrun(7009)], {7009: [legs_job()] + [wjob(n) for n in LINUX_JOBS]})
row("a green run with no macOS job at all: every macOS kind runs", api, FULL)
api.close()

api = FakeAPI([wrun(7010)], {7010: green(drop=MAC_FUZZ)})
want = dict(NO_MAC, macos_fuzz=True)
got, err, v = row("the macOS fuzz jobs never ran at the commit: they run, the green kinds do not", api, want)
say(skipped_by(v) == {"oracle-macos": ("pull_request", 7010), "macos-perf": ("pull_request", 7010)}, "L8 only the green kinds are skipped")
api.close()

api = FakeAPI([wrun(7011)], {7011: green(swap={MAC_FUZZ[2]: wjob(MAC_FUZZ[2], conclusion="cancelled")})})
row("one fuzz family cancelled in the latest attempt: macos-fuzz runs", api, dict(NO_MAC, macos_fuzz=True))
api.close()

api = FakeAPI([wrun(7012)], {7012: green(drop=[MAC_FUZZ[3]])})
row("one fuzz family missing: macos-fuzz runs", api, dict(NO_MAC, macos_fuzz=True))
api.close()

api = FakeAPI([wrun(7013)], {7013: green(extra=[wjob(MAC_FUZZ[0], conclusion="failure")])})
row("a fuzz family listed twice, once red: macos-fuzz runs", api, dict(NO_MAC, macos_fuzz=True))
api.close()

api = FakeAPI([wrun(7014)], {7014: green(swap={MAC_FUZZ[1]: wjob(MAC_FUZZ[1], labels=["ubuntu-24.04"])})})
row("a fuzz family's job that ran on Linux: macos-fuzz runs", api, dict(NO_MAC, macos_fuzz=True))
api.close()

api = FakeAPI([wrun(7015)], {7015: green(drop=MAC_PERF)})
got, err, v = row("the perf jobs absent: perf runs, and so does the oracle's macOS leg, whose artifact it reads", api,
                  dict(FULL, macos_fuzz=False))
say(skipped_by(v) == {"macos-fuzz": ("pull_request", 7015)}, "L8 only macos-fuzz is skipped when perf must run")
api.close()

api = FakeAPI([wrun(7016)], {7016: green(drop=[MAC_ORACLE])})
row("the oracle's macOS leg absent: it runs, the green kinds do not", api, dict(FULL, macos_fuzz=False, macos_perf=False))
api.close()

api = FakeAPI([wrun(7017), wrun(7018, conclusion="failure")], {7017: green(drop=MAC_FUZZ), 7018: green()})
got, err, v = row("two runs at the commit: only the green one counts", api, dict(NO_MAC, macos_fuzz=True))
say(skipped_by(v) == {"oracle-macos": ("pull_request", 7017), "macos-perf": ("pull_request", 7017)}, "L8 the red run is not relied on")
api.close()

api = FakeAPI([wrun(7019), wrun(7020, event="workflow_dispatch")], {7019: green(drop=MAC_FUZZ), 7020: green(drop=MAC_PERF + [MAC_ORACLE])})
got, err, v = row("two green runs, each with some kinds: each kind relies on a run that has it", api, NO_MAC)
say(skipped_by(v) == {"oracle-macos": ("pull_request", 7019), "macos-perf": ("pull_request", 7019),
                      "macos-fuzz": ("workflow_dispatch", 7020)}, "L8 each kind names the run it relied on")
api.close()

api = FakeAPI([wrun(7021)], {7021: green()}, page_cap=4)
row("a jobs listing over several pages is read to its count", api, NO_MAC)
say(len([p for p, _ in api.requests if "/jobs" in p]) >= 3, "L8 the planner read every page")
api.close()

api = FakeAPI([wrun(7022)], {7022: green()}, totals={7022: 99})
row("a jobs listing short of its total_count is no evidence", api, FULL)
api.close()

api = FakeAPI([wrun(7023, sha="1" * 40), wrun(7024, path=".github/workflows/float-hosts.yml")], {7023: green(), 7024: green()},
              ignore_filter=True)
row("runs of another commit or another workflow, listed anyway, do not count", api, FULL)
api.close()

for where, kind in (("/repos/%s/actions/workflows" % REPO, 500), ("/repos/%s/actions/runs" % REPO, 403),
                    ("/repos/%s/actions/workflows" % REPO, "html"), ("/repos/%s/actions/runs" % REPO, "keys"),
                    ("/repos/%s/actions/workflows" % REPO, 404)):
    api = FakeAPI([wrun(7030)], {7030: green()}, fault=(where, kind))
    row("the lookup answered %s at %s: every macOS kind runs" % (kind, where.rsplit("/", 1)[-1]), api, FULL)
    api.close()

api = FakeAPI([wrun(7031)], {7031: green()}, fault=("/repos/%s/actions/workflows" % REPO, "slow"))
t0 = time.time()
row("the lookup timed out: every macOS kind runs", api, FULL, timeout=1)
say(time.time() - t0 < 30, "L8 the timeout holds (%.1f s)" % (time.time() - t0))
api.close()

elsewhere = FakeAPI([wrun(7032)], {7032: green()})
api = FakeAPI([wrun(7032)], {7032: green()}, fault=("/repos/%s/actions/workflows" % REPO, "redirect"))
api.redirect_to = elsewhere.url
row("the API redirected: not followed, every macOS kind runs", api, FULL)
say(elsewhere.requests == [], "L8 a redirect takes the token nowhere (the other host saw %d requests)" % len(elsewhere.requests))
api.close()
elsewhere.close()

api = FakeAPI([wrun(7033)], {7033: green()})
row("no token: every macOS kind runs", api, FULL, token=None)
say(api.requests == [], "L8 without a token nothing is asked")
api.close()

api = FakeAPI([wrun(7034, sha="2" * 40)], {7034: green()})
row("the checkout is not the pushed commit: every macOS kind runs", api, FULL, sha="2" * 40)
say(api.requests == [], "L8 a checkout that is not the pushed commit asks nothing")
api.close()

for ev, want in (("pull_request", MERGE), ("schedule", BEFORE), ("workflow_dispatch", BEFORE)):
    api = FakeAPI([wrun(7040)], {7040: green()})
    got, err = push_plan(api, event=ev)
    say(got == want and api.requests == [] and not VERDICT.search(err),
        "L8 a %s run asks nothing and keeps its legs (%s)" % (ev, mac_kinds(got)))
    api.close()

say(all("ERROR" not in p for p in PLANS), "L8 every trunk push plan exits 0")
say(all("macos-latest" in [l["os"] for l in p.get("matrix_oracle", [])] for p in PLANS if p.get("macos_perf")),
    "L8 wherever macos-perf runs, the oracle's macOS leg runs")
say(SEEN and not any(TOKEN in s for s in SEEN), "L8 the token is never printed")
shutil.rmtree(GITDIR, ignore_errors=True)

print("legs-test: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
sys.exit(1 if fails else 0)
