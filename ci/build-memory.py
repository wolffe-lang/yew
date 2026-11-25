#!/usr/bin/env python3
"""Observe existing wolf builds, without changing their arguments or exit codes.

wait4 ru_maxrss is a high-water RSS, not simultaneous process-tree memory.
Darwin reports bytes; Linux reports KiB. Never subtract the pre-exec floor.
The same wait4 call's ru_majflt is kept as major_faults: on a runner short of
memory, paging can hold a build's resident peak below what it needs.
YEW_BUILD_MEMORY_ENFORCE=0 is deliberately report-only. The owner must approve
an enforcing percentage before changing that setting to 1.
"""
import argparse
import errno
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import uuid

GIB = 1024 ** 3


def rss_bytes(raw, platform=None):
    platform = sys.platform if platform is None else platform
    if platform == "darwin":
        return int(raw)
    if platform.startswith("linux"):
        return int(raw) * 1024
    raise ValueError("unsupported ru_maxrss platform: " + platform)


def records_path():
    if os.environ.get("YEW_BUILD_MEMORY_DIR"):
        return Path(os.environ["YEW_BUILD_MEMORY_DIR"])
    return Path(os.environ.get("RUNNER_TEMP", os.environ.get("YEW_ROOT", "."))) / "yew-build-memory"


def atomic_json(path, value):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False,
                                     prefix=".record-", encoding="utf-8") as stream:
        temp = Path(stream.name)
        try:
            json.dump(value, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)


def diagnostic(error):
    print("build-memory: telemetry error: " + str(error), file=sys.stderr, flush=True)


def status_code(status):
    return os.waitstatus_to_exitcode(status)


def run_build(command, directory, name, tier="native", compiler="fixture"):
    # These imports and journal operations are deliberately small. Record the
    # actual floor before fork; exec must not be mistaken for a reset of RSS.
    rss_bytes(0)  # refuse an unsupported platform before starting anything
    ident = uuid.uuid4().hex
    start_path = directory / (ident + ".start.json")
    done_path = directory / (ident + ".done.json")
    start = {"schema": 1, "id": ident, "name": name, "tier": tier,
             "argv": command, "cwd": os.getcwd(), "compiler": compiler,
             "platform": sys.platform, "raw_unit": "bytes" if sys.platform == "darwin" else "KiB"}
    journal_ok = True
    try:
        directory.mkdir(parents=True, exist_ok=True)
        atomic_json(start_path, start)
    except OSError as error:
        diagnostic(error)
        journal_ok = False
    read_fd, write_fd = os.pipe()
    parent_floor = rss_bytes(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        try:
            floor = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            os.write(write_fd, str(int(floor)).encode("ascii"))
            os.close(write_fd)
            os.execvpe(command[0], command, os.environ)
        except OSError as error:
            print("build-memory: exec: " + str(error), file=sys.stderr, flush=True)
            os._exit(127 if error.errno == errno.ENOENT else 126)
    os.close(write_fd)
    while True:
        try:
            _, status, usage = os.wait4(pid, 0)
            break
        except InterruptedError:
            continue
    child_floor = os.read(read_fd, 128)
    os.close(read_fd)
    code = status_code(status)
    try:
        floor = rss_bytes(int(child_floor))
        raw = int(usage.ru_maxrss)
        peak = rss_bytes(raw) // 2
        record = dict(start, raw_maxrss=raw, peak_bytes=peak,
                      parent_floor_bytes=parent_floor, child_floor_bytes=floor,
                      floor_limited=peak <= max(parent_floor, floor),
                      major_faults=int(usage.ru_majflt),
                      exit_code=code, signal=-code if code < 0 else None)
        if journal_ok:
            atomic_json(done_path, record)
    except (OSError, ValueError) as error:
        diagnostic(error)
    # A signaled compiler must not become a successful wrapper. Reproduce its
    # signal rather than mapping e.g. SIGSEGV to a normal exit(139).
    if code < 0:
        signum = -code
        signal.signal(signum, signal.SIG_DFL) if signum not in (signal.SIGKILL, signal.SIGSTOP) else None
        signal.pthread_sigmask(signal.SIG_UNBLOCK, {signum})
        signal.raise_signal(signum)
        return 128 + signum
    return code


def build_name(args):
    entry = next((arg for arg in args if arg.endswith(".lu")), "(unnamed entry)")
    output = "(default output)"
    for index, arg in enumerate(args):
        if arg == "-o" and index + 1 < len(args):
            output = args[index + 1]
    tier = "release" if "--release" in args else "native"
    return "%s -> %s" % (entry, output), tier


def physical_total(platform=None, meminfo=None):
    platform = sys.platform if platform is None else platform
    if platform.startswith("linux"):
        text = Path("/proc/meminfo").read_text() if meminfo is None else meminfo
        for line in text.splitlines():
            fields = line.split()
            if fields and fields[0] == "MemTotal:" and len(fields) == 3 and fields[2] == "kB":
                value = int(fields[1]) * 1024
                if value > 0:
                    return value
        raise ValueError("missing or invalid MemTotal")
    if platform == "darwin":
        value = int(subprocess.check_output(["/usr/sbin/sysctl", "-n", "hw.memsize"], text=True))
        if value > 0:
            return value
    raise ValueError("unavailable physical memory total")


def effective_total(total):
    """Walk this process's cgroup hierarchy, including finite ancestor limits."""
    if not sys.platform.startswith("linux"):
        return total
    memberships = Path("/proc/self/cgroup").read_text().splitlines()
    mounts = Path("/proc/self/mountinfo").read_text().splitlines()
    limits = [total]
    for line in memberships:
        _, controllers, relative = line.split(":", 2)
        for mount in mounts:
            before, after = mount.split(" - ", 1)
            kind, _, options = after.split()[:3]
            if not ((kind == "cgroup2" and controllers == "") or
                    (kind == "cgroup" and "memory" in controllers.split(",") and "memory" in options.split(","))):
                continue
            fields = before.split()
            root, point = fields[3], fields[4]
            relative_path = Path(relative)
            try:
                tail = relative_path.relative_to(root)
            except ValueError:
                continue
            if ".." in tail.parts:
                raise ValueError("cgroup membership escapes its mounted hierarchy")
            current = Path(point) / tail
            filename = "memory.max" if kind == "cgroup2" else "memory.limit_in_bytes"
            while True:
                path = current / filename
                if path.exists():
                    text = path.read_text().strip()
                    if text != "max":
                        value = int(text)
                        if value > 0:
                            limits.append(value)
                if current == Path(point):
                    break
                current = current.parent
    return min(limits)


def read_records(directory):
    starts, completed, errors = {}, [], []
    for path in sorted(directory.glob("*.start.json")):
        starts[path.name.removesuffix(".start.json")] = path
    for path in sorted(directory.glob("*.done.json")):
        ident = path.name.removesuffix(".done.json")
        try:
            row = json.loads(path.read_text())
            if row["schema"] != 1 or row["id"] != ident or ident not in starts:
                raise ValueError("record identity/start mismatch")
            start = json.loads(starts[ident].read_text())
            if any(row[key] != value for key, value in start.items()):
                raise ValueError("start/completion mismatch")
            for key in ("raw_maxrss", "peak_bytes", "parent_floor_bytes", "child_floor_bytes", "major_faults"):
                if type(row[key]) is not int or row[key] < 0:
                    raise ValueError("invalid " + key)
            if row["peak_bytes"] <= 0 or row["peak_bytes"] != rss_bytes(row["raw_maxrss"], row["platform"]):
                raise ValueError("bad RSS normalization")
            if row["raw_unit"] != ("bytes" if row["platform"] == "darwin" else "KiB"):
                raise ValueError("bad RSS unit")
            if type(row["floor_limited"]) is not bool:
                raise ValueError("bad floor flag")
            if type(row["exit_code"]) is not int or row["tier"] not in ("native", "release"):
                raise ValueError("bad status/tier")
            if not isinstance(row["name"], str) or not isinstance(row["argv"], list):
                raise ValueError("bad name/argv")
            completed.append(row)
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(path.name + ": " + str(error))
    missing = len(starts) - len(completed)
    if missing:
        errors.append("%d start(s) without valid completion" % missing)
    return len(starts), completed, errors


def largest(rows):
    return min(rows, key=lambda row: (-row["peak_bytes"], row["name"], json.dumps(row["argv"]))) if rows else None


def exceeds(peak, total, percent):
    return 100 * peak > percent * total


def report(directory, job, matrix, summary, enforce, percent, expect_builds=False):
    started, rows, errors = read_records(directory)
    if expect_builds and not started:
        errors.append("no observed builds: work did not start or telemetry could not be written")
    total = effective = None
    try:
        total = physical_total()
        effective = effective_total(total)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    winner = largest(rows)
    native = largest([row for row in rows if row["tier"] == "native"])
    state = "incomplete" if errors else "complete" if rows else "no-explicit-wolf-builds"
    if rows and not any(row["exit_code"] == 0 for row in rows):
        state = "incomplete" if errors else "failed-or-refused-attempts"
    if expect_builds and not started:
        state = "not-run"
    peak = winner["peak_bytes"] if winner else None
    result = {"job": job, "matrix": matrix, "state": state,
              "run_id": os.environ.get("GITHUB_RUN_ID"), "head_sha": os.environ.get("GITHUB_SHA"),
              "completed": len(rows), "started": started,
              "largest": winner["name"] if winner else None,
              "tier": winner["tier"] if winner else None,
              "exit_code": winner["exit_code"] if winner else None,
              "peak_bytes": peak, "peak_gib": round(peak / GIB, 3) if peak is not None else None,
              "native_largest": native["name"] if native else None,
              "native_peak_bytes": native["peak_bytes"] if native else None,
              "runner_total_bytes": total, "runner_total_gib": round(total / GIB, 3) if total else None,
              "effective_limit_bytes": effective,
              "margin_certified": not errors and peak is not None,
              "peak_is_lower_bound": bool(errors),
              "margin_bytes": total - peak if total and peak is not None else None,
              "margin_gib": round((total - peak) / GIB, 3) if total and peak is not None else None,
              "effective_margin_bytes": effective - peak if effective and peak is not None else None,
              "percent": round(100 * peak / total, 2) if total and peak is not None else None,
              "reader_floor_bytes": max(winner["parent_floor_bytes"], winner["child_floor_bytes"]) if winner else None,
              "floor_limited": winner["floor_limited"] if winner else None,
              "major_faults": winner["major_faults"] if winner else None,
              "policy": "enforce" if enforce else "report-only", "limit_percent": percent,
              "errors": errors}
    try:
        directory.mkdir(parents=True, exist_ok=True)
        atomic_json(directory / "report.json", result)
    except OSError as error:
        diagnostic(error)
        errors.append("baseline artifact write failed")
    line = "build-memory " + json.dumps(result, sort_keys=True, separators=(",", ":"))
    print(line, flush=True)
    if summary:
        try:
            # One data row; the same JSON fields as the single log line. HTML
            # and Markdown delimiters in compiler names cannot create markup.
            escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("`", "&#96;")
            with open(summary, "a", encoding="utf-8") as stream:
                stream.write("\n| Compiler build memory (bytes; GiB = 2³⁰ bytes) |\n| --- |\n| " + escaped + " |\n")
        except OSError as error:
            diagnostic(error)
            errors.append("summary write failed")
    if errors:
        print("::warning::build-memory observation incomplete; no safe margin certified", file=sys.stderr)
    return int(enforce and (bool(errors) or (peak is not None and exceeds(peak, effective, percent))))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "wolf":
        real, args = argv[1], argv[2:]
        if not real:
            print("wolf-memory: no real compiler", file=sys.stderr, flush=True)
            return 127
        if os.environ.get("YEW_BUILD_MEMORY") != "1" or not args or args[0] != "build":
            os.execvpe(real, [real] + args, os.environ)
        name, tier = build_name(args)
        return run_build([real] + args, records_path(), name, tier,
                         os.environ.get("YEW_MEMORY_REAL_WOLF_ID", real))
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="mode", required=True)
    run = subs.add_parser("run")
    run.add_argument("--records", type=Path, required=True)
    run.add_argument("--name", required=True)
    run.add_argument("command", nargs=argparse.REMAINDER)
    output = subs.add_parser("report")
    output.add_argument("--records", type=Path, default=records_path())
    output.add_argument("--job", default=os.environ.get("GITHUB_JOB", "local"))
    output.add_argument("--matrix", default=os.environ.get("YEW_MEMORY_MATRIX", "{}"))
    output.add_argument("--summary", default=os.environ.get("GITHUB_STEP_SUMMARY"))
    args = parser.parse_args(argv)
    if args.mode == "run":
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            parser.error("run requires a command after --")
        return run_build(command, args.records, args.name)
    enforce = os.environ.get("YEW_BUILD_MEMORY_ENFORCE", "0")
    percent = int(os.environ.get("YEW_BUILD_MEMORY_LIMIT_PERCENT", "85"))
    if enforce not in ("0", "1") or not 0 < percent <= 100:
        parser.error("expected ENFORCE=0|1 and LIMIT_PERCENT in 1..100")
    matrix = json.loads(args.matrix)
    expected = args.job in {"port", "unit", "macos-unit", "fuzz", "oracle", "oracle-cmdcomp", "macos-fuzz", "macos-perf", "collector"}
    if args.job == "oracle" and matrix.get("port") is False:
        expected = False
    # The editor perf family restores the macOS oracle leg's builds; it builds nothing.
    if args.job == "macos-perf" and matrix.get("family") == "editor":
        expected = False
    return report(args.records, args.job, args.matrix, args.summary, enforce == "1", percent, expected)


if __name__ == "__main__":
    raise SystemExit(main())
