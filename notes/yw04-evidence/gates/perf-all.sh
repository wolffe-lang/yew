#!/bin/bash
# yw04: the 2x gates at the final head, inside the container under taskset -c 0-3,
# C beside the port from the same run (each tool runs C, the port, C again).
cd /home/mfwolffe/lanes/yw04/yew
v=target/verify/perf; mkdir -p $v
echo "perf-all: head $(cat target/verify/HEAD) release $(sha256sum target/release/yew | cut -c1-12) load $(cut -d' ' -f1-3 /proc/loadavg)"
for r in 1 2 3; do
  tools/run-perf-editor --cpus 0-3 > $v/editor-$r.txt 2>&1; echo "editor run $r: exit $? load $(cut -d' ' -f1-3 /proc/loadavg)"
done
tools/run-perf-search-session --cpus 0-3 > $v/search-session.txt 2>&1; echo "search-session: exit $? load $(cut -d' ' -f1-3 /proc/loadavg)"
PERF_PREBUILT=1 tools/run-perf-cmdcomp --cpus 0-3 --trials 400 > $v/cmdcomp.txt 2>&1; echo "cmdcomp: exit $? load $(cut -d' ' -f1-3 /proc/loadavg)"
tools/run-perf-re --prebuilt --taskset 0-3 --bytes 1073741824 > $v/re.txt 2>&1; echo "re: exit $? load $(cut -d' ' -f1-3 /proc/loadavg)"
PERF_PREBUILT=1 tools/run-perf-search --taskset 0-3 --bytes 104857600 --reps 1000 > $v/search-inproc.txt 2>&1; echo "search-inproc: exit $? load $(cut -d' ' -f1-3 /proc/loadavg)"
echo END
