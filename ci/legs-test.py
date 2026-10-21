#!/usr/bin/env python3
"""ci/legs-test.py — ci/legs.py's own proof (tl30). python3 and bash only.

    ci/legs-test.py

  L1  the legs by event: a pull request and a trunk push run `oracle` on
      every host and `port` on every host but macOS; the nightly and a
      dispatch run both on every host; an event the planner does not know
      gets the pull request's legs (never more); no event is a usage error.
  L2  what the pull request leaves is exactly the macOS port, and the
      nightly runs it; the pull request keeps a macOS leg (the oracle's: its
      pty goldens caught wolf-lang#794 on macOS); every leg of every event
      is one of the legs before tl30.
  L3  the hosts before tl30 (.github/workflows/ci.yml at trunk 9bd219c):
      the nightly's legs are exactly those, so no leg left the nightly.
  L4  the wiring of .github/workflows/ci.yml: `legs` is the first job and
      runs this file before ci/legs.py; `port` and `oracle` need it and
      take their hosts from it, read with a default, with no host list of
      their own; the outputs are declared; the trunk push, the pull
      request, the nightly and the dispatch are there; cancel-in-progress
      is for pull requests only and every other run has a group of its own
      run id; a red nightly, and only a red nightly, runs
      ci/nightly-red.sh with issues: write.
  L5  ci/nightly-red.sh against a stand-in `gh`: no open issue opens one,
      labelled, under the one title; an open one gets a comment and no new
      issue; a label that already exists is no failure.

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
    env = {k: v for k, v in os.environ.items() if k not in ("EVENT",)}
    env.update(more)
    return env


def plan(event=None):
    args = [sys.executable, PLAN, "--json"] + (["--event", event] if event else [])
    r = subprocess.run(args, capture_output=True, text=True, env=clean_env())
    if r.returncode != 0:
        return {"ERROR": r.returncode}
    return json.loads(r.stdout)


# The hosts before tl30: .github/workflows/ci.yml at trunk 9bd219c.
U, M, A = "ubuntu-latest", "macos-latest", "ubuntu-24.04-arm"
BEFORE = {
    "matrix_port": [{"os": U, "builds": True}, {"os": M, "builds": True}, {"os": A, "builds": False}],
    "matrix_oracle": [{"os": U, "ccs": "--cc clang --cc gcc", "port": True}, {"os": M, "ccs": "--cc clang", "port": True},
                      {"os": A, "ccs": "--cc clang --cc gcc", "port": False}],
}
MERGE = {"matrix_port": [BEFORE["matrix_port"][0], BEFORE["matrix_port"][2]], "matrix_oracle": BEFORE["matrix_oracle"]}
MOVED = {"matrix_port": [BEFORE["matrix_port"][1]], "matrix_oracle": []}


def hosts(m):
    return {k: [l["os"] for l in v] for k, v in m.items()}


# --- L1 the legs by event ---------------------------------------------------------
for ev in ("pull_request", "push"):
    got = plan(ev)
    say(got == MERGE, "L1 %s: oracle on every host, port on every host but macOS (%s)" % (ev, json.dumps(hosts(got)) if "ERROR" not in got else got))
for ev in ("schedule", "workflow_dispatch"):
    got = plan(ev)
    say(got == BEFORE, "L1 %s: both jobs on every host (%s)" % (ev, json.dumps(hosts(got)) if "ERROR" not in got else got))
got = plan("repository_dispatch")
say(got == MERGE, "L1 an event the planner does not know gets the pull request's legs, never more")
say(plan(None) == {"ERROR": 2}, "L1 no event is a usage error")

# --- L2 what the pull request leaves ---------------------------------------------
pr, night = plan("pull_request"), plan("schedule")
if "ERROR" not in pr and "ERROR" not in night:
    left = {k: [l for l in v if l not in pr.get(k, [])] for k, v in night.items()}
    say(left == MOVED, "L2 what a pull request leaves is exactly the macOS port: %s" % json.dumps({k: hosts({k: v})[k] for k, v in left.items() if v}))
    say(all(l in night[k] for k, v in pr.items() for l in v), "L2 every leg a pull request runs, the nightly runs too")
    say(any(l["os"] == M for l in pr["matrix_oracle"]), "L2 a pull request keeps a macOS leg: the oracle's (its pty goldens, wolf-lang#794)")
    every = [l for m in (plan(e) for e in ("pull_request", "push", "schedule", "workflow_dispatch")) for v in m.values() for l in v]
    say(all(any(l in v for v in BEFORE.values()) for l in every), "L2 every leg of every event is one of the legs before tl30")
else:
    say(False, "L2 the planner ran (%s, %s)" % (pr, night))

# --- L3 no leg left the nightly ----------------------------------------------------
say(night == BEFORE, "L3 the nightly runs exactly the legs every push ran before tl30 (9bd219c): %s" % json.dumps(hosts(BEFORE)))

# --- L4 the wiring -----------------------------------------------------------------
wf = open(WORKFLOW, encoding="utf-8").read()
JOBS = re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", wf[wf.index("\njobs:\n"):], re.M)
say(JOBS == ["legs", "port", "oracle", "nightly-red"], "L4 the jobs: %s" % " ".join(JOBS))
blocks = {}
for j in JOBS:
    m = re.search(r"^  %s:\s*\n(.*?)(?=^  [A-Za-z0-9_-]+:\s*$|\Z)" % re.escape(j), wf, re.M | re.S)
    blocks[j] = m.group(1) if m else ""
lg = blocks["legs"]
say("        run: python3 ci/legs-test.py\n" in lg and 'run: python3 ci/legs.py --github-output "$GITHUB_OUTPUT"\n' in lg
    and lg.index("ci/legs-test.py") < lg.index("ci/legs.py --github-output") and "EVENT: ${{ github.event_name }}" in lg
    and re.search(r"^    runs-on: ubuntu-latest$", lg, re.M) is not None,
    "L4 the legs job runs this file, then plans from the event, on ubuntu")
say(all(("      %s: ${{ steps.legs.outputs.%s }}\n" % (k, k)) in lg for k in BEFORE), "L4 the legs job declares each matrix")
for j in ("port", "oracle"):
    b = blocks[j]
    say("    needs: legs\n" in b and ("        include: ${{ fromJSON(needs.legs.outputs.matrix_%s || '[]') }}\n" % j) in b
        and "    runs-on: ${{ matrix.os }}\n" in b and not re.search(r"^          - os: ", b, re.M),
        "L4 %s needs the legs and takes its hosts from them, with a default, and no host list of its own" % j)
say(re.search(r"^  push:\n    branches: \[trunk\]\n", wf, re.M) is not None and re.search(r"^  pull_request:\s*$", wf, re.M) is not None
    and re.search(r"^  schedule:\n(\s+#.*\n)*\s+- cron: ", wf, re.M) is not None and re.search(r"^  workflow_dispatch:\s*$", wf, re.M) is not None,
    "L4 the trunk push, the pull request, the nightly and the dispatch are there")
say("  cancel-in-progress: ${{ github.event_name == 'pull_request' }}\n" in wf, "L4 cancel-in-progress for pull requests only")
g = re.search(r"^concurrency:\n  group: (.*)$", wf, re.M)
g = g.group(1).rstrip() if g else ""
say(g.endswith("|| format('ci-{0}-{1}', github.event_name, github.run_id) }}") and "github.head_ref" in g,
    "L4 a pull request's runs share its branch's group; every other run has a group of its own run id")
n = blocks["nightly-red"]
say("    needs: [legs, port, oracle]\n" in n and "    if: ${{ failure() && github.event_name == 'schedule' }}\n" in n
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

print("legs-test: %s" % ("PASS" if fails == 0 else "FAIL (%d)" % fails))
sys.exit(1 if fails else 0)
