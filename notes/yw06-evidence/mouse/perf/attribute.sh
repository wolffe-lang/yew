#!/bin/bash
# attribute.sh — where the release burst's time goes (the yw06 lane's
# follow-up to the 6.00x burst row): run in the ctr from the clone root,
# under the job's taskset (kasumi 8-11). Builds the release perf-mouse
# (C's perf_mouse already built), prints the stage attribution three
# times, takes a flat sampling profile of the burst alone when the
# container allows perf_event_open, then runs the gate C / port / C.
set -u
export YEW_ROOT=$PWD
. tools/lib-toolchain.sh
tools/run-perf-mouse --build-only || exit 2
P=target/perf-mouse/perf-mouse
for i in 1 2 3; do
    YEW_LOG=/dev/null taskset -c 8-11 "$P" --attribute
done
if perf record -F 20000 -o target/mouse-perf.data -- "$P" --burst-loop 3000 >target/mouse-perf.out 2>&1; then
    cat target/mouse-perf.out | tail -3
    perf report -i target/mouse-perf.data --stdio --sort symbol --percent-limit 0.5 2>/dev/null | grep -v '^$' | head -60
else
    echo "attribute: perf record refused in the container:"
    tail -5 target/mouse-perf.out
fi
rm -f target/mouse-perf.data target/mouse-perf.out
PERF_PREBUILT=1 tools/run-perf-mouse --cpus 8-11
echo "attribute: gate rc=$?"
