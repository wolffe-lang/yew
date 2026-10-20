yw04-shell, 2026-10-20, kasumi, wolf 0.2.33 (85dab5d): an untyped counter
(`var k = 3`) used as the SHIFT AMOUNT of a `wrapping[u64]` is inferred as
`wrapping[u64]`: `k >= 0` is then always true and `k -= 1` wraps silently
past 0 (the run below goes 0 -> 18446744073709551615). Met in
edit.comphelp's hex formatter (`while k >= 0 { (h >> (k * 4)) & 15 … k -= 1 }`),
which ran away to 30 GB resident + 25.7 GB swap in the lane's podman
container before systemd-oomd killed the container (twice, 2026-10-20
~23:05-23:13Z); the container now runs with --memory 6g. A shift count is
not the shifted value: the count's type should not unify with the operand's
(or `k >= 0` on an unsigned should warn). Gap row G38 (docs/MAP.md §5).
Run: `wolf run main.lu` -> `run.txt`.
