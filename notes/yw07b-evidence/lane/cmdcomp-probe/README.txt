yw07b lead: src/edit_cmdcomp_shell_test.lu on the checked machine
(`wolf conform-run --deny-warnings --checked --json`, the file whole), at the tree of
706933b (the code of efe5e64), in the lane container on kasumi, 2026-10-25 18:43-18:55Z.
probe1: twice on one core, then twice sharing that core with two busy loops (1/3 of it).
probe2: once with 8 busy loops on its core (282 s, ~1/50 of plain speed), once with 16.
probe3: twice with /tmp on tmpfs (another readdir order) instead of the container's overlay.
Every one of the 8 runs: `unsupported | step budget exhausted`, never trap(assert), so
neither speed nor /tmp's filesystem reproduces CI's trap. probe2's hog16 run took 100 s
against hog8's 282 s, which is unexplained; it is not a speed claim.
