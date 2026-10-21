#!/usr/bin/env python3
"""ci/legs.py — the hosts each job of .github/workflows/ci.yml runs for an
event (tl30, the macOS cap; tl28's plan job, cut to yew's two jobs).

    ci/legs.py [--event E] [--github-output FILE] [--json]

`--event` also reads EVENT from the environment, which is how the
workflow's `legs` job passes it in. Prints `matrix_port=` and
`matrix_oracle=` (each a JSON list for `include:`), to --github-output
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
                builds there.

ci/legs-test.py is this file's proof and runs first in the same job.
"""
import argparse
import json
import os
import sys

PORT = [
    {"os": "ubuntu-latest", "builds": True},
    {"os": "macos-latest", "builds": True},
    {"os": "ubuntu-24.04-arm", "builds": False},
]
ORACLE = [
    {"os": "ubuntu-latest", "ccs": "--cc clang --cc gcc", "port": True},
    {"os": "macos-latest", "ccs": "--cc clang", "port": True},
    {"os": "ubuntu-24.04-arm", "ccs": "--cc clang --cc gcc", "port": False},
]
MATRIX = {"port": PORT, "oracle": ORACLE}
EVERY_LEG_EVENTS = ("schedule", "workflow_dispatch")


def merge_leg(job, leg):
    """Whether a pull request's run (and a trunk push's) runs this leg:
    every leg but the macOS port, the nightly's."""
    return True  # the plant: a pull request runs the macOS port again, its shape before tl30


def legs(event):
    """-> ({output name: the legs}, the reason)."""
    if event in EVERY_LEG_EVENTS:
        return {"matrix_" + j: list(v) for j, v in MATRIX.items()}, "%s: every leg" % event
    return ({"matrix_" + j: [l for l in v if merge_leg(j, l)] for j, v in MATRIX.items()},
            "%s: the merge's legs (the macOS port is the nightly's)" % (event or "no event"))


def main():
    ap = argparse.ArgumentParser(prog="ci/legs.py")
    ap.add_argument("--event", default=os.environ.get("EVENT"))
    ap.add_argument("--github-output")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not a.event:
        print("legs: no event (--event or EVENT)", file=sys.stderr)
        sys.exit(2)
    out, why = legs(a.event)
    print("legs: " + why, file=sys.stderr)
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
