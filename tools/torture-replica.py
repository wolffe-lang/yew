#!/usr/bin/env python3
"""torture-replica — the late lanes of sagitta's `tests/torture/kill9.c`,
run line for line against any child and any checker.

sagitta's driver runs its lanes in one order and stops at the first red
(`kill9.c:1159-1203`). At wolf 0.2.33 the port's save synced nothing (G3,
wolf-lang#796), so against the port's child the driver went red at
`inplace_write_failure_check` — the EIO the fault shim arms after a
directory fsync (`faultshim.c:456-462`) — and never reached the EINTR,
ENOSPC, determinism and external-SIGKILL lanes; this tool was written to run
THOSE four. Since the 0.2.34 pin the save syncs and the driver reaches every
lane itself; the replica stays as the cross-check the driver cannot make:
line for line from `kill9.c` (`injected_eintr` 907-926, `injected_enospc`
928-967, `determinism_check` 831-860 with `atomic_log_order` 321-391,
`external_kills` 1046-1104, `random_next` 1036-1044, the fixtures 19-23,
`start_save` 163-232, `run_check` 234-251), with sagitta's own fault shim,
the port's child checked by C and C's child checked by the port. It is the
PORT'S replica, not sagitta's driver, and says so in every line it prints.

    tools/torture-replica.py --child BIN --checker BIN --shim SO
                             [--iters 500] [--lanes eintr,enospc,determinism,sigkill]
                             [--live]

`--state-per-run` (yw04) gives each determinism run its own
`XDG_STATE_HOME`: C's live editor keeps its `:` history per WORKSPACE
(`cmdline.c:410-422`, `history.scope` defaults to "workspace", s25 §8), and
each kill9 case is its own workspace (`yew-live-torture.c:133-146`), so C's
two runs start from an empty history; the port's history is global until
the workspace state is ported (yw06), so with one shared state home its
second run finds `ed.quit_force` already last and appends nothing
(`cmdhist.c:75-80`). Run with the flag, the lane compares like with like.

`--live` (yw04) is kill9's `YEW_TORTURE_LANE=live-editor`: the child is
sagitta's `yew-live-torture` driving an editor binary (`YEW_TORTURE_YEW`
in the environment), which reports a failed save in-session and then
quits on the feeder's `:ed.quit_force`, so the ENOSPC lane expects exit 0
where the API child exits 3 (`kill9.c:951`); every other lane is the same.

Exit 0 when every requested lane holds. Signals go only to the children
it starts; run it inside a container (sprints/RULES.md §5).
"""
import argparse
import os
import shutil
import signal
import sys
import tempfile
import time

OLD = b"yew torture fixture: before save\nline two\n"
POST = (b"yew torture fixture: AFTER save\n"
        b"a substantially longer replacement line that forces short writes\n"
        b"final line without a newline")
MASK = (1 << 64) - 1


def random_next(state):
    x = state[0]
    x ^= (x << 13) & MASK
    x ^= x >> 7
    x ^= (x << 17) & MASK
    state[0] = x
    return x


def make_file(path, data):
    with open(path, "wb") as f:
        f.write(data)


def case_paths(root, lane, serial):
    base = os.path.join(root, f"{lane}-{serial}")
    return base + ".txt", base + ".old", base + ".new", base + ".log"


def start_save(child, shim, dst, post, log, seed, extra_env, ready_fd=None):
    env = dict(os.environ)
    env["LD_PRELOAD"] = shim
    env["YEW_FAULT_ENABLE"] = "0"
    env["YEW_FAULT_SHORT"] = "1"
    env["YEW_FAULT_LOG"] = log
    env["YEW_FAULT_SEED"] = str(seed)
    env.pop("YEW_FAULT_AT", None)
    if ready_fd is not None:
        env["YEW_TORTURE_READY_FD"] = str(ready_fd)
    else:
        env.pop("YEW_TORTURE_READY_FD", None)
    env.update(extra_env)
    pid = os.fork()
    if pid == 0:
        try:
            os.execve(child, [child, "--save", dst, post], env)
        finally:
            os._exit(126)
    return pid


def wait_code(pid):
    _, status = os.waitpid(pid, 0)
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status), status
    if os.WIFSIGNALED(status):
        return 128 + os.WTERMSIG(status), status
    return 255, status


def run_check(checker, dst, old, post):
    env = dict(os.environ)
    for k in ("LD_PRELOAD", "YEW_FAULT_AT", "YEW_FAULT_SHORT", "YEW_FAULT_ENABLE"):
        env.pop(k, None)
    pid = os.fork()
    if pid == 0:
        try:
            os.execve(checker, [checker, "--check", dst, old, post], env)
        finally:
            os._exit(126)
    code, _ = wait_code(pid)
    return code == 0


def fresh_case(root, lane, serial):
    dst, old, post, log = case_paths(root, lane, serial)
    make_file(dst, OLD)
    make_file(old, OLD)
    make_file(post, POST)
    return dst, old, post, log


def lane_eintr(a, root, serial):
    dst, old, post, log = fresh_case(root, "eintr", serial)
    code, _ = wait_code(start_save(a.child, a.shim, dst, post, log, 17, {"YEW_FAULT_EINTR_AT": "0"}))
    ok = code == 0 and run_check(a.checker, dst, old, post)
    print(f"replica: retry EINTR {'ok' if ok else 'FAILED'} (exit {code})")
    return ok


def lane_enospc(a, root, serial):
    dst, old, post, log = fresh_case(root, "enospc", serial)
    code, _ = wait_code(start_save(a.child, a.shim, dst, post, log, 17, {"YEW_FAULT_ENOSPC_AT": "0"}))
    oracle = run_check(a.checker, dst, old, post)
    with open(dst, "rb") as f:
        exact = f.read() == OLD
    with open(log, "rb") as f:
        injected = b"errno=ENOSPC" in f.read()
    expected = 0 if a.live else 3
    ok = code == expected and injected and oracle and exact
    print(f"replica: storage ENOSPC preserves old+journal {'ok' if ok else 'FAILED'} "
          f"(exit={code} expected={expected} injected={int(injected)} oracle={int(oracle)} exact={int(exact)})")
    return ok


def atomic_log_order(path):
    state = 0
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 3:
                return False, "malformed"
            _, name, action = parts
            if action == "short":
                continue
            if action != "pass":
                return False, f"{name} {action}"
            if state == 0:
                if name != "write":
                    return False, f"first call {name}, not write"
                state = 1
            elif state == 1:
                if name == "write":
                    continue
                if name != "fsync-file":
                    return False, f"{name} where fsync-file is wanted"
                state = 2
            elif state == 2:
                if name in ("fchown", "close"):
                    continue
                if name != "rename":
                    return False, f"{name} where rename is wanted"
                state = 3
            elif state == 3:
                if name != "fsync-dir":
                    return False, f"{name} where fsync-dir is wanted"
                state = 4
            if state == 4:
                break
    return state == 4, f"reached state {state}"


def lane_determinism(a, root, serial):
    logs = []
    ok = True
    for run in range(2):
        dst, old, post, log = fresh_case(root, "determinism", serial + run)
        extra = {}
        if a.state_per_run:
            state = os.path.join(root, f"state-determinism-{run}")
            os.makedirs(state, 0o700, exist_ok=True)
            extra["XDG_STATE_HOME"] = state
        code, _ = wait_code(start_save(a.child, a.shim, dst, post, log, 424242, extra))
        checked = run_check(a.checker, dst, old, post)
        order, why = atomic_log_order(log)
        with open(log) as f:
            logs.append(f.read())
        if code != 0 or not checked:
            ok = False
        print(f"replica: determinism run {run}: exit={code} check={int(checked)} "
              f"order={'ok' if order else 'NO'} ({why})")
        if not order:
            ok = False
    same = logs[0] == logs[1]
    print(f"replica: determinism same seed, same log: {'yes' if same else 'NO'}")
    print("replica: determinism log:", " | ".join(logs[0].strip().splitlines()))
    if not same:
        print("replica: determinism log of run 1:", " | ".join(logs[1].strip().splitlines()))
    return ok and same


def lane_sigkill(a, root, serial, count):
    rng = [0x7361676974746108]
    killed = 0
    attempts = 0
    safety = count * 10 + 100
    old_seen = 0
    new_seen = 0
    while killed < count and attempts < safety:
        attempts += 1
        dst, old, post, log = fresh_case(root, "signal", serial + attempts)
        r, w = os.pipe()
        os.set_inheritable(w, True)
        seed = random_next(rng)
        pid = start_save(a.child, a.shim, dst, post, log, seed, {"YEW_FAULT_DELAY_US": "5000"}, ready_fd=w)
        os.close(w)
        got = os.read(r, 1)
        os.close(r)
        if len(got) == 1:
            delay = random_next(rng) % 20000001
            time.sleep(delay / 1e9)
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        _, status = wait_code(pid)
        if not run_check(a.checker, dst, old, post):
            print(f"replica: external SIGKILL invariant FAILED at={killed}")
            return False
        with open(dst, "rb") as f:
            data = f.read()
        old_seen += data == OLD
        new_seen += data == POST
        if os.WIFSIGNALED(status) and os.WTERMSIG(status) == signal.SIGKILL:
            killed += 1
        for p in (dst, old, post, log):
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
    if killed != count:
        print(f"replica: only {killed}/{count} children received SIGKILL")
        return False
    print(f"replica: external-sigkill iterations={count} attempts={attempts} "
          f"old={old_seen} new={new_seen} ok")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--child", required=True)
    ap.add_argument("--checker", required=True)
    ap.add_argument("--shim", required=True)
    ap.add_argument("--iters", type=int, default=500)
    ap.add_argument("--lanes", default="eintr,enospc,determinism,sigkill")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--state-per-run", action="store_true")
    a = ap.parse_args()
    root = tempfile.mkdtemp(prefix="yew-torture-replica-")
    state = os.path.join(root, "state")
    os.mkdir(state, 0o700)
    os.environ["XDG_STATE_HOME"] = state
    print(f"replica: the port's replica of kill9.c's late lanes; child={a.child} checker={a.checker}"
          + (f" live-editor={os.environ.get('YEW_TORTURE_YEW', '')}" if a.live else ""))
    ok = True
    serial = 0
    for lane in a.lanes.split(","):
        serial += 10000
        if lane == "eintr":
            ok = lane_eintr(a, root, serial) and ok
        elif lane == "enospc":
            ok = lane_enospc(a, root, serial) and ok
        elif lane == "determinism":
            ok = lane_determinism(a, root, serial) and ok
        elif lane == "sigkill":
            ok = lane_sigkill(a, root, serial, a.iters) and ok
        else:
            print(f"replica: unknown lane {lane}")
            return 2
    if os.environ.get("YEW_TORTURE_KEEP"):
        print(f"replica: root retained: {root}")
    else:
        shutil.rmtree(root, ignore_errors=True)
    print("replica: GREEN" if ok else "replica: RED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
