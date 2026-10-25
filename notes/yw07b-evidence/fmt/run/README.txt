fmt black-box differential, 2026-10-25T08:15:35Z, kasumi in the lane container (ctr.sh),
wolf 0.2.35 native build of probe/main.lu at fmt fd91db4
against C yew built at the pin (9ace98c2): fmt-diff.sh. Each line of ../cases.txt
is a Fletch body: the port's answer through flfix (port.hex), C's through
io.print of the same body in a script, a raise as "!kind: msg" (c.hex).
Result: compare.log, "195 of 195 identical". The first run's 16 cases spelt
floats without a point (1e21), which both refused as parse errors; they were
respelt (1.0e21) and the whole list rerun. No NaN with its sign bit set is
among the cases: that is G51's open class (wolf-std#103).
