/*
 * yw06 (R-yw06-3 = A): M-YW5's automated twins of the field boxes the
 * port can answer today — "Workspace resume in anger" (s42 §10 :495,
 * >= 20 cycles) and the restore trials of "Zero data loss" / "Terminal
 * restore in the field" (:469, :476) — written over sagitta's own PTY
 * harness at 9ace98c2 (tests/pty/harness.c, the s25 helpers of
 * tests/pty/registry.c:6230-6400), lane evidence, never a golden.
 *
 * registry.c is included whole so its static s25 helpers are in scope;
 * its case table is renamed out of the way and this file's four cases
 * are the runner's table. Each case builds s25_resume_exact's arrangement
 * (six files, three grouped, two panes, a CJK cursor, a scrolled view, two
 * jumplist entries) and ends on the C golden `s25_resume_exact`, so the
 * last grid is held to C's as well as to the first process's:
 *
 *   trial_resume_cycles20   quit and reopen twenty times; every reopened
 *                           grid byte-identical to the one before the
 *                           first quit (ptc_check_resume_exact)
 *   trial_restore_sigkill   the debounced save (2,000 ms, state.h:76)
 *   trial_restore_sigsegv   allowed to land, then the editor killed by the
 *   trial_restore_hangup    signal / its terminal closed (the master fd
 *                           shut: the kernel's SIGHUP to the session);
 *                           the reopened grid is the arrangement exactly —
 *                           a fatal path saves nothing (s25 §5), so what
 *                           comes back is the last save, whole
 *
 * Signals go only to the editor this runner spawned, inside the lane's
 * container (RULES §5). Build and run: run-trials.sh.
 */
#define yew_pty_cases yew_pty_cases_registry
#include "registry.c"
#undef yew_pty_cases

/* The debounce's 2,000 ms plus margin, measured as output quiet. */
#define TRIAL_DEBOUNCE_QUIET_MS 2600

static void case_trial_resume_cycles20(PtyCtx *c)
{
    int cycle;

    s25_fixture_make();
    s25_spawn_bare(c);
    s25_build_session(c);
    if (c->failed) {
        s25_fixture_remove();
        return;
    }
    ptc_mark_resume(c);
    for (cycle = 0; cycle < 20 && !c->failed; cycle++) {
        /* The harness resumes once a case (harness.c:1886-1889); a cycle
         * is that resume again against the SAME first grid. */
        c->resumed = false;
        force_quit(c);
        s25_resume_bare(c);
        ptc_check_resume_exact(c);
        if (c->failed)
            (void)fprintf(stderr, "trial: cycle %d diverged\n", cycle + 1);
    }
    if (!c->failed)
        (void)fprintf(stderr, "trial: 20 cycles grid-identical\n");
    ptc_snapshot(c, "s25_resume_exact");
    force_quit(c);
    s25_fixture_remove();
}

static void trial_kill(PtyCtx *c, int how)
{
    s25_fixture_make();
    s25_spawn_bare(c);
    s25_build_session(c);
    if (c->failed) {
        s25_fixture_remove();
        return;
    }
    ptc_settle(c, TRIAL_DEBOUNCE_QUIET_MS);
    ptc_mark_resume(c);
    ptc_allow_primary(c);
    ptc_allow_restore(c);
    if (how == SIGHUP) {
        /* The terminal closed: the master end shut under the editor. */
        (void)close(c->pty.master);
        c->pty.master = -1;
        c->eof = true;
    } else if (kill(c->pty.pid, how) != 0) {
        ptc_check(c, false, "could not signal the live editor");
        s25_fixture_remove();
        return;
    }
    s25_resume_bare(c);
    ptc_check_resume_exact(c);
    ptc_snapshot(c, "s25_resume_exact");
    force_quit(c);
    s25_fixture_remove();
}

static void case_trial_restore_sigkill(PtyCtx *c)
{
    trial_kill(c, SIGKILL);
}

static void case_trial_restore_sigsegv(PtyCtx *c)
{
    trial_kill(c, SIGSEGV);
}

static void case_trial_restore_hangup(PtyCtx *c)
{
    trial_kill(c, SIGHUP);
}

/* registry.c #undefs its C() macro at its end, so the rows are spelled
 * out: {name, profile, rows, cols, fn, xfail_id}. */
const PtyCase yew_pty_cases[] = {
    {"trial_resume_cycles20", "modern", 24U, 80U, case_trial_resume_cycles20, NULL},
    {"trial_restore_sigkill", "modern", 24U, 80U, case_trial_restore_sigkill, NULL},
    {"trial_restore_sigsegv", "modern", 24U, 80U, case_trial_restore_sigsegv, NULL},
    {"trial_restore_hangup", "modern", 24U, 80U, case_trial_restore_hangup, NULL},
    {NULL, NULL, 0U, 0U, NULL, NULL}
};
