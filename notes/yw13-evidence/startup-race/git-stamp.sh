#!/bin/sh
# Logs each git child's start and end (wall seconds, microseconds) to
# $YW13_GITLOG, then runs the real git.
log=${YW13_GITLOG:-/dev/null}
/usr/bin/perl -MTime::HiRes=time -e 'printf "%.6f %d start %s\n", time, getppid(), join(" ", @ARGV)' -- "$@" >> "$log"
/usr/bin/git "$@"
rc=$?
/usr/bin/perl -MTime::HiRes=time -e 'printf "%.6f %d end rc=%s\n", time, getppid(), $ARGV[0]' -- "$rc" >> "$log"
exit $rc
