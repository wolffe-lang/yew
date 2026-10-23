#!/bin/bash
# units.sh FILE... — unit.sh over each file in turn (native whole).
set -u
for f in "$@"; do
    notes/yw06-evidence/pick/unit.sh "$f"
done
