#!/usr/bin/env python3
"""Black-box fixture source and measurement for sagitta.pin's config policy."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
root.mkdir(parents=True, exist_ok=True)
for name in ("home", "config/yew", "state", "cache", "data", "runtime", "work"):
    (root / name).mkdir(parents=True, exist_ok=True)
(root / "runtime/init.fl").write_text('bind("L", "X", "ed.nop")\n')
source = ('bind("L", "Y", "ed.nop")\n'
          'bind("L", "t h", "ed.theme.pick")\n'
          'bind("L", "Z", "ed.nop")\n')
env = dict(os.environ, HOME=str(root / "home"), XDG_CONFIG_HOME=str(root / "config"),
           XDG_STATE_HOME=str(root / "state"), XDG_CACHE_HOME=str(root / "cache"),
           XDG_DATA_HOME=str(root / "data"), YEW_RUNTIME_DIR=str(root / "runtime"))
user = root / "config/yew/init.fl"
workspace = root / "work/.yew.fl"
for kind, path in (("user", user), ("workspace", workspace)):
    if user.exists(): user.unlink()
    path.write_text(source)
    print(f"=== {kind} init.fl: before Y, unknown t h, after Z ===", flush=True)
    subprocess.run([sys.argv[2], str(user), str(root / "work")], env=env, check=True)
