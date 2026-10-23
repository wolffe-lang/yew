# the job stream's lost frame (found by the final 2× runs; not fixed here)

`perf_jobstream` (sagitta's, 2,000 Up/Down keys under `:!yes … | head -c N`,
each key given 2 s to reach a frame) intermittently fails on the PORT only:
"jobstream: key K never reached a frame". C: 0 of 72 runs. The port, 50 MiB
(the default): 1 of 4 in the final perf (`../perf-final/perf-jobstream-P2-3.txt`,
key 423), 5 of 60 (`J2.log`, keys 408-512), 1 of 12 (`J3.log`, key 624); with
a 1 ms delay between keys 0 of 6; 1 MiB 0 of 10 (`J1.log`) and 0 of 6 with the
delay. Hosted CI: run 39836026916's ubuntu oracle (key 562), run 39858036336's
macOS oracle (key 436), both in the advisory step.

The black-box driver (`js-driver.py`, the harness's shape at Python's pace,
stalls 2 of 80 in `J4.log` and 3 of 28 in `J5.log`) shows it is a STALL, not a
hang: the lost key's frame arrives ~4.0 s after it (3.95-4.00 s), and the next
key wakes the editor. At the timeout the editor sits in `poll` over three
descriptors (the terminal's duplicate fd 9, a pipe fd 14, the runtime's fd 7)
with a 3,999 ms timeout, and the terminal holds 0 unread bytes: the key was
READ but neither dispatched to a frame nor counted in the wait's deadline.
4,000 ms is `edit.message`'s `MESSAGE_INFO_MS` (an info message's expiry):
the turn that read the key posts an info message (the job's end, it seems),
and the next wait sleeps until it expires. Every stall lands ~2.5 s after the
`:!` line at the driver's pace (~0.5 s at the harness's), where the 50 MiB
stream ends. The editor's children at the stall: a forked `yew` and the
session's `sh` (no grandchildren: `yes` and `head` are gone).

Not yet located: whether `input_next` held the key or `ed_render` skipped
the frame. `term.input_deadline` answers -1 whenever no lone ESC is armed,
so decoded-but-undispatched input would not shorten the wait.
