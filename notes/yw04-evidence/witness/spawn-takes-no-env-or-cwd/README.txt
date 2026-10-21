yw04-shell, 2026-10-21, kasumi, wolf 0.2.33: a spawn takes no environment
and no working directory (G36). C's job layer builds each child's envp
(YEW_FILE, YEW_LINE, YEW_COL, YEW_WORKSPACE, YEW_JOB, PAGER=cat, less
COLUMNS/LINES) and its cwd (the workspace root) into the spawn
(sagitta src/edit/job.c:581-695). std.process's Command carries argv and
file descriptors only (set_fd/set_stdin/set_stdout/set_stderr); only
`exec`, which replaces the calling process, takes an environment. The
port's synchronous route (edit.job_run_sync) therefore sets the process's
own environment and cwd around the spawn and restores both after
(jb_apply/jb_restore); a concurrent child (the async job half, R-yw04-1)
could not do that safely. Build: `wolf build main.lu` -> run.txt (E0301
for set_cwd and set_env).
