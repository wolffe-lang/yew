#!/usr/bin/env python3
"""ci/legs.py — the hosts each job of .github/workflows/ci.yml runs for an
event (tl30, the macOS cap; tl28's plan job, cut to yew's two jobs).

    ci/legs.py [--event E] [--github-output FILE] [--json]

`--event` also reads EVENT from the environment, which is how the
workflow's `legs` job passes it in. Prints `matrix_port=` and
`matrix_oracle=` (each a JSON list for `include:`), `macos_fuzz=` and
`macos_perf=` (true or false: whether those jobs run), to --github-output
(appended) and to standard output; with --json, one JSON object. The
reason goes to standard error. Exit 0; 2 on a usage error.

THE LEGS. A leg is one entry of a job's matrix: one host.

  every leg     the nightly `schedule` and a `workflow_dispatch`: `port`
                and `oracle` on linux x86-64, macOS arm64 and linux
                aarch64 (where `port` asserts that no tier builds yet,
                wolf-lang#614, and `oracle` runs C yew alone).
  the merge's   a pull request and a push to trunk (any other event): the
                same but the macOS `port`. The org has five macOS slots for
                every repository, busy 55% of the time after the Team plan
                (tl29). In yew's runs with a macOS job the macOS `oracle`
                caught a red no linux leg did (the terminal not restored
                after a fault on macOS: wolf-lang#794, yw01 and yw03) and
                stays; the macOS `port` (both tiers, `wolf test` checked and
                native, the fuzzers) caught nothing a linux leg did not and
                held a slot for 12 to 15 minutes on every push, so it runs
                every night (ci/tl30.md). The `oracle` job builds the port on
                macOS too (release tier), so a pull request still proves it
                builds there. Since yw14 the macOS unit lanes are the
                `macos-unit` job's eight shards, which run wherever this
                plan gives `port` its macOS leg.

THE TRUNK PUSH'S macOS JOBS. Merges are fast-forwards, so a push to trunk
runs the commit its pull request's run has just passed. On a `push` the
plan asks the REST API, with the workflow's own read-only token
(LEGS_TOKEN; GITHUB_API_URL, GITHUB_REPOSITORY and GITHUB_SHA are the
runner's), for this workflow's runs at the pushed commit, and leaves a
macOS kind — the oracle's macOS leg, `macos-fuzz`, `macos-perf` — only
when a completed, successful pull_request or workflow_dispatch run there

  - tested the same tree: its `legs` job has the step `the tree under test
    is <tree>`. A pull request's run tests its merge with the base, which is
    this commit's tree only when the base was already in the commit;
  - has, at its latest attempt, each job of the kind once, green, on macOS.

Anything else runs the kind: no such run, a lookup that fails, times out,
redirects or answers oddly, a jobs listing short of its count, no token, a
checkout that is not the pushed commit. `macos-perf` reads the oracle's
macOS artifact, so where it runs the oracle's macOS leg runs too. Each
kind's verdict, and the run a skip relied on, goes to standard error and
to the step summary.

ci/legs-test.py is this file's proof and runs first in the same job.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

PORT = [
    {"os": "ubuntu-24.04", "builds": True},
    {"os": "macos-latest", "builds": True},
    {"os": "ubuntu-24.04-arm", "builds": False},
]
ORACLE = [
    {"os": "ubuntu-24.04", "ccs": "--cc clang --cc gcc", "port": True},
    {"os": "macos-latest", "ccs": "--cc clang", "port": True},
    {"os": "ubuntu-24.04-arm", "ccs": "--cc clang --cc gcc", "port": False},
]
MATRIX = {"port": PORT, "oracle": ORACLE}
EVERY_LEG_EVENTS = ("schedule", "workflow_dispatch")
MAC = "macos-latest"

# The trunk push's lookup.
WORKFLOW = ".github/workflows/ci.yml"
EVIDENCE_EVENTS = ("pull_request", "workflow_dispatch")
TREE_STEP = re.compile(r"^the tree under test is ([0-9a-f]{40}|[0-9a-f]{64})$")
MAX_RUNS = 10
MAX_PAGES = 5


def matrix_name(job, leg):
    """The name GitHub gives a job of a matrix with no `name:` of its own."""
    return "%s (%s)" % (job, ", ".join(str(v).lower() if isinstance(v, bool) else str(v) for v in leg.values()))


# Each macOS kind a trunk push may leave, by its jobs' names.
KINDS = {
    "oracle-macos": [matrix_name("oracle", l) for l in ORACLE if l["os"] == MAC],
    "macos-fuzz": ["fuzz (macOS arm64, %s)" % f for f in ("against-c-1", "against-c-2", "against-c-3", "against-c-4")],
    "macos-perf": ["perf (macOS arm64, %s)" % f for f in ("editor", "components")],
}


def merge_leg(job, leg):
    """Whether a pull request's run (and a trunk push's) runs this leg:
    every leg but the macOS port, the nightly's."""
    return not (job == "port" and leg["os"] == "macos-latest")


def legs(event, leave=()):
    """-> ({output name: value}, the reason). `leave`: the macOS kinds a
    trunk push leaves (macos_leave)."""
    if event in EVERY_LEG_EVENTS:
        out = {"matrix_" + j: list(v) for j, v in MATRIX.items()}
        out.update(macos_fuzz=True, macos_perf=True)
        return out, "%s: every leg" % event
    out = {"matrix_" + j: [l for l in v if merge_leg(j, l)] for j, v in MATRIX.items()}
    if "oracle-macos" in leave:
        out["matrix_oracle"] = [l for l in out["matrix_oracle"] if l["os"] != MAC]
    out.update(macos_fuzz="macos-fuzz" not in leave, macos_perf="macos-perf" not in leave)
    why = "%s: the merge's legs (the macOS port is the nightly's)" % (event or "no event")
    if leave:
        why += ", less the macOS kinds green at this commit: " + ", ".join(sorted(leave))
    return out, why


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """The plan follows no redirect: the token goes to the API alone."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "a redirect, not followed", headers, fp)


class Api:
    def __init__(self, base, repo, token, timeout):
        self.base, self.repo, self.token, self.timeout = base.rstrip("/"), repo, token, timeout
        self.opener = urllib.request.build_opener(NoRedirect)

    def get(self, path, **query):
        url = "%s/repos/%s/%s?%s" % (self.base, self.repo, path, urllib.parse.urlencode(query))
        req = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + self.token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "yew-ci-legs",
        })
        with self.opener.open(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8"))


def run_jobs(api, run_id):
    """A run's jobs at its latest attempt, every page; None when the listing
    falls short of its own count."""
    jobs = []
    for page in range(1, MAX_PAGES + 1):
        d = api.get("actions/runs/%d/jobs" % run_id, filter="latest", per_page=100, page=page)
        got, total = d["jobs"], int(d["total_count"])
        jobs += got
        if len(jobs) >= total:
            return jobs if len(jobs) == total else None
        if not got:
            return None
    return None


def tested_tree(jobs):
    """The tree a run's `legs` job named, or None."""
    lg = [j for j in jobs if j.get("name") == "legs"]
    if len(lg) != 1 or lg[0].get("conclusion") != "success":
        return None
    trees = [m.group(1) for s in (lg[0].get("steps") or []) if s.get("conclusion") == "success"
             for m in [TREE_STEP.match(s.get("name") or "")] if m]
    return trees[0] if len(trees) == 1 else None


def green_kind(jobs, names):
    """Whether every job of the kind is in the run once, green, on macOS."""
    found = [[j for j in jobs if j.get("name") == n] for n in names]
    return all(len(f) == 1 and f[0].get("conclusion") == "success" and MAC in (f[0].get("labels") or []) for f in found)


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, text=True, check=True).stdout.strip()


def macos_green(env, say):
    """-> ({kind: the run it is green in}, the tree) for a trunk push; no
    kind on any doubt."""
    token = env.get("LEGS_TOKEN") or ""
    hide = lambda s: s.replace(token, "<token>") if token else s
    sha, repo = env.get("GITHUB_SHA") or "", env.get("GITHUB_REPOSITORY") or ""
    if not token:
        say("no token for the lookup: every macOS kind runs")
        return {}, ""
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", sha) or not repo:
        say("no pushed commit or repository named: every macOS kind runs")
        return {}, ""
    try:
        head, tree = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
    except (OSError, subprocess.CalledProcessError) as e:
        say("git could not name the checkout (%s): every macOS kind runs" % type(e).__name__)
        return {}, ""
    if head != sha:
        say("the checkout %s is not the pushed commit %s: every macOS kind runs" % (head, sha))
        return {}, ""
    say("the pushed commit %s, tree %s" % (sha, tree))
    try:
        timeout = float(env.get("LEGS_API_TIMEOUT") or 20)
        api = Api(env.get("GITHUB_API_URL") or "https://api.github.com", repo, token, timeout)
        listing = api.get("actions/workflows/%s/runs" % os.path.basename(WORKFLOW), head_sha=sha, per_page=100)
        runs = [r for r in listing["workflow_runs"]
                if r.get("head_sha") == sha and r.get("path") == WORKFLOW and r.get("status") == "completed"
                and r.get("conclusion") == "success" and r.get("event") in EVIDENCE_EVENTS]
        runs.sort(key=lambda r: -int(r["id"]))
        found = {}
        for r in runs[:MAX_RUNS]:
            rid = int(r["id"])
            jobs = run_jobs(api, rid)
            if jobs is None:
                say("%s run %d: its jobs listing falls short of its count, not relied on" % (r["event"], rid))
                continue
            t = tested_tree(jobs)
            if t != tree:
                say("%s run %d tested tree %s, not %s: not relied on" % (r["event"], rid, t or "(not named)", tree))
                continue
            for kind, names in KINDS.items():
                if kind not in found and green_kind(jobs, names):
                    found[kind] = r
        return found, tree
    except Exception as e:  # any failure of the lookup runs every macOS kind
        say("the lookup failed (%s: %s): every macOS kind runs" % (type(e).__name__, hide(str(e))))
        return {}, ""


def leave_of(green):
    """The kinds a trunk push leaves: the green ones, but the oracle's macOS
    leg stays wherever macos-perf runs (it reads that leg's artifact)."""
    return {k: r for k, r in green.items() if not (k == "oracle-macos" and "macos-perf" not in green)}


def verdicts(green, leave, sha, tree, server, repo):
    """One line per kind: skip and the run relied on, or keep and why."""
    lines = []
    for kind in KINDS:
        r = green.get(kind)
        if kind in leave:
            url = "%s/%s/actions/runs/%d" % (server, repo, int(r["id"]))
            lines.append("skip %s: green in %s run %d at %s, tree %s (%s)" % (kind, r["event"], int(r["id"]), sha, tree, url))
        elif r is not None:
            lines.append("keep %s: green in %s run %d, but macos-perf runs and reads its artifact" % (kind, r["event"], int(r["id"])))
        else:
            lines.append("keep %s: no completed, successful pull_request or workflow_dispatch run of %s at this commit "
                         "tested this tree with every job of the kind green on macOS" % (kind, os.path.basename(WORKFLOW)))
    return lines


def main():
    ap = argparse.ArgumentParser(prog="ci/legs.py")
    ap.add_argument("--event", default=os.environ.get("EVENT"))
    ap.add_argument("--github-output")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not a.event:
        print("legs: no event (--event or EVENT)", file=sys.stderr)
        sys.exit(2)
    say = lambda s: print("legs: " + s, file=sys.stderr)
    leave = {}
    if a.event == "push":
        env = os.environ
        green, tree = macos_green(env, say)
        leave = leave_of(green)
        server, repo = env.get("GITHUB_SERVER_URL") or "https://github.com", env.get("GITHUB_REPOSITORY") or ""
        lines = verdicts(green, leave, env.get("GITHUB_SHA") or "", tree, server, repo)
        for line in lines:
            say(line)
        summary = env.get("GITHUB_STEP_SUMMARY")
        if summary:
            try:
                with open(summary, "a", encoding="utf-8") as f:
                    f.write("### The trunk push's macOS jobs\n\n" + "".join("- %s\n" % l for l in lines) + "\n")
            except OSError as e:
                say("the step summary could not be written (%s)" % e)
    out, why = legs(a.event, set(leave))
    say(why)
    if a.json:
        print(json.dumps(out))
        return
    text = "".join("%s=%s\n" % (k, json.dumps(v, separators=(",", ":"))) for k, v in out.items())
    sys.stdout.write(text)
    if a.github_output:
        with open(a.github_output, "a", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
