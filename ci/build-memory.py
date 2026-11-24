#!/usr/bin/env python3
"""Initial red scaffold: deliberately under-report the fixture."""
import json
import os
from pathlib import Path
import resource
import sys

args = sys.argv[1:]
assert args[0] == "run"
records = Path(args[args.index("--records") + 1])
records.mkdir(parents=True, exist_ok=True)
command = args[args.index("--") + 1:]
floor = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
pid = os.fork()
if pid == 0:
    os.execvp(command[0], command)
_, status, usage = os.wait4(pid, 0)
record = {"peak_bytes": 0, "parent_floor_bytes": floor, "child_floor_bytes": floor}
(records / "fixture.done.json").write_text(json.dumps(record))
sys.exit(os.waitstatus_to_exitcode(status))
